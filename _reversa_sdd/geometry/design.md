# Módulo Geometry, Design Técnico

## Interface

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `generate_wall_from_segments` | `(obj, segments)` | `None` | Constrói a malha de parede a partir dos vetores de entrada. |
| `generate_floor_from_walls` | `(obj, wall_objects)` | `bool` | Retorna sucesso. Constrói o piso conformal via Convex Hull. |
| `generate_cabinet_mesh` | `(obj, w_mm, h_mm, d_mm, th_mm)` | `None` | Modela as 5 chapas estruturais de MDF do armário. |

## Fluxo Principal — Cálculo do Piso Conformal
1. Itera sobre a lista de objetos `wall_objects`.
2. Filtra vértices da base (altura próxima ao menor Z do objeto, com tolerância de 0.01m).
3. Transforma as coordenadas locais dos vértices em globais aplicando `matrix_world`.
4. Executa Graham Scan (`_convex_hull_2d`) sobre a projeção XY bidimensional dos pontos de base.
5. Se o fecho convexo resultar em menos de 3 vértices, falha retornando `False`.
6. Instancia uma nova face plana CCW unindo os vértices no bmesh (`bm.faces.new`).
7. Limpa a malha do objeto de piso alvo e grava os novos dados geométricos.

## Dependências
- `bpy` e `bmesh` para manipulação de malhas de baixo nível.
- `mathutils` para transformações matriciais de coordenadas.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Uso de Graham Scan para contorno do piso | `mesh_gen.py:189` | 🟢 |
| Limpeza manual de bmesh (`bm.free()`) | `mesh_gen.py:13` | 🟢 |

## Estado Interno
O módulo é stateless, manipulando objetos do Blender diretamente via bmesh transiente e liberando a memória ao final do escopo de cada função.

## Riscos e Lacunas
- 🔴 O Graham Scan gera fechos convexos. Layouts de salas não-convexas (ex: formato em L ou U) resultarão em pisos projetados incorretamente por cima das quinas internas.
