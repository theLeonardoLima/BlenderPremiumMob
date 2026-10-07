---
schema_version: 1
id: BUG-20261007-VQ72
display_number: 9
title: Trecho selecionado não mostra a medida no painel do editor de paredes
status: resolved
phase: delivering
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
labels: [painel, unidades]

change_risk:
  classification: baixa
  reasons: ["só o painel do editor de paredes", "campos numéricos antigos continuam (testes e scripts)", "sem dados salvos nem contrato"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (ambiente do titular); 0/1 no ambiente de teste com a mesma unidade na planta e no painel"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RF-05", "_reversa_sdd/addenda/bug-BUG-20261007-VQ72-v001.md", "_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RF-04", "_reversa_sdd/wall_editor/requirements.md"]
  affected_code: ["caffmob_draw/walls2d/panels.py", "caffmob_draw/walls2d/ops_editor.py", "caffmob_draw/walls2d/props.py", "caffmob_draw/walls2d/window.py"]
  root_cause:
    state: confirmed
    hypothesis: "O painel mostra os campos, mas as distâncias do trecho são FloatProperty com precision=1 na unidade da cena (metros), enquanto a planta mostra a unidade do projeto (mm): 0,15 m aparece como 0.2 m, 2,6 m como 3 m, e digitar 4100 no campo vale 4100 m."
    causal_path:
      - "walls2d/props.py _length: FloatProperty(subtype='DISTANCE', unit='LENGTH', precision=1)"
      - "a cena nova fica em METRIC/METERS enquanto btm_settings.btm_unit = MILLIMETERS (a planta usa units.get_scene_length_unit = MM)"
    evidence:
      - ref: evidence/reproduction.md
        observation: "no Blender do titular: espessura 0,15 → 0.2 m; altura 2,6 → 3 m; planta 4000 mm x painel 4 m"
    code_refs:
      - {file: caffmob_draw/walls2d/props.py, symbol: _length, commit: 9cd1d21}
      - {file: caffmob_draw/data/units.py, symbol: get_scene_length_unit, commit: 9cd1d21}
  reproduction_tests: ["tests/blender_bug_VQ72_panel.py#1", "tests/blender_bug_VQ72_panel.py#2"]
  regression_tests: ["tests/blender_bug_VQ72_panel.py#3", "tests/blender_bug_VQ72_panel.py#4", "tests/blender_bug_VQ72_panel.py#5"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: code
    artifact: caffmob_draw/walls2d/props.py
    purpose: campos de texto do trecho na unidade do projeto (formatar e ler)
    diff: fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/walls2d/panels.py
    purpose: painel do trecho usa os campos de texto
    diff: fix/CHG-002.diff
  - id: CHG-003
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261007-VQ72-v001.md
    purpose: adendo aditivo (spec-gap)
    diff: null

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
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

- `evidence/blender-do-titular-painel.png` (Blender do titular: valores arredondados em metros)
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

**Causa raiz (confirmed):** o painel aparecia, mas as medidas do trecho eram `FloatProperty` com `precision=1` na unidade
da cena do Blender (metros num arquivo novo), enquanto a planta usa a unidade do projeto (mm): 0,15 m aparecia como
"0.2 m", 2,6 m como "3 m", e digitar 4100 valia 4100 m. Reproduzido no Blender do titular pelo MCP (autorizado).

**Veredito de spec:** `spec-gap` (aprovado por Leonardo Lima em 2026-10-07), adendo
`_reversa_sdd/addenda/bug-BUG-20261007-VQ72-v001.md`.

**resolution_kind:** `fixed`

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | code | `caffmob_draw/walls2d/props.py` | campos de texto na unidade do projeto |
| CHG-002 | code | `caffmob_draw/walls2d/panels.py` | painel usa os campos de texto |
| CHG-003 | specification | `_reversa_sdd/addenda/bug-BUG-20261007-VQ72-v001.md` | adendo aditivo |

**Testes (vermelho → verde):**
- Antes: `tests/blender_bug_VQ72_panel.py` → `AttributeError: 'BTM_PG_WallEditorState' object has no attribute 'length_text'`.
- Depois: `blender_bug_VQ72_panel: OK` (5 casos); suíte unitária, `blender_002_smoke`, `blender_bug_A2G7_floor`,
  `blender_bug_ZZUK_undo` e `blender_002_ui_events` (13 casos) OK; `ruff` e `check_api.py` limpos.

## Agent Notes

- Severidade/prioridade escolhidas pelo titular em 2026-10-07 (high/P1).
- Reproduzir com janela (instância separada com `--enable-event-simulate`, como em `tests/blender_002_ui_events.py`);
  não fechar o Blender do titular.
