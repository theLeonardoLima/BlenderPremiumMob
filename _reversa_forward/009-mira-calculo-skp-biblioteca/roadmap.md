# Roadmap: Mira com alinhamento e cálculo no editor de paredes; SketchUp e biblioteca de objetos

> Identificador: `009-mira-calculo-skp-biblioteca`
> Data: `2026-10-08` (revisto em 2026-10-09: sessões 2 e 3 do clarify)
> Requirements: `_reversa_forward/009-mira-calculo-skp-biblioteca/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

São três incrementos independentes, entregues nesta ordem (Esclarecimentos, Q4):

- **I1, editor de paredes** (`walls2d/`):
  - dois núcleos puros, testáveis fora do Blender: `walls2d/inference.py` (alinhamento X/Y aos vértices, com índice
    ordenado) e `data/expr.py` (expressão de medida sem `eval`);
  - no `walls2d/ops_editor.py`, a resolução do ponto passa a seguir uma cadeia única de travas (RN-03), e o modo lápis
    ganha a **direção atual** na `Session`. Ela muda só por clique ou pelas setas do teclado (RN-05, RN-06);
  - a mira e as guias são desenhadas no `draw_plan`, com as funções que o `canvas2d/draw.py` já tem.
- **I2, biblioteca de objetos** (pacote novo `caffmob_draw/object_library/`):
  - cada item é um `.blend` com a raiz (grupo de peças da 007) e as conversões já gravadas nos objetos (`btm_group`,
    `btm_aggregate`). Por isso, "salvar com a folha e as chapas" é só gravar os objetos;
  - um manifesto JSON fica ao lado de cada item, e o formato segue a biblioteca de módulos do usuário
    (`customize/library_io.py`);
  - os itens que vêm com o plugin são gerados por `tools/build_object_library.py` (BMesh) e versionados no pacote;
  - a retextura cria um material de imagem com escala em mm ou usa um acabamento do plugin.
- **I3, SketchUp:**
  - o `.skp` é lido pelo **OpenSKP** (MIT, Python puro) em qualquer plataforma, com as dependências empacotadas como
    wheels da extensão;
  - as malhas são montadas direto no Blender a partir das primitivas que o OpenSKP já triangula (posições, normais, UV,
    material), sem GLB intermediário, `trimesh` nem `Pillow`;
  - cada instância vira um grupo de peças; os materiais recebem o nome do `.skp`, e as texturas vão para a pasta do
    arquivo.

## 2. Princípios aplicados

O projeto não tem `.reversa/principles.md`. Valem as regras do `CLAUDE.md`, que foram usadas como princípios nas
features anteriores.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| API do Blender 5.2 pelo RAG, verificada por `check_api.py` | Modal 2D, `bpy.data.libraries`, materiais de imagem e `bpy.utils.previews` seguem as receitas de `docs/rag/project/02_padroes_blender_5_2.md` | respeita |
| Diferenças de versão só em `compat.py` | Nenhuma diferença nova | respeita |
| Operadores que alteram dados com `UNDO` | Inserir, acrescentar, retexturizar e importar SKP têm `{'REGISTER', 'UNDO'}`. O editor de paredes segue no rascunho próprio, com o OK como um passo | respeita |
| Arquivos do usuário em `extension_path_user` | A biblioteca do usuário fica em `extension_path_user(__package__, path="object_library")` | respeita |
| Sem threads com `bpy` | A leitura do SKP e a montagem das malhas rodam no thread principal; arquivos grandes mostram progresso no cabeçalho | respeita |
| Textos novos em pt-BR, com tradução en-US | Catálogo de traduções `object_library.json` e acréscimos em `walls2d.json` e `aggregates.json` | respeita |
| Licença GPL-3.0-or-later do plugin | As dependências do SKP são MIT (`openskp`), ISC (`mapbox_earcut`), BSD (`shapely`) e PSF (`defusedxml`), todas compatíveis. Não há binário proprietário | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | `walls2d/inference.py`: as referências são os vértices das cadeias do plano (`model.Plan`) e o ponto inicial do desenho, guardados em duas listas ordenadas (por X e por Y). A busca usa `bisect` com tolerância `8 px / escala da vista` e devolve `(x travado, ref_x, y travado, ref_y)`, escolhendo a referência mais próxima em cada eixo | RN-02 (8 px na tela, Q1); o RNF de desempenho fica em O(log n) por movimento; o índice é refeito só quando o plano muda (assinatura do `history`) | Varrer todos os vértices a cada `MOUSEMOVE` (dívida D-02 do `_reversa_sdd/architecture.md#4`); quadtree (desnecessária para busca 1D por eixo) | 🟢 |
| D-02 | Uma função `resolve_point(s, view, state, cursor, shift)` concentra as travas na ordem da RN-03: ímã do início → vértice exato (`hit_node`) → alinhamento X/Y → trava ortogonal (±2,5°) → grade. Com o Shift segurado, só o alinhamento X/Y sai da cadeia (RN-02, sessão 2). Ela substitui as chamadas soltas de `preview_point` e `snap_to_grid` no clique, na prévia e na digitação | Um clique grava exatamente o ponto mostrado (RF-02) | Manter as travas espalhadas em `_handle_draw` e `_handle` (o ponto clicado e o desenhado poderiam divergir) | 🟢 |
| D-03 | Mira desenhada em `draw_plan`: duas linhas de 1 px na largura e na altura da região, na cor `grid_axis` (neutra). O eixo travado fica na cor de acento `selected`, com uma guia tracejada (`draw.dashed`) até a referência e um anel na referência | /impeccable: linhas finas e neutras, um só acento, estado também por forma (anel e tracejado), não só por cor | Mira em cor forte o tempo todo; linhas só em volta do cursor (não mostrariam o pareamento com a parede do outro lado) | 🟢 |
| D-04 | `data/expr.py`: tokenizador e analisador descendente recursivo (soma, produto, unário, parênteses). Cada número aceita vírgula ou ponto e sufixo mm, cm ou m (sem sufixo, a unidade da cena). Teto de 64 caracteres; `ValueError("Valor Inválido: …")`. O `units.parse_length` passa a delegar a ele quando o texto tem operador. A prévia "= 16 mm" aparece ao lado do texto | RN-04; RNF de segurança (sem `eval`) | `eval` com `__builtins__` vazio (inseguro); `ast` com lista de nós permitidos (aceita mais do que precisa e esconde a semântica da unidade por número) | 🟢 |
| D-05 | A `Session` ganha `direction` (radianos ou None) e `direction_source`: |  |  |  |
|  | – antes do primeiro trecho, a direção é a do cursor com a trava ortogonal; |  |  |  |
|  | – o primeiro Enter ou clique fixa a direção; |  |  |  |
|  | – a partir daí, o Enter usa só `direction`; |  |  |  |
|  | – o clique cria o ponto (com D-02) e passa a direção para a do trecho criado; |  |  |  |
|  | – ← ↑ → ↓ põem 180/90/0/270° sem criar parede; |  |  |  |
|  | – o `MOUSEMOVE` nunca mexe em `direction`. | RN-05, RN-06 (Q2 e a resposta à pendência 1) | Direção pelo afastamento do mouse (o titular recusou); direção só pelas setas (o titular quis o clique também) | 🟢 |
| D-06 | Prévia no lápis: com o texto digitado ou com uma direção travada por digitação, a linha de prévia segue `direction` e a medida digitada, não o cursor. A seta da direção fica no último ponto, e o texto mostra "→ 0°". Sem digitação, a prévia continua indo até o cursor | O usuário vê onde o Enter vai criar a parede antes de apertar | Prévia sempre até o cursor (contradiria a direção travada) | 🟢 |
| D-07 | O `_handle_typing` (modo Selecionar, medida do trecho) e o lápis aceitam a mesma expressão: os caracteres `0-9 , . + - * / ( )`, `m`, `c` e espaço | Um único comportamento de digitação no editor | Expressão só no lápis | 🟡 |
| D-08 | Pacote `object_library/`: |  |  |  |
|  | – `catalog.py`, puro: categorias, entrada do manifesto, busca; |  |  |  |
|  | – `store.py`: pastas embutida e do usuário, listagem, nomes repetidos; |  |  |  |
|  | – `item_io.py`: salvar por `bpy.data.libraries.write` e inserir por `libraries.load` com link=False; |  |  |  |
|  | – `retexture.py`, `ops.py` e `panels.py`. |  | Estender `customize/library_io.py` (ele trata módulos com adaptadores, divisões e estilos, um domínio diferente); Asset Browser do Blender (muda o fluxo do usuário e não tem categorias por manifesto nem licença) | 🟢 |
|  | Reaproveita de `customize/library_io` a miniatura (`_thumbnail`) e a caixa (`world_box`), movendo as duas para um módulo comum sem mudar o comportamento | Mesma mecânica já testada (003) |  |  |
| D-09 | A raiz de um item é um grupo de peças (`aggregates/group.create_group`, `kind='PLAIN'`, ou o FRAME de uma esquadria) com `Object.btm_object_item` (id, categoria, origem, licença). Ao acrescentar uma seleção solta, ela é agrupada antes. As conversões ficam gravadas nos próprios objetos e voltam ao inserir | RN-11: "o que o usuário configurar fica salvo no item"; usa o modelo da 007 | Guardar a configuração no manifesto e reaplicar ao inserir (duplicaria as regras da 003/007) | 🟢 |
| D-10 | Inserir: anexa os objetos do `.blend` à coleção ativa e põe a raiz no cursor 3D. Um modal próprio, `object_library.place`, faz a raiz acompanhar o mouse no plano do chão (Z do cursor 3D, por `view3d_utils.region_2d_to_location_3d`). Clique esquerdo solta, com um passo de desfazer. Esc ou botão direito cancelam e **removem** os objetos inseridos (RF-06, sessão 2) | O `transform.translate` do Blender, ao cancelar, só devolve a posição e deixaria o item na cena; o modal próprio cumpre "Esc cancela e remove" | `transform.translate` (não remove ao cancelar) | 🟢 |
| D-11 | Acrescentar à biblioteca: diálogo com Categoria (enum fixo das 7 de RN-08), Nome, Origem e Licença (texto, pré-preenchido "Uso próprio"). Duas origens: a seleção atual (agrupada por D-09) ou um arquivo, que passa por `caffmob.import_model` e é salvo em seguida. Nome repetido na categoria: Substituir ou Renomear (sufixo " 2") | RN-10 | Categorias livres (bagunçariam a grade e a tradução) | 🟢 |
| D-12 | Retexturizar, na parte ativa ou no item inteiro: |  |  |  |
|  | (a) **Acabamento do plugin**: lista dos materiais de `product_libraries/*/assets/materials` e dos já presentes no arquivo, aplicada com `common.set_cutpart_material` nas peças `GeoNodeCutpart` e por slot nas outras malhas; |  |  |  |
|  | (b) **Imagem própria**: material "Textura: <arquivo>", Principled + Image Texture com coordenadas de objeto, mapeamento em caixa (Box projection) e escala `1 / (tamanho em mm / 1000)`. |  |  |  |
|  | Vale só para a cópia na cena (RN-12). | Box projection dá escala real sem UV, o que serve para malha importada sem UV boa | Pintar UV (inviável para o usuário); trocar o material em todas as cópias (altera itens que ele não escolheu) | 🟡 |
| D-13 | Itens embutidos gerados por `tools/build_object_library.py` (BMesh, metros, origem no canto de trás e embaixo), na pasta `caffmob_draw/object_library/items/<categoria>/<id>.blend` mais o `.json` e o `.png`: |  | Baixar de acervos CC0 (Q5 escolheu modelar); modelos do 3D Warehouse (licença proíbe, RN-09) | 🟢 |
|  | – Porta lisa 80: batente FRAME + folha de giro de 90°; |  |  |  |
|  | – Janela de correr 120: esquadria + 2 folhas de correr; |  |  |  |
|  | – Cooktop 4 bocas; |  |  |  |
|  | – Mesa 120 × 80: tampo como peça de produção; |  |  |  |
|  | – Vaso; |  |  |  |
|  | – Quadro. |  |  |  |
|  | Origem "CAFFMob Draw" e licença `GPL-3.0-or-later`. Os `.blend` são versionados e o `build.py` passa a exigir os deles | Q5 (modelados pelo projeto); `CLAUDE.md` (os `.blend` do pacote são versionados) |  |  |
| D-14 | Interface (/impeccable, como o catálogo da 008), na seção **Inserir › Objetos** da barra lateral: |  |  |  |
|  | – categorias em fileira de ícones com o nome da ativa; |  |  |  |
|  | – busca por nome; |  |  |  |
|  | – grade de 2 colunas com miniatura; |  |  |  |
|  | – "Embutido" e "Meu" marcados no tooltip; |  |  |  |
|  | – estado vazio "Nenhum objeto nesta categoria"; |  |  |  |
|  | – botões Acrescentar à biblioteca, Remover (só itens do usuário) e Retexturizar (na seção Selecionado). | Padrão visual já aprovado na 008 | Lista simples (sem miniatura, pior para reconhecer objetos) | 🟢 |
| D-15 | Leitor SKP: |  |  |  |
|  | – wheels `openskp` (py3-none-any), `defusedxml` (py3-none-any), `mapbox_earcut` e `shapely` (cp313 para linux x86_64 e aarch64, win_amd64, macOS x86_64 e arm64) em `caffmob_draw/wheels/`, declaradas em `wheels = [...]` no `blender_manifest.toml`; o Blender instala só as da plataforma; |  |  |  |
|  | – `aggregates/skp.py` faz o import tardio do `openskp` e, se faltar, devolve o motivo; |  |  |  |
|  | – `SkpFile(path).parse()` e depois `build_scene()`. | Sessão 3: funciona no Linux do titular, sem DLL nem Wine; Python puro, MIT | pyslapi + DLL da Trimble (só Windows, licença do SDK, teste pelo Wine); converter para GLB pelo `openskp.export.glb` (exige `trimesh` e `Pillow` e perde os nomes dos materiais) | 🟢 |
| D-16 | Montagem no Blender (`aggregates/skp_build.py`): |  |  |  |
|  | – percorre `scene_hierarchy`: cada instância vira um grupo de peças (007) com o nome dela, e as primitivas do `geom_name` dela viram malhas (posições, índices e UV; a normal sai do próprio Blender); |  |  |  |
|  | – os materiais são criados com o nome do `.skp` (`SkpModel.materials`), a cor base e a textura; os bytes de `scene.textures` vão para `<pasta do .blend ou temporária>/skp_textures/` e entram num Image Texture; |  |  |  |
|  | – unidade em mm convertida para m; eixo conferido pelo teste (Y-up do glTF → Z-up); |  |  |  |
|  | – um erro de leitura (`SkpParseError`) não cria nada e mostra o motivo e a alternativa (RF-12). |  |  |  |
|  | O `aggregates/ops_import.py` ganha `.skp` nos FORMATS e no `filter_glob`. | RN-13, RN-14 | Importar pelo GLB (perde os nomes dos materiais e exige mais dependências) | 🟢 |
| D-17 | Testes: |  |  |  |
|  | – unitários de `inference`, `expr`, direção (núcleo da sequência de Enter), `object_library/catalog` e `store` (manifesto); |  |  |  |
|  | – fumaça `tests/blender_009_walls_smoke.py` (janela): mira, travas, sequência, setas e clique; |  |  |  |
|  | – fumaça `tests/blender_009_library_smoke.py` (fundo): acrescentar, inserir, folha, peça de produção, retextura; |  |  |  |
|  | – fumaça `tests/blender_009_skp_smoke.py` (fundo, no Linux): um `.skp` gerado pelo próprio OpenSKP (porta com batente, folha e material com textura) entra com os grupos, a escala, os nomes dos materiais e a imagem; um `.skp` corrompido não cria nada. | Padrão das features 004 a 008 | — | 🟢 |

## 4. Premissas

Nenhuma `[DÚVIDA]` ficou aberta. Ficam como premissas verificáveis:

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| O Blender 5.2 instala as wheels declaradas no manifesto e escolhe as da plataforma num pacote único | RN-13; RNF de compatibilidade | Erro ao instalar a extensão. A mitigação é gerar um pacote por plataforma (`build.py --plataforma`) |
| As primitivas do `build_scene` vêm em mm, no referencial Y-up do glTF | §2 (teste de 2026-10-09: medidas em mm) | Objeto deitado ou 1000× maior; o teste do SKP confere a caixa e a orientação |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Editor de paredes 2D (wall_editor) | `_reversa_sdd/wall_editor/requirements.md#RF-WE-01, RF-WE-05`; `walls2d/ops_editor.py`, `walls2d/props.py` | regra-alterada | Mira, cadeia de travas com alinhamento, direção travada, expressão |
| Inferência de alinhamento | — (`walls2d/inference.py`) | componente-novo | Núcleo puro com índice ordenado por eixo |
| Medidas digitadas | `data/units.py#parse_length` | regra-alterada | Delega a `data/expr.py` quando há operador |
| Expressão de medida | — (`data/expr.py`) | componente-novo | Analisador sem `eval` |
| Biblioteca de objetos | — (`object_library/`) | componente-novo | Itens com manifesto, inserir, acrescentar, retexturizar, interface |
| Biblioteca de módulos do usuário | `customize/library_io.py` | regra-alterada | Miniatura e caixa vão para um módulo comum, com o mesmo comportamento |
| Importar modelo (003/007) | `aggregates/ops_import.py` | regra-alterada | `.skp` nos formatos |
| Leitor SketchUp | — (`aggregates/skp.py`, `aggregates/skp_build.py`, `wheels/`, `blender_manifest.toml`) | componente-novo | OpenSKP e montagem das malhas no Blender |
| Barra lateral (005) | `ui/sidebar_insert.py`, `ui/sidebar_selected.py` | regra-alterada | Grupo "Objetos" no Inserir; Retexturizar no Selecionado |
| Empacotamento | `build.py` | regra-alterada | Exige os `.blend` dos itens embutidos e as wheels declaradas no manifesto |

## 6. Delta no modelo de dados

- A `Session` do editor de paredes (memória) ganha a direção atual, as travas da mira e a prévia da expressão.
- Os objetos ganham `Object.btm_object_item`.
- Cada item da biblioteca vira três arquivos: `.blend`, `.json` e `.png`. As pastas são duas: a embutida, só de
  leitura, e a do usuário.
- Nada muda em `btm_aggregate`, `btm_group` nem no JSON de produção.
- Detalhe completo em: `_reversa_forward/009-mira-calculo-skp-biblioteca/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Item da biblioteca de objetos (manifesto JSON + `.blend` + miniatura) | arquivo | `_reversa_forward/009-mira-calculo-skp-biblioteca/interfaces/object-library-item.md` |

## 8. Plano de migração

1. Não há dados antigos a migrar. A biblioteca do usuário é nova, e a pasta é criada no primeiro uso.
2. **I1:** `expr` e `inference` com os testes, depois a `Session` e o `ops_editor`. A fumaça da 002 tem de continuar
   verde, porque desenhar com clique sem digitar não muda.
3. **I2:**
   - mover a miniatura e a caixa de `library_io` para um módulo comum (a fumaça da 003 continua verde);
   - criar o pacote `object_library`;
   - rodar `tools/build_object_library.py` para gerar os itens embutidos;
   - montar a interface.
4. **I3:**
   - baixar as wheels (`tools/fetch_wheels.py`, versões fixas) e declará-las no manifesto;
   - escrever o leitor e a montagem;
   - acrescentar o `.skp` ao `ops_import`;
   - verificar com o `.skp` gerado pelo OpenSKP, aqui no Linux.
5. Traduções, guia do usuário (`docs/usuario/editor-paredes-e-mover-sobre.md` e uma página nova
   `docs/usuario/biblioteca-de-objetos.md`) e ajuste do `build.py`.

## 9. Riscos e mitigações

| ID | Risco | Mitigação |
|----|-------|-----------|
| R-01 | Uma versão nova do OpenSKP muda a API (projeto novo, de 2026-06) | Versões fixas das wheels; o `skp_build` usa só `SkpFile`, `parse`, `build_scene`, `scene_hierarchy`, `glb_primitives`, `textures` e `materials`, cobertos pelo teste |
| R-02 | Arquivos SketchUp de 2013 a 2020 que não abrem (cerca de 1 em 4) | Mensagem com o motivo e a alternativa (RF-12) |
| R-03 | Peso do pacote com as wheels de 5 plataformas (shapely tem cerca de 2 MB por plataforma) | Aceitável; se pesar, o `build.py` gera um pacote por plataforma |
| R-04 | A mira trava em pontos demais em plantas cheias, com saltos | Só vértices (sem pontos médios nesta versão); um eixo trava na referência mais próxima dentro de 8 px; o Shift segurado desliga as travas de alinhamento (como no SketchUp) |
| R-05 | Uma letra digitada (`m`, `c`) conflita com um atalho do modal | No lápis e com o texto digitado, a digitação tem prioridade; as letras só entram depois de um dígito |
| R-06 | Peso dos `.blend` embutidos | Geometria simples (até cerca de 5 mil faces por item); materiais sem imagens grandes |
| R-07 | A textura de imagem em malha sem UV fica distorcida | Box projection com coordenadas de objeto (D-12) |

## 10. Critério de pronto

- RF-01 a RF-13 cumpridos, com os cenários do `requirements.md` verificados por teste ou fumaça, todos no Linux do
  titular (o SKP inclusive).
- Ficam verdes:
  - testes unitários;
  - `ruff`;
  - `check_api.py`;
  - fumaças antigas (002, 003, 004, 005, 006, 007, 008);
  - as duas fumaças novas.
- Guia do usuário e traduções pt-BR/en-US completos; `test_i18n_coverage` verde.
