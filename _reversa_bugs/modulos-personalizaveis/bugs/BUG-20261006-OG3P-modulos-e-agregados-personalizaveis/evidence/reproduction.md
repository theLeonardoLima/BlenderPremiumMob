# Cápsula de verificação — BUG-20261006-OG3P

- Commit base: `b92ac2e` (branch `master`), funcionalidade entregue pela feature 003 no commit `adcd52f`
- Ambiente: Linux 6.8, Blender 5.2 `--background --factory-startup`
- Antes (commit `f6d9188`, 2026-10-06): não havia `customize/` nem `aggregates/` no pacote (relato do titular; 1/1)
- Depois (2026-10-07):

```
blender_003_customize_smoke: OK     # 4 bibliotecas: frente, estilo, puxador, materiais, interior; salvar e inserir módulo
blender_003_aggregates_smoke: OK    # importar OBJ, agregado com limite/afastar/afundar, Perfurar, furo real, folha de porta
blender_003_move_over_smoke: OK
unittest test_customize_spec test_module_manifest test_aggregate_limits test_leaf_sweep: OK
```
