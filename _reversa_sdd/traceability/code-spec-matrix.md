# Matriz de Rastreabilidade (Código x Especificação) — BlenderToMob

Este documento mapeia a cobertura de arquivos do código legado do add-on **BlenderToMob** pelas especificações de unidades de design criadas no nível **Detalhado**.

---

## 1. Matriz de Cobertura

| Arquivo do Legado | Unit Correspondente | Cobertura de Requisitos | Confiança |
|-------------------|---------------------|:-----------------------:|:---------:|
| `blendertomob/data/properties.py` | `data/` | 🟢 Completa (Mapeia PropertyGroups e reatividade) | 🟢 |
| `blendertomob/geometry/mesh_gen.py` | `geometry/` | 🟢 Completa (Mapeia modeladores bmesh e Convex Hull) | 🟢 |
| `blendertomob/geometry/materials.py` | `geometry/` | 🟢 Completa (Mapeia registro de materiais e HSV) | 🟢 |
| `blendertomob/operators/wall_builder.py` | `operators/` | 🟢 Completa (Mapeia desenho modal de polilinhas) | 🟢 |
| `blendertomob/operators/opening_builder.py` | `operators/` | 🟢 Completa (Mapeia snaps, peitoril e transições de vãos) | 🟢 |
| `blendertomob/operators/floor_builder.py` | `operators/` | 🟢 Completa (Mapeia acionador do Convex Hull do piso) | 🟢 |
| `blendertomob/overlays/draw_handlers.py` | `overlays/` | 🟢 Completa (Mapeia cotas visual e grades de piso GPU) | 🟢 |
| `blendertomob/ui/panels.py` | `ui/` | 🟢 Completa (Mapeia árvore Sidebar e reatividade reativa) | 🟢 |
| `blendertomob/cutting/nesting.py` | `cutting/` | 🟢 Completa (Mapeia otimização Next-Fit Decreasing) | 🟢 |

---

## 2. Estatísticas de Cobertura

- **Total de Arquivos Código Fonte do Legado**: 9
- **Arquivos Mapeados em Especificações**: 9
- **Percentual de Cobertura**: 100% 🟢
