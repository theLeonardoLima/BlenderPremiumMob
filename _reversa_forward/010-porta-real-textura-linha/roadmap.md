# Roadmap: Porta real na parede, modo "Textura com linha" e hierarquia do SketchUp

> Identificador: `010-porta-real-textura-linha`
> Data: `2026-10-09`
> Requirements: `_reversa_forward/010-porta-real-textura-linha/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

São quatro incrementos, nesta ordem.

- **I1, hierarquia do SketchUp:** correção da 009 em `aggregates/skp_core.py` e `skp_build.py`.
  - O plano de montagem vira árvore, pelo `scene_hierarchy`.
  - Figuras de escala são puladas.
  - Material igual é reaproveitado.
  - Os testes usam `.skp` gerados pelo projeto.
- **I2, modo de vista:** o `ui/view_mode.py` novo, com Sólido · Textura e o interruptor Linhas. O modo fica salvo na
  cena e é reaplicado ao abrir o arquivo.
- **I3, porta real:**
  - O gerador do Codex (`docs/porta_realista_080x210/gerar_porta.py`) vira um núcleo puro e paramétrico,
    `openings/door_core.py`. Ele devolve a lista de peças pela largura, pela altura e pela espessura da parede.
  - O `openings/build.py` monta a porta no Blender em **poucas malhas por papel** (marco, folha, ferragens da folha,
    ferragens do marco), não em 157 objetos.
  - A porta vai dentro da caixa (`GeoNodeCage`), que continua cortando a parede, e passa para arame (`WIRE`).
  - A folha é uma folha de giro da 003/007.
  - O `openings/sync.py` refaz a porta quando a caixa muda de medida, com uma assinatura para não refazer à toa.
- **I4, janela real:** o mesmo caminho para `place_window`.
  - O `openings/window_core.py` é original: marco de alumínio, 2 folhas de correr com vidro, trilhos, puxadores e
    peitoril.
  - As folhas correm até os batentes (007).
  - Acabamento e prévia seguem os presets da `blender-product-polish`.

## 2. Princípios aplicados

O projeto não tem `.reversa/principles.md`. Valem as regras do `CLAUDE.md`.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| API do Blender 5.2 pelo RAG + `check_api.py` | BMesh, materiais, `View3DShading`/`View3DOverlay` e `load_post` conferidos no RAG antes de usar | respeita |
| Handlers com `@persistent` e remoção no `unregister` | O `load_post` que reaplica o modo de vista entra e sai com o pacote | respeita |
| Operadores que alteram dados com `UNDO` | "Atualizar portas e janelas" e os prompts têm `{'REGISTER', 'UNDO'}` | respeita |
| Sem threads com `bpy` | A montagem roda no thread principal | respeita |
| Textos em pt-BR com en-US | `openings.json` novo, mais acréscimos em `ui`, `aggregates` e `operators` | respeita |
| `.blend`/assets do pacote versionados; `build.py` confere | A textura de nogueira vai em `openings/assets/`, e o `build.py` exige os arquivos | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | `skp_core.plan` devolve uma **árvore**: cada nó do `scene_hierarchy` (instância ou grupo) vira um `GroupPlan` com `path`, `parent_path` e as malhas próprias (primitivas cujo `mesh_index[...].path` é exatamente o dele); nós sem malha também viram grupo (contêiner) | RN-07; auditoria A004: hoje tudo vira grupo de topo | Achatar e reparentar depois por nome (frágil com nomes repetidos, como `Component_1055` duas vezes) | 🟢 |
| D-02 | Filtro de figuras de escala em `skp_core`: nome ou definição casando com `^2D[_ ]?(Woman\|Man\|Person\|Figure)` ou com os nomes das figuras padrão do SketchUp (Sandra, Chris, Susan, Lily, Derrick, Laura, Nancy, Bryce, Steve, Mark, Ivan); o nó e os descendentes saem, e a contagem vai para o relatório | RN-08; A005 | Filtrar pelo número de faces (pegaria móveis pequenos) | 🟡 |
| D-03 | `skp_build`: |  |  |  |
|  | – cria os grupos de baixo para cima: o grupo filho é parentado ao grupo pai mantendo o mundo, e o contêiner sem malha é um Empty com `btm_group` (`kind PLAIN`); |  |  |  |
|  | – reaproveita o material marcado `btm_skp_material` com o mesmo nome base, a mesma cor e a mesma imagem; |  |  |  |
|  | – nome `Layer_<x>` vira `<x>`. | RN-07, RN-09; A007 | Material novo por importação (estado atual: `.001`, `.002`…) | 🟢 |
| D-04 | Fixtures do SketchUp geradas pelo projeto (`tools/make_skp_fixture.py` ampliado): `porta_aninhada.skp` (folha 75 × 200 com 3 dobradiças e a maçaneta **dentro** da definição da folha, figura `2D_Woman_Standing_Teste`, material `Layer_Layer0`). A fixture da 009 continua | RN-07 a RN-09; Q5 (sem `.skp` do 3D Warehouse) | Usar os arquivos do titular (removidos; licença) | 🟢 |
| D-05 | Modo de vista na **cena**: `Scene.btm_view_mode` (`SOLID`/`TEXTURE`) e `Scene.btm_view_lines` (bool). O update aplica em todas as áreas `VIEW_3D` da janela: |  |  |  |
|  | – `shading.type = 'SOLID'`; |  |  |  |
|  | – `shading.color_type = 'TEXTURE'` ou o anterior, guardado; |  |  |  |
|  | – `overlay.show_wireframes` com `wireframe_threshold` 0,5 (arestas de forma, sem triangulação) e `wireframe_opacity` 0,6. |  |  |  |
|  | Um `load_post` (`@persistent`) reaplica ao abrir o arquivo. | RN-06 (Q2: todos os objetos, com interruptor); salvo no arquivo | Por objeto (`show_wire`): pesado e perde-se em objetos novos; modo Material Preview (custa GPU, e o titular pediu linha + textura) | 🟡 |
| D-06 | Interface: na seção Construir, um controle segmentado (Sólido · Textura) com o interruptor Linhas ao lado e o estado escrito ("Textura com linha"), no padrão da 008/009 | /impeccable; RN-06 | Menu suspenso (esconde o estado) | 🟢 |
| D-07 | `openings/door_core.py`, puro: `door_parts(width, height, wall, swing, double=False, open_door=False)` → lista de `Part(role, name, shape, box/cyl, material, moving_leaf)`, com as medidas do gerador do Codex: |  |  |  |
|  | – folha de 40 mm, 8 mm acima do piso; |  |  |  |
|  | – montantes de 110 mm, travessas, 2 almofadas e frisos; |  |  |  |
|  | – marco de 46 mm com a **profundidade igual à espessura da parede**; |  |  |  |
|  | – batentes e vedação; guarnições de 72 mm com filete nos dois lados; |  |  |  |
|  | – 3 dobradiças; maçanetas a 1.020 mm, roseta, chave e testa. |  |  |  |
|  | Larguras e alturas variam; ferragens e perfis têm tamanho fixo. A dupla tem duas folhas e a fechadura no encontro. O vão aberto só tem marco e guarnições. | RN-01, RN-02; Q1 (modelo do Codex) | Escalar a malha fixa de 80 × 210 (distorce ferragens e guarnições); importar o OBJ (7,6 MB, sem parâmetros) | 🟢 |
| D-08 | `openings/build.py`: junta as peças em malhas por papel (BMesh): |  |  |  |
|  | – **Marco** (marco, batentes, guarnições, filetes, vedações); |  |  |  |
|  | – **Folha** (madeira da folha); |  |  |  |
|  | – **Ferragens da folha** (maçanetas, dobradiças da folha, testa); |  |  |  |
|  | – **Ferragens do marco**. |  |  |  |
|  | Os materiais vão por slot; UV de caixa por face como no gerador (veio orientado por peça); um modificador Bevel de 1 mm (limite por ângulo) + Weighted Normal por malha. Resultado: cerca de 5 objetos por porta e 3 mil faces, contra 157 objetos. | RNF de desempenho; lacuna "157 objetos" | Um objeto por peça (157 por porta); malha única (a folha precisa mover separada) | 🟡 |
| D-09 | Materiais compartilhados por arquivo: |  |  |  |
|  | – "Nogueira verniz acetinado" (Principled + cor e rugosidade + bump), com as texturas do Codex convertidas para JPG em `openings/assets/` (cerca de 0,6 MB), carregadas uma vez (`check_existing`); |  |  |  |
|  | – "Aço inox escovado", "Borracha EPDM", "Cavidades" e "Latão"; |  |  |  |
|  | – na janela, "Alumínio anodizado" e "Vidro". | Lacuna "texturas de 2 MB por porta" | Gerar a textura com numpy a cada porta (lento); PNG de 3,8 MB | 🟢 |
| D-10 | Montagem na caixa: |  |  |  |
|  | – grupo **FRAME** "Porta" filho da caixa, centrado por drivers como a janela instalada da 007 (`aggregates/install.py`: x = Dim X/2, y = Dim Y/2); |  |  |  |
|  | – a folha é um grupo **LEAF** filho do FRAME; `leaf.make_leaf(SWING)` com `hinge` e `swing_sign` do símbolo (`Is Left` → LEFT/RIGHT, `Swing Inside` → IN/OUT), ângulo máximo de 90°; |  |  |  |
|  | – a caixa passa a `display_type = 'WIRE'`, e o texto "DOOR" fica escondido na vista 3D (`hide_viewport`); o símbolo 2D continua; |  |  |  |
|  | – "Mostrar caixas de portas e janelas" mostra ou esconde a caixa em arame. | RN-01, RN-03, RN-04; a colisão da folha ignora objetos `WIRE` (`aggregates/collision.py`, `_SKIP_DISPLAY`) | Porta solta fora da caixa (perde o deslizar e o apagar com a parede, R-04 a R-07) | 🟢 |
| D-11 | `openings/sync.py`: `sync(context, cage)` refaz a porta ou a janela quando muda a assinatura (Dim X, Y e Z, tipo, lado, sentido): |  |  |  |
|  | – guarda e devolve o `open_value` e as marcações de produção; |  |  |  |
|  | – é chamado no fim da colocação, no `door_prompts`/`window_prompts`, depois do `walls2d/apply.py` e por "Atualizar portas e janelas"; |  |  |  |
|  | – no arraste da colocação **não** refaz, só ao soltar. | RN-02, RNF de desempenho, RF-06 | Refazer por handler do depsgraph a cada mudança (caro e reentrante) | 🟡 |
| D-12 | Produção: as peças da porta não são agregadas como peça de produção por padrão (`production_part` falso); a folha pode ser marcada pela seção Selecionado da 003 | RN-05 | Entrar no corte por padrão (porta pronta não é chapa do marceneiro) | 🟢 |
| D-13 | Medidas padrão em `hb_props.py`: `door_single_width` 0,80, `door_double_width` 1,60, `door_height` 2,10. Só valem para portas novas; as existentes guardam as suas | RN-02 (Q4) | — | 🟢 |
| D-14 | `openings/window_core.py`, original, no espírito do gerador da porta: |  |  |  |
|  | – marco de alumínio de 40 mm com a profundidade da parede e guarnições; |  |  |  |
|  | – 2 folhas de correr (perfil de 35 mm, vidro de 4 mm), trilhos superior e inferior; |  |  |  |
|  | – puxadores concha; peitoril de granito de 20 mm com pingadeira. |  |  |  |
|  | Folhas LEAF `SLIDE` com `slide_limits` (007). Medidas pela caixa da janela. | RN-10 (Q3) | Reaproveitar a esquadria importada da 007 (é do usuário) | 🟡 |
| D-15 | `blender-product-polish` (Q3): |  |  |  |
|  | – no material da janela, alumínio e vidro com os parâmetros do preset (rugosidade baixa, coat 1,0, IOR alto); |  |  |  |
|  | – em `tools/render_openings_preview.py`, os presets `studio` (key 350 W, fill 250, rim 250, bounce 100; EEVEE) aplicados em segundo plano, gerando `openings/assets/previa_porta.png` e `previa_janela.png` (miniaturas e guia). |  |  |  |
|  | A skill original roda pelo Blender MCP (porta 9876) com GLB; aqui os mesmos valores são aplicados por script. | Q3; lacuna "MCP" | Exigir o Blender MCP aberto (não roda em CI nem em segundo plano) | 🟡 |
| D-16 | "Atualizar portas e janelas" (`caffmob.openings_update`): percorre os objetos com `IS_ENTRY_DOOR_BP`/`IS_WINDOW_BP` sem `btm_opening` e chama `sync`; também é oferecido ao abrir um arquivo antigo, por aviso na barra lateral, nunca automático | RN-04, RF-06 | Converter ao abrir o arquivo (altera o projeto sem pedir) | 🟢 |
| D-17 | Testes: |  |  |  |
|  | – unitários de `door_core`, `window_core`, da árvore e do filtro do `skp_core` e da regra de reaproveitamento de material; |  |  |  |
|  | – fumaças em segundo plano: `blender_010_openings_smoke.py` (colocar, medidas, giro, colisão, mudar largura e espessura, Atualizar), `blender_010_view_mode_smoke.py` (shading e overlay, salvar e reabrir) e `blender_010_skp_tree_smoke.py`; |  |  |  |
|  | – as fumaças da 002, 004, 005, 007 e 009 continuam verdes. | Padrão das features 004 a 009 | — | 🟢 |

## 4. Premissas

Nenhuma `[DÚVIDA]` ficou aberta. Ficam como premissas verificáveis:

| Premissa | Origem | Risco se errada |
|----------|--------|-----------------|
| `overlay.wireframe_threshold` 0,5 mostra as arestas de forma sem a triangulação nas malhas da porta e dos móveis | RN-06 | Linhas demais ou de menos; o limiar fica numa constante, ajustada no teste visual |
| Juntar as peças por papel mantém o visual do gerador (veios, chanfros) | D-08 | Diferença de acabamento; a mitigação é comparar a prévia com `docs/porta_realista_080x210/previa.png` |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Portas e janelas de ambiente | `operators/doors_windows.py` (`_PlaceWallObjectBase`, prompts); `_reversa_sdd/domain.md#R-04..R-08` | regra-alterada | A caixa vira arame; porta e janela reais dentro dela; sync no fim e nos prompts |
| Propriedades do projeto | `hb_props.py` (medidas padrão, `update_show_entry_door_and_window_cages`) | regra-alterada | 80/160 × 210; o toggle mostra a caixa em arame |
| Aberturas reais | — (`openings/`: `door_core`, `window_core`, `build`, `sync`, `ops`, `assets/`) | componente-novo | Geradores paramétricos e montagem |
| Editor de paredes | `walls2d/apply.py` | regra-alterada | Depois de aplicar, `sync` nas aberturas das paredes mudadas |
| Leitor de SketchUp (009) | `aggregates/skp_core.py`, `skp_build.py` | regra-alterada | Árvore, figuras de escala, materiais |
| Barra lateral (005) | `ui/sidebar_build.py`; novo `ui/view_mode.py` | regra-alterada / componente-novo | Modo de vista e interruptor Linhas; aviso "Atualizar portas e janelas" |
| Empacotamento | `build.py` | regra-alterada | Exige `openings/assets/` |

## 6. Delta no modelo de dados

- Novos dados:
  - `Scene.btm_view_mode`, `Scene.btm_view_lines`;
  - `Object.btm_opening` na caixa: tipo, assinatura, versão do modelo;
  - em memória, a árvore do `skp_core` com o caminho do pai.
- Mudam os padrões de `hb_props` (portas novas).
- Detalhe completo em: `_reversa_forward/010-porta-real-textura-linha/data-delta.md`

## 7. Delta de contratos externos

Nenhum. Não há formato de arquivo novo, e o JSON de produção não muda.

## 8. Plano de migração

1. **I1:** testes e núcleo da árvore do SketchUp; fixture aninhada; `skp_build`. As fumaças da 009 continuam verdes.
2. **I2:** propriedades da cena, aplicação nas vistas, `load_post`, controle na barra lateral.
3. **I3:**
   - `door_core` com testes;
   - textura de nogueira em JPG nos `assets`;
   - `build` e `sync`;
   - ligação no `doors_windows` (colocação, prompts) e no `walls2d/apply`;
   - medidas padrão;
   - Atualizar portas e janelas.
4. **I4:** `window_core`; montagem com folhas de correr; prévia em estilo `product-polish`.
5. Traduções, guia do usuário e `build.py`.
6. Os arquivos `docs/porta_realista_080x210/` ficam como referência local. Só o `gerar_porta.py` e o LEIA-ME entram
   no repositório, como origem documentada do modelo; o OBJ, o `.blend` e o zip ficam fora (gerados).

## 9. Riscos e mitigações

| ID | Risco | Mitigação |
|----|-------|-----------|
| R-01 | A folha esbarra na própria caixa ou no marco ao abrir | Caixa em `WIRE` (ignorada pela colisão); marco no FRAME, com o batente como parada da 007; teste de 90° na fumaça |
| R-02 | Refazer a porta a cada mudança deixa o arraste lento | `sync` só ao soltar e por assinatura (D-11); cerca de 5 objetos por porta |
| R-03 | O booleano com a caixa em arame deixa de cortar | O booleano usa a geometria, não o modo de exibição; a fumaça confere o furo |
| R-04 | Arquivos antigos com a porta em caixa | Nada muda sem "Atualizar"; o aviso na barra lateral sugere |
| R-05 | Linhas em todos os objetos poluem plantas grandes | Interruptor Linhas (Q2); limiar e opacidade ajustáveis em constante |
| R-06 | `.skp` com nós muito profundos (centenas de grupos) | Contêineres vazios colapsam (um nó sem malha e com um filho só vira o filho), e o relatório informa a contagem |

## 10. Critério de pronto

- RF-01 a RF-13 cumpridos, com os cenários do requirements por teste ou fumaça.
- Verdes:
  - unitários, `ruff` e `check_api`;
  - fumaças antigas (002, 003, 004, 005, 006, 007, 008, 009);
  - as 3 fumaças novas.
- A prévia da porta parametrizada em 80 × 210 fica visualmente equivalente à `previa.png` do Codex.
- Traduções completas; `test_i18n_coverage` verde; guia atualizado.
