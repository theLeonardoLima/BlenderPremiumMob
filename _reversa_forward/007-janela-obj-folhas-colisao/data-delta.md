# Data delta: 007-janela-obj-folhas-colisao

> Base: `_reversa_sdd/architecture.md#3. Modelo de Entidades e Relacionamentos (ERD)` (`OPENING-PROPERTIES`) e o
> data-delta da 003 (`BTM_PG_Aggregate`). Medidas em metros; campos lidos por atributo.

## 1. Campos novos

### 1.1 `Object.btm_group` (`BTM_PG_Group`, no Empty de grupo)

| Campo | Tipo | Padrão | Uso |
|-------|------|--------|-----|
| `is_group` | Bool | False | Marca o Empty como grupo de peças |
| `kind` | Enum `FRAME`, `LEAF`, `PLAIN` | `PLAIN` | Esquadria, folha ou grupo comum |
| `members` | Collection de `BTM_PG_GroupMember` | — | Peças do grupo |

`BTM_PG_GroupMember`: `obj` (Pointer Object), `orig_parent` (Pointer Object) e `orig_matrix` (Float ×16), para
desfazer o grupo sem perda (RN-04).

### 1.2 `Object.btm_window` (`BTM_PG_WindowInstall`, na jaula `IS_WINDOW_BP` criada por Instalar)

| Campo | Tipo | Uso |
|-------|------|-----|
| `frame` | Pointer Object | Grupo `FRAME` instalado |
| `frame_matrix` | Float ×16 | Matriz do mundo da esquadria antes de instalar (Desinstalar devolve) |

### 1.3 `BTM_PG_Aggregate` (003): campos acrescentados

| Campo | Tipo | Padrão | Uso |
|-------|------|--------|-----|
| `contact_kind` | Enum `NONE`, `OPEN`, `CLOSE` | `NONE` | Texto "bateu em" ou "encostou em" (D-11) |
| `free_travel` | Float (m) | 0 | Curso livre medido; teto do `travel` (D-09) |
| `rest_overlap` | Float (m) | 0 | Sobreposição dos montantes no arquivo, para o batente (b) (D-10) |

### 1.4 `BTM_OT_ImportModel` (operador, não persiste)

| Campo | Tipo | Padrão |
|-------|------|--------|
| `unit` | Enum `AUTO`, `MM`, `CM`, `M`, `IN` | `AUTO` |
| `up_axis` | Enum `Z`, `Y` | `Z` |

## 2. Campos removidos

Nenhum.

## 3. Campos alterados

| Campo | Mudança |
|-------|---------|
| `BTM_PG_Aggregate.travel` | O `update` limita ao `free_travel` quando ele foi medido (> 0) |

## 4. Migrações

Nenhuma. Folhas antigas não têm `btm_group` nem `rest_overlap` e continuam com o comportamento da 003.
