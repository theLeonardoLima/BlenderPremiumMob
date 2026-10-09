# Contrato: JSON de produção (`caffmob_draw.project`) 2.2.0

> Feature: `008-editor-armario-construtor` · Decisões D-22, D-24 · Arquivo: `caffmob_draw/cutting/json_exporter.py`
> Contrato anterior: `_reversa_forward/003-modulos-agregados-reposicionar/interfaces/cut-plan-json.md` (2.1.0)

## Mudança

Versão `2.1.0` → **`2.2.0`** (menor, compatível).

1. Nova seção de topo **`hardware`** (lista de ferragens, RN-16):

```json
"hardware": [
  {"code": "PE_PLASTICO", "name": "Pé plástico 150", "quantity": 4, "module_uid": "a1b2"},
  {"code": "CORREDICA", "name": "Corrediça (par)", "quantity": 4, "module_uid": "a1b2"},
  {"code": "PISTAO", "name": "Pistão", "quantity": 2, "module_uid": "c3d4"},
  {"code": "TRILHO_SUP", "name": "Trilho superior deslizante", "quantity": 1, "module_uid": "e5f6"}
]
```

| Campo | Tipo | Regra |
|---|---|---|
| `code` | string | `PE_PLASTICO`, `PISTAO`, `CORREDICA`, `CORREDICA_BLUM`, `TRILHO_SUP`, `TRILHO_INF` |
| `name` | string | Rótulo na língua do projeto |
| `quantity` | inteiro ≥ 1 | Soma por `code` e `module_uid`; corrediça conta pares (1 por gaveta) |
| `module_uid` | string ou null | Módulo dono (null para ferragem solta) |

2. **`parts[].drilling`** deixa de ser sempre `[]`: as peças vizinhas de uma divisória **móvel** recebem a linha de
   furação para pino de prateleira (RN-10a):

```json
"drilling": [
  {"kind": "SHELF_PIN_LINE", "face": "TOP", "diameter_mm": 5.0, "depth_mm": 10.0,
   "x_mm": 37.0, "y_start_mm": 120.0, "y_end_mm": 560.0, "pitch_mm": 32.0, "source_name": "Divisória 2"}
]
```

| Campo | Tipo | Regra |
|---|---|---|
| `kind` | `"SHELF_PIN_LINE"` | Única forma nesta versão |
| `face` | `"TOP"` \| `"BOTTOM"` | Face da peça voltada para a divisória móvel |
| `x_mm` | número | Distância da borda de referência (37 da frente e 37 de trás: duas entradas) |
| `y_start_mm`, `y_end_mm`, `pitch_mm` | número | Faixa e passo dos furos, ao longo do comprimento |
| `diameter_mm`, `depth_mm` | número | 5 e 10 por padrão |
| `source_name` | string | Divisória móvel que gerou a furação |

## Compatibilidade

- `SCHEMA_VERSION = "2.2.0"`, `SUPPORTED_MAJOR = 2`. O leitor aceita 2.0, 2.1 e 2.2.
- `hardware` ausente = lista vazia. Leitores 2.0/2.1 ignoram o campo novo e as entradas de `drilling` que não conhecem.

## Erros

- Ferragem sem módulo: `module_uid: null`, contada à parte.
- Faixa de furação maior que a peça: cortada ao comprimento da peça e registrada em `limit_status` como
  `"MACHINING_CLIPPED"`, a mesma regra do `machining` da 2.1.

## Idempotência

`hardware` é ordenado por `module_uid` e depois por `code`; `drilling` por `source_name` e depois por `x_mm`. Exportar
duas vezes gera o mesmo arquivo.
