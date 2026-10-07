# Cápsula de reprodução — BUG-20261007-TBY3

- Commit base: `499068f` (branch `master`)
- Ambiente: Linux 6.8, Blender 5.2 `--background` (arquivo de fábrica, com o cubo padrão), pacote do repositório
- Comando: `blender --background --python-exit-code 1 --python evidence/reproducao.py`
- Taxa: 1/1 · Classificação: determinístico

Saída:

```
cube True WALL False                 # object_kind == 'WALL' (padrão), is_property_set('object_kind') == False
classify cube Classified(kind='WALL', obj=Cube, root=Cube, library='BTM')
is_other_layer_wall True
insert_opening poll True
depois de setar True                 # ao gravar 'WALL' de propósito, is_property_set == True
```

Também no Blender do titular (2026-10-07): o editor perguntou "Converter / Só referência" por causa do cubo
(`../../BUG-20261007-VQ72-medida-do-trecho-no-painel/evidence/reproduction.md`).

Alcance (código): `selection/classify.py:112` (painel de Propriedades e Mover Sobre), `walls2d/scene_io.py:104`,
`operators/opening_builder.py:50,59`, `overlays/draw_handlers.py:182,233`, `ui/panels.py:16` (`_scene_has_walls`, sem uso).
