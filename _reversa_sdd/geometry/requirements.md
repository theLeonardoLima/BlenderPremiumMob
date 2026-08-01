# Módulo Geometry

## Visão Geral
O módulo **geometry** fornece a engine matemática e de modelagem de malhas poligonais do add-on, gerando as geometrias 3D de paredes, pisos, armários e vãos de forma paramétrica de alto desempenho.

## Responsabilidades
- Gerar malhas paramétricas de paredes (retas e polilinhas) baseadas em espessura e pé-direito (`generate_wall_from_segments`).
- Calcular e modelar pisos conformais via Convex Hull (`generate_floor_from_walls`).
- Modelar caixas estruturais de armários MDF paramétricos (`generate_cabinet_mesh`).
- Configurar e aplicar materiais dinâmicos com controle de cor HSV (`materials.py`).

## Regras de Negócio
- **R-01 (Convexidade do Piso)**: O piso conformal gerado é o fecho convexo Graham Scan de todos os vértices inferiores de paredes na cena. 🟢
- **R-02 (Corte de Abertura Sobredimensionado)**: O cortador boolean possui largura correspondente à espessura da parede multiplicada por 3, prevenindo artefatos de renderização causados por faces coincidentes. 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Geração de malhas paramétricas via bmesh | Must | Malha limpa e construída corretamente ao alterar valores. |
| RF-02 | Cálculo de fecho convexo 2D para piso | Must | Gera polígono CCW plano a partir dos vértices inferiores. |
| RF-03 | Criação de caixa de armário paramétrica | Must | Armário modelado com laterais, tampo, base e fundo de espessura correspondente. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Estabilidade | Garbage collection manual de bmesh para evitar estouro de memória | `mesh_gen.py:13` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que o usuário altera a largura de um armário para 1000mm
Quando o Blender recarrega o callback geométrico
Então as laterais do armário são transladadas mantendo a espessura de 18mm constante
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| `generate_wall_from_segments` | Must | Lógica primária de malha para paredes polilinhas. |
| `generate_cabinet_mesh` | Must | Lógica primária de malha para mobiliário. |
| `_convex_hull_2d` | Should | Automatiza limites do piso, mas o piso pode ser simples (R-02). |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `blendertomob/geometry/mesh_gen.py` | `generate_cabinet_mesh` | 🟢 |
| `blendertomob/geometry/mesh_gen.py` | `_convex_hull_2d` | 🟢 |
| `blendertomob/geometry/materials.py` | `build_material` | 🟢 |
