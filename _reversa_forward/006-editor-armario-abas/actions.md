# Actions: Editor de armário reformulado em abas (Estrutura e Divisão)

> Identificador: `006-editor-armario-abas`
> Data: `2026-10-08`
> Roadmap: `_reversa_forward/006-editor-armario-abas/roadmap.md` (D-01 a D-15)
> Data delta: `_reversa_forward/006-editor-armario-abas/data-delta.md`
> Interfaces: `_reversa_forward/006-editor-armario-abas/interfaces/user-module-file.md`
> Incrementos:
> - I1: núcleos puros (T005–T010)
> - I2: abas e Divisão
> - I3: Estrutura
> - I4: produção e persistência
>
> Caminhos relativos à raiz do repositório.
>
> Premissa do roadmap §4: os modos Estender e Reduzir só no `btm` e na base do frameless. Nos demais casos aparecem
> desabilitados com o motivo. Ações afetadas: T010, T013–T018. Se o titular ampliar esse escopo, essas ações ganham
> emendas.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 39 |
| Paralelizáveis (`[//]`) | 24 |
| Maior cadeia de dependência | 11 (T006 → T010 → T011 → T019 → T020 → T021 → T022 → T026 → T035 → T038 → T039) |
| Ordem de entrega | I1 → I2 → I3 → I4. A passada de desenho com `/impeccable` (T025) vem antes dos painéis (T026–T028) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | `BTM_PG_StructureItem`, `BTM_PG_Structure` (`Object.btm_structure`) e `BTM_PG_Division` (`Object.btm_division`) com os campos de data-delta §1.1 e §1.2, `register` e `unregister` (este remove as propriedades de `bpy.types.Object`) | - | `[//]` | `caffmob_draw/cabinet_editor/data_props.py` | 🟢 | `[X]` |
| T002 | Campos novos em `BTM_PG_CabinetEditorState`: `tab`, `new_orientation`, `new_use_front/back`, `new_front/back` (padrão 0,02 m), `space` (enum dinâmico com cache), espelhos `structure`/`divisions` com índices e `remove_mode` (data-delta §1.3, D-01, D-14) | - | `[//]` | `caffmob_draw/cabinet_editor/props.py` | 🟢 | `[X]` |
| T003 | `BTM_PG_CabinetProperties`: `has_top/bottom/back/left/right` (padrão True), `extend_mode_*` e `thickness_*` (0 = `thickness`), todos com `update_cabinet_geom` (data-delta §1.4) | - | `[//]` | `caffmob_draw/data/properties.py` | 🟡 | `[X]` |
| T004 | `EditorState` ganha `structure` (dict) e `divisions` (list). `signature` inclui os dois, arredondados a 1 µm (D-11) | - | `[//]` | `caffmob_draw/cabinet_editor/state.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T005 | Testes do núcleo de divisões, cobrindo: caminhos `s0`, `s0.a`, `s0.b`; folhas depois de cortes aninhados; medidas vertical e horizontal com e sem recuos (20/10 mm); posição nova no meio; `DIV-001` (subvão < 50 mm) e `DIV-002` (profundidade < 50 mm); `reflow` que preserva a posição a partir da face esquerda/de baixo quando o espaço-raiz cresce | - | `[//]` | `tests/test_cabinet_editor_divisions.py` | 🟢 | `[X]` |
| T006 | Testes do núcleo da estrutura: efeito de KEEP, EXTEND e SHRINK nas medidas externas e no vão interno, por papel (tampo, base, fundo, laterais); filtro por capacidade (modo não suportado vira `STR-001` com o motivo); restaurar devolve o estado anterior | - | `[//]` | `tests/test_cabinet_editor_structure.py` | 🟡 | `[X]` |
| T007 | Testes de `signature`: mudar só `structure` ou só `divisions` muda a assinatura; diferenças abaixo de 1 µm não mudam | T004 | `[//]` | `tests/test_cabinet_editor_state.py` | 🟢 | `[X]` |
| T008 | Testes do manifesto 1.1.0: 1.0.0 continua válido; `structure`/`divisions` opcionais; erros para `role`, `mode`, `orientation` desconhecidos, `space` mal formado e medida negativa | - | `[//]` | `tests/test_module_manifest.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | Núcleo puro de divisões (sem `bpy`): `Space`, `Division`, `leaves`, `add`, `place` (caixa da chapa no referencial da raiz), `middle_offset`, `validate` (`DIV-001`, `DIV-002` como `validate.Message` de erro) e `reflow` (D-04, D-05) | T005 | `[//]` | `caffmob_draw/cabinet_editor/divisions.py` | 🟢 | `[X]` |
| T010 | Núcleo puro da estrutura (sem `bpy`): papéis, modos, `apply_mode` (medidas externas e vão), filtro por capacidade (`STR-001`), aviso de espessura que invade o vão (`STR-002`) (D-08, D-09) | T006 | `[//]` | `caffmob_draw/cabinet_editor/structure.py` | 🟡 | `[X]` |
| T011 | Contrato dos adaptadores: `inner_spaces`, `structure_parts`, `structure_caps`, `remove_part`, `restore_part`, `set_part_thickness`. A implementação padrão devolve "não suportado" com o motivo. O mesmo arquivo ganha o auxiliar comum para esconder e reafirmar uma peça (D-07) | T010 | - | `caffmob_draw/customize/adapters/common.py` | 🟡 | `[X]` |
| T012 | `generate_cabinet_mesh` gera só os painéis `has_*`, com espessura por componente, e aplica EXTEND/SHRINK na conta das vizinhas. Sem campos novos, a malha sai idêntica à de hoje (D-08, roadmap §8) | T003 | `[//]` | `caffmob_draw/geometry/mesh_gen.py` | 🟡 | `[X]` |
| T013 | Adaptador `btm`: `inner_spaces` (caixa interna da malha), `structure_parts` e `structure_caps` (três modos nas cinco peças), `remove_part`/`restore_part`/`set_part_thickness` pelos campos de T003 | T011, T012 | `[//]` | `caffmob_draw/customize/adapters/btm.py` | 🟡 | `[X]` |
| T014 | Adaptador frameless, parte 1: `inner_spaces` (jaulas `IS_FRAMELESS_BAY_CAGE`), `structure_parts` por nome (Left/Right Side, Bottom, Top, Back) e `structure_caps` (só KEEP, mais EXTEND na base via `Remove Bottom`, e o motivo nos demais) | T011 | `[//]` | `caffmob_draw/customize/adapters/frameless.py` | 🟡 | `[X]` |
| T015 | Adaptador frameless, parte 2: `remove_part`/`restore_part`. A idprop `btm_removed` entra no driver de esconder que já existe (`or btm_removed`) ou cria um driver novo; a base em EXTEND usa `Remove Bottom` (D-07, D-08) | T014 | - | `caffmob_draw/customize/adapters/frameless.py` | 🟡 | `[X]` |
| T016 | Adaptador frameless, parte 3: `set_part_thickness` tira o driver de `Thickness` da peça e grava o valor, mantendo a face externa. Voltar ao padrão (0) recria o driver de `'Material Thickness'` (D-09) | T015 | - | `caffmob_draw/customize/adapters/frameless.py` | 🟡 | `[X]` |
| T017 | Adaptador closets: `inner_spaces` (jaulas de abertura por bay), `structure_parts` (painel 0 e N como laterais, fundo e tampo por bay), `structure_caps` (KEEP), remoção e espessura gravadas para reafirmar após o recálculo | T011 | `[//]` | `caffmob_draw/customize/adapters/closets.py` | 🟡 | `[X]` |
| T018 | Adaptador face frame: `inner_spaces` (`bay_cage_dims`), `structure_parts` por `hb_part_role`, `structure_caps` (KEEP), remoção e espessura gravadas para reafirmar após o recálculo | T011 | `[//]` | `caffmob_draw/customize/adapters/face_frame.py` | 🟡 | `[X]` |
| T019 | Divisões na cena: criar, atualizar e apagar o objeto `CabinetPart` "Divisória N" filho da raiz, com `btm_division` e `btm_component='DIV'`. Material e espessura vêm do Configurador (`sheet_key(line, 'DIV', …)`, linha em `btm_line`) e o acabamento do grupo `INTERNO` (D-03, D-06) | T001, T009, T011 | - | `caffmob_draw/cabinet_editor/scene_divisions.py` | 🟢 | `[X]` |
| T020 | `scene_divisions.reflow(root)`: lê `inner_spaces` do adaptador, aplica `divisions.reflow` e atualiza os objetos. Não faz nada quando a assinatura dos espaços não mudou (D-10) | T019 | - | `caffmob_draw/cabinet_editor/scene_divisions.py` | 🟡 | `[X]` |
| T021 | Ponte: `read_state`/`apply_state` leem e reaplicam `structure` e `divisions`. `edit` ganha `ADD_DIVISION`, `EDIT_DIVISION`, `REMOVE_DIVISION`, `EDIT_PART`, `REMOVE_PART` e `RESTORE_PART` (D-11) | T004, T010, T020 | - | `caffmob_draw/cabinet_editor/bridge.py` | 🟢 | `[X]` |
| T022 | Operadores internos (sem `UNDO`, só `Session.push`): adicionar divisão com as opções de T002; editar posição, recuos, material e espessura; remover divisão; editar, remover (com modo) e restaurar componente | T002, T021 | - | `caffmob_draw/cabinet_editor/ops_actions.py` | 🟢 | `[X]` |
| T023 | Modal do editor: executa os pedidos novos; `refresh` soma `DIV-*` e `STR-*`; `_sync_ui` espelha estrutura e divisões; o clique na área livre da vista escolhe o subvão (D-13) | T022 | - | `caffmob_draw/cabinet_editor/ops_editor.py` | 🟡 | `[X]` |
| T024 | Vista frontal: subvão escolhido destacado e com o nome em texto; componentes removidos desenhados tracejados com "removido" | T002, T009 | `[//]` | `caffmob_draw/cabinet_editor/window.py` | 🟡 | `[X]` |
| T025 | Passada de desenho com `/impeccable` restrita a `UILayout`. Decide as abas (nome definitivo de "Acabamento"), o rodapé sempre visível, a lista de componentes externos, as opções antes de Adicionar e a lista de divisões, e registra o resultado em `design/editor-abas.md` (D-01, D-02) | T002 | - | `_reversa_forward/006-editor-armario-abas/design/editor-abas.md` | 🟡 | `[X]` |
| T026 | Painéis: cabeçalho com `prop_tabs_enum`, `poll` por aba nos painéis da 004 e o rodapé sempre visível (Mensagens, Ajustes, Desfazer/Refazer, Confirmar/Cancelar/Fechar, Salvar como módulo), conforme T025 (D-01, D-02) | T022, T025 | `[//]` | `caffmob_draw/cabinet_editor/panels.py` | 🟡 | `[X]` |
| T027 | Aba Estrutura: medidas com faixa, lista dos componentes externos (medidas, material, espessura, "alterado neste armário"/"removido"), Remover com escolha de modo (desabilitado com motivo, RN-07), Restaurar e o aviso do face frame | T022, T025 | `[//]` | `caffmob_draw/cabinet_editor/panels_structure.py` | 🟡 | `[X]` |
| T028 | Aba Divisão: material e espessura do Configurador, orientação, recuos com medidas, subvão escolhido, Adicionar, lista de divisões editável, "Distribuir por quantidade" (antigo "Divisões internas…") e aviso do face frame | T022, T025 | `[//]` | `caffmob_draw/cabinet_editor/panels_divisions.py` | 🟡 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T029 | `has_custom` considera `btm_structure` e divisões. `after_rebuild` reafirma remoções e espessuras pelo adaptador e chama `scene_divisions.reflow` | T013, T016, T017, T018, T020 | - | `caffmob_draw/customize/reapply.py` | 🟡 | `[X]` |
| T030 | Handler `depsgraph_update_post` `@persistent` que chama `reflow` só nos módulos com divisão cuja assinatura de espaços mudou. Registrado e removido no `register`/`unregister` (D-10) | T020 | `[//]` | `caffmob_draw/cabinet_editor/reflow_handler.py` | 🟡 | `[X]` |
| T031 | `part_roles.classify` respeita `btm_component` antes do nome e do papel (D-12) | - | `[//]` | `caffmob_draw/cutting/part_roles.py` | 🟢 | `[X]` |
| T032 | `synthetic_records` do `btm` sem componente removido, com espessura por componente e somando as divisões filhas como peças `DIV` (D-12) | T012, T031 | - | `caffmob_draw/cutting/part_sources.py` | 🟢 | `[X]` |
| T033 | Manifesto 1.1.0: `structure` e `divisions` opcionais em `build`; validação conforme `interfaces/user-module-file.md` (D-15) | T008 | `[//]` | `caffmob_draw/customize/manifest.py` | 🟢 | `[X]` |
| T034 | Salvar e importar módulo com estrutura e divisões. Na importação os `uid` são renovados, modo não suportado vira KEEP com aviso, e depois roda o `reflow` | T020, T033 | - | `caffmob_draw/customize/library_io.py` | 🟡 | `[X]` |
| T035 | Registro do pacote do editor: `data_props`, `reflow_handler`, `panels_structure` e `panels_divisions` na ordem certa; o `unregister` desfaz tudo | T001, T026, T027, T028, T030 | - | `caffmob_draw/cabinet_editor/__init__.py` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T036 | Traduções pt-BR/en-US dos textos novos: abas ("Structure", "Divisions"), modos, recuos, `DIV-*`/`STR-*`, avisos do face frame e da capacidade | T023, T026, T027, T028 | `[//]` | `caffmob_draw/data/translations/editor_grudar.json` | 🟢 | `[X]` |
| T037 | Ajustar a fumaça da 004 à navegação por abas: os painéis que ela abre agora dependem da aba | T035 | `[//]` | `tests/blender_004_cabinet_editor_smoke.py` | 🟡 | `[X]` |
| T038 | Fumaça da 006 nas quatro bibliotecas. Cobre: abas e rodapé; adicionar, mover e remover divisão (vertical com recuo na frente, horizontal num subvão); erro `DIV-001`; remover e restaurar lateral (KEEP), EXTEND na base do frameless e os três modos no `btm`; Cancelar; Confirmar = um desfazer; plano de corte; salvar e reabrir o `.blend`; mudar a largura fora do editor (reflow) | T029, T032, T034, T035 | - | `tests/blender_006_cabinet_editor_tabs_smoke.py` | 🟡 | `[X]` |
| T039 | Guia do usuário: abas, Estrutura (modos e limites por biblioteca), Divisão (subvão, recuos, Configurador) e o aviso do face frame | T038 | - | `docs/usuario/editor-de-armario.md` | 🟢 | `[X]` |

## Notas de execução

- T011 define o contrato que T013–T018 implementam. Os quatro adaptadores podem ser feitos em paralelo depois dele.
- T014, T015 e T016 compartilham o arquivo do frameless e por isso são sequenciais.
- T025 depende de uma passada humana de desenho (`/impeccable`). Se ela não for feita, T026–T028 seguem o D-02 do
  roadmap como está.
- T036: o arquivo `editor_grudar.json` já guarda os textos do editor da 004. Se o volume crescer, separar em
  `cabinet_editor.json`.
- 2026-10-08 (rodada única, T001–T039): desvios e decisões tomadas no código, sem mudar o escopo:
  - T025: o `/impeccable shape` virou `design/editor-abas.md`. O titular escolheu "✕ abre uma janela com os 3 modos"
    e o nome **Acabamento** para a terceira aba. Por isso `remove_mode` saiu do painel (data-delta §1.3).
  - T028: "Distribuir por quantidade" (o antigo "Divisões internas…" da 003) ficou na aba **Acabamento**, dentro de
    Personalizar, e não na aba Divisão. Ele mexe no interior **da biblioteca** e depende do vão selecionado na lista
    de componentes; levá-lo para a aba Divisão juntaria dois mecanismos diferentes no mesmo lugar.
  - T010/T021: o material editável da chapa é o **material da chapa** (MDF, MDP…), que vai para o plano de corte
    (`btm_raw_material`), e não o acabamento visual, que continua na aba Acabamento. O tampo usa o componente `BAS`
    do Configurador, como o legado já fazia na produção.
  - T013/T019: o `btm` ganhou `structure_info` e `elevation_parts` no contrato (a malha é única, então as chapas
    entram na vista frontal como peças sintéticas).
  - T030: o frameless muda medidas trocando de quadro (`run_calc_fix`), o que não gera `depsgraph_update_post`. O
    handler também escuta `frame_change_post`; a fumaça pegou o caso (a divisória não acompanhava a altura).
  - T023: o editor sempre abre na aba Estrutura (RF-01); a fumaça pegou a aba anterior "grudando" entre aberturas.
  - T032: a tupla de peças do `btm` foi reordenada para o scanner de traduções não confundir nomes de peça com itens
    de enum.
  - T037: a fumaça da 004 passou sem ajuste (ela não depende da aba ativa).
  - Fora do escopo, encontrado e não corrigido: `customize/library_io.load` usa a variável `missing` também quando o
    módulo não tem manifesto (`NameError` nesse caso). É anterior à feature.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-08 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-10-08 | `/reversa-coding`: T001–T039 concluídas; notas de execução | reversa |
