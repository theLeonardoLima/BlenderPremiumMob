# Módulo Data, Design Técnico

## Interface

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `update_wall_geom` | `(self, context)` | `None` | Callback de update. Reconstrói geometria de polilinha ou parede reta. |
| `update_cabinet_geom` | `(self, context)` | `None` | Callback de update. Reconstrói caixa de armário. |

## Fluxo Principal — Registro de Propriedades
1. `properties.register()` registra as classes `PropertyGroup` na API do Blender:
   - `BTM_PG_WallSegment`
   - `BTM_PG_InsertionPlane`
   - `BTM_PG_OpeningProperties`
   - `BTM_PG_CabinetProperties`
   - `BTM_PG_SceneSettings`
2. Associa as classes como propriedades de ponteiro (`PointerProperty`) nos tipos de dados do Blender:
   - `bpy.types.Object.btm_wall`
   - `bpy.types.Object.btm_plane`
   - `bpy.types.Object.btm_opening`
   - `bpy.types.Object.btm_cabinet`
   - `bpy.types.Scene.btm_settings`
3. `properties.unregister()` remove os ponteiros (`del`) e desregistra as classes na ordem reversa de registro para evitar dependências órfãs.

## Dependências
- `bpy` para registro de classes e ponteiros.
- `blendertomob/geometry/mesh_gen.py` via mesh generators.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Desregistração reversa de classes | `properties.py:369` | 🟢 |
| Atualização paramétrica dinâmica via callback | `properties.py:9` | 🟢 |

## Estado Interno
As propriedades estendem os objetos nativos do Blender. Os valores são serializados e salvos diretamente no arquivo `.blend` pelo Blender.
- A lista de segmentos de parede é mantida em formato de string JSON na custom property do objeto `"btm_wall_segments"`.

## Riscos e Lacunas
- 🟡 Modificar o JSON `"btm_wall_segments"` externamente de forma inválida pode corromper a leitura do callback, fazendo a parede cair de volta para o comportamento de segmento reto simples.
