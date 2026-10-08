# Actions: Editor de armário, grudar em superfície plana e colisão

> Identificador: `004-editor-armario-grudar`
> Data: `2026-10-07`
> Roadmap: `_reversa_forward/004-editor-armario-grudar/roadmap.md` (D-01 a D-27)
> Data delta: `_reversa_forward/004-editor-armario-grudar/data-delta.md`
> Interfaces: nenhuma (sem contrato externo)
> Incrementos: I1 grudar (`stick/`); I2 colisão (`collision/`); I3 editor de armário (`cabinet_editor/`).
>
> Caminhos relativos à raiz do repositório.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 60 |
| Paralelizáveis (`[//]`) | 22 |
| Maior cadeia de dependência | 10 (T006 → T009 → T014 → T045 → T046 → T047 → T048 → T051 → T058 → T060) |
| Ordem de entrega | I1 → I2 → I3; I3 pode ser adiado sem afetar I1 e I2 |

## Fase 1, Preparação

Núcleos puros, propriedades, preferências e pacotes.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | `aggregates/limits.box_for` ganha `clamp=True` opcional (padrão preserva o comportamento da 003), para o grudar reaproveitar sem limite de contorno (D-01) | - | `[//]` | `caffmob_draw/aggregates/limits.py` | 🟢 | `[X]` |
| T002 | Núcleo puro do grudar: referencial da face `BOX_SIDE` (seis lados da caixa local, via `face_axes`/`box_for(clamp=False)`) e `PLANE` (matriz local); posição do item ↔ (`u`, `v`, `distance`, `spin`); projeção de um ponto no plano; teste "item fora da face" (D-01, D-02, RN-06, RN-08a) | T001 | - | `caffmob_draw/stick/frame.py` | 🟢 | `[X]` |
| T003 | Núcleo puro do grudar: face plana (todos os vértices a ≤ 0,5 mm do plano) e escolha do tipo de face (`BOX_SIDE` se a normal coincide ≤ 1° com um lado e o ponto está a ≤ 0,5 mm dele, senão `PLANE`) (RN-05, D-02) | T002 | - | `caffmob_draw/stick/frame.py` | 🟢 | `[X]` |
| T004 | Núcleo puro de caixa orientada: sobreposição de duas caixas orientadas por eixo no referencial de A, profundidade (mínimo dos três eixos), eixo e sentido para fora (D-12, D-19) | - | `[//]` | `caffmob_draw/collision/obb.py` | 🟢 | `[X]` |
| T005 | Núcleo puro das regras de colisão: entrada = itens (nome, tipo, caixa, raiz, pai de agregado, hospedeiro e face de grudado, parede da abertura, `collision_override`); pares excluídos (RN-12); classificação contato ≤ 1 mm / colisão / penetração em parede ou obstáculo / piso e teto (RN-11); uma ocorrência por par; ordem estável (RN-13) | T004 | - | `caffmob_draw/collision/rules.py` | 🟢 | `[X]` |
| T006 | `walls2d/history.History` recebe a função de assinatura (padrão `model.plan_signature`, comportamento do editor de paredes preservado) (D-21) | - | `[//]` | `caffmob_draw/walls2d/history.py` | 🟢 | `[X]` |
| T007 | Núcleo puro da elevação: caixas das peças no referencial da raiz → retângulos (x, z) com nome, tipo e frente/vão; diferença antes × depois (`MOVED`/`RESIZED`/`ADDED`/`REMOVED`) excluindo o alvo da edição (D-23, D-25) | - | `[//]` | `caffmob_draw/cabinet_editor/elevation.py` | 🟢 | `[X]` |
| T008 | Núcleo puro da validação: mensagem `{code, severity, component, parameter, value, range, action, blocks}`; `DIM-001..003` (vazio, não numérico, fora da faixa; faixa = `editing.LIMITS` estreitada pela biblioteca); `GEO-001` fora do volume (+1 mm); `GEO-002` peças internas sobrepostas (via `collision/obb.py`, sem pares estruturais que só se tocam); `CAT-001` seção sem suporte (D-24, RN-03) | T004 | - | `caffmob_draw/cabinet_editor/validate.py` | 🟡 | `[X]` |
| T009 | Núcleo puro do estado do editor: `EditorState(dimensions, spec_dict)`, instantâneo inicial, pilha com o `History` genérico, `dirty()` (D-21) | T006 | - | `caffmob_draw/cabinet_editor/state.py` | 🟢 | `[X]` |
| T010 | `Object.btm_stick` (`BTM_PG_Stick`, todos os campos do data-delta §1.1) com `update` de `u`/`v`/`distance`/`spin` chamando `stick.apply.update_position` (import tardio); `register`/`unregister` | - | `[//]` | `caffmob_draw/stick/props.py` | 🟢 | `[X]` |
| T011 | Preferências do add-on: `stick_magnet` (padrão ligado) e `stick_magnet_distance` (50 mm, 1 a 500 mm) em `BTM_AddonPreferences`, com a linha no `draw` (data-delta §1.2, RN-10a, D-06) | - | `[//]` | `caffmob_draw/__init__.py` | 🟢 | `[X]` |
| T012 | `btm_settings.stick_migrated` (Bool) em `BTM_PG_SceneSettings` (data-delta §1.3, D-08) | - | `[//]` | `caffmob_draw/data/properties.py` | 🟢 | `[X]` |
| T013 | `WindowManager.btm_collision` (`BTM_PG_CollisionState` + `BTM_PG_Collision`, data-delta §1.4) com `register`/`unregister` | - | `[//]` | `caffmob_draw/collision/props.py` | 🟢 | `[X]` |
| T014 | `WindowManager.btm_cabinet_editor` (campos virtuais sobre a sessão, coleções `messages` e `adjustments`, data-delta §1.5) e o singleton de sessão (raiz, estado, vista 2D, janela, pedido pendente) | T009 | - | `caffmob_draw/cabinet_editor/props.py` | 🟢 | `[X]` |
| T015 | Extrair abrir janela, focar a aba, fechar depois e `is_editor_area` de `walls2d/window.py` para `canvas2d/window.py`, com a categoria do painel como parâmetro; o editor de paredes passa a usar o comum, sem mudança visível (D-20) | - | `[//]` | `caffmob_draw/canvas2d/window.py` | 🟢 | `[X]` |
| T016 | `tests/_bootstrap.py`: incluir `stick`, `collision` e `cabinet_editor` na lista `_stub` | - | `[//]` | `tests/_bootstrap.py` | 🟢 | `[X]` |

## Fase 2, Testes

Testes `unittest` dos núcleos puros.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T017 | Testes do grudar: ida e volta posição ↔ parâmetros nas seis faces; hospedeiro de 150 → 200 mm mantém o item em `POS_Y` encostado (≤ 0,1 mm); 10 mudanças seguidas sem erro acumulado; `PLANE` inclinado; fora da face; face não plana recusada; escolha `BOX_SIDE` × `PLANE` | T003, T016 | `[//]` | `tests/test_stick_frame.py` | 🟢 | `[X]` |
| T018 | Testes das regras de colisão: encostado a 0,5 mm não gera ocorrência; 20 mm na parede = penetração de 20 mm; pares excluídos (mesmo módulo, agregado × pai, grudado × hospedeiro, abertura × parede, `OFF`); caixa girada; uma ocorrência por par; ordem igual em duas execuções | T005, T016 | `[//]` | `tests/test_collision_rules.py` | 🟢 | `[X]` |
| T019 | Testes da elevação: retângulos de um módulo de 2 vãos; diferença detecta frente movida, prateleira redimensionada, gaveta adicionada e removida, sem listar o alvo | T007, T016 | `[//]` | `tests/test_cabinet_editor_elevation.py` | 🟢 | `[X]` |
| T020 | Testes da validação: `DIM-001`, `DIM-002`, `DIM-003` com a faixa; `GEO-001` prateleira acima do topo; `GEO-002` duas gavetas sobrepostas; `blocks` só em erro | T008, T016 | `[//]` | `tests/test_cabinet_editor_validate.py` | 🟡 | `[X]` |
| T021 | Testes do `History` com assinatura própria; os testes do editor de paredes continuam passando | T006 | `[//]` | `tests/test_walls2d_history.py` | 🟢 | `[X]` |
| T022 | Testes do estado do editor: instantâneo inicial, três edições e dois desfazer, refazer, `dirty()` | T009, T016 | `[//]` | `tests/test_cabinet_editor_state.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

**I1. Grudar**

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T023 | `stick.apply.update_position(item)`: caixa local avaliada do hospedeiro + `btm_stick` → matriz pelo `frame`; grava só quando muda; guarda `last_world` | T003, T010 | - | `caffmob_draw/stick/apply.py` | 🟢 | `[X]` |
| T024 | Handler `depsgraph_update_post` `@persistent`: caixa do hospedeiro mudou → reposiciona os itens dele; item grudado movido (inclusive G nativo) → projeta no plano, recalcula `u`/`v` e restaura `distance`/`spin`; ignora as atualizações que ele mesmo causou; índice hospedeiro → itens refeito só quando `btm_stick` muda (D-04, RN-07) | T023 | - | `caffmob_draw/stick/apply.py` | 🟡 | `[X]` |
| T025 | Vínculo perdido e fora da face no handler: hospedeiro ausente ou `parent` diferente → restaura `last_world`, apaga o vínculo e avisa "Vínculo perdido: <item>"; item fora da face → `out_of_face` e aviso "Item fora da face: <item>", pela barra de status de `ui/save_feedback` (função de exibir passa a ser pública) (D-10, RN-08, RN-08a) | T024 | - | `caffmob_draw/stick/apply.py` | 🟡 | `[X]` |
| T026 | `stick.link.stick(item, host, hit)` e `release(item)`: valida a face (`frame`), escolhe o tipo, gira o item para a normal, encosta o lado de trás da caixa, parentesco com inversa identidade e `orig_parent`; recusa agregado ("Desconverter antes"); `release` volta o pai anterior mantendo a matriz de mundo (D-03, D-05, D-07, RN-09) | T023 | - | `caffmob_draw/stick/link.py` | 🟢 | `[X]` |
| T027 | Operadores com `UNDO`: `caffmob.stick_to_face` (modal: clique faz `Scene.ray_cast` excluindo o item; face não plana → "A face não é plana" e nada muda) e `caffmob.stick_release` (RF-11, RF-16) | T026 | - | `caffmob_draw/stick/ops_stick.py` | 🟢 | `[X]` |
| T028 | `caffmob.stick_move`: modal restrito ao plano da face (matemática do mover agregado sem clamp), ímã para trocar de face, Esc devolve; `UNDO` (RF-13, D-07) | T027, T031 | - | `caffmob_draw/stick/ops_stick.py` | 🟡 | `[X]` |
| T029 | `stick.migrate.run(scene)`: módulos raiz filhos de `GeoNodeWall` sem vínculo ganham `NEG_Y`/`POS_Y` pela regra de `measure/scene_cotas._on_front_side`, `u`/`v` pela caixa e `distance` = recuo atual; não move nada; idempotente com `stick_migrated` (D-08, RN-10) | T026, T012 | - | `caffmob_draw/stick/migrate.py` | 🟢 | `[X]` |
| T030 | `hb_snap.best_hit` devolve também a normal do acerto, sem mudar os chamadores atuais (D-06) | - | `[//]` | `caffmob_draw/hb_snap.py` | 🟢 | `[X]` |
| T031 | `stick.magnet.candidate(hit, item_box, prefs)`: com ímã ligado e acerto numa face plana a até a distância, devolve a pose encostada e girada para a normal; senão `None` (RN-10a, D-06) | T003, T030, T011 | - | `caffmob_draw/stick/magnet.py` | 🟡 | `[X]` |
| T032 | `hb_placement.PlacementMixin`: fora da regra de parede de cada biblioteca, a prévia usa `magnet.candidate`; confirmar grava o vínculo por `stick.link` (RF-12) | T031, T026 | - | `caffmob_draw/hb_placement.py` | 🟡 | `[X]` |
| T033 | Override de apagar: o `poll` também aceita hospedeiros com itens grudados; antes de apagar, solta cada item no lugar e avisa "Vínculo perdido: <item>" (D-07, RF-15) | T026 | - | `caffmob_draw/aggregates/ops_aggregate.py` | 🟢 | `[X]` |
| T034 | "Converter em agregado" e "Converter em folha de porta" recusam item grudado com "Desgrudar antes" (data-delta §5) | T033 | - | `caffmob_draw/aggregates/ops_aggregate.py` | 🟢 | `[X]` |
| T035 | Painel do grudar (filho do painel de propriedades): "Elemento filho de: <hospedeiro> — <face>", `u`/`v`/`distance`/`spin`, aviso fora da face, botões Grudar/Mover/Desgrudar; no hospedeiro, a lista "Elementos filhos" (RF-17, D-11) | T027 | - | `caffmob_draw/stick/panels.py` | 🟢 | `[X]` |

**I2. Colisão**

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T036 | `collision.scan.collect(scene, scope)`: itens (`classify.movable_root`, eletrodomésticos, agregados, portas/janelas) e estáticos (`floor_builder.scene_walls`, `IS_FLOOR_BP`, `IS_CEILING_BP`, obstáculos) com caixa orientada avaliada e os dados de exclusão; ignora cortadores, anotações, cotas, `WIRE`/`BOUNDS` e ocultos (D-13) | T005, T013 | - | `caffmob_draw/collision/scan.py` | 🟡 | `[X]` |
| T037 | `collision.scan.check_all(scope)` e `check_item(root)` (só vizinhos cuja caixa toca a do item): confirma cada par por `BVHTree.overlap` com cache de BVH, grava as ocorrências no estado; falha vai para `state.error` (D-13, RN-14) | T036 | - | `caffmob_draw/collision/scan.py` | 🟡 | `[X]` |
| T038 | Handler `depsgraph_update_post` `@persistent` que marca `stale` quando um item da última verificação muda de transformação ou geometria (padrão de `cutting/stale.py`) (D-15, RF-25) | T013 | `[//]` | `caffmob_draw/collision/stale.py` | 🟢 | `[X]` |
| T039 | Operadores: `caffmob.check_collisions` (Cena/Selecionado; com `collision_global` desligado diz "Colisão desligada"), `caffmob.collision_goto` (seleciona os dois e `view3d.view_selected` em `temp_override`) e `caffmob.collision_clear` (RF-20, RF-21, D-14, D-18) | T037 | - | `caffmob_draw/collision/ops_collision.py` | 🟢 | `[X]` |
| T040 | `caffmob.collision_push_out` (Could): desloca o item pelo eixo de menor sobreposição, para fora; item grudado só no plano da face; `UNDO` (RF-26, D-19) | T039 | - | `caffmob_draw/collision/ops_collision.py` | 🟡 | `[X]` |
| T041 | Destaque: `POST_VIEW` com o contorno da caixa dos itens em colisão e `POST_PIXEL` com o rótulo do tipo, enquanto houver ocorrências; handlers removidos ao limpar e no `unregister` (RF-22, D-17) | T013 | `[//]` | `caffmob_draw/collision/overlay.py` | 🟢 | `[X]` |
| T042 | Painel "Colisões" com os estados nunca verificado / desatualizado / sem colisões / erro / desligado / lista com "Ir para", e o campo "Colisão" (Herdar/Ativa/Desativada) do item no painel de propriedades (RF-21, RF-24, RF-25) | T039 | - | `caffmob_draw/collision/panels.py` | 🟢 | `[X]` |

**I3. Editor de armário**

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T043 | Janela do editor: abre por `canvas2d/window` na categoria "Editor de Armário"; `POST_PIXEL` global que desenha só na área do editor: retângulos da elevação, componente selecionado destacado, marca nos componentes com mensagem (RF-02, D-20) | T015, T007 | - | `caffmob_draw/cabinet_editor/window.py` | 🟢 | `[X]` |
| T044 | Ponte com a cena: `read(root)` → `EditorState` (medidas por `selection/editing`, `spec` pelo adaptador da 003); `apply(root, state)` por `editing.set_dimension` e pelas funções do adaptador chamadas direto (`set_front`, `set_interior`, `reapply`); `part_boxes(root)` para a elevação (D-21, D-22) | T009 | - | `caffmob_draw/cabinet_editor/bridge.py` | 🔴 | `[X]` |
| T045 | `caffmob.cabinet_editor` (poll: módulo selecionado; abre a janela, inicia a sessão, guarda o instantâneo inicial) e o modal `{'REGISTER','UNDO','INTERNAL'}`: clique na vista seleciona o componente, Ctrl+Z / Ctrl+Shift+Z pelo `History`, executa os pedidos dos botões, janela sumida → reaplica o inicial e avisa "Editor fechado: alterações descartadas" (RF-01, RF-05, D-26) | T043, T044, T014 | - | `caffmob_draw/cabinet_editor/ops_editor.py` | 🟡 | `[X]` |
| T046 | Botões internos sem `UNDO` (`INTERNAL`): medida, frente, estilo, puxador, material e interior do componente selecionado; cada um grava um pedido; o modal aplica, valida (`validate.py`), calcula os ajustes automáticos (`elevation.diff`) e faz o checkpoint (RF-03, RF-04, RF-06, RF-07, D-22) | T045, T008 | - | `caffmob_draw/cabinet_editor/ops_actions.py` | 🔴 | `[X]` |
| T047 | Confirmar (indisponível com erro) → `FINISHED`; Cancelar → reaplica o instantâneo inicial e `CANCELLED`; "Fechar" com pendências pergunta continuar / descartar / confirmar (RF-08, RN-01, RN-04) | T046 | - | `caffmob_draw/cabinet_editor/ops_editor.py` | 🟡 | `[X]` |
| T048 | Painéis do editor (`IMAGE_EDITOR`/`UI`, "Editor de Armário"): Medidas com mín./máx., Componentes (lista), Personalizar (seções da 003 com o motivo das indisponíveis), Mensagens, Ajustes automáticos, Confirmar/Cancelar/Fechar e "Salvar como módulo" por `customize/library_io` (RF-02, RF-09, RF-10) | T047 | - | `caffmob_draw/cabinet_editor/panels.py` | 🟢 | `[X]` |
| T049 | Botão "Abrir editor de armário" na caixa de dimensões do painel de propriedades e no menu de contexto do módulo; sem módulo, indisponível com "Selecione um módulo" (RF-01, D-27) | T045 | - | `caffmob_draw/ui/object_properties.py` | 🟢 | `[X]` |

## Fase 4, Integração

Registro, ganchos nos movimentos, aviso ao salvar, traduções e fumaça por incremento.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T050 | `load_file_post` chama `stick.migrate.run` ao lado de `standards.migration.run` | T029, T011 | - | `caffmob_draw/__init__.py` | 🟢 | `[X]` |
| T051 | Registro dos pacotes `stick`, `collision` e `cabinet_editor` (props antes de operadores e painéis), handlers de depsgraph e de desenho, item do menu de contexto; `unregister` desfaz tudo | T025, T028, T035, T040, T041, T042, T038, T048, T049, T050 | - | `caffmob_draw/__init__.py` | 🟢 | `[X]` |
| T052 | `PlacementMixin`: ao confirmar uma inserção, `collision.check_item(root)`; colidindo, relata "Colide com <outro>" e liga o destaque, sem mover o item (RF-23, D-16) | T032, T037 | - | `caffmob_draw/hb_placement.py` | 🟡 | `[X]` |
| T053 | Mesmo aviso ao confirmar "Mover na Parede", "Mover agregado" e "Mover" do item grudado (RF-23, D-16) | T037, T028, T034 | - | `caffmob_draw/move_over/ops_move_on_wall.py` | 🟡 | `[X]` |
| T054 | `save_post`: "N colisões pendentes" com resultado em dia e ocorrências; "Colisões não verificadas desde a última mudança" com resultado desatualizado; nunca bloqueia (RF-27, RN-15, D-15) | T013 | `[//]` | `caffmob_draw/ui/save_feedback.py` | 🟡 | `[X]` |
| T055 | Traduções pt_BR/en_US de todo texto novo (painéis, operadores, avisos, mensagens `DIM`/`GEO`/`CAT`); texto desenhado com `tr()`/`N_()` | T035, T042, T048, T049, T054 | - | `caffmob_draw/data/translations/004_editor_grudar.json` | 🟢 | `[X]` |
| T056 | Fumaça I1: migração de arquivo antigo; espessura 150 → 200 mm com aéreo de trás encostado (≤ 0,1 mm); grudar no painel e girar; mover o item como o G nativo e conferir a projeção; ímã ligado, desligado e a 20 mm; fora da face; apagar o hospedeiro; desgrudar; salvar e reabrir (onboarding I1) | T051 | - | `tests/blender_004_stick_smoke.py` | 🟡 | `[X]` |
| T057 | Fumaça I2: penetração de 20 mm; encostados sem ocorrência; abertura × parede e agregado × pai fora da lista; `OFF`; desatualizado depois de mover; mensagem ao salvar; aviso ao soltar; tempo da verificação com 200 módulos ≤ 2 s (onboarding I2) | T051, T052, T053, T054 | - | `tests/blender_004_collision_smoke.py` | 🟡 | `[X]` |
| T058 | Fumaça I3 (com janela): nas quatro bibliotecas, abrir, editar e cancelar devolve a mesma elevação; confirmar + um Ctrl+Z na cena devolve o anterior; desfazer interno não cria passo na pilha do Blender; `DIM-003` impede Confirmar (onboarding I3) | T051, T055 | - | `tests/blender_004_cabinet_editor_smoke.py` | 🔴 | `[X]` |

## Fase 5, Polimento

Documentação do usuário.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T059 | Guia do usuário: grudar em parede, painel e superfície plana, ímã nas preferências, elemento filho e colisões | T056, T057 | `[//]` | `docs/usuario/grudar-e-colisao.md` | 🟢 | `[X]` |
| T060 | Guia do usuário: editor de armário | T058 | `[//]` | `docs/usuario/editor-de-armario.md` | 🟢 | `[X]` |

## Notas de execução

- T053 toca três arquivos (`move_over/ops_move_on_wall.py`, `aggregates/ops_aggregate.py`, `stick/ops_stick.py`) com a mesma chamada de uma linha; o arquivo alvo indica o primeiro.
- T044, T046 e T058 carregam o risco 🔴 de D-22 (undo de `bpy.ops` aninhado dentro do modal). Se a fumaça mostrar passos extras, o caminho é chamar as funções das bibliotecas sem `bpy.ops`, antes de mudar o desenho do editor.
- 2026-10-07 (rodada única, T001–T060): desvios de abordagem e de arquivo alvo, sem mudar o escopo:
  - **Assentar em vez de ganchos por modal (T024, T030, T031, T032, T052, T053).** As bibliotecas não têm um ponto
    comum de fim de posicionamento. O handler de `stick/apply.py` só anota o que se moveu; um temporizador espera não
    haver movimento modal (`Window.modal_operators`, `docs/rag/blender-api/corpus/bpy.types.Window.md#bpy.types.Window.modal_operators`)
    e então `stick/settle.py` projeta o item grudado no plano, vincula módulo novo posto na parede, aplica o ímã (com
    passo de desfazer "Grudar") e verifica colisão só de quem se moveu. Vale também para o G nativo (melhor que D-16).
    `hb_snap.py` e `hb_placement.py` **não** foram alterados (T030 e T032 registradas como `corrected` no progress).
    Custo: o ímã gruda ao soltar, sem prévia encostada durante o arraste (RF-12 parcial).
  - T001: o parâmetro é `clamp_to_face` (um `clamp` sombrearia a função `limits.clamp`).
  - T002: `u`/`v` de `BOX_SIDE` são medidos a partir da origem local do hospedeiro, não do canto mínimo da caixa: o
    hospedeiro que encolhe não arrasta o item (RN-08a), conferido na fumaça.
  - T024: proteção extra: item que foi parar além da face oposta (editor de paredes invertendo a direção) troca de
    face em vez de ser puxado através da parede. Depois de desfazer/refazer/abrir, 0,6 s sem anotar movimento, para o
    ímã não grudar de novo o que o Ctrl+Z soltou.
  - T029: a migração roda a cada abertura de arquivo (idempotente) e o assentar vincula módulos postos na parede
    depois da abertura.
  - T034: a recusa de "converter item grudado" ficou em `aggregates/convert.can_convert` (vale para agregado e folha).
  - T037/T052: `check_moved` inclui os descendentes do que se moveu (agregados e itens grudados vão junto).
  - T013: `BTM_PG_Collision.push` (vetor de afastamento) no lugar do enum `axis` do data-delta; `checked_names`
    guarda os itens verificados para o "desatualizado". `BTM_PG_Stick` ganhou `applied_spin`.
  - T044: `apply_state` só refaz frente e interior quando diferem; `edit` não reaplica a mesma frente (o face frame
    reconstruiria o vão). A vista frontal ignora gaiolas em arame (`WIRE`/`BOUNDS`), exceto os vãos.
  - T046: o undo aninhado (D-22, 🔴) foi resolvido: as edições rodam dentro do `modal()` do editor (com `UNDO`) e os
    botões do painel só registram pedidos; a fumaça T058 confirma, nas quatro bibliotecas, que um Ctrl+Z depois do
    Confirmar volta ao módulo de antes do editor.
  - T049: a entrada no menu de contexto ficou em `stick/ops_stick.draw_context_menu` (mesmo menu do Grudar).
  - Observação de biblioteca (fora do escopo): no frameless, `change_opening_type` de `OPEN` para `DOUBLE_DOORS`
    deixa uma gaiola em arame `Doors.001` sobrando. Candidato a bug próprio (`/reversa-debugger`).

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-07 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-10-07 | `/reversa-coding`: T001–T060 concluídas; notas de execução | reversa |
