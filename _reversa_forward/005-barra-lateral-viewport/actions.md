# Actions: Barra lateral em 5 seções, sem repetição, conversando com a viewport

> Identificador: `005-barra-lateral-viewport`
> Data: `2026-10-07`
> Roadmap: `_reversa_forward/005-barra-lateral-viewport/roadmap.md` (D-01 a D-16)
> Data delta: `_reversa_forward/005-barra-lateral-viewport/data-delta.md`
> Interfaces: nenhuma
> Incrementos: I1 rede de segurança (inventário e não repetição); I2 navegação única; I3 viewport.
>
> Caminhos relativos à raiz do repositório.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 38 |
| Paralelizáveis (`[//]`) | 21 |
| Maior cadeia de dependência | 10 (T002 → T010 → T016 → T017 → T021 → T024 → T033 → T034 → T037 → T038) |
| Ordem de entrega | I1 → I2 → I3; a linha de base (T006) é gravada antes de qualquer mudança de interface |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Camada falsa que imita `UILayout` (`row`, `column`, `box`, `split`, `grid_flow`, `panel`/`panel_prop` devolvendo corpo aberto, `operator` devolvendo objeto que aceita atributos, `prop`, `prop_enum`, `prop_search`, `menu`, `label`, `template_*`, `separator`) e registra cada `bl_idname` de operador e menu com a seção de origem (D-11) | - | `[//]` | `caffmob_draw/ui/layout_probe.py` | 🟢 | `[X]` |
| T002 | `WindowManager.btm_sidebar` (`BTM_PG_SidebarState`: `open_build`, `open_insert`, `open_selected`, `open_check`, `open_project`, `open_group_*`, `my_modules_filter`, `last_active`) com registro e remoção (data-delta §1.1, D-02) | - | `[//]` | `caffmob_draw/ui/sidebar_props.py` | 🟢 | `[X]` |
| T003 | Vocabulário fixo: títulos de seção e de grupo e, por ação frequente, um par rótulo + ícone usado igual no painel, no menu e no HUD (D-10) | - | `[//]` | `caffmob_draw/ui/sidebar_vocab.py` | 🟢 | `[X]` |
| T004 | Proxy de painel: `draw_panel(cls, layout, context)` testa `poll`, monta um objeto com `layout` e o resto vindo da classe (métodos ligados ao proxy) e chama `cls.draw`; também `draw_header` quando existe (D-04) | - | `[//]` | `caffmob_draw/ui/sidebar_proxy.py` | 🟡 | `[X]` |
| T005 | Roteiro de captura no Blender em segundo plano: monta 8 contextos (sem seleção; parede; balcão frameless; face frame; closets; módulo `btm`; geometria; item grudado), desenha os painéis da aba pela camada falsa com tudo aberto e devolve o inventário {operador: [seções]} (D-11) | T001 | - | `tests/blender_005_sidebar_inventory.py` | 🟢 | `[X]` |
| T006 | Gravar a linha de base com os painéis **atuais** (antes de I2): `tests/fixtures/sidebar_inventory_baseline.json`, mais as entradas atuais do menu de contexto e do HUD (D-12) | T005 | - | `tests/fixtures/sidebar_inventory_baseline.json` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T007 | Teste de inventário (RF-08): todo operador da linha de base tem caminho na barra lateral nova, no menu de contexto ou no HUD; falha listando o que sumiu | T006 | - | `tests/blender_005_sidebar_inventory.py` | 🟢 | `[X]` |
| T008 | Teste de não repetição (RF-09): nenhum operador é desenhado por duas seções da barra lateral (com os mesmos argumentos de escopo); falha listando os repetidos | T007 | - | `tests/blender_005_sidebar_inventory.py` | 🟢 | `[X]` |
| T009 | Testes unitários da camada falsa com um painel de mentira: operador dentro de `box`/`row`/`panel_prop`, atributo atribuído ao operador, menu e propriedade registrados | T001 | `[//]` | `tests/test_layout_probe.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

**I2. Navegação única**

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T010 | Painel hospedeiro `BTM_PT_sidebar` (sem cabeçalho, categoria CAFFMob Draw) com as 5 seções em `layout.panel_prop(btm_sidebar, "open_*")` e um despachante por seção (D-01) | T002, T003 | - | `caffmob_draw/ui/sidebar.py` | 🟢 | `[X]` |
| T011 | `msgbus` no objeto ativo (`LayerObjects.active`): abre `open_selected` quando o ativo muda para um objeto reconhecido; reassinado no `load_post`, removido no `unregister` (D-03) | T002 | `[//]` | `caffmob_draw/ui/sidebar_selection.py` | 🟡 | `[X]` |
| T012 | Seção **Construir**: linha principal (Desenhar Paredes, Editor de Paredes) e grupos recolhidos Paredes, Aberturas, Piso e teto, Obstáculos, Luzes, Escadas, Imagem de referência e Geometrias, com os corpos legados pelo proxy; sem parede, Aberturas e Piso e teto desabilitados com "Desenhe uma parede primeiro" (D-05, RN-07) | T004, T010 | `[//]` | `caffmob_draw/ui/sidebar_build.py` | 🟢 | `[X]` |
| T013 | `draw_library_ui(..., include_user=True)` nas três bibliotecas: com `False`, a galeria omite a seção do usuário (frameless "User", face frame, closets se houver) (D-06) | - | `[//]` | `caffmob_draw/product_libraries/frameless/props_hb_frameless.py` | 🟡 | `[X]` |
| T014 | **Meus módulos**: coletor das três origens (módulos salvos de `customize/library_io`, grupos do usuário do frameless e do face frame) com nome, origem, miniatura e o operador de inserção de cada origem; desenho da lista com o filtro `my_modules_filter` (D-06) | T002 | `[//]` | `caffmob_draw/ui/my_modules.py` | 🟡 | `[X]` |
| T015 | Seção **Inserir**: seletor `product_tab` + `draw_library_ui(include_user=False)` chamado só aqui + grupo Meus módulos (D-06, RN-04) | T010, T013, T014 | - | `caffmob_draw/ui/sidebar_insert.py` | 🟡 | `[X]` |
| T016 | `ui/object_properties.py` reorganizado em funções de grupo por tipo: para módulo, Medidas e cotas (dimensões, limites, cotas, Abrir editor de armário), Personalizar, Posição e vínculo (posição, rotação, Mover Sobre, plano de inserção, elemento filho), Abrir; recolhidos Agregados e folhas, Colisão, Arranjo, Outras/Ações; demais tipos com no máximo 4 abertos (D-07) | T004, T010 | `[//]` | `caffmob_draw/ui/object_properties.py` | 🟡 | `[X]` |
| T017 | Seção **Selecionado**: estado vazio "Selecione um objeto na viewport", grupos de T016 e "Opções do face frame" recolhido com os 7 subpainéis do face frame pelo proxy (D-07, RN-05) | T016 | - | `caffmob_draw/ui/sidebar_selected.py` | 🟡 | `[X]` |
| T018 | Seção **Verificar**: corpo da inspeção (abrir/fechar tudo, ângulo, interferência) e `draw_collisions` sem a chave Evitar Sobreposição (D-08) | T010 | `[//]` | `caffmob_draw/ui/sidebar_check.py` | 🟢 | `[X]` |
| T019 | Seção **Produção/Projeto**: Plano de corte (`draw_cut_plan`), Ambientes (corpo de `HOME_BUILDER_PT_project_rooms`), Configurações (unidade, snap, Evitar Sobreposição, padrões, chapa MDF), Projeto e Desenhos 2D recolhido (Layout Views, 2D Details, Annotations pelo proxy; some com `hide_2d_drawing_panels`) (D-09, RF-07) | T004, T010 | `[//]` | `caffmob_draw/ui/sidebar_project.py` | 🟢 | `[X]` |
| T020 | Parar de registrar na aba: `BTM_PT_EnvironmentBuilder`, `BTM_PT_NestingPanel` e os painéis `HOME_BUILDER_PT_*` (classes mantidas para o proxy); `HOME_BUILDER_PT_hidden_header` (aviso de configurações recomendadas) vai para o topo do hospedeiro (D-04) | T012, T015, T018, T019 | - | `caffmob_draw/ui/view3d_sidebar.py` | 🟡 | `[X]` |
| T021 | Parar de registrar `HB_FACE_FRAME_PT_active_cabinet` e os 7 filhos (classes mantidas para o proxy) (D-04, D-07) | T017 | `[//]` | `caffmob_draw/product_libraries/face_frame/ui_face_frame.py` | 🟡 | `[X]` |
| T022 | Subpainéis da 003 (`BTM_PT_customize_module`, `BTM_PT_module_library`, `BTM_PT_aggregate`) deixam de registrar como filhos de Propriedades e passam a expor a função de desenho usada pelos grupos (D-04, D-07) | T016 | `[//]` | `caffmob_draw/customize/panels.py` | 🟡 | `[X]` |
| T023 | Subpainéis da 004 (`BTM_PT_stick`, `BTM_PT_item_collision`, `BTM_PT_collisions`) deixam de registrar e expõem a função de desenho usada pelos grupos e por Verificar (D-04, D-07, D-08) | T016, T018 | `[//]` | `caffmob_draw/stick/panels.py` | 🟡 | `[X]` |
| T024 | Registro em `ui/__init__.py`: props, msgbus, hospedeiro e módulos de seção, na ordem certa; `unregister` desfaz tudo; `BTM_PT_object_properties` deixa de ser painel de topo (vira grupos) (D-01) | T011, T020, T021, T022, T023 | - | `caffmob_draw/ui/__init__.py` | 🟢 | `[X]` |

**I3. Viewport**

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T025 | Menu do botão direito unificado (prepend em `VIEW3D_MT_object_context_menu`): submenu `MENU_ID` do objeto e as ações do tipo (módulo/geometria: Grudar ou Desgrudar, Mover no plano, Mover Sobre, Abrir editor de armário, Verificar colisões do item, Abrir/Fechar frentes; todos: Usar como plano de inserção) com o vocabulário de T003 (D-13, RN-09) | T003 | `[//]` | `caffmob_draw/ui/context_menu.py` | 🟢 | `[X]` |
| T026 | Remover as três inserções antigas no menu de contexto (`ui/menu_apend.py`, `stick/ops_stick.draw_context_menu`, `move_over/insertion_plane._menu`), agora cobertas por T025 | T025 | - | `caffmob_draw/ui/menu_apend.py` | 🟢 | `[X]` |
| T027 | HUD: terceira linha `_ItemActionButton` com até 4 ações do item ativo (Grudar/Desgrudar, Mover Sobre, Abrir editor de armário, Verificar colisões), rótulos de T003, visível só com item reconhecido (D-14, RF-12) | T003 | `[//]` | `caffmob_draw/operators/viewport_hud.py` | 🟡 | `[X]` |
| T028 | `use_viewport_hud` com padrão `True` (valor salvo pelo usuário prevalece) (D-14, RF-11) | - | `[//]` | `caffmob_draw/__init__.py` | 🟡 | `[X]` |
| T029 | `magnet.preview_pose(item, hit)`: matriz encostada (orientação de `link.orient`, deslocamento de `frame.shift`) e cantos da caixa nessa pose, **sem alterar o objeto** (D-15) | - | `[//]` | `caffmob_draw/stick/magnet.py` | 🟡 | `[X]` |
| T030 | Prévia do ímã: `POST_VIEW` (contorno da face e caixa na pose encostada) e `POST_PIXEL` (nome do hospedeiro) só durante movimento modal com ímã ligado; item = ativo ou a prévia do `PlacementMixin`; nada para módulo em parede da biblioteca; handlers removidos no `unregister` (D-15, RF-14, RF-15) | T029 | - | `caffmob_draw/stick/magnet_preview.py` | 🟡 | `[X]` |
| T031 | `build.py` deixa de empacotar `caffmob_draw/catalog/` (D-16, RF-10) | - | `[//]` | `build.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T032 | Registrar `stick.magnet_preview` no pacote `stick` (ordem e `unregister`) | T030 | - | `caffmob_draw/stick/__init__.py` | 🟢 | `[X]` |
| T033 | Inventário passa a ler também o menu de contexto unificado e a linha do HUD; T007 e T008 passando contra a barra nova | T008, T024, T026, T027 | - | `tests/blender_005_sidebar_inventory.py` | 🟢 | `[X]` |
| T034 | Fumaça com janela: 5 seções e nenhum painel legado; Selecionado abre ao selecionar e Construir lembra o estado; Construir sem parede desabilitado; menu de contexto do balcão e da parede; HUD visível e com ações do item; prévia do ímã aparece a 30 mm, some a 80 mm e com Esc; desenho de todas as seções com todos os grupos abertos sem erro; capturas da barra lateral (onboarding) | T024, T032, T033 | - | `tests/blender_005_viewport_smoke.py` | 🟡 | `[X]` |
| T035 | Traduções pt-BR/en-US dos textos novos (seções, grupos, estados vazios, vocabulário, prévia do ímã) | T012, T015, T017, T018, T019, T025, T027, T030 | - | `caffmob_draw/data/translations/sidebar.json` | 🟢 | `[X]` |
| T036 | Ajustar fumaças e testes existentes que abrem painéis removidos ou a aba antiga (`btm_active_tab`, `BTM_PT_*`, `HOME_BUILDER_PT_*`) para a navegação nova | T024 | `[//]` | `tests/blender_002_ui_events.py` | 🟡 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T037 | Guia do usuário da barra lateral: as 5 seções, onde ficou cada coisa (tabela "antes → agora"), menu do botão direito, HUD e prévia do ímã | T034 | - | `docs/usuario/barra-lateral.md` | 🟢 | `[X]` |
| T038 | Atualizar os caminhos de interface citados nos outros guias (`modulos-personalizaveis`, `agregados-e-folhas`, `editor-paredes-e-mover-sobre`, `grudar-e-colisao`, `editor-de-armario`, `inspecao-e-movimento`, `configurador-e-producao`) | T037 | - | `docs/usuario/` | 🟢 | `[X]` |

## Notas de execução

- T013 toca as três bibliotecas (`props_hb_frameless.py`, `props_hb_face_frame.py`, `props_closets.py`) com o mesmo
  parâmetro; o arquivo alvo indica o primeiro.
- T026 toca três arquivos com a mesma remoção de uma inserção de menu; o arquivo alvo indica o primeiro.
- T006 precisa rodar **antes** de T010–T024: a linha de base tem de refletir a interface antiga.
- 2026-10-08 (rodada única, T001–T038): desvios e decisões tomadas no código, sem mudar o escopo:
  - T005/T006: a captura usa um contexto substituto com `space_data` simulado (a viewport não existe em segundo
    plano), abre todas as seções `show_*` das galerias, passa pelas três bibliotecas do seletor e escolhe um tipo de
    obstáculo (o botão só aparece com tipo escolhido). Linha de base: 81 operadores, nenhum erro de desenho. O cabeçalho
    legado passou a ler as preferências com segurança (`addons.get`), como o ímã já fazia.
  - T012: "Abrir editor de paredes" saiu do grupo da parede em Selecionado (repetiria Construir); continua no menu do
    botão direito da parede. Os grupos legados de Construir só aparecem quando o Room Layout permite (fora de vistas de
    layout e de detalhe).
  - T014: **Meus módulos** junta as três origens como três blocos com filtro (cada um com os próprios operadores de
    inserir, renomear e apagar), e não como uma lista única intercalada: os formatos das bibliotecas são diferentes.
  - T015/T016: **Importar modelo 3D** foi para Inserir (antes só aparecia no painel de agregados, também sem seleção);
    `draw_aggregate(include_import=False)` em Selecionado. A classe `BTM_PT_ObjectProperties` foi removida (substituída
    por `draw_selected`); os outros painéis antigos ficam como classes não registradas, desenhadas pelo proxy.
  - T018: o botão de Mover Sobre saiu da caixa de inspeção (repetiria Selecionado › Posição e vínculo); a chave Evitar
    Sobreposição saiu de `draw_collisions` (fica em Produção/Projeto › Configurações).
  - T019: `panels.draw_settings` extraída da aba Configurações; a cópia do gerenciador de ambientes daquela aba não foi
    levada (Ambientes usa o painel Project › Rooms, com reordenar).
  - T025: o vocabulário separa **Abrir frentes** e **Fechar frentes** e ganhou **Limpar plano de inserção**.
  - T027: a linha do HUD não repete Mover Sobre (já está na linha dos modos); com um módulo, mostra Grudar, Abrir editor
    de armário e Verificar colisões.
  - T034: a fumaça revelou que cancelar um G perto de uma face grudava o item (o assentar via a volta à posição como
    movimento novo). `stick/settle.py` agora lembra a posição em que tratou cada item e ignora o movimento que termina
    no mesmo lugar (`returned_to_rest`). Altera o comportamento da 004 só nesse caso.
  - `Scene.btm_settings.btm_active_tab` (abas antigas) deixou de ser usado; continua registrado.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-07 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-10-08 | `/reversa-coding`: T001–T038 concluídas; notas de execução | reversa |
