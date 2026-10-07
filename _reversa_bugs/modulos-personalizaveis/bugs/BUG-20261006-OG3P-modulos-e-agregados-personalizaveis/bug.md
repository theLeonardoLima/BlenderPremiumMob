---
schema_version: 1
id: BUG-20261006-OG3P
display_number: 5
title: Módulos instalados não podem ser personalizados nem salvos e não existem agregados
status: resolved
phase: delivering
severity: critical
priority: P0
created: 2026-10-06
updated: 2026-10-07

origin:
  type: manual-report
  external_ref: null

area: modulos
module: product_common
feature: 001-addon-moveis-planejados
labels: [spec-gap, change-request, agregados]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_forward/001-addon-moveis-planejados/requirements.md", "_reversa_sdd/addenda/bug-BUG-20261006-OG3P-v001.md", "_reversa_forward/003-modulos-agregados-reposicionar/requirements.md", "_reversa_sdd/product_common/requirements.md"]
  affected_code: ["blendertomob/product_libraries/", "blendertomob/inspection/", "blendertomob/ui/object_properties.py"]
  root_cause:
    state: confirmed
    hypothesis: "Funcionalidade inexistente: não havia personalização por instância, biblioteca de módulos do usuário, agregados nem folha de porta convertida (spec-gap)."
    causal_path:
      - "commit f6d9188: o pacote não tinha customize/ nem aggregates/"
      - "feature 003 (commit adcd52f) entregou os quatro itens do pedido"
    evidence:
      - ref: evidence/reproduction.md
        observation: "testes da 003 verdes no master b92ac2e"
    code_refs:
      - {file: caffmob_draw/customize/, symbol: "personalização e biblioteca de módulos", commit: adcd52f}
      - {file: caffmob_draw/aggregates/, symbol: "agregados e folhas", commit: adcd52f}
  reproduction_tests: ["tests/blender_003_customize_smoke.py", "tests/blender_003_aggregates_smoke.py"]
  regression_tests: ["tests/blender_003_customize_smoke.py", "tests/blender_003_aggregates_smoke.py", "tests/test_customize_spec.py", "tests/test_aggregate_limits.py", "tests/test_leaf_sweep.py", "tests/test_module_manifest.py"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: code
    artifact: "caffmob_draw/customize/, caffmob_draw/aggregates/ (feature 003)"
    purpose: personalização, biblioteca de módulos, agregados e folha de porta
    diff: "commit adcd52f"
  - id: CHG-002
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261006-OG3P-v001.md
    purpose: adendo aditivo apontando os requisitos da feature 003
    diff: null

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Módulos instalados não podem ser personalizados nem salvos e não existem agregados

## Summary

O titular quer personalizar os módulos instalados (portas, gavetas, puxadores, materiais, divisões internas) e salvar
o resultado como **módulo novo na biblioteca**. Também quer **agregados**: qualquer malha importada (ex.: uma porta
baixada do SketchUp/OBJ) pode ser convertida em agregado de um elemento; o agregado fica colado ao elemento pai, só se
move dentro do espaço do pai, pode se afastar dele ou afundar nele com opção de perfurar; uma malha convertida em
folha de porta ganha propriedades e uma barra que simula a abertura conforme o usuário arrasta.

## Expected Behavior

**spec-gap:** o comportamento acima não está especificado (a 001 previa "criar móveis prontos e guardá-los na
biblioteca", sem detalhes). Pedido do titular, 2026-10-06:
- personalizar portas, gavetas, puxadores, materiais e divisões internas;
- salvar o módulo personalizado como novo módulo na biblioteca;
- agregados: converter malha em agregado preso ao pai, movimento limitado ao pai, afastar/afundar com opção de perfurar;
- folha de porta a partir de malha importada, com barra de abertura.

## Actual Behavior

Existem dimensões editáveis (002), cores de acabamento personalizadas (frameless) e biblioteca de detalhes 2D; não há
salvar módulo personalizado, nem agregados, nem conversão de malha em folha de porta com barra de abertura.

## Steps to Reproduce

1. Inserir um módulo da biblioteca.
2. Tentar trocar puxador/porta por uma malha própria e salvar como novo módulo: não há caminho.

## Evidence

- Relato: `../../intake/relato-20261006-0900.md` (P4) e resposta do titular de 2026-10-06 (agregados).

## Suspected Area

`blendertomob/product_libraries/*` (bibliotecas e biblioteca de produtos), `inspection/` (abertura de frentes, base
para a barra de abertura), `ui/object_properties.py`.

## Acceptance Criteria

- Personalizar portas, gavetas, puxadores, materiais e divisões internas de um módulo inserido.
- Salvar o módulo personalizado como novo item da biblioteca e inseri-lo de novo.
- Converter uma malha importada em agregado de um elemento, com movimento limitado ao pai, afastar/afundar e perfurar.
- Converter uma malha em folha de porta com barra de abertura.

## Traceability

- Specs: `_reversa_forward/001-addon-moveis-planejados/requirements.md`, `_reversa_sdd/product_common/requirements.md` (spec-gap).
- Código: ver Suspected Area.

## Resolution

**Causa raiz (confirmed):** funcionalidade inexistente (spec-gap). Entregue pela feature 003
(`_reversa_forward/003-modulos-agregados-reposicionar/`, commit `adcd52f`).

**Veredito de spec:** `spec-gap` (aprovado por Leonardo Lima em 2026-10-07), adendo
`_reversa_sdd/addenda/bug-BUG-20261006-OG3P-v001.md` (aponta os requisitos da 003).

**resolution_kind:** `fixed`

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | code | `caffmob_draw/customize/`, `caffmob_draw/aggregates/` | entregue pela feature 003 (commit `adcd52f`) |
| CHG-002 | specification | `_reversa_sdd/addenda/bug-BUG-20261006-OG3P-v001.md` | adendo aditivo |

**Testes:** antes, o caminho não existia (`f6d9188`); depois, `blender_003_customize_smoke`,
`blender_003_aggregates_smoke`, `blender_003_move_over_smoke` e os testes unitários da 003 OK no `master` `b92ac2e`.

## Agent Notes

- É escopo de feature (vários requisitos novos), não um defeito pontual: o caminho natural é `/reversa-requirements`
  (feature nova) em vez de `/reversa-debugger-fix`. Registrado aqui para rastreabilidade a pedido do titular.
- Prioridade P0 assumida (titular informou só "critical").
