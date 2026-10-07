---
schema_version: 1
id: BUG-20261007-ZZUK
display_number: 8
title: Ctrl+Z não desfaz dentro do editor de paredes
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
labels: [spec-gap, desfazer]

change_risk:
  classification: baixa
  reasons: ["só o editor de paredes (rascunho em memória)", "sem dados salvos nem contrato", "OK e Cancelar não mudam"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261007-VQ72
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RN-16", "_reversa_sdd/addenda/bug-BUG-20261007-ZZUK-v001.md", "_reversa_sdd/wall_editor/requirements.md"]
  affected_code: ["caffmob_draw/walls2d/ops_editor.py", "caffmob_draw/walls2d/props.py", "caffmob_draw/walls2d/model.py"]
  root_cause:
    state: confirmed
    hypothesis: "O modal caffmob.wall_editor_modal não trata Ctrl+Z/Ctrl+Shift+Z e o rascunho (Session.plan) não guarda histórico; o desfazer do Blender não alcança o rascunho em memória."
    causal_path:
      - "walls2d/ops_editor.py BTM_OT_WallEditorModal.modal/_handle: nenhum ramo para a tecla Z com Ctrl"
      - "walls2d/props.py Session: só guarda a assinatura da abertura (para o Cancelar), sem pilha de estados"
    evidence:
      - ref: evidence/reproduction.md
        observation: "mudar o comprimento e teclar Ctrl+Z na janela do editor não volta o rascunho (desfez False)"
    code_refs:
      - {file: caffmob_draw/walls2d/ops_editor.py, symbol: BTM_OT_WallEditorModal, commit: ec8b3f8}
      - {file: caffmob_draw/walls2d/props.py, symbol: Session, commit: ec8b3f8}
  reproduction_tests: ["tests/blender_bug_ZZUK_undo.py"]
  regression_tests: ["tests/test_walls2d_history.py", "tests/blender_bug_ZZUK_undo.py#editor-aberto-3d-intacto"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: code
    artifact: caffmob_draw/walls2d/history.py
    purpose: histórico do rascunho (desfazer/refazer, 100 passos)
    diff: fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/walls2d/props.py
    purpose: sessão com histórico; painel grava passo; undo/redo
    diff: fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/walls2d/ops_editor.py
    purpose: Ctrl+Z / Ctrl+Shift+Z / Ctrl+Y no modal; passo por ação concluída
    diff: fix/CHG-003.diff
  - id: CHG-004
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261007-ZZUK-v001.md
    purpose: adendo aditivo (spec-gap)
    diff: null

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Ctrl+Z não desfaz dentro do editor de paredes

## Summary

Dentro do editor de paredes (janela própria, planta 2D), Ctrl+Z não faz nada. O titular espera desfazer passo a passo
as ações no rascunho, antes do OK.

## Expected Behavior

**spec-gap:** a 002 especifica o rascunho e o OK como um único passo de desfazer no 3D
(`_reversa_forward/002-editor-parede-mover-sobre/requirements.md` RN-16, RF-09), mas não especifica desfazer **dentro**
do editor. Decisão do titular (2026-10-07): Ctrl+Z desfaz, uma por vez, cada ação na planta (desenhar trecho, mover
vértice, mudar medida, apagar, inverter, adicionar/remover vértice, fechar); Ctrl+Shift+Z refaz. O OK continua sendo
um passo de desfazer no 3D.

## Actual Behavior

Ctrl+Z não desfaz nada dentro do editor (relato do titular). Ainda não reproduzido aqui.

## Steps to Reproduce

1. Abrir o Editor de Paredes.
2. Desenhar um trecho ou mudar a medida de um trecho.
3. Teclar Ctrl+Z: nada muda.

## Evidence

- `evidence/reproduction.md`, `evidence/saida.txt`, `evidence/reproducao-com-janela.py`
- Relato bruto: `../../intake/relato-20261007-1500.md`

## Suspected Area

Hipótese (não confirmada): o modal `caffmob.wall_editor` (`walls2d/ops_editor.py`) não trata Ctrl+Z, e o rascunho
(`walls2d/props.py` sessão + `walls2d/model.py` `WallPlan`) não guarda histórico. O desfazer do Blender não vale para
o rascunho em memória (só para dados do `.blend`).

## Acceptance Criteria

- Desenhar 3 trechos e teclar Ctrl+Z três vezes deixa a planta como antes; Ctrl+Shift+Z refaz um por vez.
- Mudar a medida de um trecho pelo painel ou digitando e teclar Ctrl+Z volta a medida anterior.
- Ctrl+Z no editor não mexe no 3D nem no desfazer do Blender; OK continua gerando um passo de desfazer no 3D.

## Traceability

- Specs: `_reversa_forward/002-editor-parede-mover-sobre/requirements.md` RN-16 (rascunho e OK), `_reversa_sdd/wall_editor/requirements.md`
- Código afetado: `walls2d/ops_editor.py`, `walls2d/props.py`, `walls2d/model.py`
- Testes: nenhum

## Resolution

**Causa raiz (confirmed):** o modal `caffmob.wall_editor_modal` não tratava Ctrl+Z/Ctrl+Shift+Z e a sessão do rascunho
não guardava histórico; o desfazer do Blender não alcança o rascunho em memória.

**Veredito de spec:** `spec-gap` (aprovado por Leonardo Lima em 2026-10-07), adendo
`_reversa_sdd/addenda/bug-BUG-20261007-ZZUK-v001.md`.

**resolution_kind:** `fixed`

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | code | `caffmob_draw/walls2d/history.py` | histórico do rascunho (100 passos) |
| CHG-002 | code | `caffmob_draw/walls2d/props.py` | sessão com histórico; painel grava passo; undo/redo |
| CHG-003 | code | `caffmob_draw/walls2d/ops_editor.py` | atalhos no modal; passo por ação concluída |
| CHG-004 | specification | `_reversa_sdd/addenda/bug-BUG-20261007-ZZUK-v001.md` | adendo aditivo |

Diffs: `fix/CHG-001.diff` a `fix/CHG-003.diff`.

**Testes (vermelho → verde):**
- Antes: `test_walls2d_history` → `ImportError`; `blender_bug_ZZUK_undo.py` → "FALHA Ctrl+Z desfaz a medida mudada no
  painel 3.5" e "FALHA 2× Ctrl+Z apaga os 2 trechos desenhados desenhados=2 restam=2".
- Depois: `blender_bug_ZZUK_undo: OK` (4 casos); suíte unitária OK; `blender_002_ui_events` (13 casos),
  `blender_002_smoke` e `blender_bug_A2G7_floor` OK; `ruff` e `check_api.py` limpos.

## Agent Notes

- Severidade/prioridade escolhidas pelo titular em 2026-10-07 (high/P1).
- Escopo decidido pelo titular: desfazer passo a passo no rascunho, com refazer.
