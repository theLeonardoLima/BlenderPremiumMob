# Investigation: 007-janela-obj-folhas-colisao

> Data: `2026-10-08`. Fontes: leitura de `caffmob_draw/` e medições no Blender 5.2 com `inputs/janela_preta_1400mm.obj`.

## 1. O arquivo

As medidas abaixo estão em mm, no espaço do arquivo: X largura, Y profundidade, Z altura.

| Grupo | Peças | Caixa (mm) |
|---|---|---|
| Folha esquerda | 15 | X −676 a 16; Y −36,2 a −11; Z 31 a 819 |
| Folha direita | 15 | X −16 a 676; Y −4,2 a 21; Z 31 a 819 |
| Marco | 4 | Face interna em X = ±678; Z 22 a 828 |
| Bordas | 8 | Y ±34 a ±40 |
| Trilhos e guias | 4 | Trilho 1 em Y −26 a −22, Z 22 a 30; trilho 2 em Y 6 a 10 |

Conclusões:
- Fechadas, as folhas se sobrepõem 32 mm no centro e estão a 2 mm do marco do próprio lado.
- A folha fica 1 mm acima do trilho (Z 31 contra 30) e 1 mm abaixo da guia (819 contra 820). O encolhimento de 1 mm
  da colisão da 003 é suficiente para não acusar contato em repouso.

Importado hoje pelo plugin: 1400 × 850 × 80 **metros**, girado 90° em X, com 46 malhas e 4 materiais.

## 2. O que existe

- `aggregates/ops_import.py`: chama `wm.obj_import` sem `global_scale` nem `up_axis`. O padrão é Y para cima e
  `forward_axis = −Z` (`docs/rag/blender-api/corpus/bpy.ops.wm.md#bpy.ops.wm.obj_import`).
- `aggregates/leaf.py`: a folha é um objeto. Usa um pivô Empty "<folha> - Eixo"; correr = translação em ±X do pai.
- `aggregates/sweep.py`: fechar é livre por regra (003 RN-11a). Para ir mais longe que isso, precisa de varredura nos
  dois sentidos.
- `aggregates/collision.py`: `_excluded` tira do teste o pai, o módulo do pai e **todos os filhos** dele.
- Paredes:
  - **HB** (`IS_WALL_BP`, uma por segmento): janela = `GeoNodeCage` com `IS_WINDOW_BP`, filha da parede em
    coordenadas locais. É cortada por `cut_wall` (`operators/doors_windows.py:430`, boolean EXACT), limitada a
    `[0, comprimento − largura]` (`set_position_on_wall`). Acompanha a espessura no editor de paredes
    (`walls2d/apply.py:152`) e é apagada com a parede (`KEEP_WITH_WALL`).
  - **BTM** (malha única com segmentos em JSON): o editor de paredes converte para HB.
- `stick/` (004): gruda na face da parede, mas não corta o vão nem limita ao segmento.
- `inspection/pivot_math.py`: matemática de dobradiça e de correr para portas de ambiente. A folha da 003 já cobre o
  correr.

## 3. Alternativas avaliadas

| Alternativa | Por que não |
|---|---|
| Juntar as peças da folha numa malha | Descartada no clarify (Q4): perde nomes, vidro e materiais separados |
| Colisão 3D entre as folhas para "encostar na outra" | Trilhos distintos: nunca há contato. O batente real é a sobreposição dos montantes (D-10) |
| Grudar a janela na parede (004) em vez de jaula HB | Não corta o vão, não limita ao segmento e não segue a espessura como janela |
| Detectar a unidade lendo o LEIA-ME | Não é padrão; o tamanho do modelo resolve (RN-01) |

## 4. Referências da API (RAG 5.2)

- `bpy.ops.wm.obj_import(global_scale, up_axis, forward_axis)`
- A confirmar na codificação: `import_scene.fbx(global_scale, axis_up)` e `import_scene.gltf` (o glTF já é Y-up por
  especificação e não precisa de eixo).
