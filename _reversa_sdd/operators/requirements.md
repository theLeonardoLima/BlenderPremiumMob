# Módulo Operators

## Visão Geral
O módulo **operators** implementa todos os comandos, lógicas interativas e operadores modais do add-on **BlenderToMob**, capturando cliques, movimentos de cursor e buffers de teclado para desenho CAD e inserção paramétrica na Viewport.

## Responsabilidades
- Gerenciar o desenho interativo em polilinha para construção de paredes (`BTM_OT_WallBuilder`).
- Posicionar e snappar portas e janelas mantendo-as presas às paredes e rotacionadas corretamente (`BTM_OT_InsertOpening`).
- Otimizar limites de piso conformal gerando a malha do piso a partir das paredes da cena (`BTM_OT_AdjustFloor`).
- Instanciar armários paramétricos na cena (`BTM_OT_CabinetBuilder`).

## Regras de Negócio
- **R-01 (Aderência ao Segmento)**: Portas e janelas herdam rotação e espessura do segmento de parede hospedeiro. 🟢
- **R-02 (Movimento Constrangido)**: Aberturas só deslizam ao longo do comprimento da parede (eixo X local) e altura do peitoril (eixo Z local). 🟢
- **R-03 (Clamping de Limites)**: O cursor de portas/janelas é limitado entre $0.0$ e o comprimento máximo do segmento de parede. 🟢
- **R-04 (Transição de Quina)**: Se o cursor passar do limite do segmento e ficar mais próximo de outra parede, ele transiciona e snappa para ela. 🟢
- **R-05 (Sill Fixo de Portas)**: Portas têm altura de peitoril fixada em $0.0$ mm. 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Construção modal de paredes por cliques no piso Z=0 | Must | Conclui com loop fechado ou RMB; gera malha. |
| RF-02 | Inserção modal de vãos com snap à parede mais próxima | Must | Abertura herda normal e se alinha com a parede ativa. |
| RF-03 | Escrita numérica rápida via buffer de teclado durante modal | Must | Digitar número e pressionar Enter snappa a essa cota exata. |
| RF-04 | Transição automática entre paredes adjacentes no modal | Should| Quando a distância da parede vizinha for menor, snappa para ela. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | Evitar recálculos de snap desnecessários se o cursor não se mover | `opening_builder.py:114` | 🟡 |
| Estabilidade | Limpeza de draw handlers da GPU do Blender ao cancelar modal | `opening_builder.py:465` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que há paredes na cena
Quando o usuário aciona "Inserir Porta" e passa o mouse sobre uma parede
Então o preview da porta fica travado no plano da parede, snappado ao ponto mais próximo

Dado que a porta está snappada no limite do segmento da parede
Quando o usuário digita "600" e pressiona ENTER
Então o preview da porta snappa exatamente a 600mm do vértice inicial da parede
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| `BTM_OT_WallBuilder` | Must | Sem construção de paredes o add-on não tem propósito. |
| `BTM_OT_InsertOpening` | Must | Funcionalidade crítica de snapping interativo de portas/janelas. |
| `BTM_OT_AdjustFloor` | Should | Automatiza limites do piso, mas o piso pode ser criado manualmente. |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `blendertomob/operators/wall_builder.py` | `BTM_OT_WallBuilder` | 🟢 |
| `blendertomob/operators/opening_builder.py` | `BTM_OT_InsertOpening` | 🟢 |
| `blendertomob/operators/floor_builder.py` | `BTM_OT_AdjustFloor` | 🟢 |
