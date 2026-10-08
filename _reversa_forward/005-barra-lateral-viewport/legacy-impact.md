# Legacy impact — 005-barra-lateral-viewport

> Gerado por `/reversa-coding` em 2026-10-08 (rodada única: T001–T038, todas concluídas).
> Base: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`, `_reversa_sdd/ui/requirements.md` e as features 002–004.

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `caffmob_draw/ui/sidebar.py`, `sidebar_props.py`, `sidebar_selection.py`, `sidebar_vocab.py`, `sidebar_proxy.py`, `sidebar_build.py`, `sidebar_insert.py`, `sidebar_selected.py`, `sidebar_check.py`, `sidebar_project.py`, `my_modules.py` | Barra lateral única (nova) | componente-novo | MEDIUM | Painel hospedeiro com 5 seções em `panel_prop`, estado em `WindowManager.btm_sidebar`, Selecionado aberto pelo `msgbus` (D-01..D-10) |
| `caffmob_draw/ui/panels.py` | Painel com abas e plano de corte | componente-extinto | MEDIUM | `BTM_PT_EnvironmentBuilder` e `BTM_PT_NestingPanel` não são mais registrados; `draw_settings` extraída; Mover Sobre saiu da caixa de inspeção |
| `caffmob_draw/ui/view3d_sidebar.py` | Painéis legados do Home Builder | regra-alterada | MEDIUM | Painéis `HOME_BUILDER_PT_*` não registram mais (desenhados pelo proxy); só os menus continuam registrados; preferências lidas com segurança |
| `caffmob_draw/ui/object_properties.py` | Propriedades do objeto (002/003) | regra-alterada | MEDIUM | `draw_selected` com grupos por tipo (máx. 4 abertos); `BTM_PT_ObjectProperties` removido; "Abrir editor de paredes" saiu do grupo da parede |
| `caffmob_draw/product_libraries/face_frame/ui_face_frame.py` | Painel do face frame | regra-alterada | MEDIUM | Painel e 7 subpainéis viram "Opções do face frame" em Selecionado |
| `caffmob_draw/product_libraries/{frameless,face_frame,closets}/props_*.py` | Galerias das bibliotecas | regra-alterada | LOW | `draw_library_ui(include_user=...)` para a galeria omitir a parte do usuário |
| `caffmob_draw/customize/panels.py`, `aggregates/panels.py`, `stick/panels.py`, `collision/panels.py` | Subpainéis 003/004 | regra-alterada | LOW | Não registram mais; funções de desenho usadas pelos grupos; importar saiu do grupo de agregados |
| `caffmob_draw/ui/context_menu.py`, `ui/menu_apend.py`, `stick/ops_stick.py`, `move_over/insertion_plane.py` | Menu do botão direito | regra-alterada | MEDIUM | Uma inserção só, com submenu `MENU_ID` e ações frequentes do tipo; as três inserções antigas saíram |
| `caffmob_draw/operators/viewport_hud.py`, `caffmob_draw/__init__.py` | HUD da viewport e preferências | regra-alterada | MEDIUM | Linha de ações do item; `use_viewport_hud` padrão `True` |
| `caffmob_draw/stick/magnet.py`, `stick/magnet_preview.py`, `stick/link.py`, `stick/settle.py`, `stick/__init__.py` | Grudar (004) | regra-alterada | MEDIUM | Prévia do ímã durante o arraste; orientação extraída em `oriented_matrix`; movimento que volta ao lugar não aciona o ímã |
| `caffmob_draw/ui/layout_probe.py`, `tests/blender_005_*.py`, `tests/test_layout_probe.py`, `tests/fixtures/sidebar_inventory_baseline.json` | Testes de interface | componente-novo | LOW | Camada falsa de layout, inventário de capacidade e não repetição |
| `caffmob_draw/data/translations/sidebar.json` | Tradução | regra-nova | LOW | 37 textos novos em pt-BR e en-US |
| `build.py` | Empacotamento | regra-alterada | LOW | `catalog/` (não registrado) fica fora do pacote |
| `tests/blender_002_smoke.py`, `tests/_bootstrap.py` | Testes | regra-alterada | LOW | Painel esperado passa a ser `BTM_PT_sidebar`; pacote `ui` na lista de stubs |

## Diff conceitual por componente

**Barra lateral.** Antes, a aba tinha um painel com 4 abas internas mais 11 painéis de topo do Home Builder e
subpainéis das features 002–004, com 17 operadores desenhados em mais de um lugar e a galeria em dobro. Agora há um
painel hospedeiro com 5 seções recolhíveis (Construir, Inserir, Selecionado, Verificar, Produção/Projeto). O conteúdo
dos painéis legados é desenhado dentro delas pelo próprio `draw` de cada classe (proxy), então a lógica das bibliotecas
não mudou. Dois testes provam que nenhuma das 81 ações da linha de base sumiu e que nenhum operador aparece em duas
seções.

**Viewport.** O menu do botão direito é um só, com as ações frequentes do tipo do objeto. O HUD ganhou a linha de ações
do item e vem ligado em instalações novas. O ímã mostra a face e a pose encostada durante o arraste. O assentar da 004
passou a ignorar o movimento que termina onde o item já estava: cancelar um G não gruda mais.

**Regra recuperada.** Em Construir, aberturas e piso e teto voltam a ficar indisponíveis sem paredes, como manda a
regra R-01 da UI e a R-01 de domínio (a aba antiga mostrava os botões sempre).

## Preservadas

Regras 🟢 de `_reversa_sdd/domain.md` intactas: R-02..R-10 (piso conformal, orientação de paredes, aberturas, peitoril,
nesting). R-01 (dependência do piso) é preservada e passa a ser aplicada também em Construir.

Da UI (`_reversa_sdd/ui/requirements.md`): R-02 (propriedades conforme o tipo do objeto ativo) preservada, agora em
Selecionado com no máximo 4 grupos abertos.

## Modificadas

- `_reversa_sdd/ui/requirements.md` RF-01 (painéis na categoria da barra lateral): a aba continua, mas com **um** painel
  hospedeiro em vez de vários painéis de topo.
- `_reversa_sdd/ui/requirements.md` R-01 (aberturas e piso só com paredes): volta a valer em Construir, com o motivo em
  texto.
- 004 (D-04/D-06, ímã ao assentar): o movimento que termina na posição já tratada não aciona o ímã.
