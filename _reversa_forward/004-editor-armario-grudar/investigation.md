# Investigation: Editor de armário, grudar em superfície plana e colisão

> Identificador: `004-editor-armario-grudar`
> Data: `2026-10-07`
> Fontes: leitura do código em `caffmob_draw/` (três varreduras), features 001-003, RAG `docs/rag/`

## 1. O que o código faz hoje

### 1.1 Móveis na parede

| Biblioteca | Onde | Comportamento |
|---|---|---|
| Frameless | `product_libraries/frameless/operators/ops_placement.py:421-434`, `1520-1564` | Filho da parede; frente `y = 0`, giro 0; trás `x + largura`, `y = Thickness`, giro π; cantos em `y = 0` |
| Face frame | `product_libraries/face_frame/operators/ops_placement.py:2484-2486`, `2697-2704` | Filho com inversa identidade; frente `y = recess`; trás `y = thickness − recess`, giro π |
| Closets | `product_libraries/closets/operators/ops_closet.py:949-966`, `809-820` | Frente `y = 0`; trás `y = thickness`, giro π; lado escolhido por `local_y < thickness/2` |
| `btm` | `operators/cabinet_builder.py:47-48` | Só no cursor 3D, sem parede |

- Nenhum idprop guarda o lado; ele é deduzido em `measure/scene_cotas.py:43-46`.
- A origem do módulo fica nas costas, e o corpo cresce para −Y (`move_over/ops_move_on_wall.py:60`).
- `GeoNodeWall` (`hb_types.py:405-460`) tem origem no ponto inicial, no piso, e o corpo ocupa Y local de 0 a +Thickness.
- **Defeito confirmado:** mudar a espessura move só a face Y = espessura. Nada reposiciona os filhos:
  - `walls2d/apply.py:146-154` só ajusta o `Dim Y` das aberturas;
  - `operators/walls.py:1644`, `:2416-2421` e `:4300-4335` não tocam nos filhos.
  - Resultado: o módulo de trás fica dentro da parede quando ela engrossa, ou solto quando ela afina.
- O legado não usa o mesmo nome para o mesmo lado: `operators/walls.py:1192` e `:2979` chamam Y = 0 de "back face", enquanto o posicionamento a trata como frente.

### 1.2 Agregados e plano de inserção (003)

- `aggregates/limits.py` é puro e trabalha com os seis lados da caixa local, sempre com clamp de contorno.
- `aggregates/apply.py:80-104` já reposiciona os agregados quando a caixa avaliada do pai muda, num handler `depsgraph_update_post`.
- `aggregates/convert.py:26-49` guarda o pai e a matriz originais e faz o parentesco com inversa identidade.
- `move_over/insertion_plane.py:13-46` faz um `Scene.ray_cast` e usa a normal do polígono, sem testar se a face é plana. O resultado fica no `WindowManager` e não é salvo.
- `hb_snap.best_hit` (`hb_snap.py:48-82`) descarta a normal. Nenhum código encaixa um item numa face pela normal.

### 1.3 Colisão

- `inspection/interference.py` cobre só o envelope de abertura das frentes:
  - tolerância de 1 mm, cascos encolhidos 1 mm;
  - pré-filtro por caixa, depois `BVHTree.overlap` com a malha avaliada;
  - resultado em `WindowManager.btm_inspection`, sem marca de desatualizado.
- O "Ir para" atual (`inspection/ops_interference.py:41-68`) só desloca a vista, não enquadra.
- `move_over/scene.overlapping` (`:162-176`) usa só caixas de módulo. O Mover Sobre pede uma segunda confirmação quando há sobreposição.
- Campos existentes:
  - `btm_settings.collision_global` ("Evitar Sobreposição") já é usado por `hb_placement.avoid_overlap`;
  - `btm_plane.collision_override` existe e nada o lê.
- `cutting/stale.py:60` é o padrão de "desatualizado" por depsgraph.
- `ui/save_feedback.py` é o padrão de aviso na barra de status vindo de um handler.

### 1.4 Editor de paredes como molde

- Abertura da janela: `walls2d/window.py:58-113` usa `area_dupli`, transforma a área em `IMAGE_EDITOR` e tem fallback para a área atual.
- Desenho: um `POST_PIXEL` global que filtra pela área do editor (`window.py:141-154`).
- Rascunho: um singleton de sessão (`walls2d/props.py:17-101`) com histórico de cópias (`walls2d/history.py`, limite de 100). Ctrl+Z dentro do modal não chega ao undo do Blender (`ops_editor.py:361`, `378-389`).
- Passo de desfazer: um só, porque o modal tem `UNDO` e devolve `FINISHED` depois de `apply_plan`. Cancelar devolve `CANCELLED`.
- Diferença para o editor de armário: a parede tem um modelo puro (`WallPlan`) aplicado no OK. O módulo não tem esse modelo, e cada biblioteca reconstrói as próprias peças.

### 1.5 Medidas por biblioteca

- `selection/editing.set_dimension` (`:75-92`):
  - frameless: GN `Dim X/Y/Z`;
  - face frame: `face_frame_cabinet.*`, sem mínimo nem máximo;
  - closets: `hb_closet_starter.*`, sem mínimo nem máximo;
  - `btm`: `btm_cabinet.*`, de 0,1 a 3,0 m.
- Limite geral: `editing.LIMITS` (0,01 a 10 m).

## 2. Alternativas avaliadas

| Tema | Alternativa | Por que ficou ou saiu |
|---|---|---|
| Identidade da face | Índice do polígono do `ray_cast` | Saiu: o GN reavalia e as booleanas de abertura mudam a topologia |
| Identidade da face | Lado da caixa local (`BOX_SIDE`) + plano local (`PLANE`) | Ficou (D-02): segue a medida do hospedeiro no caso comum |
| Manter na face | Gancho só nos operadores do plugin | Saiu: o G nativo tiraria o item da face |
| Manter na face | Handler de depsgraph com projeção no plano | Ficou (D-04), no padrão de `aggregates/apply.py` |
| Espessura da parede | Corrigir em cada lugar que muda a espessura (4 pontos) | Saiu: frágil; o handler cobre todos |
| Vínculo | Constraint `CHILD_OF` | Saiu: o legado já usa o parentesco direto |
| Profundidade da colisão | Malha × malha | Saiu: caro; caixa orientada + BVH para confirmar o par |
| Aviso no G nativo | Temporizador que adivinha o fim do arraste | Saiu: frágil; o resultado só fica "desatualizado" |
| Rascunho do editor | Modelo puro do módulo | Saiu: as quatro bibliotecas reconstroem as peças de jeitos diferentes |
| Rascunho do editor | Duplicar o módulo e trocar no fim | Saiu: quebra nomes, drivers e vínculos |
| Rascunho do editor | Edição ao vivo + instantâneo (medidas + `spec`) reaplicado | Ficou (D-21); risco do undo aninhado em D-22 |
| Global de colisão | Campo novo | Saiu: `collision_global` já existe com esse sentido |

## 3. Referências da API (RAG 5.2)

- `docs/rag/blender-api/corpus/mathutils.bvhtree.md#mathutils.bvhtree.BVHTree.overlap`
- `docs/rag/blender-api/corpus/bpy.ops.view3d.md#bpy.ops.view3d.view_selected`
- `docs/rag/blender-api/corpus/bpy.types.Operator.md#modifying-blender-data-undo`: o passo de desfazer nasce quando o operador com `UNDO` devolve `FINISHED`
- `docs/rag/project/04_armadilhas.md#Undo`: devolver `CANCELLED` depois de mudar dados deixa mudanças sem passo. O editor reaplica o instantâneo antes de cancelar (D-21).
- `Scene.ray_cast` e `depsgraph_update_post` já são usados no projeto (`move_over/insertion_plane.py:46`, `aggregates/apply.py:81`).

## 4. Padrões aplicáveis do projeto

- Núcleo puro + `tests/test_*.py` com `_bootstrap`. Os pacotes novos entram na lista `_stub` de `tests/_bootstrap.py`.
- Fumaça `tests/blender_*.py` com `assert`, rodada com `--background --factory-startup`.
- Tradução: texto novo em `data/translations/*.json` com pt_BR e en_US. O teste `tests/test_i18n_coverage.py` confere a cobertura.
