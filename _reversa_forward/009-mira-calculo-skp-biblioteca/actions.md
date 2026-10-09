# Actions: Mira com alinhamento e cálculo no editor de paredes; SketchUp e biblioteca de objetos

> Identificador: `009-mira-calculo-skp-biblioteca`
> Data: `2026-10-08`
> Roadmap: `_reversa_forward/009-mira-calculo-skp-biblioteca/roadmap.md` (D-01 a D-17)
> Data delta: `_reversa_forward/009-mira-calculo-skp-biblioteca/data-delta.md`
> Interfaces: `interfaces/object-library-item.md`
> Incrementos (roadmap §1):
> - I1 editor de paredes: T002, T005–T007, T010–T013, T023–T026, T037, T040
> - I2 biblioteca de objetos: T001, T003, T008, T014, T015, T018–T022, T027–T032, T035, T038, T041
> - I3 SketchUp (OpenSKP): T016, T033, T034, T039, T042–T046
> - T036 (traduções) atravessa os três
>
> Caminhos relativos à raiz do repositório.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 43 (T001–T046, sem T004, T009 e T017, removidas na revisão de 2026-10-09) |
| Paralelizáveis (`[//]`) | 25 |
| Maior cadeia de dependência | 12 (T008 → T014 → T015 → T018 → T019 → T027 → T028 → T029 → T030 → T031 → T032 → T038) |
| Ordem de entrega | Por incremento: I1 → I2 → I3 (Esclarecimentos, Q4). Cada incremento fecha com a sua fumaça |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | `BTM_PG_ObjectItem` (`is_item`, `item_id`, `category` com as 7 categorias, `source`, `license`) em `Object.btm_object_item`, com `register`/`unregister` (D-09) | - | `[//]` | `caffmob_draw/object_library/props.py` | 🟢 | `[X]` |
| T002 | `Session` do editor de paredes: `direction`, `direction_locked`, `lock_x`, `lock_y`, `typed_preview` e o índice de inferência; zerados em `_restore` (data-delta §1) | - | `[//]` | `caffmob_draw/walls2d/props.py` | 🟢 | `[X]` |
| T042 | Baixar as wheels com versões fixas (`openskp` 1.3.0, `defusedxml` 0.7.1, `mapbox_earcut` 2.1.0 e `shapely` 2.2.0; cp313 para linux x86_64 e aarch64, win_amd64, macOS x86_64 e arm64) em `caffmob_draw/wheels/`, por um script reprodutível, e declará-las em `wheels = [...]` no `blender_manifest.toml` (D-15) | - | `[//]` | `tools/fetch_wheels.py` | 🟡 | `[X]` |
| T003 | Mover `_thumbnail` e `world_box` de `customize/library_io.py` para um módulo comum, sem mudar o comportamento; o `library_io` passa a importar de lá (D-08) | - | `[//]` | `caffmob_draw/library_common.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T043 | Testes do núcleo SKP (puro): primitivas em mm e Y-up viram vértices em m e Z-up; instâncias da hierarquia viram grupos com o nome da instância; índice de material vira o nome do `SkpModel.materials`; textura gravada com o nome de arquivo seguro; motivo em texto para cada falha | - | `[//]` | `tests/test_skp_core.py` | 🟢 | `[X]` |
| T005 | Testes da expressão: `100`, `2*8`=16 mm, `200/2`, `(3000-150)/2`, `1,5m+20`, vírgula e ponto, unário; erros `10/0`, `2*`, `((1)`, `abc`, ≤ 0, mais de 64 caracteres, mais de 1 km (RN-04) | - | `[//]` | `tests/test_measure_expr.py` | 🟢 | `[X]` |
| T006 | Testes do alinhamento: travar X e Y a até 8 px na escala da vista; referência mais próxima; as duas travas juntas; nada fora da tolerância; o ponto inicial do desenho conta; 2.000 vértices em menos de 2 ms (RN-02, RNF) | - | `[//]` | `tests/test_wall_inference.py` | 🟢 | `[X]` |
| T007 | Testes da direção: a sequência 100, 285, 2*8, 200/2, 2000 a 0° termina em (2,501; 0); as setas dão 0/90/180/270°; o clique passa a direção para a do trecho; mover o mouse não muda nada (RN-05, RN-06) | - | `[//]` | `tests/test_wall_direction.py` | 🟢 | `[X]` |
| T008 | Testes da biblioteca: manifesto válido e inválido; `item_id` em slug; nome repetido com Substituir ou Renomear (" 2"); listagem das duas pastas; item sem `.png`; categoria desconhecida vira `OTHER`; origem "3D Warehouse" recusada na pasta embutida (interfaces/object-library-item.md) | - | `[//]` | `tests/test_object_library.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T010 | Analisador da expressão de medida, sem `eval`: tokenizador, descendente recursivo, unidade por número, teto de 64 caracteres, "Valor Inválido" (D-04) | T005 | `[//]` | `caffmob_draw/data/expr.py` | 🟢 | `[X]` |
| T011 | `parse_length` delega a `expr` quando o texto tem operador ou parênteses; o resto do comportamento não muda | T010 | - | `caffmob_draw/data/units.py` | 🟢 | `[X]` |
| T012 | Núcleo do alinhamento: índice ordenado por X e Y, consulta com `bisect` e tolerância em metros (`px / escala`), retorno `(x, ref_x, y, ref_y)` (D-01) | T006 | `[//]` | `caffmob_draw/walls2d/inference.py` | 🟢 | `[X]` |
| T013 | Núcleo da direção: `next_point(start, direction, length)`, `arrow_direction(tecla)`, `segment_direction(a, b)`, `initial_direction(start, cursor)` com a trava ortogonal (D-05) | T007 | `[//]` | `caffmob_draw/walls2d/direction.py` | 🟢 | `[X]` |
| T014 | Catálogo da biblioteca, puro: categorias com rótulo e ícone, entrada do manifesto (ler, validar, escrever), slug do `item_id`, busca por nome (D-08) | T008 | `[//]` | `caffmob_draw/object_library/catalog.py` | 🟢 | `[X]` |
| T015 | Pastas e listagem: embutida (`object_library/items`) e do usuário (`extension_path_user`); listar por categoria; nomes repetidos (Substituir/Renomear); apagar só item do usuário (D-08, D-11) | T014 | - | `caffmob_draw/object_library/store.py` | 🟢 | `[X]` |
| T016 | Leitor SKP: import tardio do `openskp`; `read(path)` devolve o `SkpModel` e a cena (`parse` + `build_scene`) ou o motivo (`SkpParseError`, dependência ausente) em texto (D-15) | T042 | - | `caffmob_draw/aggregates/skp.py` | 🟢 | `[X]` |
| T044 | Núcleo SKP puro: conversão de eixo e unidade, plano de montagem (grupo → malhas com vértices, triângulos, UV e material), nomes de materiais e de arquivos de textura (D-16) | T043 | `[//]` | `caffmob_draw/aggregates/skp_core.py` | 🟢 | `[X]` |
| T018 | Salvar item: raiz (agrupa a seleção solta com `group.create_group`), `btm_object_item`, `bpy.data.libraries.write(fake_user, RELATIVE_ALL)`, manifesto e miniatura (D-09, D-11) | T001, T003, T015 | - | `caffmob_draw/object_library/item_io.py` | 🟢 | `[X]` |
| T019 | Inserir item: `libraries.load` dos objetos, ligar à coleção ativa, raiz no cursor 3D, "Item corrompido" se faltar a raiz; devolve a raiz (D-10) | T018 | - | `caffmob_draw/object_library/item_io.py` | 🟡 | `[X]` |
| T020 | Retextura: acabamento do plugin (materiais de `product_libraries/frameless/frameless_assets/materials`, `face_frame/face_frame_assets/materials`, `closets/assets/materials` e os já presentes no arquivo, aplicados com `set_cutpart_material` ou por slot) e imagem própria (material "Textura: …", Box projection, coordenadas de objeto, escala em mm, reutilização), na parte ou no item (D-12) | T001 | `[//]` | `caffmob_draw/object_library/retexture.py` | 🟡 | `[X]` |
| T021 | Gerador dos itens embutidos (BMesh): Porta lisa 80 (FRAME + folha de giro de 90°), Janela de correr 120 (esquadria + 2 folhas), Cooktop 4 bocas, Mesa 120 × 80 (tampo como peça de produção), Vaso, Quadro; salva com `item_io` (D-13) | T018, T020 | - | `tools/build_object_library.py` | 🟢 | `[X]` |
| T022 | Rodar o gerador e versionar os itens (`.blend`, `.json`, `.png`) por categoria | T021 | - | `caffmob_draw/object_library/items/` | 🟢 | `[X]` |

| T045 | Montagem no Blender: malhas por BMesh com UV, materiais com cor base e Image Texture (bytes gravados em `skp_textures/` ao lado do `.blend` ou na pasta temporária), grupos de peças da 007 com o nome de cada instância (D-16) | T044 | - | `caffmob_draw/aggregates/skp_build.py` | 🟢 | `[X]` |
| T046 | Gerar o `.skp` de teste com o OpenSKP (porta com o componente "Batente" em material "Branco" e "Folha" em "Madeira" com textura PNG) e versioná-lo em `tests/fixtures/porta_teste.skp` | T042 | `[//]` | `tools/make_skp_fixture.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T023 | `resolve_point` com a cadeia de travas da RN-03 (ímã → vértice → alinhamento → ortogonal → grade); com o Shift segurado, só o alinhamento X/Y sai da cadeia; prévia, clique e movimento de vértice passam por ela (D-02) | T002, T012 | `[//]` | `caffmob_draw/walls2d/ops_editor.py` | 🟢 | `[X]` |
| T024 | Mira no `draw_plan`: duas linhas de 1 px na cor `grid_axis`; eixo travado em `selected` com guia tracejada e anel na referência (D-03) | T023 | - | `caffmob_draw/walls2d/ops_editor.py` | 🟢 | `[X]` |
| T025 | Lápis: digitação com expressão e prévia "= …"; o Enter usa a direção travada; o clique fixa a direção do trecho; ← ↑ → ↓ trocam a direção; a prévia segue a direção quando há digitação; seta e "→ 0°" no último ponto (D-05, D-06) | T011, T013, T024 | - | `caffmob_draw/walls2d/ops_editor.py` | 🟢 | `[X]` |
| T026 | Modo Selecionar: a medida digitada do trecho aceita expressão, com o mesmo conjunto de caracteres e a mesma prévia (D-07) | T025 | - | `caffmob_draw/walls2d/ops_editor.py` | 🟡 | `[X]` |
| T027 | Modal "Inserir objeto" (`object_library.place`): insere no cursor 3D, a raiz acompanha o mouse no plano do chão, o clique esquerdo solta (um passo de desfazer), Esc ou botão direito cancelam e removem; mais o operador Remover da biblioteca (só itens do usuário, com confirmação) (D-10) | T019 | `[//]` | `caffmob_draw/object_library/ops.py` | 🟢 | `[X]` |
| T028 | Operador Acrescentar à biblioteca: diálogo (Categoria, Nome, Origem, Licença), origem na seleção ou num arquivo (via `caffmob.import_model`), Substituir/Renomear (D-11) | T027 | - | `caffmob_draw/object_library/ops.py` | 🟢 | `[X]` |
| T029 | Operadores de retextura: Acabamento (lista) e Imagem própria (seletor de arquivo + tamanho em mm), na parte ativa ou no item inteiro, com UNDO (D-12) | T020, T028 | - | `caffmob_draw/object_library/ops.py` | 🟡 | `[X]` |
| T030 | Interface da biblioteca (/impeccable, padrão da 008): categorias em ícones com o nome da ativa, busca, grade de 2 colunas com miniatura, "Embutido"/"Meu" no tooltip, estado vazio, botões (D-14) | T029 | - | `caffmob_draw/object_library/panels.py` | 🟢 | `[X]` |
| T031 | Barra lateral: grupo "Objetos" em Inserir (`ui/sidebar_insert.py`) e Retexturizar na seção Selecionado (`ui/sidebar_selected.py`) para objetos que são item ou peça de item | T030 | - | `caffmob_draw/ui/sidebar_insert.py`, `caffmob_draw/ui/sidebar_selected.py` | 🟢 | `[X]` |
| T032 | Registro do pacote `object_library` (props, ops, previews) e ligação no `register` da extensão; o `unregister` desfaz tudo | T031 | - | `caffmob_draw/object_library/__init__.py` | 🟢 | `[X]` |
| T033 | `.skp` no `import_model`: entra nos FORMATS e no `filter_glob`, lê pelo `aggregates/skp` e monta pelo `skp_build`; a unidade e o eixo da 007 não se aplicam ao SKP, que já vem em metros e Z-up (D-16) | T016, T045 | `[//]` | `caffmob_draw/aggregates/ops_import.py` | 🟢 | `[X]` |
| T034 | Falha de leitura do SKP: nada é criado; o relatório mostra "Não foi possível ler o SketchUp: <motivo>. Salve numa versão recente ou exporte em glTF/OBJ/FBX"; arquivos grandes mostram o progresso no cabeçalho (RF-12) | T033 | - | `caffmob_draw/aggregates/ops_import.py` | 🟢 | `[X]` |
| T035 | `build.py`: exige os `.blend` dos itens embutidos e as wheels declaradas no manifesto; recusa um manifesto embutido com origem "3D Warehouse" | T022, T042 | - | `build.py` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T036 | Traduções pt-BR/en-US: mira, expressão, direção, biblioteca, retextura e SketchUp, em `walls2d.json`, `aggregates.json` e no novo `object_library.json`; `test_i18n_coverage` verde | T026, T031, T034 | `[//]` | `caffmob_draw/data/translations/object_library.json`, `walls2d.json`, `aggregates.json` | 🟢 | `[X]` |
| T037 | Fumaça do editor de paredes (janela): mira travando a 8 px e ponto pareado exato; Shift; sequência 100/285/2*8/200/2/2000; mouse sem clique mantém a direção; setas; clique muda a direção; `10/0` inválido; depois do OK, os cinco trechos colineares continuam separados (RN-07); a fumaça da 002 continua verde | T026 | `[//]` | `tests/blender_009_walls_smoke.py` | 🟢 | `[X]` |
| T038 | Fumaça da biblioteca (fundo): itens embutidos listados; inserir a porta e abrir a folha a 90°; mesa com o tampo no plano de corte; retextura por acabamento e por imagem; acrescentar um OBJ, reabrir noutro Blender e inserir com a folha; Substituir/Renomear | T032, T022 | `[//]` | `tests/blender_009_library_smoke.py` | 🟢 | `[X]` |
| T039 | Fumaça do SKP (fundo, no Linux): `tests/fixtures/porta_teste.skp` entra com os grupos "Batente 1" e "Folha 1", em pé, na escala certa, com os materiais "Branco" e "Madeira" e a imagem da textura carregada; um `.skp` corrompido não cria nada e mostra o motivo | T034, T046 | `[//]` | `tests/blender_009_skp_smoke.py` | 🟢 | `[X]` |
| T040 | Guia do usuário: mira, alinhamento, Shift, expressão e direção travada no editor de paredes | T026 | `[//]` | `docs/usuario/editor-paredes-e-mover-sobre.md` | 🟢 | `[X]` |
| T041 | Guia novo da biblioteca de objetos: inserir (clique solta, Esc cancela), acrescentar, conversões, retextura, SketchUp (versões, limite de 2013 a 2020, alternativa) e como usar modelos do 3D Warehouse dentro da licença | T032, T034 | `[//]` | `docs/usuario/biblioteca-de-objetos.md` | 🟢 | `[X]` |

## Notas de execução

- T023 a T026 compartilham `walls2d/ops_editor.py`, T018 e T019 compartilham `item_io.py`, T027 a T029 compartilham
  `object_library/ops.py`, e T033 e T034 compartilham `aggregates/ops_import.py`: são sequenciais.
- Tudo é verificável no Linux do titular, inclusive o SketchUp, com o `.skp` gerado pelo OpenSKP (T046).
- Premissa a conferir no T042: o Blender 5.2 instala só as wheels da plataforma a partir de um pacote único. Se não
  instalar, o `build.py` (T035) passa a gerar um pacote por plataforma.

- 2026-10-09, `/reversa-coding` (rodada única, 43 ações):
  - **Premissa das wheels confirmada:** o zip instalado num Blender 5.2 limpo (`extension install-file`) teve as
    wheels da plataforma instaladas em `extensions/.local/lib/python3.13/site-packages`, e o `openskp` passou a ser
    importável pela extensão. Não é preciso um pacote por plataforma.
  - **T042:** o `pip` do Python do sistema está quebrado. O `tools/fetch_wheels.py` baixa pela API JSON do PyPI e
    confere o SHA-256.
  - **T037:** a fumaça do editor de paredes roda em fundo, acionando os tratadores do modal como a da 002. O desenho
    da mira na janela é exercitado pela `blender_002_ui_events.py`, que abre o editor de verdade e passou.
  - **Testes antigos ajustados à RN-06** (o mouse sem clique não muda a direção): `blender_002_smoke.py` e
    `blender_002_ui_events.py` passaram a trocar a direção pelas setas.
  - **Teste antigo ajustado à RN-04:** `test_units` aceitava a decisão PL-03 da 001 ("3/4" recusado como fração de
    polegada). Agora `3/4` é conta, 0,75 mm; pés e polegadas continuam recusados.
  - **`blender_003_aggregates_smoke.py`** usava `.skp` como formato não suportado; agora usa `.3ds`.
  - **Clique do lápis:** a trava é calculada no próprio clique a partir do pixel do evento (não só no `MOUSEMOVE`),
    para o clique e o desenho nunca divergirem.
  - **Fixture do SketchUp (T046, linha `corrected` no progress):** a primeira versão tinha a folha invadindo o
    montante em 0,75 pol, e a colisão da 007 a travava. A folha passou a caber entre os montantes.
  - **`.gitignore`:** a regra `wheels/` ignorava `caffmob_draw/wheels/`, e um clone sairia sem o leitor de SketchUp.
    Foi acrescentada a exceção `!caffmob_draw/wheels/`.
  - **`test_packaging.test_blends_do_pacote_estao_no_git`** só passa depois do commit dos 6 `.blend` novos de
    `object_library/items/`. O commit fica a cargo do titular.

## Ações removidas (IDs não reciclados)

| ID | Motivo |
|----|--------|
| T004 | Vendorizar o pyslapi e a DLL da Trimble: substituído pelo OpenSKP (Esclarecimentos, sessão 3); as wheels entram por T042 |
| T009 | Testes da disponibilidade do SKP por plataforma: o OpenSKP roda em todas; o teste do núcleo é T043 |
| T017 | `importer.py` adaptado do pyslapi: substituído por T044 e T045 |

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-08 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-10-09 | Revisão depois das sessões 2 e 3 do clarify e da auditoria: SketchUp pelo OpenSKP (T042–T046 novas; T004, T009 e T017 removidas; T016, T033 a T035 e T039 reescritas); Shift (T023); inserção com Esc que remove (T027); A003 (T039), A004 (T020), A005 (T031, T036) e A006 (T037) | reversa |
