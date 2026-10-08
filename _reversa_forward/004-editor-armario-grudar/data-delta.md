# Data Delta: Editor de armário, grudar em superfície plana e colisão

> Identificador: `004-editor-armario-grudar`
> Data: `2026-10-07`
> Base: `_reversa_sdd/data-dictionary.md`, `_reversa_sdd/erd-complete.md`, `caffmob_draw/data/properties.py`, data-delta da 003

## 1. Campos novos

### 1.1 `Object.btm_stick` — `BTM_PG_Stick` (novo, `stick/props.py`, salvo no `.blend`)

| Campo | Tipo | Padrão | Uso |
|---|---|---|---|
| `is_stuck` | Bool | False | Vínculo ativo |
| `host` | Pointer `Object` | None | Hospedeiro (também é o `parent` Blender, D-03) |
| `face_kind` | Enum `BOX_SIDE` / `PLANE` | `BOX_SIDE` | D-02 |
| `face` | Enum `POS_X`…`NEG_Z` | `NEG_Y` | Lado da caixa local do hospedeiro, quando `BOX_SIDE` |
| `plane` | FloatVector(16) | identidade | Matriz do plano no referencial local do hospedeiro, quando `PLANE` |
| `u`, `v` | Float `LENGTH` | 0 | Posição do canto de referência do item no plano da face, a partir do canto mínimo da face |
| `distance` | Float `LENGTH` | 0 | Distância à face; negativo = entra no hospedeiro (recuo do face frame) |
| `spin` | Float `ANGLE` | 0 | Giro do item em torno da normal da face |
| `out_of_face` | Bool | False | RN-08a: o item saiu da face e o aviso ainda vale |
| `orig_parent` | Pointer `Object` | None | Pai antes de grudar, devolvido ao desgrudar |
| `last_world` | FloatVector(16) | identidade | Última matriz de mundo aplicada; usada se o hospedeiro sumir sem passar pelo override de apagar |

Regra de atualização: os `update` de `u`, `v`, `distance` e `spin` chamam `stick/apply.update_position` (sem clamp).

### 1.2 Preferências do add-on (`BTM_AddonPreferences`, `__init__.py:106`)

| Campo | Tipo | Padrão | Faixa |
|---|---|---|---|
| `stick_magnet` | Bool | True | — |
| `stick_magnet_distance` | Float `LENGTH` | 0,05 m | 0,001 a 0,5 m |

### 1.3 `Scene.btm_settings` (`BTM_PG_SceneSettings`, `data/properties.py:602`)

| Campo | Tipo | Padrão | Uso |
|---|---|---|---|
| `stick_migrated` | Bool | False | Migração D-08 já feita neste arquivo |

### 1.4 `WindowManager.btm_collision` — `BTM_PG_CollisionState` (novo, `collision/props.py`, não salvo)

| Campo | Tipo | Uso |
|---|---|---|
| `items` | Collection de `BTM_PG_Collision` | Ocorrências |
| `index` | Int | Linha ativa na lista |
| `checked` | Int (−1 = nunca) | Quantidade de itens verificados |
| `scope` | Enum `ALL` / `SELECTED` | Escopo da última verificação |
| `stale` | Bool | RN-14 |
| `error` | String | Falha de cálculo (vazio = sem erro) |

`BTM_PG_Collision`:

| Campo | Tipo | Uso |
|---|---|---|
| `kind` | Enum `WALL` / `ITEM` / `FLOOR_CEILING` | RN-13; obstáculo entra como `WALL` |
| `name_a`, `name_b` | String | Item e o outro |
| `depth` | Float `LENGTH` | Profundidade máxima |
| `axis` | Enum `X` / `Y` / `Z` | Eixo de menor sobreposição, no referencial de A (D-19) |
| `location` | FloatVector `TRANSLATION` | Ponto para o destaque |

### 1.5 `WindowManager.btm_cabinet_editor` — `BTM_PG_CabinetEditorState` (novo, não salvo)

Campos virtuais (get/set) sobre a sessão em memória, como `BTM_PG_WallEditorState` (`walls2d/props.py:267-319`):

| Campo | Uso |
|---|---|
| `width`, `height`, `depth` | Medidas do rascunho, na unidade da cena |
| `component_index` | Componente selecionado na lista |
| `messages` | Coleção de mensagens de validação: `code`, `severity`, `component`, `parameter`, `value`, `range`, `action`, `blocks` |
| `adjustments` | Coleção de ajustes automáticos: `component`, `change` (`MOVED` / `RESIZED` / `ADDED` / `REMOVED`) |

A sessão Python (fora do `bpy`) guarda o objeto raiz, o instantâneo inicial, a pilha de instantâneos `EditorState`
(`dimensions` + `spec.to_dict()`), a vista 2D e o estado da janela.

## 2. Campos existentes que passam a ser lidos

| Campo | Onde | Antes | Agora |
|---|---|---|---|
| `Object.btm_plane.collision_override` | `data/properties.py:202` | sem uso | Exceção por item na colisão (D-18) |
| `Scene.btm_settings.collision_global` | `data/properties.py:641` | só no posicionamento e no Mover Sobre | Também liga ou desliga a verificação de colisão |

## 3. Campos removidos

Nenhum.

## 4. Migração

| Gatilho | Ação | Idempotência |
|---|---|---|
| `load_file_post` | Para cada módulo raiz (`classify.module_root`) com `parent` = `GeoNodeWall` e `btm_stick.is_stuck = False`: `face = NEG_Y` se o giro Z ≈ 0 e o Y local < espessura/2, senão `POS_Y`; `u`/`v` pela caixa atual; `distance` = afastamento atual da face (≤ 0 com recuo); `host` = parede | `btm_settings.stick_migrated`; módulos já vinculados são pulados |
| Arquivo antigo sem `btm_stick` | O Blender cria o PropertyGroup vazio | — |
| Versão anterior do plugin abrindo arquivo novo | `btm_stick` é ignorado; o parentesco continua | — |

O item **não** se move na migração: só ganha o vínculo que descreve a posição que já tem.

## 5. Invariantes

- `btm_stick.is_stuck` ⇒ `obj.parent is btm_stick.host` e `host` existe. O handler conserta isso ou solta o item (RN-08).
- Item grudado nunca é agregado ao mesmo tempo: grudar um agregado pede antes "Desconverter", e converter um item grudado pede antes "Desgrudar".
- Ocorrências de colisão só existem com `stale = False` ou mostradas sob o título "Desatualizado".
