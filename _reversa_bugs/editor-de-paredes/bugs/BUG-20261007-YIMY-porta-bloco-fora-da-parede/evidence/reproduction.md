# Cápsula de reprodução: BUG-20261007-YIMY

- Commit base: `b92ac2e` (`master`), com as mudanças do #4 ainda sem commit (não tocam paredes nem aberturas)
- Ambiente: Linux 6.8, Blender 5.2, `--background --factory-startup`, addon registrado por `tests/_blender_env.py`
- Comando: `blender --background --factory-startup --python <scratchpad>/repro_yimy.py` (e `repro_yimy_esp.py`); o
  script cria a sala 4 x 3 m pelo editor (`walls2d.apply.apply_plan`) e põe a porta simples pelos mesmos métodos do
  botão (`create_placed_object`, `set_position_on_wall`, `cut_wall` de `place_door`)
- Exit code 0; taxa 3/3 (determinístico)

## Medidas (eixos locais da parede; a espessura vai de y=0 a y=0,15)

| Situação | Parede (y) | Porta (y) | Furo de face a face |
|---|---|---|---|
| Logo após inserir | 0 … 0,15 | 0 … 0,15 | sim |
| Direção da sala trocada no editor 2D + OK | 0 … 0,15 | **-0,15 … 0** (fora) | não: a porta não encosta na parede |
| Espessura 0,15 → 0,25 no editor 2D + OK | 0 … 0,25 | **0 … 0,15** | **não**: o raio no meio do vão bate na parede |

A inserção em si coloca a porta certa. Ela sai da parede quando a parede é reaplicada pelo editor.

## O "bloco sem detalhe"

Ele vem da gaiola de recorte, desenhada sólida e na frente da parede (`show_entry_door_and_window_cages`, padrão ligado).
É o comportamento do legado. Porta realista é escopo de feature nova (decisão do titular nas Agent Notes).

## Depois da correção (CHG-001)

```
blender_bug_YIMY_openings: OK          # antes: AssertionError ((1.086, 2.0), (-0.15, 0.0), (0.0, 2.134)) no §1
                                       #        e ((1.0, 1.914), (0.0, 0.15), (0.0, 2.134)) no §2
blender_002_smoke, blender_002_ui_events, blender_bug_A2G7_floor, blender_bug_ZZUK_undo, blender_bug_VQ72_panel,
blender_bug_TBY3_walls, blender_003_move_over_smoke: exit 0
unittest (167 testes): OK · ruff: ok · check_api: ok
```
