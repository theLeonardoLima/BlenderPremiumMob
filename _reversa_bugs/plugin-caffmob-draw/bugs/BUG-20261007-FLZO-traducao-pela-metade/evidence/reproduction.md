# Cápsula de reprodução: BUG-20261007-FLZO

- Commit base: `b92ac2e` (`master`) + mudanças do #4/#7 sem commit
- Ambiente: Linux 6.8, Blender 5.2 `--background --factory-startup`
- Taxa: 1/1 do titular (print) + sonda local determinística

## Sonda do mecanismo de tradução (`bpy.app.translations`)

Dicionário de teste com `("*", "Place Door")`, `("Operator", "Flip Swing")` (pt_BR) e `("*", "Clique numa face")` (en_US):

```
pt_BR | pgettext_iface("Place Door")=Inserir Porta | ("Place Door","Operator")=Place Door | ("Flip Swing","Operator")=Inverter Abertura
en_US | pgettext_iface("Clique numa face")=Click a face
```

- Entradas `en_US` registradas valem com o Blender em inglês.
- Rótulos de operador são traduzidos no contexto `"Operator"`: a chave `"*"` não casa. O `data/i18n.py` só usa `"*"`.

## Levantamento dos textos (AST, heurística de idioma; scratchpad `ui_strings.py`)

5.404 ocorrências, 3.975 textos únicos: ~2.192 em inglês, ~436 em português, ~1.347 neutros ou curtos demais para classificar.
`data/i18n.py` traz ~270 pares. Ocorrências por área (pt / en / neutro / com f-string):

| área | pt | en | neutro | f-string |
|---|---|---|---|---|
| product_libraries/face_frame | 3 | 1354 | 659 | 95 |
| product_libraries/frameless | 5 | 797 | 489 | 84 |
| operators | 95 | 328 | 213 | 103 |
| ui | 76 | 124 | 191 | 29 |
| (raiz) | 38 | 128 | 137 | 4 |
| product_libraries/closets | 0 | 129 | 114 | 17 |
| data | 110 | 2 | 22 | 0 |
| product_libraries/common | 0 | 70 | 29 | 0 |
| customize, aggregates, walls2d, move_over, standards, inspection, catalog, geometry_free, molding | 166 | 6 | 122 | 43 |
