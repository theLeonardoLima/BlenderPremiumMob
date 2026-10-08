# Requirements: Janela importada (OBJ) com folhas de correr, agregados por grupo e colisão coerente

> Identificador: `007-janela-obj-folhas-colisao`
> Data: `2026-10-08`
> Pasta da extração reversa: `_reversa_sdd/`
> Origem: pedido do titular ("adicione o OBJ deste zip no Blender e torne o plugin capaz de manipular um OBJ assim:
> criar agregados facilmente transformando as peças em agregados e manipular a abertura da janela com colisão, a folha
> batendo na esquadria e não abrindo mais que isso, e encostando na outra folha e não fechando mais que isso").
> Insumo: `inputs/janela_preta_1400mm.obj` (+ `.mtl`, `LEIA-ME.txt`).
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O projetista recebe janelas e portas prontas em OBJ (aqui, uma janela preta de correr de duas folhas, 1400 × 850 ×
80 mm, com 46 peças nomeadas: 15 por folha e 16 na esquadria). Hoje o plugin importa esse arquivo 1000 vezes maior e deitado. Além disso, uma folha de
porta só pode ser **uma** malha, mas cada folha deste arquivo tem cerca de 15 peças. E a folha não colide com a
própria esquadria nem com a outra folha. Esta feature faz o OBJ entrar na escala e na posição certas, transforma as
peças em agregados em poucos cliques (uma folha = o grupo das peças dela) e faz a abertura parar na esquadria ao abrir
e na outra folha ao fechar.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/domain.md#1.1 Entidades do Ambiente 3D` | Abertura (porta/janela) é vão na parede; janela tem peitoril configurável | 🟢 |
| `_reversa_sdd/domain.md#2.2 Regras de Snapping e Movimentação de Aberturas` (R-04 a R-08) | Abertura presa ao segmento de parede, com movimento travado no plano da parede | 🟢 |
| `_reversa_sdd/architecture.md#1. Visão Geral do Sistema` | Operadores modais sobre a cena; geometria por `bmesh` | 🟢 |
| `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#4` (RN-07, RN-11, RN-11a, RN-12) | Agregado preso ao pai; folha de giro ou de correr com barra de abertura de 0 a 100%; ao abrir, para no primeiro contato; desconverter devolve a malha | 🟢 |
| `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#5` (RF-11) | "Importar uma porta em OBJ coloca a malha em escala correta" | 🟢 |
| `caffmob_draw/aggregates/ops_import.py` | Chama `wm.obj_import` com os padrões do Blender: sem escala de unidade e com a suposição "Y para cima" | 🟢 |
| `caffmob_draw/aggregates/leaf.py` (`make_leaf`, `leaf_box`, `rebuild_pivot`) | A folha é **um** objeto; a caixa da folha e o pivô saem só dele | 🟢 |
| `caffmob_draw/aggregates/collision.py` (`_excluded`) | O teste de contato ignora o pai da folha, o módulo do pai e **todos os filhos dele**: a esquadria (pai) e a outra folha (filha do mesmo pai) nunca são alvo | 🟢 |
| `caffmob_draw/aggregates/leaf.py` (`update_open`) | Só a abertura testa contato; "fechar continua livre" (003 RN-11a) | 🟢 |
| Medição no Blender 5.2 (importando `inputs/janela_preta_1400mm.obj` pelo plugin) | Entram 46 malhas e 4 materiais (`Aluminio_Preto`, `Cavidade_Preta`, `Ferragem_Preta`, `Vidro_Transparente`). Caixa de 1400 × 850 × 80 **metros**, girada 90° em X. Fechadas, as folhas se sobrepõem 32 mm no centro e ficam em trilhos com profundidades diferentes | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de interiores | Usar uma esquadria pronta de fornecedor | Importa o OBJ da janela de correr e ela aparece com 1400 × 850 × 80 mm, em pé, com os materiais preto e vidro |
| Projetista de interiores | Transformar o modelo em peça "viva" | Com dois cliques, as peças `Folha_Esquerda_*` viram a folha esquerda, as `Folha_Direita_*` a direita, e o batente e as guias formam a esquadria |
| Projetista de interiores | Apresentar a janela aberta sem erro visual | Arrasta a barra da folha esquerda até 100%: ela corre e para ao bater na esquadria; volta a 0 e para encostada na outra folha |

## 4. Regras de negócio novas ou alteradas

**Glossário desta feature.**
- *Esquadria*: o conjunto fixo da janela: marco (`Marco_Externo_*`), bordas (`Borda_*`), trilhos (`Trilho_Inferior_*`)
  e guias (`Guia_Superior_*`).
- *Folha*: o conjunto móvel de peças: perfis, baguetes, vidro e puxador.
- *Grupo de peças*: as malhas importadas que passam a se mover juntas como uma coisa só, sem virar uma malha única.
- *Batente de abertura* e *batente de fechamento*: os pontos onde a folha para em cada sentido.

**A. Importar**

1. **RN-01:** Na importação, o projetista informa a **unidade do arquivo** (mm, cm, m ou polegada) e o **eixo vertical**
   (Z ou Y). O padrão é sugerido pelo tamanho do modelo: um modelo com mais de 50 unidades numa medida sugere mm. O
   objeto entra em pé e na escala certa. 🟢 (clarify 2026-10-08, Q5)
   - Origem no legado: `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#5` (RF-11)
   - Tipo: alterada (a 003 promete escala correta, e o código não entrega)
2. **RN-02:** Os nomes das peças e os materiais do arquivo são mantidos. 🟢 (medido: 46 nomes e 4 materiais)
   - Tipo: nova
3. **RN-03:** A janela importada entra **solta** na cena. Um botão **"Instalar na parede"** a leva para uma parede
   escolhida, corta o vão do tamanho da esquadria e a deixa presa à parede como as janelas de ambiente: herda a
   rotação e a espessura, desliza só no plano da parede e não sai do segmento. "Desinstalar" devolve a janela solta e
   fecha o vão. 🟢 (clarify 2026-10-08, Q1)
   - Origem no legado: `_reversa_sdd/domain.md#2.2 Regras de Snapping e Movimentação de Aberturas` (R-04 a R-06)
   - Tipo: nova

**B. Agrupar e converter**

4. **RN-04:** O projetista pode transformar **várias peças selecionadas** num **grupo de peças** que se move junto:
   uma folha ou a esquadria. As peças continuam objetos separados, presos a um objeto de grupo que é quem se move, e
   mantêm nome, material e o vidro à parte. Desfazer o grupo devolve as peças soltas na mesma posição. 🟢 (clarify
   2026-10-08, Q4)
   - Origem no legado: `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#4` (RN-07, RN-12)
   - Tipo: alterada (na 003, folha e agregado são de uma malha só)
5. **RN-05:** O plugin **sugere os grupos pelo nome das peças**, usando o prefixo comum (`Folha_Esquerda_*`,
   `Folha_Direita_*`; o que não é folha = esquadria). O projetista confirma ou ajusta a sugestão antes de converter.
   🟡
   - Tipo: nova
6. **RN-06:** Uma folha formada por grupo de peças aceita os mesmos movimentos da 003 (giro ou correr, com sentido,
   ângulo ou curso e barra de 0 a 100%). A caixa da folha, o eixo e o trilho saem do **grupo inteiro**. 🟢 (003 RN-11)
   - Origem no legado: `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#4` (RN-11)
   - Tipo: alterada
7. **RN-07:** Na folha de correr, o curso padrão é a **distância livre até a esquadria** no sentido de abrir. O
   projetista pode diminuir esse valor, mas não aumentar. 🟡
   - Tipo: nova
7a. **RN-07a:** Cada folha abre, por padrão, **para o próprio lado**: a esquerda corre para a esquerda e a direita
    para a direita. O projetista pode **inverter o sentido** de cada folha. 🟢 (clarify 2026-10-08, Q3)
    - Tipo: nova

**C. Colisão coerente**

8. **RN-08:** A esquadria da própria janela **conta** como obstáculo para as folhas dela: ao abrir, a folha para ao
   encostar na esquadria e o valor da barra fica preso no ponto do contato. Isso muda a exclusão de hoje (pai e filhos
   do pai nunca são alvo). 🟢 (pedido do titular)
   - Origem no legado: `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#4` (RN-11a)
   - Tipo: alterada
9. **RN-09:** Ao fechar, a folha para no **primeiro** destes três limites que alcançar:
   - (a) a **posição fechada do arquivo**: nunca volta além dela (ex.: montantes centrais sobrepostos 32 mm);
   - (b) a **posição atual da outra folha**: encosta no montante dela, e o limite acompanha se a outra também estiver
     aberta;
   - (c) a **esquadria** do lado oposto ao de abrir.

   Assim abrir e fechar têm batente nos dois sentidos. As folhas correm em trilhos diferentes, então (b) é um batente
   pela sobreposição dos montantes, e não um toque em 3D. 🟢 (clarify 2026-10-08, Q2)
   - Origem no legado: `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#4` (RN-11a: "fechar
     continua livre")
   - Tipo: alterada
10. **RN-10:** Ao parar num batente, o painel avisa em texto "Folha bateu em <peça>" (abrir) ou "Folha encostou em
    <folha>" (fechar), e a peça do contato é destacada na vista. 🟢 (003 RF-17)
    - Tipo: alterada
11. **RN-11:** As folhas e a esquadria continuam sendo **acessório**: ficam fora do plano de corte, a menos que o
    projetista marque "Peça de produção". 🟢 (003 RN-13)
    - Tipo: preservada

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Importar OBJ com unidade e eixo vertical escolhidos, com sugestão automática (RN-01) | Must | `janela_preta_1400mm.obj` com "mm" e "Z" entra com 1400 × 850 × 80 mm, em pé (altura no Z do mundo) | 🟡 |
| RF-02 | Manter nomes e materiais das peças importadas (RN-02) | Must | Depois de importar há 46 objetos com os nomes do arquivo e os 4 materiais | 🟢 |
| RF-03 | Janela entra solta; "Instalar na parede" corta o vão e prende a janela à parede; "Desinstalar" desfaz (RN-03) | Should | Instalar a janela numa parede de 150 mm abre um vão de 1400 × 850 mm; arrastá-la a mantém no plano da parede; Desinstalar fecha o vão | 🟢 |
| RF-04 | Criar grupo de peças a partir da seleção, como folha ou como esquadria, e desfazer o grupo (RN-04) | Must | Selecionar as 15 peças `Folha_Esquerda_*` e criar a folha: ao arrastar a barra, as 15 se movem juntas; "Desfazer grupo" as devolve soltas no lugar | 🟡 |
| RF-05 | Sugerir os grupos pelo prefixo dos nomes, com confirmação (RN-05) | Should | Com as 46 peças importadas, a sugestão traz 3 grupos: Folha_Esquerda (15), Folha_Direita (15) e esquadria (16) | 🟡 |
| RF-06 | Folha de grupo com giro ou correr, eixo/trilho calculado pela caixa do grupo (RN-06) | Must | Folha esquerda de correr para +X: 50% desliza metade do curso; 0% volta exatamente à posição importada | 🟢 |
| RF-07 | Curso padrão da folha de correr = distância livre até a esquadria; não aceita valor maior (RN-07) | Should | Curso sugerido ≈ distância até a esquadria no sentido de abrir; digitar mais que isso fica no máximo | 🟡 |
| RF-07a | Sentido padrão "para o próprio lado" e opção de inverter por folha (RN-07a) | Must | A folha esquerda abre para −X por padrão; "Inverter sentido" a faz abrir para +X | 🟢 |
| RF-08 | Ao abrir, a folha para ao encostar na esquadria da própria janela (RN-08) | Must | Barra da folha esquerda em 100% com curso maior que o livre: para no contato com o batente direito e o painel cita a peça | 🟢 |
| RF-09 | Ao fechar, a folha para no primeiro limite entre: posição fechada do arquivo, montante da outra folha e esquadria (RN-09) | Must | Com a outra folha fechada, a barra em 0 devolve a folha à posição do arquivo; com a outra folha aberta no caminho, a folha para encostada no montante dela e o painel cita a folha | 🟢 |
| RF-10 | Aviso em texto e destaque da peça de contato (RN-10) | Must | Ao parar, o painel mostra o nome da peça e ela aparece destacada na vista | 🟢 |
| RF-11 | Folhas e esquadria fora do plano de corte por padrão (RN-11) | Must | Gerar o plano de corte com a janela na cena não lista vidro nem perfis | 🟢 |
| RF-12 | Textos novos em pt-BR e en-US | Must | Com a interface em inglês, as opções de importação e de grupo aparecem em inglês | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Arrastar a barra de abertura de uma folha de 15 peças responde em até 100 ms por passo numa cena com até 200 objetos | A varredura de contato da 003 usa caixa + BVH em cache; o grupo não pode multiplicar o custo por peça | 🟡 |
| Confiabilidade | Abrir e fechar nunca alteram a malha das peças; 0% devolve a pose importada exata (diferença < 0,1 mm) | 003 RN-11 ("abrir nunca altera a malha") | 🟢 |
| Confiabilidade | Converter, agrupar e desfazer o grupo geram um passo de desfazer cada | Regra do projeto: operadores com `UNDO` (`CLAUDE.md`) | 🟢 |
| Compatibilidade | Funciona no alvo do projeto (Blender 5.2) com OBJ; FBX e glTF seguem o mesmo fluxo de grupo | `CLAUDE.md`; 003 RF-11 | 🟡 |
| Usabilidade | Da importação à janela abrindo com colisão em no máximo 5 ações do projetista (importar, aceitar sugestão de grupos, converter folhas, mover a barra) | Pedido do titular: "permitir facilmente" | 🟡 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Importar a janela em escala e em pé
  Dado o arquivo janela_preta_1400mm.obj em milímetros e com Z vertical
  Quando o projetista importa o modelo escolhendo "mm" e "Z"
  Então a janela aparece com 1400 × 850 × 80 mm e com a altura no eixo vertical
  E as 46 peças mantêm os nomes e os materiais do arquivo

Cenário: Sugestão automática de unidade
  Dado um OBJ cuja maior medida passa de 50 unidades
  Quando o projetista abre a importação
  Então a unidade sugerida é "mm"

Cenário: Sugerir e confirmar os grupos
  Dado as 46 peças da janela importadas
  Quando o projetista pede a sugestão de grupos
  Então aparecem "Folha_Esquerda" com 15 peças, "Folha_Direita" com 15 e a esquadria com 16
  Quando ele confirma
  Então cada grupo passa a se mover como uma coisa só

Cenário: Folha de correr bate na esquadria
  Dado a folha esquerda convertida em folha de correr, com o sentido invertido para a direita
  Quando o projetista leva a barra a 100%
  Então a folha desliza e para encostada no batente direito
  E o painel mostra "Folha bateu em" e o nome da peça
  E a peça de contato aparece destacada

Cenário: Curso não passa da esquadria
  Dado a folha esquerda de correr
  Quando o projetista digita um curso maior que a distância livre até a esquadria
  Então o curso fica no máximo permitido

Cenário: Folha volta à posição fechada do arquivo
  Dado a folha esquerda aberta a 60% e a folha direita fechada
  Quando o projetista leva a barra a 0%
  Então a folha volta exatamente à posição do arquivo e não passa dela

Cenário: Folha encosta na outra folha ao fechar
  Dado as duas folhas com o sentido para o centro e a folha direita aberta a 40%
  E a folha esquerda aberta a 80%
  Quando o projetista leva a barra da folha esquerda a 0%
  Então a folha esquerda para encostada no montante da folha direita
  E o painel mostra "Folha encostou em" e o nome da folha direita

Cenário: Instalar na parede
  Dado a janela importada solta e uma parede de 150 mm
  Quando o projetista usa "Instalar na parede" e escolhe a parede
  Então a parede ganha um vão de 1400 × 850 mm
  E a janela só desliza no plano da parede, sem sair do segmento
  Quando ele usa "Desinstalar"
  Então a janela volta solta e o vão fecha

Cenário: Desfazer o grupo
  Dado a folha direita formada por 15 peças
  Quando o projetista desfaz o grupo
  Então as 15 peças voltam soltas para a posição importada, com nome e material intactos

Cenário: Fora do plano de corte
  Dado a janela importada com folhas e esquadria convertidas
  Quando o projetista gera o plano de corte
  Então nenhuma peça da janela aparece na lista

Cenário: Seleção sem malha
  Dado a seleção sem nenhum objeto de malha
  Quando o projetista tenta criar um grupo
  Então o botão fica indisponível com o aviso "Selecione as peças do grupo"

Cenário: Interface em inglês
  Dado a interface em en-US
  Quando o projetista abre a importação e a criação de grupos
  Então as opções aparecem em inglês
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01, RF-02 | Must | Sem escala e posição corretas nada mais funciona; corrige o RF-11 da 003 |
| RF-04, RF-06 | Must | Núcleo do pedido: folha feita de várias peças |
| RF-08, RF-09, RF-10 | Must | Pedido do titular: colisão coerente nos dois sentidos |
| RF-11, RF-12 | Must | Regras do projeto (produção e tradução) |
| RF-05, RF-07 | Should | "Facilmente": reduzem cliques, mas dá para fazer à mão |
| RF-03 | Should | Depende da resposta de RN-03 |
| Janela paramétrica (redimensionar o OBJ mantendo perfis) | Won't (nesta feature) | Fora do pedido; o OBJ é um modelo fixo |

## 9. Esclarecimentos

### Sessão 2026-10-08

- **Q:** A janela importada fica solta ou entra numa parede? **R:** (c) Os dois: importa solta e há um botão
  "Instalar na parede" que corta o vão. → RN-03, RF-03
- **Q:** Ao fechar, até onde a folha volta? **R:** (a) + (b) + (c): a posição fechada do arquivo, a posição atual da
  outra folha e a esquadria do lado oposto valem juntas, e a folha para no primeiro limite. → RN-09, RF-09
- **Q:** Para que lado cada folha abre? **R:** (b) Para o próprio lado, com opção de ajustar o sentido de cada folha.
  → RN-07a, RF-07a
- **Q:** Como as peças de uma folha viram "uma coisa só"? **R:** (a) Ficam objetos separados, presos a um objeto de
  grupo que se move. → RN-04
- **Q:** A sugestão automática de unidade pelo tamanho (mais de 50 unidades = mm) serve? **R:** (a) Sim. → RN-01

## 10. Lacunas

- 🔴 Risco físico de RN-07a no arquivo de teste: fechadas, as folhas já estão quase encostadas na esquadria do próprio
  lado: a folha esquerda começa em X = −676 mm e a face interna do marco esquerdo está em −678 mm (o mesmo vale,
  espelhado, para a direita). Com "abrir para o próprio lado" e a colisão com a esquadria (RN-08), cada folha abre
  **2 mm**. Para esta janela, abrir de verdade pede **inverter o
  sentido** (RN-07a). Confirmar com o titular se o padrão "para o próprio lado" continua valendo ou se, quando o curso
  livre for menor que 10% da largura da folha, o sentido padrão passa para o centro.
- 🟡 Inferências sem marcador:
  - grupos por prefixo de nome (RN-05);
  - curso padrão = distância livre (RN-07);
  - meta de 100 ms por passo (§6).
- 🟡 Achado: o RF-11 da 003 (escala correta) não vale para OBJ em mm. Esta feature corrige isso para todo OBJ, não só
  para a janela.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-08 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-10-08 | Sessão de esclarecimentos: 5 respostas integradas (RN-01, RN-03, RN-04, RN-07a, RN-09) | reversa-clarify |
