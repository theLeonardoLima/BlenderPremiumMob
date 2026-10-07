# Cápsula de reprodução — BUG-20261007-ZZUK

- Commit base: `ec8b3f8` (branch `master`)
- Ambiente: Linux 6.8, Blender 5.2 com janela (`--factory-startup --enable-event-simulate`), instância própria; o Blender do titular não foi usado
- Comando: `blender --factory-startup --enable-event-simulate --python evidence/reproducao-com-janela.py`
- Exit: 0 · Taxa: 1/1 · Classificação: determinístico (o modal não tem caminho para Ctrl+Z)

Roteiro: sala 4 x 3 m aplicada; abrir o editor; selecionar um trecho; mudar o comprimento pelo campo do painel
(+0,5 m); Ctrl+Z (evento simulado na janela do editor).

Saída (`saida.txt`):

```
medida mudou True
CTRL+Z -> sessão viva True desfez False
```
