# Módulo Operators, Design Técnico

## Interface

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `BTM_OT_WallBuilder.modal` | `(context, event)` | `{'RUNNING_MODAL', 'FINISHED', 'CANCELLED'}` | Trata clicks, mousemove e buffers numéricos de paredes. |
| `BTM_OT_InsertOpening.modal` | `(context, event)` | `{'RUNNING_MODAL', 'FINISHED', 'CANCELLED'}` | Trata clicks, snaps de distância e verticalidade de vãos. |
| `BTM_OT_AdjustFloor.execute` | `(context)` | `{'FINISHED', 'CANCELLED'}` | Executa o fecho convexo das paredes e gera o piso. |

## Fluxo Principal — Inserção de Aberturas
1. `BTM_OT_InsertOpening.invoke` abre caixa de diálogo de propriedades de largura/altura.
2. `BTM_OT_InsertOpening.execute` instancia `preview_obj` com display em wireframe ciano e adiciona modal_handler.
3. `modal` captura `MOUSEMOVE`:
   - Raycast da tela para o piso Z=0 (`_update_mouse_position`).
   - Busca a parede e segmento mais próximos do cursor no plano XY (`_update_closest_wall_segment`).
   - Projecta a altura do peitoril no plano vertical do segmento ativo (`_update_preview`).
   - Atualiza localização e rotação do `preview_obj`.
4. `modal` captura `LEFTMOUSE` ou `ENTER`:
   - Converte o preview em objeto permanente, aplica parentesco e cria o modificador `Boolean` em modo de diferença exata na parede correspondente.

## Dependências
- `blendertomob/geometry/mesh_gen.py` via `generate_opening_tool_mesh` (para atualizar espessuras e tamanhos de vãos).
- `blendertomob/overlays/draw_handlers.py` via draw callback (para renderizar cotas e guias dinâmicas).

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Travamento no plano vertical da parede pelo cursor | `opening_builder.py:340` | 🟢 |
| Modificador boolean em modo EXACT para corte limpo | `opening_builder.py:440` | 🟢 |

## Estado Interno
- `typed_value`: String buffer acumulando dígitos numéricos inseridos pelo usuário.
- `active_field`: String identificando o campo sob foco (`POSITION` ou `SILL_HEIGHT`).
- `wall_t`: Float representativo da projeção normalizada da abertura ao longo da parede ($[0.0, 1.0]$).

## Riscos e Lacunas
- 🔴 Se as paredes adjacentes estiverem desalinhadas com quinas abertas (gaps), a menor distância pode fazer o vão piscar entre paredes consecutivas na quina.
- 🟡 Performance de busca de menor distância linear em loops pode ter queda de frames caso haja dezenas de paredes complexas na cena.
