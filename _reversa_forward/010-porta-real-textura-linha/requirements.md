# Requirements: Porta real na parede, modo "Textura com linha" e hierarquia do SketchUp

> Identificador: `010-porta-real-textura-linha`
> Data: `2026-10-09`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA
> Origem: achados A001 a A008 de `_reversa_forward/009-mira-calculo-skp-biblioteca/audit/cross-check.md`.

## 1. Resumo executivo

Para o projetista que monta o ambiente, a feature tem três partes:
- A porta de parede (Construir › Aberturas) passa a inserir uma **porta real**: batente com guarnição, folha,
  maçaneta e dobradiças. Hoje ela insere uma caixa com o texto "DOOR".
- A viewport ganha o modo **Textura com linha**: sólido com textura e as arestas desenhadas por cima.
- A importação de SketchUp da 009 é corrigida:
  - componentes aninhados mantêm a hierarquia (as ferragens ficam dentro da folha);
  - figuras de escala do SketchUp não entram;
  - reimportar não duplica materiais.

Tudo segue o padrão de interface da 008/009 (/impeccable).

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/domain.md#2.2` (R-04 a R-08) | A abertura se prende ao segmento de parede, herda rotação e espessura, e o cortador booleano tem 3× a espessura; o movimento é preso ao plano da parede e ao comprimento do segmento; ao chegar perto da vizinha ela troca de parede; a porta tem peitoril fixo em 0 | 🟢 |
| `_reversa_sdd/hb_placement/requirements.md#RN-10, RN-20, RN-21` | Portas (`IS_ENTRY_DOOR_BP`) e janelas bloqueiam os dois lados da parede no vão livre, e as bordas que coincidem com elas recebem recuo | 🟢 |
| `caffmob_draw/operators/doors_windows.py` (`_PlaceWallObjectBase`, l. 739-779; `place_door`, `place_double_door`, `place_open_door`) | A porta é uma caixa `GeoNodeCage` (`Dim X` largura, `Dim Y` espessura da parede, `Dim Z` altura), com um símbolo de abertura 2D (`GeoNodeDoorSwing`) e o texto "DOOR". A caixa corta a parede por modificador booleano (`cut_wall`). Medidas padrão: 36" × 84" (914 × 2134 mm) na simples e 72" na dupla (`hb_props.py`, l. 482-484) | 🟢 |
| `caffmob_draw/hb_props.py#update_show_entry_door_and_window_cages` (l. 161-168) | "Mostrar caixas de portas e janelas": ligado, a caixa aparece sólida e na frente; desligado, só em arame | 🟢 |
| `caffmob_draw/inspection/room_door_math.py` | A inspeção (005) mede o giro da porta pela caixa e pelo símbolo de abertura: a caixa continua sendo a referência das medidas | 🟢 |
| `caffmob_draw/ops.py` (l. 51, 93-96) | As configurações recomendadas ligam `overlay.show_wireframes` (limiar 0, opacidade 0,8). Não há botão próprio de modo de vista | 🟢 |
| `_reversa_forward/009-mira-calculo-skp-biblioteca/` (RN-09, RN-13, RN-14; `aggregates/skp_core.py`, `skp_build.py`; `object_library/`) | Biblioteca de objetos (itens embutidos só do projeto; os do 3D Warehouse ficam na biblioteca do usuário); leitor de SketchUp pelo OpenSKP; folha de porta de giro com batentes (003/007) | 🟢 |
| Teste de 2026-10-09 com dois `.skp` do 3D Warehouse do titular, depois removidos do repositório (auditoria A004, A005, A007) | Os dois arquivos abrem. Na porta de 75, a folha (750 × 35 × 2000 mm) chega separada de 6 ferragens que estavam dentro dela, e entra também a figura de escala `2D_Woman_Standing_Sandra`. A porta de 80 (batente com guarnição 1000 × 210 × 2200, folha 840 × 30 × 2120 e maçaneta) não tem material próprio, e cada reimportação cria `Layer_Layer0.00N` | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de interiores | Ver o ambiente como o cliente vai ver | Põe uma porta de 80 × 210 na parede e vê batente, folha, maçaneta e dobradiças, abrindo pela barra de abertura, e não uma caixa escrito "DOOR" |
| Projetista apresentando ao cliente | Ler a forma dos móveis sem perder a cor | Liga "Textura com linha" e vê o acabamento com as arestas marcadas |
| Projetista que traz modelos do SketchUp | Usar a porta baixada sem consertar | Importa uma porta com ferragens: a folha vem com as dobradiças e a maçaneta dentro dela, sem a figura humana de escala |

## 4. Regras de negócio novas ou alteradas

### Porta real na parede

1. **RN-01, a porta é real.** As portas simples, dupla e de vão aberto continuam sendo um vão (`GeoNodeCage`) que
   corta a parede e segue R-04 a R-08. Dentro do vão, a simples e a dupla ganham a porta, com:
   - batente com guarnição nos dois lados da parede, ajustado à espessura dela;
   - folha (uma ou duas) com o lado da dobradiça do símbolo de abertura;
   - maçaneta;
   - duas ou três dobradiças.

   A caixa sólida e o texto "DOOR" deixam de aparecer na vista 3D. O vão aberto continua sem folha, mas ganha batente
   e guarnição. 🟡
   - Origem no legado: `operators/doors_windows.py#_PlaceWallObjectBase`; `_reversa_sdd/domain.md#R-04..R-08`
   - Tipo: alterada
   - Modelo (Esclarecimentos 2026-10-09, Q1): a **porta realista do projeto**, criada a pedido do titular em
     `docs/porta_realista_080x210/`. É um modelo original, gerado por `gerar_porta.py`, que não converte o `.skp` de
     referência, e tem:
     - marco, batentes e guarnições nas duas faces;
     - folha de 40 mm com duas almofadas rebaixadas e frisos;
     - três dobradiças com parafusos;
     - maçanetas de alavanca com rosetas e cilindro;
     - vedações e madeira nogueira com veios.

     O gerador vira paramétrico no plugin: largura, altura e espessura da parede no lugar dos 80 × 210 × 145 mm
     fixos, sem distorcer ferragens.
2. **RN-02, medidas.** A porta acompanha o vão. Mudar a largura ou a altura (W, prompts da porta, editor de
   paredes) refaz a porta. As medidas padrão passam a ser as brasileiras: 80 × 210 cm na simples e 160 × 210 cm na
   dupla (Q4). A folha tem 40 mm, como a porta realista, e o marco acompanha a espessura da parede. 🟢
   - Origem no legado: `hb_props.py` (36" × 84")
   - Tipo: alterada
3. **RN-03, a folha abre.** A folha é uma folha de porta de giro (003/007): abre pela barra de abertura na seção
   Selecionado até o ângulo máximo (90° por padrão), para no batente e esbarra em parede e móvel. O lado e o
   sentido seguem o símbolo de abertura (`SINGLE_DOOR_SWINGS`). 🟢
   - Origem: `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#RN-11`; 007 (batentes)
   - Tipo: alterada (a porta de parede passa a usar a folha da 003)
4. **RN-04, o que fica.** Continuam iguais:
   - o corte da parede;
   - o vão livre e os recuos (`hb_placement` RN-10, RN-20, RN-21);
   - o símbolo 2D de abertura nas plantas;
   - a inspeção de giro (005);
   - "Mostrar caixas de portas e janelas", que passa a mostrar ou esconder só a caixa de referência (em arame).

   Arquivos antigos com portas em caixa continuam abrindo; a porta real entra na primeira edição da porta ou por um
   comando "Atualizar portas". 🟡
   - Tipo: alterada
5. **RN-05, produção.** Batente, guarnição e folha são acessórios por padrão (fora do plano de corte), como os
   agregados (003 RN-13); o projetista pode marcar como peça de produção. 🟡
   - Origem: `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#RN-13`
   - Tipo: nova

### Modo "Textura com linha"

6. **RN-06, modo de vista.** A barra lateral oferece, para a viewport ativa:
   - os modos **Sólido** (como hoje) e **Textura** (sólido com as texturas dos materiais);
   - um interruptor **Linhas**, que liga e desliga as arestas de **todos os objetos** da cena, finas e escuras,
     legíveis sobre madeira clara e escura.

   "Textura com linha" é Textura com Linhas ligado. O modo e o interruptor ficam salvos no arquivo. 🟢
   (Esclarecimentos 2026-10-09, Q2)
   - Origem no legado: `ops.py` (configurações recomendadas com `show_wireframes`)
   - Tipo: nova
10. **RN-10, janela real.** A janela de parede (`place_window`), hoje uma caixa com o texto "WINDOW", ganha uma janela
    realista do projeto pelo mesmo caminho da porta, com:
    - marco e guarnições;
    - duas folhas de correr de alumínio com vidro;
    - trilhos;
    - puxadores;
    - peitoril.

    As folhas abrem pela barra de abertura e param nos batentes (007). O modelo é original, gerado por script como a
    porta. A prévia e o acabamento seguem a `blender-product-polish` (`~/.agent/skills/product-polish`: iluminação de
    estúdio e material polido). 🟡 (Esclarecimentos 2026-10-09, Q3)
    - Origem no legado: `operators/doors_windows.py#place_window`
    - Tipo: alterada

### Hierarquia do SketchUp (correção da 009)

7. **RN-07, componentes aninhados.** Um componente ou grupo do SketchUp dentro de outro vira um grupo de peças
   dentro do grupo do pai, com a mesma árvore. As peças soltas de cada nível ficam no grupo daquele nível.
   Converter a folha em folha de porta leva as dobradiças e a maçaneta junto. 🟢
   - Origem: `_reversa_forward/009-mira-calculo-skp-biblioteca/requirements.md#RN-14`; auditoria A004
   - Tipo: alterada
8. **RN-08, figuras de escala.** Instâncias que são figuras de escala do SketchUp não entram na importação. Elas são
   reconhecidas pelo nome ou pela definição (por exemplo, `2D_Woman_*`, `2D_Man_*` ou as figuras padrão do
   SketchUp, como Sandra, Chris, Susan, Lily, Derrick e Laura), e o relatório da importação diz quantas foram
   puladas. 🟡
   - Origem: auditoria A005
   - Tipo: nova
9. **RN-09, materiais sem duplicar.** Um material do SketchUp que já existe no arquivo com o mesmo nome e a mesma cor
   (ou a mesma imagem) é reaproveitado, sem sufixo `.001`. Um material só de camada (`Layer_*`) recebe o nome da
   camada sem o prefixo. 🟢
   - Origem: auditoria A007; `aggregates/skp_build.py#_material`
   - Tipo: alterada

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | A porta simples insere a porta realista do projeto no vão (marco, batentes, guarnições, folha almofadada, maçanetas e dobradiças), sem a caixa sólida nem o texto "DOOR" na vista 3D (RN-01) | Must | Uma porta de 80 × 210 numa parede de 150 mm mostra marco e guarnições nos dois lados, folha de 40 mm com duas almofadas, maçanetas e 3 dobradiças; nenhum objeto visível chamado "DOOR" | 🟢 |
| RF-02 | A dupla tem duas folhas, e o vão aberto só batente e guarnição (RN-01) | Must | Dupla de 160: duas folhas de cerca de 80, maçanetas no meio; vão aberto: sem folha | 🟡 |
| RF-03 | A porta acompanha largura, altura e espessura da parede, com as medidas padrão brasileiras (RN-02) | Must | Mudar a largura para 90 refaz a folha com 90 menos as folgas, sem distorcer maçaneta e dobradiças; a porta nova sai com 80 × 210 | 🟡 |
| RF-04 | A folha abre pela barra e respeita os batentes e a colisão (RN-03) | Must | 100% da barra = 90° com o lado de giro do símbolo; com um móvel a 30 cm, para no contato | 🟢 |
| RF-05 | Corte, vão livre, recuos, símbolo 2D e inspeção iguais aos de hoje (RN-04) | Must | As fumaças da 002, 004 e 005 continuam verdes; o furo na parede tem as mesmas medidas | 🟢 |
| RF-06 | "Atualizar portas" troca as portas em caixa de um arquivo antigo pela porta real (RN-04) | Should | Um `.blend` com 3 portas antigas fica com 3 portas reais, nas mesmas posições e medidas | 🟡 |
| RF-07 | Peças da porta fora do corte por padrão, com a opção de peça de produção (RN-05) | Should | O plano de corte não muda ao inserir uma porta; marcar a folha como peça de produção a põe na lista | 🟡 |
| RF-08 | Modos de vista Sólido e Textura, com o interruptor Linhas, na barra lateral (RN-06) | Must | Textura com Linhas ligado mostra a madeira com as arestas de todos os objetos; desligar Linhas tira as arestas; voltar a Sólido restaura a vista; modo e interruptor ficam salvos no arquivo | 🟢 |
| RF-09 | SketchUp com hierarquia: componentes aninhados como grupos dentro do pai (RN-07) | Must | Um `.skp` de teste gerado pelo projeto (porta 75 × 200 com a folha contendo 3 dobradiças e a maçaneta) entra com o grupo da folha contendo as 4 ferragens; converter a folha em folha de porta move as ferragens junto | 🟢 |
| RF-10 | Figuras de escala do SketchUp são puladas (RN-08) | Should | O mesmo `.skp` de teste, com uma instância `2D_Woman_Standing_Teste`, entra sem ela, e o relatório diz "1 figura de escala ignorada" | 🟡 |
| RF-11 | Reimportar não duplica materiais; o material de camada fica sem o prefixo `Layer_` (RN-09) | Should | Um `.skp` de teste com material `Layer_Layer0`, importado duas vezes, deixa um material só, chamado `Layer0` | 🟢 |
| RF-12 | Guia do usuário: porta e janela reais, Atualizar portas, modos de vista e o que muda na importação de SketchUp | Should | `docs/usuario/` atualizado | 🟢 |
| RF-13 | A janela de parede insere a janela realista: marco, guarnições, 2 folhas de correr com vidro, trilhos, puxadores e peitoril, refeita pelas medidas do vão (RN-10) | Must | Uma janela de 120 × 100 mostra marco, 2 folhas de vidro e peitoril; as folhas correm até os batentes; nenhum texto "WINDOW" visível | 🟡 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Inserir e mover uma porta continua fluido: a geometria da porta tem até cerca de 3 mil faces, e o arraste no modo de inserção não refaz a porta a cada movimento (só ao soltar ou ao mudar a medida) | O modal de aberturas já recalcula distâncias a cada `MOUSEMOVE` (`_reversa_sdd/architecture.md#4`, D-02) | 🟡 |
| Licença | Nenhum modelo do 3D Warehouse vai no pacote nem no repositório. Os exemplos do titular já foram removidos de `docs/` (Q5). Os testes do SketchUp usam `.skp` gerados pelo projeto com o OpenSKP, e a porta e a janela são modelos originais | 009 RN-09; termos do 3D Warehouse | 🟢 |
| Compatibilidade | Arquivos salvos com portas em caixa abrem sem erro e mantêm o furo na parede | RN-04 | 🟢 |
| Design (/impeccable) | Modo de vista num controle segmentado (Sólido · Textura), com o interruptor Linhas ao lado e o estado escrito; porta e janela com as proporções da porta realista (folha de 40 mm, maçaneta a 1.020 mm do piso, folga de 8 mm no piso) | Padrão da 008/009; `docs/porta_realista_080x210/LEIA-ME.md` | 🟢 |
| Internacionalização | Textos novos em pt-BR e en-US | `CLAUDE.md` | 🟢 |
| Testes | Núcleos puros (medidas da porta, árvore do SketchUp, filtro de figuras, reaproveitamento de material) testados fora do Blender; fumaças da porta, do modo de vista e do SketchUp com fixture aninhada | Padrão 004 a 009 | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Porta real na parede
  Dado um cômodo com paredes de 150 mm
  Quando o projetista insere uma porta simples com as medidas padrão
  Então surgem marco e guarnições nos dois lados, uma folha almofadada de 40 mm, maçanetas e 3 dobradiças num vão de 800 × 2100 mm
  E a parede tem o furo de 800 × 2100 mm
  E nenhuma caixa sólida nem texto "DOOR" aparece na vista 3D

Cenário: A folha abre e para no móvel
  Dado a porta inserida e um armário a 300 mm da dobradiça, no lado de abertura
  Quando o projetista leva a barra de abertura a 100%
  Então a folha gira até encostar no armário e o painel avisa o contato

Cenário: Janela real na parede
  Dado um cômodo com paredes de 150 mm
  Quando o projetista insere uma janela de 120 × 100
  Então surgem marco, guarnições, 2 folhas de correr com vidro, trilhos, puxadores e peitoril
  E a folha corre até o batente pela barra de abertura
  E nenhum texto "WINDOW" aparece na vista 3D

Cenário: Mudar a largura da porta
  Dado a porta de 800 mm
  Quando o projetista muda a largura para 900 mm
  Então a folha e o batente são refeitos para 900 mm e a maçaneta mantém o tamanho

Cenário: Arquivo antigo
  Dado um arquivo salvo com 3 portas em caixa
  Quando o projetista usa "Atualizar portas"
  Então as 3 viram portas reais nas mesmas posições e medidas, com o furo na parede igual

Cenário: Textura com linha
  Dado uma cozinha com móveis de madeira texturizada
  Quando o projetista escolhe "Textura com linha"
  Então a viewport mostra as texturas com as arestas desenhadas
  E ao escolher "Sólido" a vista volta ao normal

Cenário: Porta do SketchUp com ferragens
  Dado um .skp de teste gerado pelo projeto (porta 75 × 200 com ferragens dentro da folha e uma figura de escala)
  Quando o projetista o importa
  Então surge o grupo da folha com as 4 ferragens dentro dele
  E a figura de escala não é importada e o relatório diz que ela foi ignorada

Cenário: Reimportar sem duplicar material
  Dado um .skp de teste com o material de camada "Layer_Layer0" já importado
  Quando o projetista o importa de novo
  Então o arquivo continua com um material só, chamado "Layer0"

Cenário: Porta embutida não pode vir do 3D Warehouse
  Dado o pacote gerado por build.py
  Quando os modelos de porta do pacote são verificados
  Então nenhum tem origem "3D Warehouse" e nenhum .skp do 3D Warehouse está no repositório
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 a RF-05, RF-13 | Must | Pedido central: porta e janela têm de parecer reais, sem perder o corte nem as regras de aberturas |
| RF-08 | Must | Pedido explícito do titular |
| RF-09 | Must | Defeito da 009 que impede usar portas do SketchUp com ferragens |
| RF-06, RF-07, RF-10, RF-11, RF-12 | Should | Compatibilidade, produção e acabamento da importação |
| RNF de desempenho e de licença | Must | A inserção já é sensível ao custo por movimento; a licença não admite exceção |

## 9. Esclarecimentos

### Sessão 2026-10-09

- **Q:** De onde vem a porta real da parede (RN-01)?
  **R:** Da porta que o titular pediu ao Codex: `docs/porta_realista_080x210/`, feita com a `blender-product-polish`.
  É um modelo original, gerado por `gerar_porta.py`, com OBJ/MTL, texturas de nogueira e uma cena de apresentação.
  O gerador passa a ser paramétrico no plugin.
- **Q:** Onde aparecem as linhas do "Textura com linha" (RN-06)?
  **R:** Em todos os objetos (opção A), com opção para ativar e desativar: o interruptor Linhas.
- **Q:** A janela de parede entra nesta feature?
  **R:** Sim (opção A): gerar a janela usando a `blender-product-polish`, pelo mesmo caminho da porta (RN-10).
- **Q:** Medidas padrão da porta simples (RN-02)?
  **R:** 80 × 210 cm, e a dupla 160 × 210 (opção A).
- **Q:** O que fazer com os `.skp` do 3D Warehouse em `docs/`?
  **R:** Remover e gerar equivalentes para o Blender. Em 2026-10-09 os dois arquivos já não estavam em `docs/` (nunca
  entraram no git). Os equivalentes são a porta realista (80 × 210, já gerada), a variante 75 × 200 pelo gerador
  paramétrico e os `.skp` de teste gerados pelo projeto com o OpenSKP para a hierarquia, as figuras de escala e os
  materiais (RF-09 a RF-11).

## 10. Lacunas

- 🟡 A `blender-product-polish` roda pelo addon Blender MCP (porta 9876) e trabalha com GLB. Para a janela, o
  acabamento e a iluminação de estúdio dela entram na prévia e na cena de apresentação. A geometria vem de um script
  original, como a porta do Codex. Sem o Blender MCP aberto, os mesmos ajustes (presets `studio`, rugosidade e
  clearcoat) são aplicados pelo script em segundo plano.
- 🟡 A porta realista tem 157 objetos e texturas de 2 MB cada. O plano deve definir como juntar as peças (por
  exemplo, marco, folha e ferragens) e compartilhar as texturas entre portas, para o arquivo não pesar com várias
  portas.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-09 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-10-09 | Sessão 1 do `/reversa-clarify`: porta realista do Codex, Linhas em todos com interruptor, janela real, 80 × 210, `.skp` removidos e fixtures próprias | reversa |
