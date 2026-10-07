<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-07T14:33:37+00:00 a partir de 5 bugs -->

# Grafo · editor-de-paredes

```mermaid
graph LR
  BUG_20261006_KFAR["#4 Erro ao salvar no Windows com o editor d"]
  BUG_20261007_A2G7["#6 Ajustar Piso ignora as paredes do editor"]
  BUG_20261007_VQ72["#9 Trecho selecionado não mostra a medida n"]
  BUG_20261007_YIMY["#7 Porta e janela inseridas viram bloco lis"]
  BUG_20261007_ZZUK["#8 Ctrl+Z não desfaz dentro do editor de pa"]
  BUG_20261007_A2G7 -.->|related-to| BUG_20261007_YIMY
  BUG_20261007_ZZUK -.->|related-to| BUG_20261007_VQ72
```

## Clusters

- `wall_editor`: BUG-20261006-KFAR, BUG-20261007-VQ72, BUG-20261007-ZZUK
- `operators`: BUG-20261007-A2G7, BUG-20261007-YIMY

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

- BUG-20261006-KFAR: 0
- BUG-20261007-YIMY: 0
