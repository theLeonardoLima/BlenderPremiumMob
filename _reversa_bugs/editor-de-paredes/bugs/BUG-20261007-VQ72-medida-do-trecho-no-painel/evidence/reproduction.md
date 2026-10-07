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

## Reprodução no Blender do titular (2026-10-07, MCP 9876, autorizado: "use o MCP e manipule o blender")

- Extensão instalada `bl_ext.user_default.caffmob_draw` (pacote de `9cd1d21`), arquivo novo, interface en_US.
- Sala 4 x 3 m aplicada; editor aberto por `caffmob.wall_editor(other_walls='REFERENCE')`; trecho (0, 1) selecionado.
- Print: `blender-do-titular-painel.png`. O painel aparece, mas os valores estão arredondados e em metros:

| campo | valor real | painel |
|---|---|---|
| Thickness | 0,15 m | 0.2 m |
| Start/End Height | 2,6 m | 3 m |
| Length | 4,0 m | 4 m (a planta mostra 4000 mm) |

- Unidade do projeto (planta): `MM` (`btm_settings.btm_unit = MILLIMETERS`); unidade da cena (painel): `METRIC / METERS`.
- Taxa: 1/1 · Classificação: determinístico (ambiente com cena em metros e projeto em mm, o padrão de um arquivo novo).
- Achado lateral: o cubo padrão da cena é tomado por "parede da outra camada" (`scene_io.is_other_layer_wall`, padrão
  `object_kind = 'WALL'`, achado A012), e o editor pergunta "Converter / Só referência" ao abrir.
