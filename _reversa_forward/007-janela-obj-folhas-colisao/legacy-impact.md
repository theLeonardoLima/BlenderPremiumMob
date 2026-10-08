# Legacy impact: 007-janela-obj-folhas-colisao

> Data: 2026-10-08. Rodada única do `/reversa-coding` (T001–T030).
> Base: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`.

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `caffmob_draw/aggregates/ops_import.py` | Importar modelo (003) | regra-alterada | MEDIUM | Unidade e eixo vertical; a Automática reescala para mm. Corrige o RF-11 da 003 para OBJ em mm |
| `caffmob_draw/aggregates/import_units.py`, `grouping.py`, `slide_limits.py` | Agregados: núcleos | componente-novo | LOW | Puros, testados |
| `caffmob_draw/aggregates/group_props.py`, `group.py`, `ops_group.py` | Agregados: grupo de peças | componente-novo | MEDIUM | `Object.btm_group`; Criar/Desfazer grupo; Montar esquadria |
| `caffmob_draw/aggregates/leaf.py` | Folha de porta (003) | regra-alterada | HIGH | Folha de grupo; numa esquadria, fechar deixa de ser livre (batentes); sentido padrão e curso livre |
| `caffmob_draw/aggregates/sweep.py` | Folha de porta: varredura | regra-alterada | MEDIUM | Varredura de fechar opcional (`close=True`), com limite; a chamada antiga continua igual |
| `caffmob_draw/aggregates/collision.py` | Folha de porta: colisão | regra-alterada | HIGH | Com pai = esquadria, as peças da esquadria contam como obstáculo; caixa do grupo |
| `caffmob_draw/aggregates/convert.py`, `ops_aggregate.py` | Agregados: converter | regra-alterada | LOW | Aceitam um grupo de peças |
| `caffmob_draw/aggregates/props.py` | Agregados: dados | delta-de-dados | LOW | `contact_kind`, `free_travel`, `rest_overlap`; teto do `travel` |
| `caffmob_draw/aggregates/overlay.py`, `panels.py` | Agregados: interface | regra-alterada | LOW | Destaque da peça de contato; aviso de pouco curso; botões novos |
| `caffmob_draw/aggregates/window_props.py`, `install.py`, `ops_install.py` | Janela na parede | componente-novo | MEDIUM | Jaula `IS_WINDOW_BP` + `cut_wall`; esquadria centrada por driver |
| `caffmob_draw/operators/doors_windows.py` | Portas e janelas de ambiente | regra-alterada | LOW | `cut_wall` vira função de módulo; o método chama a função (mesmo comportamento) |
| `caffmob_draw/aggregates/__init__.py` | Agregados: registro | regra-alterada | LOW | Módulos novos |
| `caffmob_draw/data/translations/aggregates.json` | Tradução | regra-nova | LOW | 48 textos pt-BR/en-US |
| `tests/test_import_units.py`, `test_grouping.py`, `test_slide_limits.py`, `test_leaf_sweep.py`, `blender_007_window_smoke.py` | Testes | regra-nova | LOW | Cobertura nova |
| `docs/usuario/agregados-e-folhas.md` | Documentação | regra-alterada | LOW | Importar com unidade, grupos, Montar esquadria, instalar |
| `_reversa_forward/007-janela-obj-folhas-colisao/inputs/` | Insumo | — | LOW | OBJ, MTL e LEIA-ME do titular (usados pela fumaça) |

## Diff conceitual por componente

**Importar.** O OBJ e o FBX passam a receber o eixo vertical no importador, e a escala é aplicada depois, sobre as
raízes importadas e gravada na malha (peças com escala 1). A Automática mede o modelo em escala 1. Um arquivo em
metros com Z continua entrando igual.

**Grupo de peças.** Um Empty com `btm_group` é o pai das peças. A folha e a colisão da 003 usam a caixa da união das
peças, com os cantos na ordem do `bound_box` do Blender, da qual as faces do teste de contato dependem. "Montar
esquadria" cria a esquadria (grupo FRAME) e as folhas (grupos LEAF) já convertidas.

**Folha numa esquadria.** Só quando o pai é um grupo FRAME:
- a esquadria conta como obstáculo;
- fechar testa contato e para no primeiro batente: a pose do arquivo, `slide_limits.close_stop` (o montante da outra
  folha) ou o contato;
- o curso de correr é medido até a esquadria e vira teto;
- o sentido padrão é para o próprio lado.

Folhas da 003 com outro pai seguem com "fechar livre".

**Janela na parede.** Reaproveita a jaula das janelas de ambiente. A esquadria é filha dela, com drivers que a
centralizam em X e na espessura. Por isso o editor de paredes, que muda o `Dim Y` das janelas, a mantém no meio sem
mudança no `walls2d/apply.py` (T027 resolvido pelo driver).

## Preservadas

Regras 🟢 de `_reversa_sdd/domain.md` que continuam intactas:
- R-01, R-02, R-03 (paredes e piso);
- R-04 a R-08 (aberturas do BTM: o fluxo antigo de inserir abertura não mudou; a janela importada usa a jaula HB);
- R-09, R-10 (nesting: janela é acessório).

## Modificadas

Nenhuma regra 🟢 de `_reversa_sdd/domain.md` foi alterada ou removida. A mudança de comportamento da folha (fechar com
batentes numa esquadria) altera a regra RN-11a da feature 003, que não está no `domain.md`. Ela fica em "Observações"
no `regression-watch.md`.
