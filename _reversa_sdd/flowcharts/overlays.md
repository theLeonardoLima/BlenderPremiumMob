# Fluxograma do Módulo: Overlays

Este documento apresenta a integração do ciclo de desenho personalizado na GPU do módulo **overlays**, no nível de documentação **Detalhado**.

---

## 1. Ciclo de Desenho no Viewport 3D

O Blender redesenha a viewport continuamente. O módulo overlays injeta callbacks na fila de renderização do Blender 3D:

```mermaid
flowchart TD
    A[Chamada de Registro: register] --> B[bpy.types.SpaceView3D.draw_handler_add]
    B --> C[Adiciona callback _draw_all_overlays na fila POST_VIEW]
    
    C --> D[Aguardando Evento de Redesenho do Blender]
    D --> E[Executa _draw_all_overlays]
    
    E --> F[draw_grid_overlay: desenha grade de pontos]
    E --> G[draw_grid_lines: desenha grade de linhas finas]
    E --> H[draw_insertion_plane_highlight: realce amarelo sob cursor]
    E --> I[draw_dimension_labels: cota de tamanho de parede]
    
    F --> J[Loop de desenho finalizado]
    G --> J
    H --> J
    I --> J
    
    J --> D
    
    K[Chamada de Unregister: unregister] --> L[bpy.types.SpaceView3D.draw_handler_remove]
    L --> M[Remove callback da fila de renderização]
    M --> N[Fim]
```
