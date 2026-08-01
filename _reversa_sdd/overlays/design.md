# Módulo Overlays, Design Técnico

## Interface

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `draw_grid_overlay` | `()` | `None` | Renderiza grade de pontos no piso. |
| `draw_grid_lines` | `()` | `None` | Renderiza grade de linhas no piso. |
| `draw_insertion_plane_highlight` | `()` | `None` | Renderiza destaque amarelo no objeto ativo. |
| `draw_dimension_labels` | `()` | `None` | Renderiza cotas lineares das paredes. |

## Fluxo Principal — Renderização de Overlays
1. O Blender Viewport emite o evento de redesenho do espaço 3D.
2. O callback `_draw_all_overlays` é executado na fila `POST_VIEW` da janela ativa.
3. Se a grade estiver ativa, calcula os limites da caixa envolvente com base nas coordenadas de mundo do piso ou do grid padrão e renderiza os lotes geométricos (`UNIFORM_COLOR` e `POLYLINE_UNIFORM_COLOR` shaders).
4. Se houver plano de inserção sob foco, recupera os vértices inferiores da malha em coordenadas globais, instanciando um lote de face (`TRI_FAN`) na cor amarela semitransparente (`1.0, 0.9, 0.2, 0.12`).
5. Se cotas de dimensões estiverem ativas, localiza paredes e desenha linhas de extensão conectando vértices de base no bmesh, computando cotas numéricas texturizadas via `blf` nas coordenadas projetadas de 2D.

## Dependências
- `gpu` e `gpu_extras.batch` para renderização acelerada de linhas e pontos por shader.
- `blf` para renderização bitmap de fontes TrueType na viewport do Blender.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Acoplamento de overlays à fila POST_VIEW de SpaceView3D | `draw_handlers.py:302` | 🟢 |
| Destaque de plano via TRI_FAN com transparência | `draw_handlers.py:211` | 🟢 |

## Estado Interno
O módulo armazena uma única referência de runtime global `_grid_handler` que aponta para o callback registrado no Blender.

## Riscos e Lacunas
- 🟡 Modificações na API `gpu` ou mudanças no backend de desenho de shaders do Blender (ex: migração completa para Vulkan em versões futuras) podem quebrar funções built-in como `from_builtin('POLYLINE_UNIFORM_COLOR')`.
