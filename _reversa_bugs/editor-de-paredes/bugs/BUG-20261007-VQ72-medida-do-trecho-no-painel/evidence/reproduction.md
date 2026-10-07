# Cápsula de reprodução — BUG-20261007-VQ72

- Commit base: `ec8b3f8` (branch `master`)
- Ambiente: Linux 6.8, Blender 5.2 com janela (`--factory-startup --enable-event-simulate`, interface em inglês), instância própria
- Comando: `blender --factory-startup --enable-event-simulate --python evidence/reproducao-com-janela.py`
- Exit: 0 · Taxa: 0/1 · Classificação: **not-reproduced**

Roteiro: sala 4 x 3 m aplicada; abrir o editor; ferramenta Selecionar/Mover; clique simulado no meio de um trecho.

Resultado:
- o clique seleciona o trecho (`sel (0, 1)`, linha interna) e a seta aparece;
- o painel "Panel" (aba "Wall Editor") mostra Line, Length, Absolute/Relative Angle, Lock Angle, Thickness,
  Start/End Height, Direction e Wall Type (`editor-painel-depois-do-clique.png`);
- o campo Length tem o valor do trecho (4 m) e mudar o campo altera o rascunho (`medida mudou True`).

Não foi possível olhar o Blender do titular: a ponte MCP (porta 9876) recusou a conexão em 2026-10-07.
Diferenças possíveis do ambiente do titular: extensão instalada (não o pacote do repositório), interface em pt_BR,
outro arquivo/paredes, outra aba na região lateral ("Tool"/"View"), painel recolhido.
