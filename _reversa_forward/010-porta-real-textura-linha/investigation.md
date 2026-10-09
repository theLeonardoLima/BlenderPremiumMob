# Investigação: 010-porta-real-textura-linha

> Data: 2026-10-09.

## 1. Porta de parede hoje

`operators/doors_windows.py#_PlaceWallObjectBase.create_placement_object` cria:
- uma caixa `GeoNodeCage` (Dim X largura, Dim Y espessura da parede, Dim Z altura), com `IS_ENTRY_DOOR_BP`, cor da
  preferência e, com "Mostrar caixas", `display_type TEXTURED` e `show_in_front`;
- o símbolo 2D `GeoNodeDoorSwing`, com os sockets `Swing Inside`, `Is Left` e `Is Double`;
- um texto "DOOR".

A caixa é o próprio objeto que corta a parede (`cut_wall`: booleano DIFFERENCE/EXACT com `mod.object = caixa`). Os
padrões são americanos (`hb_props.py`: 36" × 84", 72" na dupla). A inspeção da 005 (`inspection/room_door_math.py`)
mede o giro pela caixa e pelo símbolo.

## 2. Porta realista do Codex (`docs/porta_realista_080x210/`)

- Gerada por `gerar_porta.py` (cerca de 200 linhas, Blender em segundo plano), com:
  - **157 objetos**, cada um com Bevel (até 4 segmentos) e Weighted Normal;
  - textura de nogueira gerada com numpy (1024 × 2048, cor e rugosidade, PNG de cerca de 2 MB cada);
  - OBJ/MTL de 7,6 MB;
  - cena de apresentação em Cycles.
- Medidas: folha de 800 × 40 × 2100, 8 mm acima do piso; marco de 46 mm com 145 mm de profundidade; guarnições de
  72 mm com filete; 3 dobradiças a 250, 1050 e 1860 mm; maçaneta a 1020 mm; folga lateral de 3 mm.
- O LEIA-ME declara: "Modelo original […] inspirado apenas nas dimensões do nome da referência […]; não é uma
  conversão desse arquivo." Logo, pode ir para o plugin, sob a licença do projeto.
- Para o plugin, duas conclusões:
  - 157 objetos por porta pesam numa planta com 10 portas. Juntar por papel (D-08) reduz para cerca de 5;
  - a textura procedural custa a cada geração. Convertida uma vez para JPG, fica compartilhada (D-09).

## 3. `blender-product-polish` (`~/.agent/skills/product-polish`)

- A skill não modela. Ela importa um GLB pelo addon Blender MCP (porta 9876) e:
  - limpa a cena;
  - tira os mapas de normal e rugosidade ruidosos;
  - aplica um material "glass-like" (rugosidade 0,02, coat 1,0, IOR alto);
  - monta a iluminação de 4 pontos (`studio`: 350/250/250/100 W);
  - usa EEVEE com ray tracing.
- O Codex usou a skill na apresentação da porta. Para a janela, os mesmos valores entram no material de alumínio e
  vidro e no script de prévia, sem depender do MCP aberto (D-15).

## 4. Janela de parede

Igual à porta: uma caixa `IS_WINDOW_BP` com texto. A 007 (`aggregates/install.py`) já mostrou o padrão de pôr uma
esquadria dentro da caixa, centrada por drivers, com o slide limitado pelos batentes (`aggregates/slide_limits.py`).
Esse padrão é reaproveitado (D-10, D-14).

## 5. Modo de vista

- O Blender 5.2 tem, em `View3DShading`, o `color_type` `'TEXTURE'` (textura no modo sólido) e, em `View3DOverlay`,
  `show_wireframes`, `wireframe_threshold` (0 = só arestas de forma; 1 = todas) e `wireframe_opacity`.
- Conferir no RAG antes do código: `docs/rag/blender-api/corpus/bpy.types.View3DShading.md`,
  `bpy.types.View3DOverlay.md`.
- As configurações recomendadas do legado (`ops.py`) já ligam `show_wireframes` com limiar 0 e opacidade 0,8, mas
  dentro de um conjunto maior. A 010 dá um controle próprio, salvo na cena (D-05).

## 6. Hierarquia do SketchUp

- No OpenSKP, `scene.scene_hierarchy` é uma árvore de `InstanceNode` (com nome, definição, caminho e filhos), e
  `mesh_index[geom_name].path` diz a que nó pertence cada primitiva.
- A 009 agrupava por caminho completo e criava todos os grupos no topo. Na porta de 75 do titular, isso deu 7 grupos
  soltos (a folha mais 6 ferragens filhas).
- A árvore (D-01) cria os grupos aninhados.
- As figuras de escala do SketchUp vêm como componentes `2D_*` ou com o nome das figuras padrão; a de 75 trazia
  `2D_Woman_Standing_Sandra` (883 faces).
