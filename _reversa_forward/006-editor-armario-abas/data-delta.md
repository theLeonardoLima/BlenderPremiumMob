# Data delta: 006-editor-armario-abas

> Base: `_reversa_sdd/architecture.md#3. Modelo de Entidades e Relacionamentos (ERD)` (`CABINET-PROPERTIES`) e
> `_reversa_sdd/code-analysis.md#1.4 Parâmetros de Módulos de Mobiliário`.
> Unidade interna: metros. Todos os campos novos são lidos por atributo, nunca por `obj["..."]`.

## 1. Campos novos

### 1.1 `Object.btm_structure` (`BTM_PG_Structure`, na raiz do módulo)

| Campo | Tipo | Padrão | Uso |
|-------|------|--------|-----|
| `components` | Collection de `BTM_PG_StructureItem` | vazia | Só componentes que o usuário mexeu; ausente = como a biblioteca faz |

`BTM_PG_StructureItem`:

| Campo | Tipo | Padrão | Uso |
|-------|------|--------|-----|
| `role` | Enum `TOP`, `BOTTOM`, `BACK`, `LEFT`, `RIGHT` | — | Tampo, base, fundo, lateral esquerda, lateral direita |
| `removed` | Bool | False | RN-04 |
| `mode` | Enum `KEEP`, `EXTEND`, `SHRINK` | `KEEP` | RN-06 (Manter tudo, Estender as vizinhas, Reduzir o armário) |
| `thickness` | Float (m), 0 = segue | 0.0 | RN-05, sobrescrita por armário |
| `material` | String (nome do material) | "" | RN-05; a peça também recebe `btm_custom.material` (003) |

### 1.2 `Object.btm_division` (`BTM_PG_Division`, em cada objeto de divisão)

| Campo | Tipo | Padrão | Uso |
|-------|------|--------|-----|
| `is_division` | Bool | False | Marca o objeto |
| `uid` | String | uuid4 curto | Identidade estável; o nome do objeto pode mudar |
| `space` | String | `s0` | Caminho do subvão que a divisão corta (D-04) |
| `orientation` | Enum `VERTICAL`, `HORIZONTAL` | `VERTICAL` | RN-08 |
| `offset` | Float (m) | meio do subvão | Distância da face esquerda/de baixo do subvão até a face da chapa (RN-11) |
| `use_front` / `front` | Bool / Float (m) | False / 0.02 | Recuo da frente (RN-13) |
| `use_back` / `back` | Bool / Float (m) | False / 0.02 | Recuo de trás (RN-13) |
| `thickness` | Float (m), 0 = segue o Configurador | 0.0 | RN-12 |
| `material` | String, "" = segue o Configurador | "" | RN-12 |

Os objetos de divisão também carregam `btm_component = 'DIV'` (string), lido por `cutting/part_roles.classify`.

### 1.3 `WindowManager.btm_cabinet_editor` (campos novos de interface, não persistem no `.blend` do projeto)

| Campo | Tipo | Padrão |
|-------|------|--------|
| `tab` | Enum `STRUCTURE`, `DIVISIONS`, `FINISH` | `STRUCTURE` |
| `new_orientation` | Enum `VERTICAL`, `HORIZONTAL` | `VERTICAL` |
| `new_use_front`, `new_use_back` | Bool | False |
| `new_front`, `new_back` | Float (m) | 0.02 |
| `space` | Enum dinâmico (subvãos-folha) | o único, ou o último escolhido |
| `divisions`, `division_index` | Collection de espelho + índice | — |
| `structure`, `structure_index` | Collection de espelho + índice | — |
| `remove_mode` | Enum `KEEP`, `EXTEND`, `SHRINK` | `KEEP` |

### 1.4 `BTM_PG_CabinetProperties` (módulo `btm`, `data/properties.py`)

| Campo | Tipo | Padrão | Uso |
|-------|------|--------|-----|
| `has_top`, `has_bottom`, `has_back`, `has_left`, `has_right` | Bool | True | Painéis gerados por `generate_cabinet_mesh` |
| `extend_mode_*` | Enum `KEEP`/`EXTEND`/`SHRINK` (por painel) | `KEEP` | Conta da vizinhança no `btm` (D-08) |
| `thickness_top`, `thickness_bottom`, `thickness_back`, `thickness_left`, `thickness_right` | Float (m), 0 = `thickness` | 0.0 | Espessura por componente |

### 1.5 Rascunho do editor (`cabinet_editor/state.EditorState`, em memória)

| Campo | Tipo | Uso |
|-------|------|-----|
| `structure` | dict `{role: {removed, mode, thickness, material}}` | Instantâneo da Estrutura |
| `divisions` | list de dict `{uid, space, orientation, offset, use_front, front, use_back, back, thickness, material}` | Instantâneo da Divisão |

`signature()` passa a incluir os dois (arredondados a 1 µm).

## 2. Campos removidos

Nenhum.

## 3. Campos alterados

| Campo | Mudança |
|-------|---------|
| Expressão do driver `hide_viewport`/`hide_render` das peças frameless que já têm driver | Ganha a variável `btm_removed` (idprop da peça) com `or` (D-07) |
| `Thickness` das peças com espessura sobrescrita (frameless) | O driver é removido enquanto houver sobrescrita e recriado ao voltar ao padrão (D-09) |

## 4. Migrações

Nenhuma ativa. A ausência dos campos equivale a "nada removido, nenhuma divisão, espessuras do padrão". Ver
`roadmap.md#8. Plano de migração`.
