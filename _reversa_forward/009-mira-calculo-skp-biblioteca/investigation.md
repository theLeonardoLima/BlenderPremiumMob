# Investigação: 009-mira-calculo-skp-biblioteca

> Data: 2026-10-08.

## 1. Alinhamento na mira (inferência)

- **Referência de mercado.** O SketchUp e o AutoCAD (Object Snap Tracking) mostram uma linha-guia quando o cursor fica
  na mesma X ou Y de um ponto já desenhado. O AutoCAD usa uma abertura em pixels (`APERTURE`, padrão 10 px), e o
  SketchUp, uma tolerância em pixels de tela. O titular escolheu 8 px na tela (Q1).
- **Custo.** Uma busca por eixo é 1D: duas listas ordenadas e `bisect` dão O(log n) por movimento. A quadtree só valeria
  para "ponto mais perto em 2D", que o `hit_node` já faz para clique em vértice. A dívida D-02
  (`_reversa_sdd/architecture.md#4`) registra o custo de varrer tudo a cada `MOUSEMOVE`.
- **Fora desta versão:** pontos médios, interseções e prolongamento de linhas. Seriam inferências a mais, e a RN-02
  pede só os vértices.

## 2. Expressão de medida

- **Alternativas:**
  - `eval` com `__builtins__` vazio: inseguro, porque é escapável por atributos de objetos literais;
  - `ast.parse` com lista branca de nós: seguro, mas a unidade por número (`1,5m+20`) e a vírgula decimal exigiriam
    pré-processar o texto;
  - analisador próprio de cerca de 80 linhas: escolhido.
- **Gramática:**

  ```text
  expr   := term (('+'|'-') term)*
  term   := factor (('*'|'/') factor)*
  factor := ('+'|'-') factor | '(' expr ')' | number
  number := dígitos [(','|'.') dígitos] [mm|cm|m]
  ```

- **Unidades.** Cada número vira metros na hora (sem sufixo, a unidade da cena). Num produto ou num quociente, só faz
  sentido um fator com unidade; os demais são tratados como escalares. `2*8` vira 16 mm, e não 16 mm² (regra simples,
  documentada).
- **Erros:** texto vazio, caractere inválido, parênteses sem par, divisão por zero, resultado ≤ 0 ou acima de 1 km.
  Todos dão "Valor Inválido".

## 3. Direção travada

- **Comportamento atual** (`walls2d/ops_editor.py#_handle_draw`): o Enter calcula a direção do último ponto até o
  cursor. Depois de um Enter, o último ponto pula para a frente, e o cursor fica para trás, então o próximo Enter
  inverteria a direção. É exatamente a queixa do titular.
- **Modelo novo** (D-05): a direção é estado da sessão. Só o clique e as setas a mudam (Q2 e pendência 1).

## 4. SketchUp

### 4.1 Escolhido: OpenSKP (2026-10-09, sessão 3)

- [OpenSKP](https://github.com/iamahsanmehmood/openskp) 1.3.0 (PyPI `openskp`, licença MIT; criado em 2026-06,
  ativo). Leitor e escritor de `.skp` por engenharia reversa, sem vínculo com a Trimble, em Python puro.
- **Suporte:**
  - VFF (SketchUp 2021+): completo;
  - MFC legado (2013 a 2020): 11 de 15 arquivos de teste do projeto abrem.
- **Dependências:**
  - para ler: `defusedxml` (PSF, puro) e `mapbox_earcut` (ISC, binário);
  - `shapely` (BSD, binário) só num caminho de anéis sobrepostos, importado sob demanda;
  - `trimesh` e `Pillow` só na exportação GLB, que não usamos.

  Todas têm wheels cp313 para linux x86_64 e aarch64, win_amd64 e macOS x86_64 e arm64. O Python do Blender 5.2 é o
  3.13.13, com numpy 2.3.4.
- **Teste feito aqui:**
  - um `.skp` criado pelo próprio OpenSKP (`SkpBuilder`): porta com o componente "Batente" (material sólido) e
    "Folha" (material com textura PNG);
  - lido de volta com `SkpFile.parse()` e `build_scene()`: 4 primitivas (`positions`, `normals`, `uvs`, `indices`,
    `material_index`, `geom_name`), `scene_hierarchy` com "Batente 1" e "Folha 1", e `textures` com os bytes da
    imagem;
  - convertido em GLB e importado no Blender 5.2: medidas em mm (batente 863,6 × 38,1 × 2133,6) e textura presente.
    Os nomes dos materiais se perdem no GLB ("Material_0"), por isso a montagem é direta (D-16).
- **API:** `build_scene()` só devolve o glTF em Y-up, e a exportação GLB só aceita `units='mm'`. A montagem própria
  converte as duas coisas.

### 4.2 Descartado: pyslapi (RedHaloStudio/Sketchup_Importer)

- **Release 0.27.0** (2026-01-26), baixado em pasta temporária para análise:
  - `sketchup.cp37/39/310/311/313/314-win_amd64.pyd`;
  - `SketchUpAPI.dll` e `SketchUpCommonPreferences.dll`;
  - `__init__.py` (cerca de 1.100 linhas: `SceneImporter`, `ImportSKP`, `SceneExporter`) e `SKPutil/`.
- **Plataformas.** Não há binários de macOS nem de Linux. O README diz "Linux Support: Not available due to
  limitations in the SketchUp SDK".
- **Licenças:**
  - o código Python é GPLv3 ("or any later version"), compatível com o `GPL-3.0-or-later` do plugin;
  - o repositório RedHaloStudio não tem arquivo de licença; o cabeçalho do código é o que vale;
  - a DLL é do SDK da Trimble, com termos próprios de redistribuição a confirmar.
- **Ponto de adaptação.** `SceneImporter.load` lê
  `context.preferences.addons[__name__.split(".")[0]].preferences`. Vendorizado, isso aponta para o CAFFMob Draw, que
  não tem esses campos; é preciso trocar por um objeto de padrões. As opções do `load` são `reuse_material`,
  `reuse_existing_groups` e `max_instance`, entre outras.
- **Rota universal.** O SketchUp exporta glTF, OBJ e FBX, que o plugin já importa (003/007). Fora do Windows, a
  orientação é essa.

## 5. 3D Warehouse

- [Terms of Use / General Model License](https://embed-3dwarehouse-classic.sketchup.com/tos/):
  - permite usar e alterar os modelos, inclusive em trabalho comercial;
  - proíbe "aggregate any content (including Models) obtained from 3D Warehouse for redistribution";
  - proíbe remover os avisos de autoria.
- O download exige uma conta Trimble. Não automatizamos o download; seria o ToS e a conta do usuário.
- **Consequência:**
  - a biblioteca embutida é modelada pelo projeto (Q5);
  - o fluxo do 3D Warehouse é do usuário: baixar, importar, converter e guardar na biblioteca local;
  - o manifesto guarda a origem e o autor (RN-08), para não apagar a autoria.

## 6. Biblioteca e retextura

- **Formato.** O mesmo mecanismo da biblioteca de módulos (`customize/library_io.py`): `bpy.data.libraries.write` com
  `fake_user`, miniatura de 256 px e manifesto ao lado. O Asset Browser do Blender foi descartado: ele exige marcar
  assets e um catálogo `.cats.txt`, não guarda licença e muda o fluxo do usuário.
- **Retextura sem UV.** O nó Image Texture com projeção `BOX` e coordenadas `Object` dá escala real em qualquer
  malha (`docs/rag`: `ShaderNodeTexImage.projection`, `projection_blend`).

## 7. Padrões aplicáveis

- O catálogo em grade da 008 (`cabinet_editor/panels.catalog_grid`, `previews.py`) é reutilizado como padrão visual.
- O grupo de peças e a esquadria da 007 são a raiz do item.
- A gravação da folha e da peça de produção nos próprios objetos vem da 003.
