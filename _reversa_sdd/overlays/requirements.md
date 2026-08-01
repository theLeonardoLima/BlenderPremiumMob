# Módulo Overlays

## Visão Geral
O módulo **overlays** implementa a renderização em tempo real de informações visuais auxiliares na Viewport 3D do Blender (linhas de cota, plano de inserção sob destaque e grade de piso), guiando o usuário de forma intuitiva sem poluir os objetos da cena.

## Responsabilidades
- Renderizar uma grade (grade de linhas e grade de pontos) no piso Z=0.
- Destacar o plano de inserção ativo sob o cursor com sombreamento amarelo semitransparente.
- Desenhar linhas de cota e medições dinâmicas de comprimento de paredes e peitoris.

## Regras de Negócio
- **R-01 (Visibilidade da Grade)**: A grade só é desenhada no piso se a flag `show_grid` das configurações globais estiver ativa. 🟢
- **R-02 (Destaque de Inserção)**: O sombreamento amarelo de inserção só é desenhado sobre superfícies com classificação de plano válida (`btm_plane.object_kind`). 🟢
- **R-03 (Exibição de Cotas)**: Cotas numéricas e linhas auxiliares de medidas das paredes respeitam a flag `show_dimensions`. 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Renderização de grade de piso pontilhada e linear | Must | Grade redesenha corretamente ao ajustar espaçamento na UI. |
| RF-02 | Destaque amarelo semitransparente de plano ativo | Should | Face superior/base do plano brilha sob o cursor. |
| RF-03 | Projeção bidimensional de textos de cotas | Must | Medida em mm desenhada na tela perto da respectiva parede. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | Desenho via lote (batching) na GPU para evitar quedas de framerate | `draw_handlers.py:80` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que o usuário ativa a flag "Exibir Cotas" nas configurações
Quando ele seleciona uma parede na cena
Então a cota numérica do comprimento é desenhada na tela perto da base da parede
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| `draw_grid_lines` | Must | Grade visual para referência espacial CAD. |
| `draw_dimension_labels` | Must | Indicação dinâmica de comprimento de paredes e aberturas. |
| `draw_insertion_plane_highlight` | Should | Destaque do plano de inserção sob o cursor (feedback de foco). |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `blendertomob/overlays/draw_handlers.py` | `draw_grid_lines` | 🟢 |
| `blendertomob/overlays/draw_handlers.py` | `draw_dimension_labels` | 🟢 |
