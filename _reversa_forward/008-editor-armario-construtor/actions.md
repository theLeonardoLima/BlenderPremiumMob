# Actions: Editor de armário no modelo do "Construtor de Armários" (Promob)

> Identificador: `008-editor-armario-construtor`
> Data: `2026-10-08`
> Roadmap: `_reversa_forward/008-editor-armario-construtor/roadmap.md` (D-01 a D-20)
> Data delta: `_reversa_forward/008-editor-armario-construtor/data-delta.md`
> Interfaces: nenhuma
> Incrementos (roadmap §1):
> - I1 núcleos (T013–T020, T022)
> - I2 fluxo (T030–T037)
> - I3 abas reaproveitadas (T021, T023, T039, T040, T042, T044)
> - I4 Internos (T025, T041)
> - I5 Deslizantes (T026, T043)
> - I6 Estrutura completa (T024, T033, T038)
> - I6b ferragens (T054, T057, T059–T062)
> - I7 acabamento (T035, T048–T052)
>
> Caminhos relativos à raiz do repositório.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 62 (T001–T063, sem T058) |
| Paralelizáveis (`[//]`) | 41 |
| Maior cadeia de dependência | 11 (T001 → T002 → T024 → T027 → T028 → T029 → T030 → T031 → T034 → T051 → T052) |
| Ordem de entrega | Por incremento. O I2 (fluxo) testa o Aplicar (`ed.undo_push` no modal) antes de seguir (roadmap §9) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | `BTM_PG_Extra` em `Object.btm_extra` (`is_extra`, `kind`, `catalog_id`, `space`, `slot`, `params`) com registro e remoção (data-delta §1.1) | - | `[//]` | `caffmob_draw/cabinet_editor/data_props.py` | 🟡 | `[X]` |
| T002 | `BTM_PG_Structure` ganha `back_mode`, `back_setback` (0,02), `auto_back` (True) e `extras` (`BTM_PG_StructureExtra`: kind, enabled, value), com `to_dict`/`from_dict`; `BTM_PG_Division` ganha `bay`, `kind` (FIXED/MOVABLE/SPACER) e `follow` (data-delta §1.2, §1.3; D-22) | T001 | - | `caffmob_draw/cabinet_editor/data_props.py` | 🟡 | `[X]` |
| T003 | `BTM_PG_CabinetEditorState`: `tab` com as 7 abas (cai em STRUCTURE para valores antigos) e as opções de cada aba, `catalog_item`, `invert`, `step`, `step_initial` (data-delta §1.4) | - | `[//]` | `caffmob_draw/cabinet_editor/props.py` | 🟢 | `[X]` |
| T004 | `EditorState` ganha `extras`, `slides`, `interiors` e `backs`; a assinatura inclui os quatro (data-delta §1.5) | - | `[//]` | `caffmob_draw/cabinet_editor/state.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T005 | Testes do catálogo: cada aba tem os itens das capturas (Divisões 2 + 3 distanciadores; Gavetas c/ CF + Reta; Internos 9; Portas 4×4 filtros; Deslizantes 2 famílias e 18 estilos; Fundos 2); ids únicos; medida mínima; quem aceita "invertido" | - | `[//]` | `tests/test_cabinet_catalog.py` | 🟢 | `[X]` |
| T006 | Testes das peças extras no caso 800 × 2250 × 550 com 15 mm: rodapé frontal (altura = pés, recuo 50), rodapés laterais, fechamentos 50, vistas 150, vistas altas até 2,70 m, base superior recuada 20 mm, pés nos 4 cantos a 50 mm; pé desligado não gera peça | - | `[//]` | `tests/test_cabinet_extras.py` | 🟡 | `[X]` |
| T007 | Testes do Número de vãos: interno 770; N = 2 → divisória no meio; N = 3 → três vãos iguais; reduzir N lista as divisórias removidas; divisões comuns (não `bay`) preservadas | - | `[//]` | `tests/test_cabinet_bays.py` | 🟡 | `[X]` |
| T008 | Testes dos deslizantes: largura da folha `(L + (N−1)·30)/N`; profundidade escalonada por trilho (18 mm); profundidade mínima `N × 18`; invertido troca a folha da frente; estilos com rasgo | - | `[//]` | `tests/test_cabinet_slides.py` | 🟡 | `[X]` |
| T009 | Testes do painel de eletro: recorte centrado com as medidas de catálogo; externo × embutido (recuo da espessura); item que não cabe devolve a medida mínima; apoio logo abaixo do eletro | - | `[//]` | `tests/test_cabinet_appliances.py` | 🟡 | `[X]` |
| T010 | Testes de `add_many`: 3 verticais num vão de 768 → 4 subvãos de (768 − 45)/4; horizontal; N que não cabe gera `DIV-001` | - | `[//]` | `tests/test_cabinet_editor_divisions.py` | 🟢 | `[X]` |
| T011 | Testes das cotas: anterior/posterior = recuos; inferior/superior (horizontal) e esquerda/direita (vertical) = distâncias às faces do subvão; editar a cota inferior muda o `offset`; passo e passo inicial | - | `[//]` | `tests/test_cabinet_position.py` | 🟡 | `[X]` |
| T053 | Testes dos itens novos de Divisões: distanciador de 30 num vão de 768 deixa uma folha de 738 (sem dois subvãos); "p/ Divisão" segue a divisória ao mover; Sem Divisória remove e junta; móvel tem a mesma geometria da fixa | T010 | - | `tests/test_cabinet_editor_divisions.py` | 🟡 | `[X]` |
| T054 | Testes da lista de ferragens e da furação: soma por código e módulo; 4 gavetas = 4 pares de corrediça (Blum à parte); linha de furação a 37 mm, passo 32, na faixa do subvão, nas duas peças vizinhas | - | `[//]` | `tests/test_cabinet_hardware.py` | 🟢 | `[X]` |
| T012 | Testes do ponto de Aplicar: depois de `apply_point`, `dirty()` é falso; Cancelar volta ao ponto aplicado, não ao inicial; desfazer no rascunho não passa do ponto aplicado | - | `[//]` | `tests/test_cabinet_editor_state.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T013 | Catálogo puro com os itens das capturas por aba e subaba, rótulo, descrição, chave de miniatura, parâmetros (mm), mínimo, invertido e ação (D-01) | T005 | `[//]` | `caffmob_draw/cabinet_editor/catalog.py` | 🟢 | `[X]` |
| T014 | Núcleo puro das peças extras: caixas de cada `kind` a partir da caixa da carcaça e das espessuras (D-13) | T006 | `[//]` | `caffmob_draw/cabinet_editor/extras.py` | 🟡 | `[X]` |
| T015 | Núcleo puro do Número de vãos: posições das divisórias `bay` e a diferença ao mudar N (D-15) | T007 | `[//]` | `caffmob_draw/cabinet_editor/bays.py` | 🟡 | `[X]` |
| T016 | Núcleo puro dos deslizantes: trilhos, folhas, sobreposição, profundidade mínima, rasgo por estilo (D-18) | T008 | `[//]` | `caffmob_draw/cabinet_editor/slides.py` | 🟡 | `[X]` |
| T017 | Núcleo puro dos internos: medidas de catálogo, painel com recorte, externo/embutido, apoio, cabe/não cabe (D-17) | T009 | `[//]` | `caffmob_draw/cabinet_editor/appliances.py` | 🟡 | `[X]` |
| T018 | `divisions.add_many(roots, divisions, space, orientation, n, thickness, …)` com subvãos iguais (D-10) | T010 | `[//]` | `caffmob_draw/cabinet_editor/divisions.py` | 🟢 | `[X]` |
| T055 | `divisions.py`: `kind` SPACER (faixa ocupada sem criar subvãos), MOVABLE (geometria da fixa), `follow` (posição presa à divisória seguida) e `remove_in_space` (Sem Divisória) (D-22) | T018, T053 | - | `caffmob_draw/cabinet_editor/divisions.py` | 🟡 | `[X]` |
| T019 | Núcleo puro das cotas e do passo: `cotas(subvão, divisão)`, `offset_from_cota`, `step_move` (D-16) | T011 | `[//]` | `caffmob_draw/cabinet_editor/position.py` | 🟡 | `[X]` |
| T020 | `Draft.apply_point()`: o estado atual vira a nova referência (Cancelar e "sujo") e o histórico recomeça dele (D-04) | T004, T012 | - | `caffmob_draw/cabinet_editor/state.py` | 🟢 | `[X]` |
| T021 | Contrato `opening_boxes(context, root)` → {caminho do vão da biblioteca: Box} no referencial da raiz, pela caixa avaliada de cada `adapter.openings` (D-05) | - | `[//]` | `caffmob_draw/customize/adapters/common.py` | 🟢 | `[X]` |
| T022 | `structure.layout` aceita o recuo do fundo (o fundo e o vão interno recuam `back_setback`) (D-11) | - | `[//]` | `caffmob_draw/cabinet_editor/structure.py` | 🟡 | `[X]` |
| T023 | Fundo recuado no adaptador `btm`, pelo layout de T022 (D-11) | T022 | - | `caffmob_draw/customize/adapters/btm.py` | 🟡 | `[X]` |
| T063 | Fundo recuado nos adaptadores frameless, closets e face frame: a peça do fundo desloca-se para dentro e é reafirmada em `reaffirm` (D-11) | T022 | `[//]` | `caffmob_draw/customize/adapters/frameless.py` | 🟡 | `[X]` |
| T024 | Peças extras na cena: criar, atualizar e apagar `CabinetPart` (ou ferragem) por `kind` a partir de `btm_structure.extras`, com `btm_component`/`btm_hardware` (D-12, D-13, D-14) | T002, T014 | `[//]` | `caffmob_draw/cabinet_editor/scene_extras.py` | 🟡 | `[X]` |
| T025 | Internos na cena: painel `CabinetPart` com recorte (`aggregates/perforate`), eletro de referência (caixa com material, fora do corte), apoio (divisão horizontal da 006) e pistão (ferragem) (D-17) | T001, T017 | `[//]` | `caffmob_draw/cabinet_editor/scene_interiors.py` | 🟡 | `[X]` |
| T026 | Deslizantes na cena: grupo FRAME "Trilhos" filho da raiz + N folhas `CabinetPart` em grupos LEAF de correr (007), sentido para o centro, curso livre medido; reinserir troca o conjunto (D-18) | T001, T016 | `[//]` | `caffmob_draw/cabinet_editor/scene_slides.py` | 🟡 | `[X]` |
| T027 | Ponte: `read_state`/`apply_state` leem e reaplicam `extras`, `slides`, `interiors` e `backs` (D-20) | T020, T023, T024, T025, T026 | - | `caffmob_draw/cabinet_editor/bridge.py` | 🟢 | `[X]` |
| T028 | Ponte, edições da Estrutura e dos Fundos: `TOGGLE_EXTRA`, `SET_EXTRA_VALUE`, `SET_BAYS` (`bays`) e `SET_BACK` (modo, recuo, automático) (D-07, D-11, D-15) | T015, T027 | - | `caffmob_draw/cabinet_editor/bridge.py` | 🟡 | `[X]` |
| T029 | Ponte, inserções: `ADD_MANY`, `INSERT_DRAWERS` e `INSERT_DOORS` (vão da biblioteca do alvo; mapeamento de D-08 com invertido), `INSERT_INTERIOR`, `INSERT_SLIDES`, `REMOVE_ITEM` (D-05, D-08, D-10) | T018, T021, T028 | - | `caffmob_draw/cabinet_editor/bridge.py` | 🟡 | `[X]` |
| T056 | Ponte, variantes de Gavetas: Gavetões (2 a 4), Internas (frameless: interior com gavetas atrás da porta; outras bibliotecas: motivo), Blum (marca `slide_kind`), puxador nas frentes inseridas (D-23) | T029 | - | `caffmob_draw/cabinet_editor/bridge.py` | 🟡 | `[X]` |
| T030 | Modal: **Aplicar** (`ed.undo_push` + `apply_point`), **OK** = Aplicar + fechar, **Cancelar** volta ao ponto aplicado; validação das peças novas no `refresh` (D-04) | T029 | - | `caffmob_draw/cabinet_editor/ops_editor.py` | 🟡 | `[X]` |
| T031 | Modal: o clique escolhe peça (sobre peça) ou vão (área livre) em qualquer aba; o vão da biblioteca do alvo vai para a sessão; setas movem a divisão selecionada pelo passo (D-05, D-06, D-16) | T019, T030 | - | `caffmob_draw/cabinet_editor/ops_editor.py` | 🟡 | `[X]` |
| T032 | Operadores: `cabinet_editor_insert` (aba + item + opções da aba) com `poll` que desabilita sem vão alvo ("Selecione um vão na vista"; para Gavetas e Portas, também sem vão da biblioteca), `cabinet_editor_apply`, `cabinet_editor_ok`, `cabinet_editor_remove_item` (só `Session.push`) (D-21) | T003, T013 | `[//]` | `caffmob_draw/cabinet_editor/ops_actions.py` | 🟢 | `[X]` |
| T033 | Campos virtuais (get/set → `Session.push`): caixas da árvore (componentes e extras) com valores, `bays`, cotas `pos_*` (D-07, D-16) | T003, T019 | - | `caffmob_draw/cabinet_editor/props.py` | 🟡 | `[X]` |
| T034 | Vista: barra "Selecionado: …", linhas de abertura tracejadas das portas e destaque do vão da biblioteca do alvo, com aviso quando for maior que o subvão (D-05, D-06, D-09) | T031 | - | `caffmob_draw/cabinet_editor/window.py` | 🟢 | `[X]` |
| T035 | Prévias: coleção `bpy.utils.previews` carregada sob demanda de `cabinet_editor/thumbnails/<chave>.png`, com ícone nativo se faltar; `unregister` remove (D-19) | - | `[//]` | `caffmob_draw/cabinet_editor/previews.py` | 🟢 | `[X]` |
| T036 | Passada de desenho com `/impeccable` (`UILayout`): 7 abas (texto ou só ícone), grade de catálogo, área de propriedades, árvore, rodapé OK/Cancelar/Aplicar; registra em `design/construtor-abas.md` | T013 | - | `_reversa_forward/008-editor-armario-construtor/design/construtor-abas.md` | 🟡 | `[X]` |
| T037 | Painéis base: cabeçalho com as 7 abas, área de propriedades com "Não há propriedades disponíveis", rodapé com OK/Cancelar/Aplicar e mensagens; a aba Acabamento sai (D-02, D-03) | T032, T036 | - | `caffmob_draw/cabinet_editor/panels.py` | 🟡 | `[X]` |
| T038 | Aba Estrutura: tipo do armário (origem por biblioteca, D-25), definições, Número de vãos, Posição (cotas habilitadas só com seleção), árvore com caixas e valores (componentes + extras), Movimentação e Materiais (recolhido) | T033, T036 | `[//]` | `caffmob_draw/cabinet_editor/panels_structure.py` | 🟡 | `[X]` |
| T039 | Aba Divisões: Vertical/Horizontal/Inserção múltipla; Móveis/Fixas/Distanciador/Sem divisória (D-22); catálogo com/sem recuo frontal; Inserir (desabilitado sem vão, D-21); lista; Interior da biblioteca | T032, T036 | `[//]` | `caffmob_draw/cabinet_editor/panels_divisions.py` | 🟡 | `[X]` |
| T040 | Aba Gavetas: subabas Gavetas/Gavetões/Internas/Blum (D-23), opções de gaveta e de frente com miniatura, número de gavetas, puxador, Inserir no vão da biblioteca (desabilitado sem vão, D-21) | T032, T036 | `[//]` | `caffmob_draw/cabinet_editor/panels_drawers.py` | 🟡 | `[X]` |
| T041 | Aba Internos: Painel p/ Eletros (Externos/Embutidos), Biblioteca, Apoios, Pistões; itens que não cabem desabilitados com a medida mínima | T032, T036 | `[//]` | `caffmob_draw/cabinet_editor/panels_interior.py` | 🟡 | `[X]` |
| T042 | Aba Portas: Inferior/Superior/Alta/Basculante, Ambas/Inteira/Esquerda/Direita, grade de estilos, Inserir invertido, puxadores | T032, T036 | `[//]` | `caffmob_draw/cabinet_editor/panels_doors.py` | 🟡 | `[X]` |
| T043 | Aba Deslizantes: Alumínio/Madeira, estilos (com os de puxador integrado), folhas, Inserir invertido, aviso de profundidade | T032, T036 | `[//]` | `caffmob_draw/cabinet_editor/panels_sliding.py` | 🟡 | `[X]` |
| T044 | Aba Fundos: Inteiro/Inteiro Recuado, recuo, Inserir automaticamente, item "Fundo Inteiro <espessura>" | T032, T036 | `[//]` | `caffmob_draw/cabinet_editor/panels_backs.py` | 🟡 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T045 | `after_rebuild` reafirma o recuo do fundo e reposiciona peças extras, internos e deslizantes; com "automático", restaura o fundo removido | T023, T024, T025, T026 | - | `caffmob_draw/customize/reapply.py` | 🟡 | `[X]` |
| T046 | Plano de corte: objetos com `btm_hardware` e eletros de referência ficam fora; peças `btm_extra` de chapa entram com o componente (inclusive no `btm` sintético) | - | `[//]` | `caffmob_draw/cutting/part_sources.py` | 🟢 | `[X]` |
| T057 | Furação das divisórias móveis: as peças vizinhas (laterais, divisórias ou carcaça) recebem as linhas de pino de prateleira calculadas pelo núcleo; resultado por peça para o exportador (D-22, D-24) | T055, T054 | `[//]` | `caffmob_draw/cutting/drilling.py` | 🟡 | `[X]` |
| T059 | Lista de ferragens: núcleo puro (soma por código e módulo) e coletor da cena (`btm_hardware`, frentes de gaveta → pares de corrediça, `slide_kind` BLUM) (D-24) | T054 | `[//]` | `caffmob_draw/cutting/hardware.py` | 🟢 | `[X]` |
| T060 | JSON de produção 2.2.0: `hardware[]` e `parts[].drilling` preenchido; `validate` aceita 2.0 a 2.2 (contrato `interfaces/cut-plan-json.md`) | T057, T059 | - | `caffmob_draw/cutting/json_exporter.py` | 🟢 | `[X]` |
| T061 | Testes do contrato 2.2.0: `schema_version`, `hardware` ordenado e idempotente, `drilling` de uma móvel, leitura de 2.1 sem `hardware` | T060 | - | `tests/test_production_contracts.py` | 🟢 | `[X]` |
| T062 | Caixa "Ferragens" no painel do plano de corte (Produção/Projeto), com nome, quantidade e módulo | T059 | `[//]` | `caffmob_draw/ui/sidebar_project.py` | 🟢 | `[X]` |
| T047 | Registro do pacote do editor: `previews` e os painéis novos, na ordem certa; o `unregister` desfaz tudo | T035, T037, T038, T039, T040, T041, T042, T043, T044 | - | `caffmob_draw/cabinet_editor/__init__.py` | 🟢 | `[X]` |
| T048 | Gerador de miniaturas (Workbench) para os itens do catálogo e os PNG gerados em `caffmob_draw/cabinet_editor/thumbnails/` | T013 | `[//]` | `tools/render_cabinet_thumbnails.py` | 🟡 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T049 | Traduções pt-BR/en-US: abas, catálogo, mensagens, barra de estado e lista de ferragens | T037, T038, T039, T040, T041, T042, T043, T044, T062 | `[//]` | `caffmob_draw/data/translations/cabinet_editor.json` | 🟢 | `[X]` |
| T050 | Ajustar a fumaça da 006 às abas novas (FINISH saiu; painéis por aba) | T047 | `[//]` | `tests/blender_006_cabinet_editor_tabs_smoke.py` | 🟡 | `[X]` |
| T051 | Fumaça da 008 nas quatro bibliotecas, uma seção por incremento: fluxo (abas, barra, Inserir sem vão desabilitado, Aplicar/Cancelar, um passo de desfazer por Aplicar), Divisões (múltipla, móvel com furação, distanciador 30, sem divisória), Gavetas (gavetões, internas, Blum, puxador), Portas com invertido e linhas, Fundos recuado, Internos, Deslizantes com batentes, extras, Número de vãos, setas, lista de ferragens, JSON 2.2.0, plano de corte e caso 800/2250/550/770 | T034, T045, T046, T047, T048, T056, T060, T062, T063 | - | `tests/blender_008_construtor_smoke.py` | 🟡 | `[X]` |
| T052 | Guia do usuário: as 7 abas, o vão alvo, Aplicar e o que cada catálogo faz e não faz (premissas do roadmap §4) | T051 | - | `docs/usuario/editor-de-armario.md` | 🟢 | `[X]` |

## Notas de execução

- T027, T028 e T029 compartilham `bridge.py`, e T030 e T031 compartilham `ops_editor.py`: são sequenciais.
- T002 e T001 compartilham `data_props.py`, e T003 e T033 compartilham `props.py`.
- 2026-10-08, revisão depois da auditoria (`audit/cross-check.md`) e da sessão 2 do clarify. Nenhum ID foi
  reciclado.
  - T032 ganhou o bloqueio sem vão (A001).
  - T002, T039 e T040 ganharam os itens novos de Divisões e Gavetas (A002).
  - T020 deixou de ser `[//]` (A007).
  - T023 ficou só com o `btm` e os outros três adaptadores foram para T063 (A008).
  - T038 ganhou a origem do tipo (A006).
  - T051 e T049 incluem os itens novos.
  - Ações novas: T053 a T063, exceto T058 (pulado).
- T030 é o ponto de verificação do risco do Aplicar (`ed.undo_push` no modal). Se falhar, aplicar a alternativa do
  roadmap §4 antes de seguir.
- Cada incremento termina com a seção correspondente da fumaça (T051) funcionando, para poder ir para o projeto
  separado.
- 2026-10-08, `/reversa-coding` (rodada única, T001–T063 sem T058):
  - **Risco do Aplicar (T030):** `ed.undo_push` dentro do modal funciona. Na fumaça da 008, um Ctrl+Z na cena
    desfaz o Aplicar inteiro, e o Cancelar depois de um Aplicar mantém o aplicado. A alternativa do roadmap §4 não
    foi usada.
  - **A101:** a área de propriedades das abas de inserção é `panels.properties_box` (RN-05/RN-06). Sem parâmetros,
    ela mostra "Não há propriedades disponíveis".
  - **A102:** a furação da móvel vai nas peças **vizinhas** do subvão (laterais, divisórias ou a carcaça sintética
    do `btm`), não na própria divisória. É o que o contrato `interfaces/cut-plan-json.md` descreve.
  - **A103:** `slide_kind` está em `BTM_PG_CustomSpec`. A lista de ferragens conta a gaveta do vão marcado BLUM como
    `CORREDICA_BLUM`.
  - **T045, desvio da D-11:** "Inserir automaticamente" reafirma o recuo e reposiciona extras, internos e deslizantes
    depois de uma reconstrução. Ele **não** devolve um fundo que o projetista removeu, porque isso desfaria uma
    remoção explícita. O critério do RF-13 ("mudar a largura recalcula o fundo") continua atendido. Inserir na aba
    Fundos devolve o fundo removido.
  - **Bug encontrado pela fumaça:** no `btm`, as peças sintéticas e as nossas numeravam o uid cada uma a partir de 0,
    e uma folha de correr ou um apoio repetiam `POR/0` e `PRAT/0`. Agora `part_sources.synthetic_records` numera as
    duas listas juntas. Os uids que já existiam não mudam, porque os nomes sintéticos ordenam antes dos objetos.
  - **Sem fundo:** o roupeiro padrão do closets não tem fundo. A aba Fundos avisa "Este armário não tem fundo" (LIB-001)
    e não grava o modo.
  - **Face frame:** os extras aparecem no 3D, mas o módulo continua fora do plano de corte e da lista de ferragens.
    É a lacuna herdada da 006, porque o `part_sources.iter_modules` não lista face frame.
  - **GEO-002 com peças da biblioteca:** uma divisória nossa que cruza uma prateleira da própria biblioteca (como a
    "Shelf" do balcão frameless ou as prateleiras que a porta do roupeiro traz) gera erro e bloqueia o Aplicar. É o
    comportamento da 006, mantido.
  - **Caso 800/2250/550/770:** o vão de 770 supõe laterais de 15 mm. O `btm` padrão tem laterais de 18 mm (vão de
    764). A fumaça confere vão = largura − 2 × lateral e 3 vãos iguais.
  - **Leitura sem gravar:** `iter_modules(scene, ensure_uid=False)` serve para a caixa Ferragens, porque o `draw` do
    Blender não pode gravar o `btm_uid`.
  - **Versão do JSON:** três fumaças antigas (`blender_smoke`, `blender_increment1_smoke`,
    `blender_003_aggregates_smoke`) e `test_production_contracts` fixavam "2.1.0" e passaram para "2.2.0".

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-08 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-10-08 | Revisão pós-auditoria: T053–T057, T059–T063; T002, T020, T023, T032, T038–T040, T049, T051 ajustadas | reversa |
