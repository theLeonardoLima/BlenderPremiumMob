---
schema_version: 1
id: BUG-20261007-VQ72
display_number: 9
title: Trecho selecionado não mostra a medida no painel do editor de paredes
status: open
phase: reproducing
severity: high
priority: P1
created: 2026-10-07
updated: 2026-10-07

origin:
  type: manual-report
  external_ref: null

area: paredes
module: wall_editor
feature: 002-editor-parede-mover-sobre
labels: [painel]

visibility: normal
security_suspected: false

reproduction:
  classification: not-reproduced
  rate: "0/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RF-05", "_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RF-04", "_reversa_sdd/wall_editor/requirements.md"]
  affected_code: ["caffmob_draw/walls2d/panels.py", "caffmob_draw/walls2d/ops_editor.py", "caffmob_draw/walls2d/props.py", "caffmob_draw/walls2d/window.py"]
  root_cause: null
  reproduction_tests: []
  regression_tests: []

spec_verdict: null

change_set: []

closure:
  policy: local-software
  satisfied: false
resolution_kind: null
---
# Trecho selecionado não mostra a medida no painel do editor de paredes

## Summary

No editor de paredes, ao selecionar um trecho (aparece a seta de direção), o painel ao lado não mostra nada: a medida
não aparece para o usuário mudar ali.

## Expected Behavior

Spec efetiva: `_reversa_forward/002-editor-parede-mover-sobre/requirements.md` RF-05 (🟢): o painel "Painel" do trecho
selecionado mostra comprimento, ângulos, bloquear ângulo, espessura, pé-direito inicial e final, Direção e tipo; mudar
o comprimento estende o trecho no sentido da seta. RF-04: selecionar a linha interna ou externa mostra e edita a medida
dela. RF-06: o painel acompanha o arraste em tempo real.

## Actual Behavior

Relato do titular (2026-10-07): ao clicar no trecho, a seta aparece, mas o painel ao lado "não mostra nada" (vazio ou
com "Selecione um trecho na planta."). Ainda não reproduzido aqui.

## Steps to Reproduce

1. Abrir o Editor de Paredes com paredes no ambiente.
2. Ferramenta Selecionar/Mover; clicar num trecho (aparece a seta).
3. Olhar o painel lateral "Painel": a medida não aparece.

## Evidence

- `evidence/reproduction.md` (não reproduziu), `evidence/editor-painel-depois-do-clique.png`, `evidence/saida.txt`
- Relato bruto: `../../intake/relato-20261007-1500.md`

## Suspected Area

Hipóteses (não confirmadas):
1. O painel `BTM_PT_wall_editor_segment` (`walls2d/panels.py:36-64`) lê `props.session().segment()`; a seleção feita
   pelo modal pode não chegar à sessão ou o painel não redesenha depois do clique (região lateral sem `tag_redraw`).
2. O clique perto da seta seleciona algo que não é um trecho (vértice ou linha externa) e o painel mostra o estado vazio.
3. Os campos do painel (`btm_wall_editor.length` etc.) não são sincronizados com o trecho selecionado.

## Acceptance Criteria

- Clicar num trecho mostra no painel o comprimento (na linha escolhida), os ângulos, a espessura, as alturas e a Direção.
- Mudar o comprimento no painel altera o trecho na planta no sentido da seta, na hora.
- Selecionar outro trecho atualiza o painel; clicar no vazio volta para "Selecione um trecho na planta.".

## Traceability

- Specs: `_reversa_forward/002-editor-parede-mover-sobre/requirements.md` RF-04, RF-05, RF-06; `_reversa_sdd/wall_editor/requirements.md`
- Código afetado: `walls2d/panels.py`, `walls2d/ops_editor.py`, `walls2d/props.py`, `walls2d/window.py`
- Testes existentes relacionados: `tests/blender_002_ui_events.py`, `tests/test_walls2d_model.py`

## Resolution

(preenchida pelo `/reversa-debugger-fix`)

## Agent Notes

- Severidade/prioridade escolhidas pelo titular em 2026-10-07 (high/P1).
- Reproduzir com janela (instância separada com `--enable-event-simulate`, como em `tests/blender_002_ui_events.py`);
  não fechar o Blender do titular.
