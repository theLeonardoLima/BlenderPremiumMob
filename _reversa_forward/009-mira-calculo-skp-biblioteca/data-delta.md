# Data delta: 009-mira-calculo-skp-biblioteca

> Data: 2026-10-08. Diff conceitual sobre o modelo extraído (`_reversa_sdd/data-dictionary.md`) e sobre o que as
> features 002, 003 e 007 acrescentaram.

## 1. Editor de paredes: `walls2d.props.Session` (memória, não persiste)

| Campo | Tipo | Padrão | Uso |
|---|---|---|---|
| `direction` | float ou None | None | Direção atual em radianos (RN-05). None até o primeiro trecho |
| `direction_locked` | bool | False | True depois do primeiro Enter, clique ou seta; o `MOUSEMOVE` nunca o desliga |
| `lock_x`, `lock_y` | (valor, ponto de referência) ou None | None | Travas de alinhamento ativas, para o desenho da mira |
| `typed_preview` | str | "" | Resultado da expressão ("= 16 mm") ou "Valor Inválido" |
| `_inference_index` | objeto | None | Listas ordenadas por X e Y; refeitas quando a assinatura do plano muda |

O `_restore` e o `_finish_drawing` zeram `direction`, `direction_locked` e as travas.

`BTM_PG_WallEditorState` não muda. Não há preferência nova; o Shift segurado desliga o alinhamento (R-04).

## 2. Objeto: `Object.btm_object_item` (novo, `bpy.props.PointerProperty`)

| Campo | Tipo | Padrão | Uso |
|---|---|---|---|
| `is_item` | Bool | False | Marca a raiz de um item da biblioteca |
| `item_id` | String | "" | Id estável do item (slug do nome + 6 caracteres) |
| `category` | Enum | `OTHER` | `DOORS`, `WINDOWS`, `COOKTOPS`, `TABLES`, `SEATING`, `DECOR`, `OTHER` |
| `source` | String | "" | "CAFFMob Draw", "3D Warehouse: <autor>", nome do arquivo… |
| `license` | String | "" | Licença informada |

Lido por atributo (`obj.btm_object_item.category`), registrado e desregistrado pelo pacote `object_library`.

## 3. Arquivos da biblioteca de objetos

```text
<pacote>/object_library/items/<CATEGORIA>/<item_id>.blend|.json|.png    (embutida, só leitura)
<extension_path_user>/object_library/<CATEGORIA>/<item_id>.blend|.json|.png   (do usuário)
```

O formato do manifesto está em `interfaces/object-library-item.md`.

## 4. Material de retextura

O material criado tem o nome `Textura: <nome do arquivo>`. Ele guarda as propriedades `btm_texture_path` (caminho da
imagem) e `btm_texture_size_mm` (tamanho real da imagem), para reabrir a retextura com os valores. Um material com o
mesmo arquivo e o mesmo tamanho é reutilizado.

## 5. O que não muda

- `btm_aggregate`, `btm_group`, `btm_custom`, `btm_structure` e o JSON de produção 2.2.0 (as chapas marcadas como
  peça de produção já entram pelo `geometry_records` da 003).
- O modelo do plano do editor de paredes (`walls2d/model.py`): trechos colineares ficam como nós separados, o que o
  modelo já permite.

## 6. Dependências da extensão

O `blender_manifest.toml` ganha `wheels = [...]` com `openskp`, `defusedxml`, `mapbox_earcut` e `shapely` (versões
fixas, em `caffmob_draw/wheels/`). Não é dado do usuário: não há migração.

## 7. Migrações

Não há. Os campos novos têm padrão, e a biblioteca do usuário nasce vazia.
