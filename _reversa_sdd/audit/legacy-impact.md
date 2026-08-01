# Relatório de Impacto Legado & Coexistência (Legacy Impact)

**Data:** 2026-08-01  
**Módulos Impactados:** `hb_props.py`, `hb_utils.py`, `units.py`, `operators/walls.py`, `catalog/ops_catalog.py`, `blendertomob/compat.py`

---

## 1. Mapeamento de Mudanças por Arquivo

| Arquivo Modificado | Elemento Adicionado / Alterado | Raciocínio da Mudança | Impacto em Versões Antigas |
|--------------------|--------------------------------|-----------------------|----------------------------|
| `__init__.py` | `bl_info["blender"] = (3, 6, 0)` | Estender compatibilidade do add-on para Blender 3.6 / 4.x / 5.0.2 / 5.1+ | 🟢 Permite carregar o add-on em builds legados sem erro de versão mínima. |
| `blender_manifest.toml` | `blender_version_min = "3.6.0"` | Sincronizar o manifesto de extensões com o `bl_info` | 🟢 Suporta versões a partir de 3.6.0. |
| `hb_utils.py` | `get_builtin_shader()` | Prover shader GPU compatível entre Blender 3.6, 4.x, 5.0.2 e 5.1+ (`UNIFORM_COLOR` vs `2D_UNIFORM_COLOR`) | 🟢 Previne crash em renderização de overlays GPU em Blender legados. |
| `blendertomob/compat.py` | `get_builtin_shader()` | Sincronizar o utilitário de compatibilidade no pacote `blendertomob` | 🟢 Safe fallback em qualquer versão. |
| `units.py` | `convert_to_meters`, `convert_from_meters`, `format_length_unit` | Suporte a conversão dinâmica de unidades (`mm`, `cm`, `m`, `in`, `ft`) | 🟢 Sem regressão nos formatadores existentes (`unit_to_string`). |
| `hb_props.py` | `HB_Wall_Editor_Props` | Registrar PropertyGroup do Editor de Parede em `scene.hb_wall_editor` | 🟢 Isolado em namespace dedicado. |
| `catalog/ops_catalog.py` | `_apply_global_assembly_config` | Aplicar configurações globais de montagem aos móveis da galeria do catálogo | 🟢 Corrige a ausência de estilos globais em itens da galeria. |
| `operators/walls.py` | `home_builder_walls_OT_interactive_wall_editor`, `home_builder_walls_OT_wall_properties_panel`, `draw_wall_editor_overlay` | Algoritmo do Editor de Parede 🧱 com snap, indicação angular e cota dinâmica | 🟢 Adiciona novo operador modal sem alterar operadores de parede legados. |
| `operators/viewport_hud.py` | `_WallEditorButton` | Botão `🧱 Editor de Parede` no Viewport HUD | 🟢 Integração limpa no HUD de 3D Viewport. |

---

## 2. Garantia de Retrocompatibilidade

- ✅ **Blender 5.0.2 / 4.x / 3.6+**: Acesso a modificadores de Geometry Nodes mantido dinâmico (`mod[identifier]` em Blender < 5.2 e `mod.properties.inputs` em 5.2+).
- ✅ **Móveis da Galeria**: Itens do catálogo agora recebem automaticamente as configurações globais de montagem (estilo ativo, materiais, recuo de rodapé, folgas).
- ✅ **Dimensões Parâmetricas**: Conversão transparente entre `mm`, `cm`, `m`, `in`, `ft` em tempo real.
