# Actions: Porta real na parede, modo "Textura com linha" e hierarquia do SketchUp

> Identificador: `010-porta-real-textura-linha`
> Data: `2026-10-09`
> Roadmap: `_reversa_forward/010-porta-real-textura-linha/roadmap.md` (D-01 a D-17)
> Data delta: `_reversa_forward/010-porta-real-textura-linha/data-delta.md`
> Interfaces: nenhuma
> Incrementos (roadmap §1):
> - I1 SketchUp: T004, T005, T009, T010, T031, T033
> - I2 modo de vista: T008, T011, T023, T024, T030
> - I3 porta real: T001-T003, T006, T012, T014, T015, T017, T019-T022, T025, T026, T029, T032, T034
> - I4 janela real: T007, T013, T016, T018, T027
> - T028 (traduções) atravessa os quatro
>
> Caminhos relativos à raiz do repositório.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 34 (T001–T034) |
| Paralelizáveis (`[//]`) | 23 |
| Maior cadeia de dependência | 7 (T006 → T012 → T014 → T016 → T018 → T019 → T028) |
| Ordem de entrega | I1 → I2 → I3 → I4, cada um fechando com a sua fumaça |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | `BTM_PG_Opening` em `Object.btm_opening` (`kind`, `signature`, `model_version`, `assembly`), com `register`/`unregister` (data-delta §2) | - | `[//]` | `caffmob_draw/openings/props.py` | 🟢 | `[X]` |
| T002 | Converter as texturas de nogueira do Codex (PNG 1024 × 2048, cor e rugosidade) para JPG em `caffmob_draw/openings/assets/`, por script reprodutível em segundo plano (D-09) | - | `[//]` | `tools/build_openings_assets.py` | 🟢 | `[X]` |
| T003 | Medidas padrão das portas novas: simples 0,80, dupla 1,60, altura 2,10 (D-13) | - | `[//]` | `caffmob_draw/hb_props.py` | 🟢 | `[X]` |
| T004 | Gerar `tests/fixtures/porta_aninhada.skp` pelo OpenSKP: folha 75 × 200 com 3 dobradiças e a maçaneta **dentro** da definição da folha, batente, figura `2D_Woman_Standing_Teste` e material `Layer_Layer0` (D-04) | - | `[//]` | `tools/make_skp_fixture.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T005 | Testes da árvore do SketchUp: nós aninhados com `parent_path` e malhas próprias; contêiner sem malha vira grupo; figura de escala (nome e definição) sai com os descendentes e é contada; `Layer_Layer0` → `Layer0`; contêiner com um filho só colapsa (R-06) | - | `[//]` | `tests/test_skp_tree.py` | 🟢 | `[X]` |
| T006 | Testes da porta paramétrica: 80 × 210 numa parede de 150: folha de 800 × 40 × 2100 a 8 mm do piso; marco com profundidade 150; maçaneta a 1020 mm; 3 dobradiças; largura 900: ferragens com o mesmo tamanho; lado e sentido do símbolo; dupla com 2 folhas; vão aberto sem folha; papéis das peças | - | `[//]` | `tests/test_door_core.py` | 🟢 | `[X]` |
| T007 | Testes da janela paramétrica: 120 × 100 com marco de alumínio de 40 mm, 2 folhas de correr com sobreposição no meio, vidro de 4 mm, trilhos, puxadores e peitoril; medidas pela caixa | - | `[//]` | `tests/test_window_core.py` | 🟡 | `[X]` |
| T008 | Testes do modo de vista (puro): Sólido/Textura × Linhas → `shading.color_type`, `show_wireframes`, limiar e opacidade; voltar a Sólido devolve o `color_type` anterior | - | `[//]` | `tests/test_view_mode.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | `skp_core`: plano em árvore pelo `scene_hierarchy` (nó → malhas próprias, `parent_path`), filtro de figuras de escala, contêiner que colapsa, nome de material sem `Layer_` (D-01, D-02) | T005 | - | `caffmob_draw/aggregates/skp_core.py` | 🟢 | `[X]` |
| T010 | `skp_build`: grupos de baixo para cima, filho dentro do pai mantendo o mundo, Empty de contêiner com `btm_group`, reaproveitamento de material igual (nome base, cor, imagem), contagem de figuras no relatório (D-03) | T009, T004 | - | `caffmob_draw/aggregates/skp_build.py` | 🟢 | `[X]` |
| T011 | Núcleo do modo de vista: `settings(mode, lines, previous_color)` → valores de shading e overlay; constantes de limiar 0,5 e opacidade 0,6 (D-05) | T008 | `[//]` | `caffmob_draw/ui/view_mode_core.py` | 🟡 | `[X]` |
| T012 | `door_core`: peças da porta pela largura, altura, espessura da parede, lado e sentido, a partir do gerador do Codex: folha, almofadas, frisos, marco, batentes, vedações, guarnições, dobradiças, maçanetas, testa; variantes dupla e vão aberto (D-07) | T006 | `[//]` | `caffmob_draw/openings/door_core.py` | 🟢 | `[X]` |
| T013 | `window_core`: peças da janela pela caixa: marco de alumínio, 2 folhas de correr, vidro, trilhos, puxadores concha, peitoril com pingadeira (D-14) | T007 | `[//]` | `caffmob_draw/openings/window_core.py` | 🟡 | `[X]` |
| T015 | Materiais compartilhados por arquivo: Nogueira verniz acetinado (cor + rugosidade + bump dos JPG), Aço inox escovado, Borracha EPDM, Cavidades, Latão, Alumínio anodizado e Vidro (valores da `product-polish`), reaproveitados pelo nome e por uma marca (D-09, D-15) | T002 | `[//]` | `caffmob_draw/openings/materials.py` | 🟢 | `[X]` |
| T014 | Montagem da porta: junta as peças por papel (Marco, Folha, Ferragens da folha, Ferragens do marco) em BMesh, com slots de material, UV de caixa com veio por peça e Bevel 1 mm por ângulo + Weighted Normal (D-08) | T012, T015 | - | `caffmob_draw/openings/build.py` | 🟡 | `[X]` |
| T016 | Montagem da janela no mesmo módulo: Marco/Peitoril, Folha 1 e Folha 2 (perfil + vidro + puxador), Trilhos (D-08, D-14) | T013, T014 | - | `caffmob_draw/openings/build.py` | 🟡 | `[X]` |
| T017 | `sync` da porta na caixa: grupo FRAME filho da caixa, centrado por drivers (padrão da 007); folha LEAF com `make_leaf(SWING)`, `hinge` e `swing_sign` do símbolo; caixa em `WIRE` e texto escondido na 3D; assinatura que pula o que não mudou; devolve o `open_value` e a marcação de produção ao refazer (D-10, D-11, D-12) | T001, T014 | - | `caffmob_draw/openings/sync.py` | 🟡 | `[X]` |
| T018 | `sync` da janela: folhas LEAF `SLIDE` com limites nos batentes (`slide_limits` da 007), mesmo FRAME e assinatura | T016, T017 | - | `caffmob_draw/openings/sync.py` | 🟡 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T019 | `doors_windows`: `sync` ao confirmar a colocação (não no arraste) e no `door_prompts`/`window_prompts`; caixa nova já em `WIRE` (D-10, D-11) | T017, T018 | - | `caffmob_draw/operators/doors_windows.py` | 🟡 | `[X]` |
| T020 | "Mostrar caixas de portas e janelas" mostra ou esconde a caixa em arame (não volta ao sólido) (RN-04) | T017 | - | `caffmob_draw/hb_props.py` | 🟢 | `[X]` |
| T021 | Editor de paredes: depois de aplicar o plano, `sync` nas aberturas das paredes que mudaram de espessura (D-11) | T017 | `[//]` | `caffmob_draw/walls2d/apply.py` | 🟡 | `[X]` |
| T022 | Operador "Atualizar portas e janelas" (`caffmob.openings_update`, UNDO): caixas com `kind NONE` ou versão antiga → `sync`; relatório com as quantidades (D-16) | T017 | `[//]` | `caffmob_draw/openings/ops.py` | 🟢 | `[X]` |
| T023 | Modo de vista na cena: `Scene.btm_view_mode`, `btm_view_lines`, `btm_view_prev_color` com update que aplica em todas as `VIEW_3D`; `load_post` `@persistent` reaplica; `unregister` desfaz (D-05) | T011 | `[//]` | `caffmob_draw/ui/view_mode.py` | 🟡 | `[X]` |
| T024 | Barra lateral, seção Construir: controle segmentado Sólido · Textura, interruptor Linhas e o estado escrito; aviso "Atualizar portas e janelas" quando houver caixas antigas (D-06, D-16) | T022, T023 | - | `caffmob_draw/ui/sidebar_build.py` | 🟢 | `[X]` |
| T025 | Registro do pacote `openings` (props, ops) e do `ui/view_mode` na extensão | T001, T022, T023 | - | `caffmob_draw/openings/__init__.py` | 🟢 | `[X]` |
| T026 | `build.py` exige `openings/assets/` (as texturas JPG) | T002 | `[//]` | `build.py` | 🟢 | `[X]` |
| T027 | Prévia em estilo `blender-product-polish` (preset `studio`: key 350 W, fill 250, rim 250, bounce 100; EEVEE) da porta 80 × 210 e da janela 120 × 100 em `openings/assets/previa_*.png`; comparar com a `previa.png` do Codex (D-15) | T016, T018 | - | `tools/render_openings_preview.py` | 🟡 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T028 | Traduções pt-BR/en-US: porta e janela, Atualizar, modos de vista, Linhas e relatório do SketchUp, em `openings.json` (novo), `sidebar.json`, `aggregates.json` e `operators.json`; `test_i18n_coverage` verde | T010, T019, T024 | `[//]` | `caffmob_draw/data/translations/openings.json` | 🟢 | `[X]` |
| T029 | Fumaça das aberturas (fundo): porta 80 × 210: peças, sem "DOOR" visível, furo na parede igual, folha a 90° e parando num armário; largura 900 sem distorcer ferragens; espessura da parede pelo editor; dupla e vão aberto; janela com folhas correndo; Atualizar num arquivo com caixa antiga; fumaças 002, 004 e 005 verdes | T019, T020, T021, T022, T025 | `[//]` | `tests/blender_010_openings_smoke.py` | 🟢 | `[X]` |
| T030 | Fumaça do modo de vista (fundo): settings aplicados na `View3DShading`/`Overlay` de uma tela, salvar e reabrir mantém o modo, `load_post` reaplica | T023, T024 | `[//]` | `tests/blender_010_view_mode_smoke.py` | 🟢 | `[X]` |
| T031 | Fumaça da árvore do SketchUp (fundo): `porta_aninhada.skp` com a folha contendo 4 ferragens, a figura ignorada no relatório, reimportação com um material `Layer0`, converter a folha leva as ferragens | T010, T004 | `[//]` | `tests/blender_010_skp_tree_smoke.py` | 🟢 | `[X]` |
| T032 | Guia: porta e janela reais, medidas padrão, Atualizar portas e janelas, modo de vista e Linhas | T024, T019 | `[//]` | `docs/usuario/editor-paredes-e-mover-sobre.md` | 🟢 | `[X]` |
| T033 | Guia da biblioteca: SketchUp com hierarquia, figuras de escala ignoradas, materiais reaproveitados | T010 | `[//]` | `docs/usuario/biblioteca-de-objetos.md` | 🟢 | `[X]` |
| T034 | Repositório: de `docs/porta_realista_080x210/` só `gerar_porta.py` e `LEIA-ME.md` entram; OBJ, MTL, PNG, `.blend` e o zip no `.gitignore` (roadmap §8.6) | - | `[//]` | `.gitignore` | 🟢 | `[X]` |

## Notas de execução

- T014 e T016 compartilham `openings/build.py`, T017 e T018 compartilham `openings/sync.py`, e T003 e T020
  compartilham `hb_props.py`: são sequenciais, e o T020 não é `[//]`.
- Cadeia mais longa: T006 → T012 → T014 → T016 → T018 → T019 → T028.

- 2026-10-09, `/reversa-coding` (rodada única, 34 ações):
  - **Nome do dado:** o legado já registra `Object.btm_opening` (`data/properties.py`, `BTM_PG_OpeningProperties`).
    O dado da 010 passou a se chamar `Object.btm_opening_real` (data-delta §2, com o mesmo conteúdo).
  - **Medida da porta = folha:** a largura e a altura digitadas (colocação, prompts) são as da folha, e a caixa ganha
    o marco e a folga (`door_core.hole_size`: + 98 mm na largura, + 59 mm na altura). A largura por dois pontos na
    parede continua sendo a do furo.
  - **Lado e sentido medidos no Blender:** `Swing Inside` desenha o arco no −Y da caixa, e `Is Left` põe a dobradiça
    em x = largura da caixa.
  - **Defeitos achados nas fumaças e corrigidos:**
    - a folha batia no próprio marco (dobradiças intercaladas, lingueta na contratesta): a colisão da 003/007 passou
      a ignorar o marco da montagem para as folhas dela (`aggregates/collision.py`, `btm_opening_frame`);
    - a folha girava pelo canto da caixa com as maçanetas (8 cm à frente) e entrava na parede: o grupo da folha
      passou a ter só a madeira, com as ferragens como filhas;
    - os grupos da montagem nasciam alinhados ao mundo, e numa parede girada a janela corria para o lado errado e a
      dobradiça trocava de lado: os grupos foram alinhados aos eixos da caixa;
    - a janela não tinha batente porque o marco deixou de ser obstáculo: o curso de cada folha passou a ser
      geométrico (`window_core.travel`, 535 mm em 1,20 m).
  - **Texto "DOOR":** também é anotação 2D. Fica escondido; o símbolo de giro continua.
  - **Duplicatas do SketchUp:** instâncias repetidas têm o mesmo caminho (as 3 dobradiças). Cada primitiva vai para a
    instância cuja origem (`position_mm`) fica mais perto.
  - **T030:** a fumaça do modo de vista roda com janela (xvfb), porque em segundo plano não há vista 3D.
  - **`test_packaging.test_blends_do_pacote_estao_no_git`** continua vermelho até o commit dos 6 `.blend` da
    biblioteca da 009, a cargo do titular.
  - **Peso:** 4 malhas e cerca de 2.200 faces por porta (contra 157 objetos); textura de nogueira em JPG de 0,55 MB,
    compartilhada; pacote de 60,6 MB.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-09 | Versão inicial gerada por `/reversa-to-do` | reversa |
