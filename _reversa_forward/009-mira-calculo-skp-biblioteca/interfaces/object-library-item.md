# Contrato: item da biblioteca de objetos

> Feature: `009-mira-calculo-skp-biblioteca` · Decisões D-08, D-09, D-11, D-13 · Arquivos:
> `caffmob_draw/object_library/store.py`, `item_io.py`

## Arquivos de um item

Três arquivos com o mesmo nome-base (`item_id`) na pasta da categoria:

| Arquivo | Conteúdo |
|---|---|
| `<item_id>.blend` | Objetos do item (raiz com `btm_object_item.is_item` e os filhos), com `fake_user`, gravados por `bpy.data.libraries.write(path_remap='RELATIVE_ALL')` |
| `<item_id>.json` | Manifesto (abaixo) |
| `<item_id>.png` | Miniatura de 256 × 256 px, fundo transparente |

## Manifesto (`format: "caffmob_draw.object_item"`, versão 1)

```json
{
  "format": "caffmob_draw.object_item",
  "version": 1,
  "item_id": "porta-lisa-80-a1b2c3",
  "name": "Porta lisa 80",
  "category": "DOORS",
  "root": "Porta lisa 80",
  "source": "CAFFMob Draw",
  "author": "",
  "license": "GPL-3.0-or-later",
  "size_mm": [800.0, 35.0, 2100.0],
  "features": ["LEAF_SWING", "PRODUCTION_PART"],
  "materials": ["Branco Neve"],
  "created_at": "2026-10-08T22:00:00-03:00",
  "addon_version": "1.9.0"
}
```

| Campo | Tipo | Regra |
|---|---|---|
| `format`, `version` | string, inteiro | Fixos. Um formato diferente faz o item ser ignorado, com um aviso na listagem |
| `item_id` | string | `[a-z0-9-]`, único na categoria; é o nome-base dos três arquivos |
| `name` | string | Rótulo exibido; não precisa ser único fora da categoria |
| `category` | string | Uma das 7 de RN-08 (`DOORS` … `OTHER`) |
| `root` | string | Nome do objeto raiz dentro do `.blend` |
| `source`, `author`, `license` | string | Origem e autoria (RN-08). A embutida usa `CAFFMob Draw` e `GPL-3.0-or-later`; `source` nunca é "3D Warehouse" na pasta embutida (verificado pelo `build.py`) |
| `size_mm` | 3 números | Largura, profundidade e altura da caixa do item |
| `features` | lista | O que o item já traz: `GROUP`, `FRAME`, `LEAF_SWING`, `LEAF_SLIDE`, `AGGREGATE`, `PRODUCTION_PART`, `TEXTURED` (só para exibir) |
| `materials` | lista | Nomes dos materiais usados (para avisar se faltarem) |
| `created_at`, `addon_version` | string | Rastreio |

## Erros

- Falta o `.blend` ou o `.json`: o item não aparece, e a listagem registra um aviso.
- Falta a `.png`: o item aparece com o ícone nativo da categoria.
- O `.blend` não tem o objeto `root`: Inserir falha com "Item corrompido: <nome>" e nada é inserido.
- Nome repetido ao acrescentar: Substituir (regrava os três arquivos) ou Renomear (sufixo " 2", " 3"…).

## Idempotência

Salvar o mesmo item duas vezes com Substituir gera os mesmos arquivos, salvo `created_at`. Inserir não altera a
biblioteca.
