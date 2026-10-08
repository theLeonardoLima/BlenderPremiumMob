# Data Delta: Barra lateral em 5 seções

> Identificador: `005-barra-lateral-viewport`
> Data: `2026-10-07`

## 1. Campos novos

### 1.1 `WindowManager.btm_sidebar` — `BTM_PG_SidebarState` (novo, `ui/sidebar_props.py`, não salvo)

| Campo | Tipo | Padrão | Uso |
|---|---|---|---|
| `open_build` | Bool | True | Seção Construir aberta |
| `open_insert` | Bool | False | Seção Inserir |
| `open_selected` | Bool | False | Seção Selecionado (aberta pelo msgbus ao selecionar, D-03) |
| `open_check` | Bool | False | Seção Verificar |
| `open_project` | Bool | False | Seção Produção/Projeto |
| `open_group_<id>` | Bool (um por grupo) | conforme D-05..D-09 | Grupos internos recolhíveis |
| `my_modules_filter` | Enum `ALL` / `MODULES` / `FRAMELESS` / `FACE_FRAME` | `ALL` | Filtro de Inserir › Meus módulos |
| `last_active` | String | "" | Nome do último ativo visto (evita reabrir Selecionado sem troca) |

## 2. Campos alterados

| Campo | Onde | Antes | Agora |
|---|---|---|---|
| `use_viewport_hud` | `BTM_AddonPreferences` (`caffmob_draw/__init__.py`) | padrão `False` | padrão `True`; valor salvo pelo usuário é respeitado (D-14) |

## 3. Campos removidos

Nenhum. `Scene.btm_settings.btm_active_tab` (abas antigas) deixa de ser usado pela interface. O campo continua
registrado para não invalidar arquivos salvos.

## 4. Migração

Nenhuma migração de dados de projeto. A linha de base do inventário (`tests/fixtures/sidebar_inventory_baseline.json`) é
um artefato de teste, gravado uma vez antes da mudança.
