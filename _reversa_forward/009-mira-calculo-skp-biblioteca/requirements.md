# Requirements: Mira com alinhamento e cálculo no editor de paredes; SketchUp e biblioteca de objetos

> Identificador: `009-mira-calculo-skp-biblioteca`
> Data: `2026-10-08`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Para o projetista que desenha a planta e monta o ambiente no CAFFMob Draw, a feature tem três entregas:
- **No editor de paredes:**
  - uma mira em cruz no ponteiro, que se alinha sozinha a pontos já desenhados;
  - digitação de medidas com conta (`2*8`, `200/2`), aplicada na direção atual, sem depender do mouse.
- **Importação de SketchUp (`.skp`):** pelo leitor de código aberto OpenSKP, em qualquer plataforma.
- **Biblioteca de objetos do ambiente** (portas, janelas, cooktops, mesas, decoração), organizada por categoria. O
  usuário acrescenta os próprios modelos e os torna manipuláveis: folha de porta, chapas como peças de produção,
  retexturização.

O legado já tem o editor 2D e a importação OBJ/FBX/glTF com conversão em agregado e folha (003/007). Faltam a precisão
de alinhamento, a digitação contínua, o formato do SketchUp e um lugar organizado para guardar e reutilizar objetos.

Restrições achadas na pesquisa (2026-10-08 e 2026-10-09):
- o importador pyslapi só tem binários para **Windows** (o SDK da Trimble não tem bibliotecas para Linux). Por isso, a
  leitura do `.skp` passou para o **OpenSKP** (MIT, Python puro), que funcionou no Linux do titular (sessão 3);
- a licença dos modelos do 3D Warehouse **proíbe agregá-los numa biblioteca redistribuída** (RN-09).

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/wall_editor/requirements.md#RF-WE-01, RF-WE-05` | Snap na aresta ou extremidade mais próxima; digitação direta de comprimento na unidade escolhida | 🟢 |
| `_reversa_sdd/domain.md#2.1` (R-01 a R-03) | Paredes e piso: o piso segue o perímetro interno; o sentido da parede define o lado da espessura | 🟢 |
| `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RN-12, RN-15` | Encontros entre trechos ligados refeitos no OK; linha interna e externa | 🟢 |
| [OpenSKP](https://github.com/iamahsanmehmood/openskp) 1.3.0 (PyPI `openskp`, MIT), testado em 2026-10-09 | Lê SketchUp 2013 a 2026 em Python puro. Um `.skp` criado por ele (porta com batente e folha texturizada) foi lido de volta com a hierarquia "Batente 1"/"Folha 1", as medidas em mm (863,6 × 2133,6) e a textura; a leitura precisa só de `defusedxml` e `mapbox_earcut` | 🟢 |
| `caffmob_draw/walls2d/ops_editor.py` (`_handle_draw`, `preview_point`, `close_snap`) | No lápis, Enter usa a direção do **cursor** no momento; aceita só dígitos, vírgula e ponto; trava ortogonal de ±2,5°; ímã do ponto inicial de 15 px; grade magnética | 🟢 |
| `caffmob_draw/data/units.py#parse_length` | Medida com sufixo mm/cm/m; sem expressões | 🟢 |
| `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#RF-11, RN-11, RN-13, RF-16` | Importar OBJ/FBX/glTF; malha trazida por outro addon (`.skp`) pode virar agregado ou folha de porta; peça de produção é opcional | 🟢 |
| `_reversa_forward/007-janela-obj-folhas-colisao/` | Unidade e eixo na importação; grupos de peças; "Montar esquadria"; folhas com batentes | 🟢 |
| `caffmob_draw/customize/library_io.py` | Biblioteca do usuário: `.blend` + manifesto JSON + miniatura em `extension_path_user` | 🟢 |
| Release `RedHaloStudio/Sketchup_Importer` 0.27.0 (2026-01-26), baixado em pasta temporária | `.pyd` só `win_amd64` (CPython 3.7 a 3.14), `SketchUpAPI.dll` (SDK proprietário da Trimble), código Python GPLv3; o README diz "Linux Support: Not available"; suporta Blender 5.1 alpha e SketchUp 2026.1 | 🟢 |
| [3D Warehouse: Terms of Use](https://embed-3dwarehouse-classic.sketchup.com/tos/) (General Model License) | Permite usar modelos em obras próprias, inclusive comerciais; proíbe "aggregate any content (including Models) obtained from 3D Warehouse for redistribution"; o download exige conta Trimble | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de interiores (vindo do Promob/SketchUp) | Desenhar a planta rápido e alinhada | Ao desenhar a parede da frente, a mira trava na altura do canto da parede oposta e o ponto sai pareado sem medir |
| Projetista medindo na obra | Lançar as medidas da trena em sequência | Digita `2850` Enter, `1200` Enter, `3200-150` Enter, e as paredes saem na direção escolhida, sem mexer o mouse |
| Projetista que usa o 3D Warehouse | Trazer uma porta ou um cooktop que já baixou | Importa o `.skp` ou o glTF/OBJ, transforma a folha em folha de porta, troca a textura e guarda na biblioteca "Portas" |
| Marceneiro | Aproveitar o tampo de uma mesa como chapa | Marca o tampo importado como peça de produção, e ele sai no plano de corte |

## 4. Regras de negócio novas ou alteradas

### Incremento 1: editor de paredes

1. **RN-01, mira em cruz.** No modo lápis e em Selecionar/Mover, o ponteiro mostra duas linhas que atravessam a vista
   inteira, uma horizontal e uma vertical, passando pelo ponto do cursor. 🟢
   - Origem no legado: `_reversa_sdd/wall_editor/requirements.md#RF-WE-01` (snap passa a incluir alinhamento)
   - Tipo: nova
2. **RN-02, alinhamento (inferência).** As referências são os vértices das paredes, desenhadas e em desenho, e o ponto
   inicial do desenho atual.
   - Quando a coordenada Y do cursor chega perto da Y de uma referência, a linha horizontal trava nela, fica destacada
     e liga o cursor à referência por uma linha tracejada.
   - O mesmo vale para X e a linha vertical.
   - As duas travas podem valer ao mesmo tempo, e o ponto fica no cruzamento.
   - **Shift** segurado desliga só o alinhamento X/Y; a trava ortogonal, o vértice exato e o ímã do início continuam.
     🟢 (Esclarecimentos 2026-10-08, sessão 2, Q1)
   - A tolerância é de **8 px na tela**, igual em qualquer zoom. Com a vista aproximada, 8 px ficam perto dos 5 mm
     pedidos; com a vista afastada, a trava continua fácil de acertar.

   🟢 (Esclarecimentos 2026-10-08, Q1)
   - Tipo: nova
3. **RN-03, prioridade das travas.** A ordem é: ímã do ponto inicial (fechar), depois vértice exato, depois
   alinhamento X/Y, depois trava ortogonal (±2,5°) e, por fim, grade magnética. Um clique com trava ativa grava o ponto
   travado, e o ponto clicado fica exatamente pareado (diferença 0). 🟡
   - Origem no legado: `walls2d/ops_editor.py#preview_point`, `close_snap`
   - Tipo: alterada
4. **RN-04, expressão na medida.** A digitação aceita números com vírgula ou ponto, `+ - * /`, parênteses e sufixo de
   unidade no número (`2*8`, `200/2`, `(3000-150)/2`, `1,5m+20`). O resultado é avaliado sem `eval` e mostrado ao
   lado do texto (`2*8 = 16 mm`). Um texto inválido, um resultado ≤ 0 ou uma divisão por zero mostra "Valor Inválido"
   e não cria parede. 🟢
   - Origem no legado: `data/units.py#parse_length`
   - Tipo: alterada (amplia)
5. **RN-05, direção atual.** A direção vem do primeiro movimento do mouse a partir do ponto inicial, com a trava
   ortogonal aplicada. Cada Enter cria um trecho com o comprimento digitado **nessa direção, sem levar o mouse em
   conta**, e o fim do trecho vira o novo ponto de partida. Exemplo: `100` Enter, `285` Enter, `2*8` Enter, `200/2`
   Enter e `2000` Enter criam cinco trechos seguidos, de 100, 285, 16, 100 e 2000 mm, na mesma direção. 🟢
   - Origem no legado: `walls2d/ops_editor.py#_handle_draw` (Enter usa o cursor)
   - Tipo: alterada
6. **RN-06, mudar de direção.** Mover o mouse **sem clicar não muda** a direção atual: ela continua travada, mesmo
   que o mouse vá para outro lado. A direção muda de dois jeitos:
   - **Clique na nova direção:** cria o ponto no cursor, como hoje, com as travas da RN-03. A direção do trecho criado
     vira a direção atual dos próximos Enter.
   - **Setas do teclado:** → 0°, ↑ 90°, ← 180°, ↓ 270°, na planta. Trocam a direção sem criar parede.

   A direção atual aparece como uma seta no último ponto e no texto ("→ 0°"). 🟢 (Esclarecimentos 2026-10-08, Q2)
   - Tipo: nova
7. **RN-07, trechos colineares.** Trechos seguidos na mesma direção ficam separados: cada Enter é uma parede, como
   pediu o titular. O OK do editor não os funde. 🟡
   - Tipo: nova

### Incremento 2: biblioteca de objetos

8. **RN-08, categorias.** A biblioteca de objetos do ambiente tem as categorias Portas, Janelas, Cooktops e
   eletros, Mesas, Cadeiras e assentos, Decoração e Outros. Cada item guarda o nome, a categoria, a miniatura, a
   origem (arquivo e autor, quando houver), a licença informada e a data. 🟡
   - Tipo: nova
9. **RN-09, origem dos itens.** A biblioteca **que vem com o plugin** só contém modelos que o plugin pode
   redistribuir: feitos pelo projeto, CC0 ou com licença compatível registrada. Modelos do 3D Warehouse **não vêm com
   o plugin**, porque a licença proíbe agregá-los para redistribuição. O usuário pode baixá-los com a própria conta e
   acrescentá-los à **sua** biblioteca local, que fica com ele. 🟢
   - Tipo: nova
10. **RN-10, acrescentar item.** O usuário traz um item de um arquivo (OBJ, FBX, glTF/GLB e, quando disponível, SKP)
    ou de objetos já na cena. Ele escolhe a categoria e o nome, e o item é salvo com a miniatura na biblioteca do
    usuário, sem ir para a pasta do plugin. Um nome repetido na mesma categoria pede para substituir ou renomear. 🟢
    - Origem no legado: `customize/library_io.py` (formato da biblioteca do usuário)
    - Tipo: alterada (amplia para objetos)
11. **RN-11, item manipulável.** Ao inserir ou acrescentar um item, o plugin oferece as conversões que já existem:
    - grupo de peças (007);
    - agregado (003);
    - folha de porta de giro ou de correr, com batentes (003/007);
    - peça de produção para as chapas (003 RN-13).

    O que o usuário configurar fica salvo no item: inserir de novo traz a folha e as chapas já configuradas. 🟢
    - Origem no legado: `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#RN-11, RN-13`
    - Tipo: alterada (passa a persistir na biblioteca)
12. **RN-12, retexturizar.** Num item inserido, o usuário troca o material de uma parte ou do item inteiro pelos
    materiais do plugin (acabamentos) ou por uma imagem de textura própria, com a escala em mm. A troca vale para
    aquela cópia, e salvar de novo na biblioteca é opcional. 🟡
    - Tipo: nova

### Incremento 3: SketchUp

13. **RN-13, importar `.skp`.** O CAFFMob Draw lê `.skp` com o **OpenSKP** (MIT, Python puro) em Linux, Windows e
    macOS, sem a DLL da Trimble e sem Wine.
    - Formatos: o SketchUp 2021+ (VFF) é totalmente suportado; nos arquivos de 2013 a 2020, cerca de 3 em cada 4
      abrem, segundo os testes do próprio projeto.
    - Um arquivo que não abre mostra o motivo e a alternativa: abrir no SketchUp e salvar numa versão recente, ou
      exportar em glTF, OBJ ou FBX.
    - Dependências empacotadas como wheels da extensão, com licenças compatíveis com a GPL:
      - `openskp` (MIT);
      - `defusedxml` (PSF);
      - `mapbox_earcut` (ISC);
      - `shapely` (BSD).

    🟢 (Esclarecimentos 2026-10-09, sessão 3)
    - Tipo: nova
14. **RN-14, depois de importar o SKP.**
    - Componentes e grupos do SketchUp viram grupos de peças (007).
    - Materiais e texturas são mantidos: os objetos recebem os materiais do `.skp`, com as imagens das texturas
      carregadas (verificado em teste, sessão 2, Q3).
    - A unidade é a do arquivo, e o eixo vertical é Z.
    - O modelo entra pronto para RN-11.

    🟡
    - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Mira em cruz no ponteiro do editor de paredes (RN-01) | Must | As duas linhas atravessam a vista e acompanham o cursor nos modos lápis e Selecionar/Mover | 🟢 |
| RF-02 | Alinhamento X/Y a vértices, com destaque e linha-guia tracejada (RN-02, RN-03) | Must | Com um vértice em Y = 2000 mm, levar o cursor a Y = 2003 mm trava em 2000, e o ponto clicado tem Y = 2000 exato | 🟡 |
| RF-03 | Expressão na medida com resultado ao lado (RN-04) | Must | `2*8` mostra "= 16 mm", e Enter cria 16 mm; `200/2` cria 100 mm; `10/0` mostra "Valor Inválido" e nada muda | 🟢 |
| RF-04 | Enter usa a direção atual, não o cursor; o ponto de partida avança (RN-05) | Must | Com a direção 0°, a sequência 100, 285, 2*8, 200/2, 2000 cria 5 trechos colineares que somam 2501 mm, com o mouse parado em qualquer lugar | 🟢 |
| RF-05 | Mudar a direção por clique ou pelas setas do teclado; o mouse sem clique não muda a direção (RN-06) | Must | Depois dos 5 trechos, mover o mouse para cima sem clicar e digitar 300 Enter ainda cria um trecho a 0°; apertar ↑ e digitar 1200 Enter cria 1200 mm a 90° | 🟢 |
| RF-06 | Biblioteca de objetos com categorias, miniaturas e busca por nome (RN-08) | Must | A aba lista as 7 categorias; um item clicado aparece no cursor 3D, acompanha o mouse e um clique o solta; o Esc cancela e remove o item | 🟢 |
| RF-07 | Itens iniciais **modelados pelo projeto**: 1 porta, 1 janela, 1 cooktop, 1 mesa e 2 de decoração, em geometria simples e limpa, já com folha, chapas e materiais configurados (RN-09) | Should | Cada item tem origem "CAFFMob Draw" e a licença do plugin no manifesto; a porta abre com a barra; o tampo da mesa é peça de produção | 🟢 |
| RF-08 | Acrescentar à biblioteca a partir de arquivo ou da seleção, com categoria, nome e miniatura (RN-10) | Must | Uma porta glTF acrescentada em "Portas" aparece na grade com a miniatura e continua lá depois de reiniciar o Blender | 🟢 |
| RF-09 | Conversões no item (grupo, agregado, folha, peça de produção) salvas com ele (RN-11) | Must | Uma porta salva com a folha de giro de 90° volta, ao inserir, com a barra de abertura funcionando | 🟢 |
| RF-10 | Retexturizar uma parte ou o item, com material do plugin ou imagem própria (RN-12) | Should | Trocar o tampo de uma mesa para "Carvalho" muda só o tampo; a textura própria aceita PNG ou JPG com escala em mm | 🟡 |
| RF-11 | Importar `.skp` em qualquer plataforma pelo OpenSKP, mantendo hierarquia, materiais (com os nomes) e unidade (RN-13, RN-14) | Must | Um `.skp` de porta entra com as instâncias como grupos de peças, na escala certa, com os materiais nomeados e as imagens das texturas; verificado no Linux do titular | 🟢 |
| RF-12 | Um `.skp` que o leitor não abre mostra o motivo e a alternativa, sem deixar nada pela metade na cena (RN-13) | Must | Um arquivo corrompido ou de versão não suportada avisa "Não foi possível ler o SketchUp: <motivo>. Salve numa versão recente ou exporte em glTF/OBJ/FBX", e nenhum objeto é criado | 🟢 |
| RF-13 | Guia do usuário: alinhamento, cálculo, biblioteca, como usar modelos do 3D Warehouse dentro da licença | Should | `docs/usuario/` tem a seção, com o aviso de licença | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | A busca de alinhamento roda a cada movimento do mouse sem travar: até 2.000 vértices em menos de 2 ms (índice ordenado por X e por Y, não varredura O(n²)) | `_reversa_sdd/architecture.md#4` (D-02: varredura a cada `MOUSEMOVE` degrada em layouts grandes) | 🟡 |
| Segurança | A expressão é avaliada por um analisador próprio, sem `eval`, `exec` nem `ast.literal_eval` de código, com um teto de 64 caracteres | Entrada do usuário dentro do Blender | 🟢 |
| Segurança e licença | Nenhum modelo de terceiros sem licença de redistribuição vai no pacote; cada item do pacote tem a licença no manifesto; binários proprietários só entram com a decisão de RN-13 | Termos do 3D Warehouse; SDK da Trimble | 🟢 |
| Compatibilidade | O leitor SKP funciona em Linux, Windows e macOS (wheels cp313 para x86_64 e arm64). Se a wheel de uma plataforma faltar, só a opção SKP fica indisponível, com o motivo, e o registro do plugin não falha | OpenSKP é Python puro; `mapbox_earcut` e `shapely` têm wheels para todas as plataformas no PyPI | 🟢 |
| Design (/impeccable) | Linhas da mira finas e neutras; destaque de trava numa só cor de acento; texto da medida junto do cursor; biblioteca em grade com miniaturas, como o catálogo da 008; estados vazios e de erro escritos | Padrão de design do projeto (008) | 🟡 |
| Internacionalização | Todo texto novo em pt-BR e en-US | Regra do projeto (`CLAUDE.md`) | 🟢 |
| Testes | Núcleos puros testados fora do Blender: alinhamento, expressão, direção e manifesto da biblioteca; fumaça no Blender para o editor e para a biblioteca | Padrão das features 004 a 008 | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Ponto pareado pela mira
  Dado o editor de paredes com uma parede cujo canto está em Y = 2000 mm
  E o modo lápis com o desenho começado do outro lado da planta
  Quando o usuário leva o cursor até Y = 2003 mm e clica
  Então a linha horizontal da mira fica destacada com uma guia até o canto
  E o ponto criado tem Y = 2000 mm exato

Cenário: Sequência de medidas com conta na direção atual
  Dado o modo lápis com o ponto inicial em (0, 0) e o mouse movido para a direita (0°)
  Quando o usuário digita "100" Enter, "285" Enter, "2*8" Enter, "200/2" Enter e "2000" Enter
  Então são criados 5 trechos a 0° com 100, 285, 16, 100 e 2000 mm
  E o último ponto fica em (2501, 0) mm, qualquer que seja a posição do mouse

Cenário: O mouse sem clique não muda a direção
  Dado a sequência anterior terminada em (2501, 0) com a direção 0°
  Quando o usuário move o mouse para cima do último ponto, sem clicar, e digita "300" Enter
  Então o trecho de 300 mm sai a 0° e termina em (2801, 0)

Cenário: Mudar de direção pelas setas e continuar
  Dado a sequência terminada em (2801, 0)
  Quando o usuário aperta a seta para cima e digita "1200" Enter
  Então um trecho de 1200 mm a 90° termina em (2801, 1200)

Cenário: Mudar de direção com um clique
  Dado a direção atual 90° e o último ponto em (2801, 1200)
  Quando o usuário clica à esquerda do último ponto, na trava ortogonal, e digita "500" Enter
  Então o clique cria o trecho até o cursor
  E o trecho de 500 mm sai a 180°, a partir do ponto clicado

Cenário: Expressão inválida
  Dado o modo lápis com a direção definida
  Quando o usuário digita "10/0" e Enter
  Então aparece "Valor Inválido" junto do cursor
  E nenhuma parede é criada

Cenário: Acrescentar uma porta à biblioteca
  Dado uma porta importada em glTF e convertida em folha de giro de 90°
  Quando o usuário escolhe "Acrescentar à biblioteca" em "Portas" com o nome "Porta lisa 80"
  Então o item aparece na categoria com a miniatura
  E, inserido noutro projeto, abre com a barra de abertura até 90°

Cenário: Retexturizar uma parte e usar a chapa no corte
  Dado uma mesa inserida da biblioteca, com o tampo como parte separada
  Quando o usuário troca o material do tampo para "Carvalho" e marca o tampo como peça de produção
  Então só o tampo muda de material
  E o plano de corte lista o tampo com as medidas da chapa

Cenário: Importar um SketchUp no Linux
  Dado o Blender no Linux e um arquivo "porta.skp" com as instâncias "Batente 1" e "Folha 1" e o material "Madeira" com textura
  Quando o usuário importa o arquivo por "Importar modelo"
  Então surgem os grupos "Batente 1" e "Folha 1" na escala do arquivo
  E a folha tem o material "Madeira" com a imagem da textura carregada

Cenário: SketchUp que o leitor não abre
  Dado um arquivo .skp corrompido
  Quando o usuário tenta importá-lo
  Então aparece o motivo e a alternativa (salvar numa versão recente ou exportar em glTF/OBJ/FBX)
  E nenhum objeto é criado

Cenário: Item do 3D Warehouse não é empacotado
  Dado o pacote gerado por build.py
  Quando o manifesto da biblioteca embutida é verificado
  Então nenhum item tem a origem "3D Warehouse"
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 a RF-05 | Must | Pedido central do titular, de baixo risco e ganho diário de precisão (incremento 1) |
| RF-06, RF-08, RF-09, RF-12 | Must | Biblioteca e conversões são a base para usar qualquer modelo trazido |
| RF-07, RF-10, RF-13 | Should | Itens iniciais, retextura e guia completam a experiência |
| RF-11 | Must | Com o OpenSKP, o SketchUp funciona e é testado na máquina do titular |
| RNF de desempenho e segurança | Must | A mira roda a cada movimento; a expressão é entrada do usuário |

## 9. Esclarecimentos

### Sessão 2026-10-08

- **Q:** Tolerância da mira (RN-02): medida na tela ou na planta?
  **R:** Na tela, 8 px, igual em qualquer zoom (opção A).
- **Q:** Mudança de direção na digitação (RN-06): quando a direção atual muda?
  **R:** Mudar pelo mouse fica difícil, porque o mouse sai do lugar com facilidade. A direção pode mudar pelo mouse
  desde que haja um **clique** na nova direção; mover sem clicar mantém a direção travada. Também pelas **setas**.
  Interpretação registrada: o clique cria o ponto como hoje, e a direção do trecho criado vira a atual; as setas do
  teclado trocam a direção sem criar parede.
- **Q:** (pendência) O clique na nova direção também cria o ponto?
  **R:** O clique serve para garantir que mover o mouse enquanto se digitam medidas não leve a parede para onde o
  mouse está: vale a direção travada. Regra confirmada: só o clique ou as setas mudam a direção; o movimento do mouse,
  sozinho, nunca muda.
- **Q:** SketchUp no Windows (RN-13): detectar um importador instalado ou empacotar?
  **R:** Empacotar os `.pyd` e a `SketchUpAPI.dll` dentro do plugin, só para Windows; a licença do SDK da Trimble fica
  para confirmar (opção B).
- **Q:** Escopo: tudo na 009 ou dividir?
  **R:** Tudo na 009, em três incrementos: paredes → biblioteca → SketchUp (opção A).
- **Q:** Itens que vêm com o plugin (RN-09, RF-07): de onde saem?
  **R:** Modelados pelo projeto (porta, janela, cooktop, mesa e 2 de decoração), em geometria simples e limpa, já com
  folha e chapas configuradas (opção A).

### Sessão 2026-10-08 (2), depois da auditoria

- **Q:** Shift desligando o alinhamento da mira (A001): vira regra?
  **R:** Sim: segurar Shift desliga só o alinhamento X/Y; ortogonal, vértice e ímã continuam (opção A).
- **Q:** Como o item da biblioteca entra na cena (A002)?
  **R:** Aparece no cursor 3D, acompanha o mouse e um clique solta; o Esc cancela e remove (opção A).
- **Q:** SketchUp, materiais e texturas (A003): o que conferir?
  **R:** Que os materiais do `.skp` chegam aos objetos, com as imagens das texturas carregadas (opção A). O titular não
  tem Windows: os testes do SketchUp devem rodar aqui mesmo. Decisão: usar o Blender 5.2 de Windows (zip portátil)
  sob o Wine 11, já instalado, em `--background`, carregando o importador empacotado. O `.skp` de exemplo deve ter
  licença que permita uso em teste (não do 3D Warehouse); se nenhum servir, o titular fornece um arquivo próprio.

### Sessão 2026-10-09 (3), novo leitor de SketchUp

- **Q:** Achei um leitor de `.skp` de código aberto (OpenSKP, MIT) que funcionou no Linux do titular. Qual caminho
  seguir para o SketchUp?
  **R:** Só o OpenSKP. A decisão substitui a resposta da sessão 1 (empacotar o pyslapi e a DLL da Trimble) e a da
  sessão 2 (teste pelo Wine). Sem DLL proprietária, sem Wine; o teste roda no Linux com um `.skp` gerado pelo próprio
  OpenSKP (sem problema de licença de modelo).

## 10. Lacunas

- 🟡 Arquivos SketchUp de 2013 a 2020: cerca de 1 em cada 4 não abre no OpenSKP (falha conhecida do projeto). A
  mensagem orienta a salvar numa versão recente.
- 🟡 Pedido 2 do titular ("entrar no 3D Warehouse e baixar modelos"): o download exige conta Trimble, e a licença
  proíbe redistribuí-los na biblioteca do plugin. Esta feature o atende como fluxo do usuário (baixar com a própria
  conta → importar → converter → guardar na biblioteca local), testado com modelos de licença livre e com arquivos que
  o titular fornecer.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-08 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-10-08 | Sessão 1 do `/reversa-clarify`: tolerância, direção, SketchUp, escopo e itens iniciais | reversa |
| 2026-10-08 | Sessão 2 do `/reversa-clarify` (achados da auditoria A001 a A003): Shift, inserção, materiais do SKP e teste pelo Wine | reversa |
| 2026-10-09 | Sessão 3: SketchUp passa a ser lido pelo OpenSKP (MIT) em todas as plataformas; pyslapi, DLL e Wine saem | reversa |
