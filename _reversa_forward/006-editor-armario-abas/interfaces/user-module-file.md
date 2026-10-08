# Interface: arquivo de módulo do usuário (`caffmob_draw.user-module`) 1.1.0

> Contrato base: `_reversa_forward/003-modulos-agregados-reposicionar/interfaces/user-module-file.md` (1.0.0).
> Código: `caffmob_draw/customize/manifest.py`, `caffmob_draw/customize/library_io.py`.

## Mudança

`schema_version` passa de `1.0.0` para `1.1.0` (mudança compatível: só acrescenta campos opcionais).

```json
{
  "format": "caffmob_draw.user-module",
  "schema_version": "1.1.0",
  "...": "campos da 1.0.0 sem mudança",
  "structure": {
    "RIGHT": {"removed": true, "mode": "KEEP", "thickness_mm": 0, "material": ""},
    "TOP": {"removed": false, "mode": "KEEP", "thickness_mm": 18, "material": ""}
  },
  "divisions": [
    {"uid": "a1b2c3", "space": "s0", "orientation": "VERTICAL", "offset_mm": 400,
     "use_front": true, "front_mm": 20, "use_back": false, "back_mm": 20, "thickness_mm": 0, "material": ""}
  ]
}
```

## Regras

- `structure` e `divisions` são opcionais. Ausentes = nada removido, nenhuma divisão.
- `role`: `TOP`, `BOTTOM`, `BACK`, `LEFT`, `RIGHT`. `mode`: `KEEP`, `EXTEND`, `SHRINK`. `orientation`: `VERTICAL`,
  `HORIZONTAL`.
- Medidas em mm. `thickness_mm = 0` e `material = ""` significam "segue o Configurador ou a biblioteca".
- `space` usa o caminho de subvão (`s<n>` para espaço-raiz, `.a`/`.b` para cada metade).

## Erros

`validate()` acrescenta:
- `role`, `mode` ou `orientation` desconhecido;
- `space` mal formado;
- medida negativa.

Erro impede a importação, como já acontece na 1.0.0.

Se a biblioteca do destino não permitir um `mode` que está no arquivo, a importação aplica `KEEP` e mostra aviso.

## Compatibilidade

- Leitor 1.1 abre arquivos 1.0.0 sem mudança.
- Leitor 1.0 abre arquivos 1.1.0, porque o major é 1, e ignora `structure` e `divisions`.
- Idempotência: importar o mesmo arquivo duas vezes gera dois módulos iguais. Os `uid` das divisões são renovados
  na importação.
