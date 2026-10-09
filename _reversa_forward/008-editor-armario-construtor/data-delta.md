# Data delta: 008-editor-armario-construtor

> Base: data-delta da 006 (`btm_structure`, `btm_division`, `WindowManager.btm_cabinet_editor`, `EditorState`) e
> `_reversa_sdd/architecture.md#3. Modelo de Entidades e Relacionamentos (ERD)`. Medidas em metros.

## 1. Campos novos

### 1.1 `Object.btm_extra` (`BTM_PG_Extra`, em cada peça criada pelas abas novas)

| Campo | Tipo | Uso |
|-------|------|-----|
| `is_extra` | Bool | Marca o objeto |
| `kind` | Enum: `BASE_TOP_RECESSED`, `FOOT`, `KICK_FRONT`, `KICK_LEFT`, `KICK_RIGHT`, `KICK_GRANITE`, `CLOSURE`, `VIEW_FRONT`, `VIEW_LEFT`, `VIEW_RIGHT`, `VIEW_TALL_*`, `APPLIANCE_PANEL`, `APPLIANCE`, `APPLIANCE_SUPPORT`, `PISTON`, `SLIDE_TRACK`, `SLIDE_LEAF` | Tipo da peça (D-12) |
| `catalog_id` | String | Item de catálogo de origem (D-01) |
| `space` | String | Subvão alvo (Internos) |
| `slot` | Int | Posição (pé 1 a 4; folha 1 a 3) |
| `params` | String (JSON) | Parâmetros do item: altura dos pés, largura da vista, medidas do eletro, estilo da folha… |

Peças de chapa também levam `btm_component` (006) e, se for o caso, `btm_raw_material` (006). Ferragem leva
`btm_hardware` (string, D-14).

### 1.2 `BTM_PG_Structure` (006): campos acrescentados

| Campo | Tipo | Padrão | Uso |
|-------|------|--------|-----|
| `back_mode` | Enum `FULL`, `RECESSED` | `FULL` | Inteiro / Inteiro Recuado (RN-14) |
| `back_setback` | Float (m) | 0,02 | Recuo do fundo |
| `auto_back` | Bool | True | Inserir automaticamente (RN-15) |
| `extras` | Collection de `BTM_PG_StructureExtra` (`kind`, `enabled`, `value`) | vazia | Estado da árvore (RN-07a) |

### 1.3 `BTM_PG_Division` (006): campos acrescentados

| Campo | Tipo | Padrão | Uso |
|-------|------|--------|-----|
| `bay` | Bool | False | Divisória gerada pelo Número de vãos (D-15) |
| `kind` | Enum `FIXED`, `MOVABLE`, `SPACER` | `FIXED` | Divisória fixa, móvel (furação) ou distanciador (D-22) |
| `follow` | String (uid) | "" | Distanciador p/ Divisão: divisória que ele acompanha (D-22) |

### 1.3a Ferragem (objetos e coletor, D-24)

| Onde | Campo | Uso |
|------|-------|-----|
| Objeto | `btm_hardware` (string: `PE_PLASTICO`, `PISTAO`, `TRILHO_SUP`, `TRILHO_INF`) | Ferragem física na cena |
| Vão da biblioteca | `btm_custom.slide_kind` (string: "" ou `BLUM`) | Corrediça das gavetas inseridas pela subaba Blum |
| JSON | `hardware[]`: `{code, name, quantity, module_uid}` | Lista de ferragens exportada (contrato 2.2.0) |

### 1.4 `WindowManager.btm_cabinet_editor` (interface)

| Campo | Tipo | Padrão |
|-------|------|--------|
| `tab` | Enum de 7 (D-02) | `STRUCTURE` |
| `div_mode` | Enum `VERTICAL`, `HORIZONTAL`, `MULTIPLE` | `VERTICAL` |
| `div_kind` | Enum `MOVABLE`, `FIXED`, `SPACER`, `NONE` | `FIXED` |
| `div_count` | Int (1 a 10) | 2 |
| `drawer_count` | Int (1 a 8) | 4 |
| `drawer_front` | Enum (estilos da biblioteca) | — |
| `drawer_tab` | Enum `DRAWERS`, `TALL`, `INTERNAL`, `BLUM` | `DRAWERS` |
| `drawer_pull` | Enum (puxadores) | o do projeto |
| `door_region` | Enum `LOWER`, `UPPER`, `TALL`, `FLIP` | `LOWER` |
| `door_scope` | Enum `BOTH`, `WHOLE`, `LEFT`, `RIGHT` | `BOTH` |
| `door_style` | Enum (estilos da biblioteca) | — |
| `invert` | Bool | False |
| `interior_group` | Enum `PANELS`, `LIBRARY`, `SUPPORTS`, `PISTONS` | `PANELS` |
| `interior_filter` | Enum `EXTERNAL`, `BUILT_IN` | `EXTERNAL` |
| `slide_family` | Enum `ALUMINIUM`, `WOOD` | `WOOD` |
| `slide_style` | Enum (estilos de D-18) | `LISA` |
| `slide_leaves` | Int (2 a 3) | 2 |
| `back_tab` | Enum `FULL`, `RECESSED` | `FULL` |
| `catalog_item` | String | item escolhido na grade |
| `step`, `step_initial` | Float (m) | 0,01 / 0 |
| `bays` | Int virtual (get/set) | número atual de vãos |
| `pos_front`, `pos_back`, `pos_low`, `pos_high` | Float virtual (get/set) | cotas do item selecionado |

### 1.5 `EditorState` (rascunho)

| Campo | Tipo | Uso |
|-------|------|-----|
| `extras` | list de dict | Peças extras e pés |
| `slides` | dict | Trilhos e folhas (família, estilo, número, aberturas) |
| `interiors` | list de dict | Painéis, eletros, apoios e pistões |
| `backs` | dict | `back_mode`, `back_setback`, `auto_back` |

## 2. Campos removidos

| Campo | Mudança |
|-------|---------|
| `tab = 'FINISH'` (006) | Valor removido; um editor aberto nele cai em `STRUCTURE` |

## 3. Migrações

Nenhuma ativa. A ausência dos campos novos equivale a "nada inserido", "fundo inteiro" e "inserir automaticamente".
