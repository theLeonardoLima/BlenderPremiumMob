# Legacy impact: 006-editor-armario-abas

> Data: 2026-10-08. Rodada única do `/reversa-coding` (T001–T039).
> Base: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`.

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `caffmob_draw/cabinet_editor/data_props.py` | Editor de armário (UI/Operators, `architecture.md#1`) | delta-de-dados | MEDIUM | `Object.btm_structure` e `Object.btm_division`, gravados no `.blend` |
| `caffmob_draw/cabinet_editor/divisions.py` | Editor de armário: núcleo | componente-novo | LOW | Subvãos, chapas, recuos e `DIV-*` (puro, testado) |
| `caffmob_draw/cabinet_editor/structure.py` | Editor de armário: núcleo | componente-novo | LOW | Papéis, modos de remoção, caixa do `btm`, `STR-*` (puro, testado) |
| `caffmob_draw/cabinet_editor/scene_divisions.py` | Editor de armário: cena | componente-novo | MEDIUM | Cria e apaga objetos `CabinetPart` filhos da raiz do módulo |
| `caffmob_draw/cabinet_editor/reflow_handler.py` | Editor de armário: cena | componente-novo | MEDIUM | Handlers `depsgraph_update_post` e `frame_change_post` (removidos no `unregister`) |
| `caffmob_draw/cabinet_editor/bridge.py`, `state.py`, `props.py`, `ops_actions.py`, `ops_editor.py`, `window.py` | Editor de armário | regra-alterada | MEDIUM | Rascunho com estrutura e divisões; seis ações novas; clique escolhe subvão na aba Divisão |
| `caffmob_draw/cabinet_editor/panels.py`, `panels_structure.py`, `panels_divisions.py`, `__init__.py` | Editor de armário: painéis | regra-alterada | LOW | Abas Estrutura · Divisão · Acabamento e rodapé fixo |
| `caffmob_draw/customize/adapters/common.py`, `btm.py`, `frameless.py`, `closets.py`, `face_frame.py` | Personalização (003): adaptadores | regra-nova | MEDIUM | Contrato opcional: `inner_spaces`, `structure_*`, `remove_part`, `restore_part`, `set_part_thickness`, `reaffirm` |
| `caffmob_draw/customize/reapply.py` | Personalização (003) | regra-alterada | MEDIUM | `after_rebuild` reafirma remoções e espessuras e reposiciona divisões |
| `caffmob_draw/customize/manifest.py`, `library_io.py` | Módulo salvo (003) | delta-de-contrato-externo | LOW | Manifesto 1.1.0 com `structure`/`divisions` opcionais; uids renovados na inserção |
| `caffmob_draw/geometry/mesh_gen.py` | geometry / mesh_gen (`architecture.md#1`) | regra-alterada | MEDIUM | `generate_cabinet_mesh` gera a caixa por `structure.layout`; sem estrutura, malha idêntica |
| `caffmob_draw/data/properties.py` | data / properties (`architecture.md#3`, `CABINET-PROPERTIES`) | delta-de-dados | MEDIUM | `has_*`, `mode_*`, `thickness_*` por chapa no módulo `btm` |
| `caffmob_draw/cutting/part_roles.py`, `part_sources.py`, `part_extractor.py` | cutting / nesting (`architecture.md#1`) | regra-alterada | HIGH | Peças do `btm` respeitam estrutura e somam divisões; `btm_component` explícito; material da chapa sobrescrito vence o Configurador |
| `caffmob_draw/data/translations/cabinet_editor.json` | Tradução | regra-nova | LOW | 95 textos pt-BR/en-US |
| `tests/test_cabinet_editor_divisions.py`, `test_cabinet_editor_structure.py`, `test_cabinet_editor_state.py`, `test_module_manifest.py`, `blender_006_cabinet_editor_tabs_smoke.py` | Testes | regra-nova | LOW | Cobertura nova |
| `docs/usuario/editor-de-armario.md` | Documentação | regra-alterada | LOW | Guia das abas |

## Diff conceitual por componente

**Editor de armário.** Os painéis foram redistribuídos em três abas, com um rodapé igual em todas. O rascunho
(`EditorState`) agora leva a estrutura e as divisões, então Cancelar, desfazer no rascunho e o único passo de desfazer
do Confirmar continuam valendo para tudo. A vista frontal desenha os subvãos e as chapas removidas.

**Adaptadores da 003.** Cada biblioteca ganhou um contrato opcional para a estrutura. Os padrões ficam em `common.py`.
Remover é esconder por driver, somando-se ao esconder que a biblioteca já dirige. Espessura sobrescrita é gravada na
peça e reafirmada depois de cada recálculo. Só o `btm` (todos os modos) e a base do frameless (`Remove Bottom`) fazem
Estender e Reduzir.

**Divisões.** São objetos próprios: `CabinetPart` filho direto da raiz, sem `hb_part_role`, o que deixa as
bibliotecas reconstruírem as peças delas sem tocar nas divisões. Material e espessura vêm do Configurador, componente
Divisória da linha. Elas acompanham o vão em três situações:
- pela ponte, dentro do editor;
- por `after_rebuild`, depois de cada recálculo da biblioteca;
- pelos handlers, fora do editor.

**Plano de corte.** No módulo `btm`, a lista sintética deixa de fixar as cinco chapas: respeita as removidas, as
espessuras por chapa e soma as divisões. Em todas as bibliotecas, a peça marcada com `btm_raw_material` usa esse
material no lugar do material do Configurador. Sem estrutura editada, a lista sai igual à de antes (medido na fumaça
com Cancelar e no teste de reaplicar o estado inicial).

**Malha do `btm`.** As contas da caixa saíram de `generate_cabinet_mesh` para `structure.layout`. Com a estrutura
padrão, as coordenadas são as de antes.

## Preservadas

Regras 🟢 de `_reversa_sdd/domain.md` que continuam intactas:
- R-01 Dependência do piso;
- R-02 Ajuste conformal de piso;
- R-03 Sentido de orientação de paredes;
- R-04 Aderência ao segmento;
- R-05 Movimento constrangido;
- R-06 Clamping de limites;
- R-07 Transição entre segmentos;
- R-08 Sill fixo de portas;
- R-09 Precedência de área no nesting: as divisões entram como peças comuns, sem mudar o algoritmo;
- R-10 Corte guilhotinado.

## Modificadas

Nenhuma regra 🟢 de `_reversa_sdd/domain.md` foi alterada ou removida. As mudanças de comportamento (lista de peças do
`btm`, material sobrescrito) não estavam documentadas como regra no `domain.md` e ficam em "Observações" do
`regression-watch.md`.
