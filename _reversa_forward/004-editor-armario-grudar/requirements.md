# Requirements: Editor de armário, grudar em superfície plana e colisão

> Identificador: `004-editor-armario-grudar`
> Data: `2026-10-07`
> Pasta da extração reversa: `_reversa_sdd/`
> Origem: pedido do titular ("editor de armário e capacidade de grudar itens em paredes, painéis ou outra superfície
> plana") + elicitações `inputs/elicitacao-editor-de-armario.md` e `inputs/elicitacao-elemento-parede-colisao.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

> **Nota de evidência.** As duas elicitações foram escritas a partir dos **nomes** de dois vídeos de referência, sem
> ver os quadros. Só o tema ("editor de armário", "elemento grudado na parede", "colisão") é fato. Todo comportamento
> herdado delas entra aqui como 🟡 e precisa do aval do titular. O que é 🟢 vem do código e das features 001 a 003.

## 1. Resumo executivo

Hoje o projetista personaliza um módulo pelo painel lateral da 003, mas não tem uma tela própria para editar o armário
inteiro com visão de conjunto, rascunho e confirmação. Um móvel posto na parede vira filho dela a uma distância fixa e
não acompanha a face quando a espessura muda; não há como prender um item a um painel ou a outra face plana e mantê-lo
ali. E não há aviso quando dois móveis ocupam o mesmo espaço ou um entra na parede. Esta feature entrega ao projetista
três coisas: (A) **editor de armário** numa tela própria; (B) **grudar** qualquer item numa superfície plana, com vínculo
que sobrevive a mudanças do hospedeiro; (C) **colisão**: detectar, explicar e ajudar a resolver sobreposições.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#5` (RF-01..RF-10) | Painel "Personalizar módulo" das quatro bibliotecas (frameless, face frame, closets, `btm`) com adaptadores por biblioteca e "Salvar como módulo" | 🟢 |
| `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#4` (RN-07..RN-09) | Agregado preso à face do pai, limitado ao **contorno** do pai, com afastamento/afundamento | 🟢 |
| `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#5` (RF-28) | Plano de inserção: face escolhida vale para as próximas inserções, sem vínculo persistente com o item | 🟢 |
| `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#5` (RF-01..RF-10, RF-44) | Editor de paredes em janela 2D própria com rascunho, OK/Cancelar, ímã de 15 px e aviso de itens presos a parede encurtada | 🟢 |
| `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#2` | Referência de vídeo cita botões "Colisão", "Junções" e "Auto Rebaixar" no inspetor | 🟡 |
| `_reversa_sdd/domain.md#2.2 Regras de Snapping e Movimentação de Aberturas` (R-04..R-06) | Abertura presa ao segmento: herda rotação e espessura, move só no plano da parede, com limite no comprimento | 🟢 |
| `_reversa_sdd/hb_placement/requirements.md#Regras de Negócio` (RN-09..RN-24) | Vão livre na parede com obstáculos, filtro vertical e encosto módulo-a-módulo; módulos de parede não são alvo de encosto | 🟢 |
| `caffmob_draw/product_libraries/frameless/operators/ops_placement.py` (linhas 421-434, 1520-1544) | Módulo posto na parede vira filho dela com Y local = 0 (face da frente) ou = espessura (face de trás), valor fixo | 🟢 |
| `caffmob_draw/walls2d/apply.py` (linhas 131-154) | Ao aplicar o editor de paredes, filhos mantêm a posição local; aberturas recebem a nova espessura, módulos não | 🟢 |
| `caffmob_draw/inspection/interference.py` | Interferência existe só para o **envelope de abertura das frentes**, com tolerância de 1 mm para encostar não contar como bater | 🟢 |
| `caffmob_draw/data/properties.py` (`BTM_PG_InsertionPlane.collision_override`, `parent_plane`) | Campos "Colisão" (Herdar/Ativa/Desativada) e "Plano Pai" declarados e sem uso pela colisão | 🟢 |
| `_reversa_sdd/architecture.md#4` (D-02) | Cálculo contra todas as paredes a cada movimento do mouse degrada cenas grandes | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de interiores | Montar um armário com visão do conjunto | Abre o editor de um roupeiro, muda a largura de 2.400 para 2.000 mm, troca um vão de portas por gavetas, vê os avisos e confirma num passo só |
| Projetista de interiores | Prender itens a superfícies e não perdê-los | Gruda um nicho na lateral de um painel e um aéreo na parede; muda a espessura da parede de 150 para 200 mm e os dois continuam encostados |
| Projetista de interiores | Não entregar projeto com móveis sobrepostos | Antes de gerar o plano de corte, roda "Verificar colisões" e vê que o balcão entra 20 mm no pilar, com botão para ir até ele |
| Revisor interno | Conferir encaixes | Lê no painel de colisões o tipo, os itens e a profundidade de cada sobreposição, e as exceções aceitas |

## 4. Regras de negócio novas ou alteradas

**Glossário desta feature.** *Contato*: faces a até 1 mm, sem entrar uma na outra. *Grudado*: item com vínculo
gravado a uma face plana de outro objeto (o **hospedeiro**); na interface ele se chama **elemento filho** do hospedeiro
("Elemento filho de: <hospedeiro> — <face>"). *Agregado* (003): item preso à face do pai **e** limitado ao
contorno dele. *Colisão*: dois volumes entrando um no outro mais que 1 mm. *Penetração*: colisão com parede, piso ou teto.

**A. Editor de armário**

1. **RN-01:** O editor trabalha sobre **um módulo inserido**, de qualquer biblioteca suportada pela 003. Nada no projeto
   muda de forma definitiva antes de **Confirmar**; **Cancelar** devolve o módulo exatamente como era; Confirmar gera um
   único passo de desfazer. 🟡
   - Origem no legado: `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#5` (rascunho e OK do editor de paredes)
   - Tipo: nova
2. **RN-02:** Toda alteração automática feita pelo recálculo (frente redistribuída, prateleira que mudou de altura,
   item removido por falta de espaço) aparece numa lista "Ajustes automáticos" antes de Confirmar. 🟡
   - Tipo: nova
3. **RN-03:** Mensagens de validação têm código, gravidade (erro, aviso, informação), componente, parâmetro, valor
   atual, faixa permitida e ação sugerida. **Erro** impede Confirmar; aviso e informação não. 🟡
   - Tipo: nova
4. **RN-04:** Fechar o editor com alterações pendentes pergunta: continuar editando, descartar ou confirmar. 🟡
   - Tipo: nova

**B. Grudar em superfície plana**

5. **RN-05:** Hospedeiro é qualquer **face plana** de parede (frente ou trás), painel, peça de módulo, módulo,
   geometria (placa/caixa da 002) ou objeto de malha. Face plana = todos os vértices a até 0,5 mm do plano. Piso e teto
   ficam de fora (o piso já é o apoio padrão). 🟡
   - Tipo: nova
6. **RN-06:** Item grudado guarda: hospedeiro, face, posição no plano da face, distância à face (padrão 0) e
   rotação em torno da normal. Ele se move **só no plano da face**, sem limite de contorno (diferença para o agregado
   da 003). 🟡
   - Origem no legado: `_reversa_sdd/domain.md#2.2` (R-05, movimento restrito ao plano da parede)
   - Tipo: nova (estende a regra das aberturas a qualquer item e qualquer face)
7. **RN-07:** O item segue o hospedeiro: mover ou girar o hospedeiro leva o item; mudar a espessura da parede ou a
   medida do painel mantém o item **encostado na mesma face** com a mesma distância. 🟡
   - Origem no legado: `caffmob_draw/walls2d/apply.py` (hoje só aberturas recebem a nova espessura)
   - Tipo: alterada
8. **RN-08:** Quando a relação não pode ser mantida, o item **não** fica com referência inválida em silêncio:
   hospedeiro apagado → item fica solto no mesmo lugar do mundo e o relatório avisa "Vínculo perdido: <item>";
   face que deixou de existir ou de ser plana → mesmo tratamento. 🟡
   - Tipo: nova
8a. **RN-08a:** Hospedeiro que encolhe e deixa o item fora da face (ex.: painel encurtado) mantém a posição e o vínculo
   do item e avisa no relatório "Item fora da face: <item>". 🟢 (Esclarecimentos 2026-10-07, Q4)
   - Tipo: nova
9. **RN-09:** Desgrudar mantém a posição do item no mundo e apaga o vínculo. Proximidade sozinha nunca cria vínculo ao
   reabrir o arquivo; só o vínculo gravado conta. 🟡
   - Tipo: nova
10. **RN-10:** Módulos já postos na parede pelo posicionamento atual (filhos da parede com Y local = 0 ou = espessura)
    passam a ser tratados como grudados na face correspondente, **automaticamente ao abrir o arquivo**, sem pergunta e
    sem o usuário refazer nada; na interface aparecem como elemento filho da parede. 🟢 (Esclarecimentos 2026-10-07, Q5)
    - Origem no legado: `caffmob_draw/product_libraries/frameless/operators/ops_placement.py` (linhas 421-434)
    - Tipo: alterada

**C. Colisão**

10a. **RN-10a:** O ímã automático (RF-12) vem **ligado**, com distância de **50 mm**; o usuário pode desligá-lo e mudar
    a distância nas preferências do plugin, e a escolha vale para todos os arquivos. Com o ímã desligado, só o comando
    "Grudar" cria vínculo. 🟢 (Esclarecimentos 2026-10-07, Q3)
    - Tipo: nova

11. **RN-11:** Encostar (até 1 mm) não é colisão. Entrar mais que 1 mm é colisão (entre itens) ou penetração (em
    parede, piso ou teto). A tolerância é a mesma da interferência de frentes. 🟢
    - Origem no legado: `caffmob_draw/inspection/interference.py` (`TOLERANCE = 0.001`)
    - Tipo: alterada (passa a valer para corpos inteiros, não só envelope de abertura)
12. **RN-12:** Pares que **não** são colisão: peças do mesmo módulo entre si; agregado e o pai dele; item grudado e o
    hospedeiro na face do vínculo; porta/janela e a parede dela; itens com "Colisão: Desativada". 🟡
    - Origem no legado: `caffmob_draw/data/properties.py` (`collision_override`, hoje sem uso)
    - Tipo: nova
13. **RN-13:** Cada par de itens gera **uma** ocorrência, com os dois nomes, o tipo e a profundidade máxima. A lista é
    ordenada sempre igual: penetração em parede → colisão entre itens → piso/teto; dentro do tipo, maior profundidade
    primeiro. 🟡
    - Tipo: nova
14. **RN-14:** Resultado de colisão vira "desatualizado" quando qualquer item envolvido muda. A interface nunca diz "sem
    colisões" com resultado desatualizado ou com cálculo que falhou. 🟡
    - Tipo: nova
15. **RN-15:** Colisão **não** bloqueia salvar o arquivo: salvar com colisões mostra o aviso com a contagem. 🟡
    - Tipo: nova (decisão contrária ao "bloquear salvamento" da elicitação, porque bloquear o salvar do Blender arrisca perder trabalho)

## 5. Requisitos Funcionais

**A. Editor de armário**

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Abrir o editor do módulo selecionado, numa **tela própria** (como o editor de paredes), pelo painel de propriedades e pelo menu do botão direito; sem módulo selecionado, o botão fica indisponível com o motivo | Must | Com um balcão frameless selecionado, o editor abre com ele; sem seleção, o botão diz "Selecione um módulo" | 🟡 |
| RF-02 | O editor mostra a **vista frontal** do módulo e a **lista de componentes** (caixa, vãos, frentes, interior, agregados); selecionar num lado seleciona no outro | Must | Clicar na gaveta 2 na vista destaca "Gaveta 2" na lista, e vice-versa | 🟡 |
| RF-03 | Editar largura, altura e profundidade na unidade da cena, com mínimo e máximo visíveis; valor inválido (vazio, texto, negativo, fora da faixa) não é aplicado e o campo mostra o erro | Must | Digitar 50 mm numa largura com mínimo 150 mm mostra "DIM-003: mínimo 150 mm" e o módulo não muda | 🟡 |
| RF-04 | Dentro do editor, as edições da 003 (frente, estilo, puxador, material, divisões internas) sobre o componente selecionado | Must | Trocar o vão 1 de portas por 3 gavetas atualiza a vista frontal no rascunho | 🟢 |
| RF-05 | Desfazer e refazer dentro do editor (Ctrl+Z / Ctrl+Shift+Z), sem afetar o histórico da cena até Confirmar | Must | Três edições, dois Ctrl+Z: o rascunho volta à primeira edição; a cena só muda ao Confirmar | 🟡 |
| RF-06 | Validação contínua com as mensagens de RN-03: componente fora do volume do módulo, componentes internos que se sobrepõem, medida fora da faixa, componente sem suporte na biblioteca | Must | Prateleira digitada acima do topo gera erro "GEO-001" com o componente e o botão Confirmar fica indisponível | 🟡 |
| RF-07 | Lista "Ajustes automáticos" com o que o recálculo mudou sozinho (RN-02) | Should | Reduzir a largura de 2.400 para 2.000 mm lista as frentes redistribuídas | 🟡 |
| RF-08 | Confirmar aplica tudo num passo de desfazer; Cancelar ou Esc descarta; fechar com pendências pergunta (RN-01, RN-04) | Must | Confirmar e depois Ctrl+Z na cena devolve o módulo anterior inteiro | 🟢 |
| RF-09 | "Salvar como módulo" (003 RF-07) disponível no editor | Should | Salvar pelo editor grava na biblioteca do usuário igual ao painel da 003 | 🟢 |
| RF-10 | Seções sem suporte na biblioteca do módulo aparecem desabilitadas com o motivo (mesma regra da 003) | Must | Num módulo `btm`, "Gavetas internas" aparece desabilitada com o motivo | 🟢 |

**B. Grudar em superfície plana**

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-11 | Comando "Grudar": escolher o item e clicar numa face plana; o item gira para a normal da face e encosta a face de trás nela (RN-05) | Must | Grudar um nicho na lateral de um painel deixa o fundo do nicho encostado na lateral, a 0 mm | 🟡 |
| RF-12 | Ímã ao mover ou inserir: perto de uma face plana o item mostra a prévia encostada nela; soltar ali grava o vínculo; o ímã pode ser desligado e ter a distância mudada nas preferências (RN-10a) | Should | Ímã ligado a 50 mm: arrastar um aéreo a 30 mm da parede o encosta na prévia e soltar o deixa grudado; com o ímã desligado ou a distância em 20 mm, o mesmo arraste não gruda | 🟢 |
| RF-13 | Item grudado move só no plano da face, arrastando ou pelos campos de posição e distância (RN-06) | Must | Arrastar o aéreo grudado não o tira da parede; digitar distância 10 mm o afasta 10 mm | 🟡 |
| RF-14 | Seguir o hospedeiro em mover, girar e mudar medida, mantendo a face e a distância (RN-07) | Must | Espessura da parede de 150 para 200 mm pelo editor de paredes: o aéreo grudado na face de trás continua encostado | 🟡 |
| RF-15 | Hospedeiro apagado ou face perdida: item solto no lugar e aviso no relatório (RN-08) | Must | Apagar o painel deixa o nicho no mesmo lugar, sem vínculo, e o relatório cita o nicho | 🟡 |
| RF-16 | "Desgrudar" mantém a posição e apaga o vínculo (RN-09) | Must | Desgrudar e mover o painel: o nicho não acompanha | 🟡 |
| RF-17 | Estado visível em texto no painel de propriedades: "Elemento filho de: <hospedeiro> — <face>", com distância; nunca só por cor | Must | Selecionar o aéreo mostra "Elemento filho de: Parede 3 — frente" | 🟢 |
| RF-18 | Vínculo salvo no arquivo e restaurado ao reabrir | Must | Salvar, fechar e reabrir: mover a parede ainda leva o aéreo | 🟡 |
| RF-19 | Módulos já na parede tratados como grudados automaticamente ao abrir o arquivo (RN-10) | Should | Arquivo antigo com balcão filho da parede: ao abrir, o balcão mostra "Elemento filho de: Parede 1 — frente"; mudar a espessura o mantém encostado | 🟢 |

**C. Colisão**

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-20 | "Verificar colisões" na cena inteira ou só no item selecionado, entre módulos, geometrias, agregados, eletrodomésticos, paredes, piso e teto (RN-11) | Must | Balcão 20 mm dentro de um pilar gera uma ocorrência "Penetração em parede, 20 mm" | 🟡 |
| RF-21 | Painel de colisões com tipo, os dois itens, profundidade e "Ir para" que seleciona e enquadra o par (RN-13) | Must | "Ir para" seleciona o balcão e o pilar e centraliza a vista neles | 🟢 |
| RF-22 | Destaque na viewport dos itens em colisão, com o rótulo de texto do tipo, não só cor | Should | O balcão em colisão aparece contornado e com o rótulo "Colisão" | 🟡 |
| RF-23 | Ao soltar um movimento que deixa o item em colisão, o sistema **só avisa** e destaca os dois itens; não impede nem empurra o item | Must | Mover um aéreo sobre outro deixa o aéreo onde foi solto, destaca os dois e mostra "Colide com <outro>" no relatório | 🟢 |
| RF-24 | Campo "Colisão: Herdar / Ativa / Desativada" por item e chave global na cena; pares de RN-12 nunca são listados | Should | Desativar a colisão do rodapé tira as ocorrências dele da lista | 🟢 |
| RF-25 | Resultado marcado "desatualizado" após mudança; falha de cálculo mostrada como erro, nunca como "sem colisões" (RN-14) | Must | Mover um item depois de verificar troca o título do painel para "Desatualizado, verifique de novo" | 🟡 |
| RF-26 | "Afastar até encostar": move o item selecionado pelo menor deslocamento que tira a colisão, com prévia e desfazer | Could | O balcão 20 mm dentro do pilar volta 20 mm e fica encostado | 🟡 |
| RF-27 | Salvar o arquivo com colisões mostra o aviso com a contagem, sem bloquear (RN-15) | Should | Salvar com 2 colisões grava o arquivo e avisa "2 colisões pendentes" | 🟡 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Verificar colisões numa cena com 200 módulos em até 2 s; o aviso ao soltar um movimento (RF-23) em até 100 ms, testando só os vizinhos próximos do item | `_reversa_sdd/architecture.md#4` (D-02); RNF-010 da elicitação de colisão | 🟡 |
| Desempenho | Edição no editor de armário reflete na vista frontal em até 200 ms para um módulo de 4 vãos | RNF-002 da elicitação do editor | 🟡 |
| Precisão | Item grudado fica a ≤ 0,1 mm da face após qualquer mudança do hospedeiro; 10 mudanças seguidas de espessura não acumulam erro | RNF-003 das elicitações; 003 (precisão de 0,1 mm) | 🟡 |
| Determinismo | Mesma cena dá a mesma lista de colisões, na mesma ordem (RN-13) | RNF-001 da elicitação de colisão | 🟡 |
| Consistência | Grudar, desgrudar, confirmar o editor e "Afastar até encostar" são um passo de desfazer cada; cancelar não deixa resto (prévias, handlers) | CLAUDE.md (handlers e `UNDO`); 003 RNF de consistência | 🟢 |
| Compatibilidade | Blender 5.2; propriedades lidas por atributo; diferenças de versão só em `compat.py`; arquivos antigos abrem e ganham o vínculo de RN-10 | CLAUDE.md "Regras do código" | 🟢 |
| Usabilidade | Textos de UI em português e inglês; estado de vínculo e de colisão sempre em texto | Commit `53f594c` (interface pt_BR/en_US); RNF-006 da elicitação | 🟢 |
| Observabilidade | Vínculo perdido, falha de cálculo de colisão e erro de validação aparecem no relatório do Blender com o item e o motivo | 003 RNF de observabilidade | 🟡 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Editar e confirmar um armário (RF-01..RF-04, RF-08)
  Dado um roupeiro de 2.400 mm selecionado
  Quando abro o editor, mudo a largura para 2.000 mm, troco o vão 1 por 3 gavetas e clico Confirmar
  Então o roupeiro fica com 2.000 mm e 3 gavetas no vão 1
  E um Ctrl+Z na cena devolve o roupeiro de 2.400 mm inteiro

Cenário: Cancelar o editor (RF-05, RF-08)
  Dado o editor aberto com três alterações no rascunho
  Quando clico Cancelar e escolho descartar
  Então o módulo na cena é o mesmo de antes de abrir o editor

Cenário: Erro de validação impede confirmar (RF-03, RF-06)
  Dado o editor aberto num balcão com largura mínima de 150 mm
  Quando digito largura 50 mm
  Então o campo mostra "DIM-003" com a faixa permitida
  E o botão Confirmar fica indisponível

Cenário: Ajustes automáticos visíveis (RF-07)
  Dado um roupeiro de 3 vãos no editor
  Quando reduzo a largura em 400 mm
  Então a lista "Ajustes automáticos" mostra cada frente redistribuída

Cenário: Grudar num painel e seguir o hospedeiro (RF-11, RF-14, RF-17)
  Dado um nicho e um painel de 18 mm
  Quando grudo o nicho na lateral do painel e giro o painel 90°
  Então o nicho gira junto e continua encostado na lateral
  E o painel de propriedades do nicho diz "Elemento filho de: Painel — lateral"

Cenário: Espessura da parede muda (RF-14, RF-19)
  Dado um aéreo grudado na face de trás de uma parede de 150 mm
  Quando mudo a espessura para 200 mm no editor de paredes e confirmo
  Então o aéreo continua encostado na face de trás, a no máximo 0,1 mm

Cenário: Hospedeiro apagado (RF-15)
  Dado um nicho grudado num painel
  Quando apago o painel
  Então o nicho fica no mesmo lugar, sem vínculo
  E o relatório avisa "Vínculo perdido: Nicho"

Cenário: Hospedeiro encolhe (RN-08a)
  Dado um nicho grudado perto da borda de um painel de 600 mm
  Quando encurto o painel para 300 mm e o nicho fica fora da face
  Então o nicho fica no mesmo lugar e continua elemento filho do painel
  E o relatório avisa "Item fora da face: Nicho"

Cenário: Ímã desligado (RF-12)
  Dado o ímã automático desligado nas preferências
  Quando arrasto um aéreo a 30 mm da parede e solto
  Então o aéreo fica onde foi solto, sem vínculo

Cenário: Colisão ao soltar só avisa (RF-23)
  Dado dois aéreos na mesma parede
  Quando arrasto um sobre o outro e solto
  Então o aéreo fica onde foi solto
  E os dois aparecem destacados e o relatório diz "Colide com Aéreo 2"

Cenário: Desgrudar (RF-16)
  Dado um nicho grudado num painel
  Quando desgrudo e movo o painel
  Então o nicho não se move

Cenário: Grudar em face que não é plana (RF-11)
  Dado um objeto de malha com face curva
  Quando tento grudar um item nela
  Então o relatório diz "A face não é plana" e nada muda na cena

Cenário: Vínculo sobrevive a reabrir (RF-18)
  Dado um aéreo grudado na parede e o arquivo salvo
  Quando reabro o arquivo e movo a parede
  Então o aéreo acompanha a parede

Cenário: Encostar não é colisão (RF-20)
  Dado dois balcões lado a lado, encostados com 0,5 mm de diferença
  Quando verifico colisões
  Então nenhuma ocorrência é criada

Cenário: Penetração em parede (RF-20, RF-21)
  Dado um balcão 20 mm dentro de um pilar
  Quando verifico colisões
  Então aparece uma ocorrência "Penetração em parede" com 20 mm, o balcão e o pilar
  E "Ir para" seleciona os dois

Cenário: Pares permitidos não aparecem (RF-24)
  Dado um agregado afundado 10 mm no pai e uma porta de ambiente na parede
  Quando verifico colisões
  Então nenhum desses pares aparece na lista

Cenário: Resultado desatualizado (RF-25)
  Dado a verificação feita sem colisões
  Quando movo um balcão
  Então o painel mostra "Desatualizado" e não diz mais "Sem colisões"

Cenário: Salvar com colisão (RF-27)
  Dado duas colisões pendentes
  Quando salvo o arquivo
  Então o arquivo é gravado e o aviso diz "2 colisões pendentes"
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-11, RF-13..RF-18 | Must | Pedido explícito do titular ("grudar"); corrige o defeito real de espessura de parede (RN-07) |
| RF-12, RF-19 | Should | Ímã e migração dos módulos existentes aceleram o uso; o comando "Grudar" cobre o caso |
| RF-20, RF-21, RF-23, RF-25 | Must | Sem detectar e explicar, o projeto sai com sobreposição para a fábrica |
| RF-22, RF-24, RF-27 | Should | Destaque visual, exceções e aviso ao salvar |
| RF-26 | Could | Correção automática; o usuário resolve movendo |
| RF-01..RF-06, RF-08, RF-10 | Must | Pedido explícito do titular ("editor de armário") |
| RF-07, RF-09 | Should | Transparência do recálculo e atalho para a biblioteca |
| Área de abertura de portas/gavetas na colisão de corpo | Won't | Já coberta pela interferência de frentes da 001 (`inspection/interference.py`) |
| Multiusuário, concorrência de edição, orçamento, CNC | Won't | Fora do escopo das elicitações (§2.3) e do produto local |

**Orçamento de esforço.** São 27 RF em três blocos. O plano deve entregar em incrementos com teste de fumaça próprio,
na ordem **B → C → A**: grudar reutiliza agregados e plano de inserção da 003 e corrige um defeito concreto; a colisão
de corpo dá o núcleo de validação que o editor usa (RF-06); o editor é o maior bloco e depende dos dois.

## 9. Esclarecimentos

### Sessão 2026-10-07

- **Q:** O editor de armário é uma tela própria ou o painel "Personalizar módulo" ampliado? **R:** Tela própria, como o editor de paredes: vista frontal, lista de componentes, rascunho e Confirmar/Cancelar. → RF-01..RF-10.
- **Q:** Quando um movimento deixa o item em colisão, o sistema avisa, impede ou empurra? **R:** Só avisa ao soltar e destaca os dois itens. → RF-23.
- **Q:** Como um item gruda numa face? **R:** Pelo comando "Grudar" e também por ímã automático a 50 mm, com opção de desligar o ímã e de mudar a distância. → RN-10a, RF-12.
- **Q:** Hospedeiro que encolhe e deixa o item fora da face? **R:** Mantém a posição e avisa "Item fora da face: <item>". → RN-08a.
- **Q:** Módulos que já estão na parede em arquivos antigos? **R:** Passam a contar como grudados automaticamente ao abrir o arquivo; na interface o item grudado se chama **elemento filho**. → RN-10, RF-17, RF-19, glossário.

## 10. Lacunas

- 🟡 Os vídeos de referência não foram vistos quadro a quadro; mensagens, rótulos e a sequência real do fluxo devem ser
  conferidos pelo titular antes de declarar paridade.
- 🟡 Nome do hospedeiro na interface: as respostas fixaram "elemento filho" para o item; o plano define se o hospedeiro
  aparece como "elemento pai" ou só pelo nome do objeto, sem confundir com o pai do agregado da 003.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-07 | Versão inicial gerada por `/reversa-requirements` a partir do pedido do titular e das duas elicitações | reversa |
| 2026-10-07 | `/reversa-clarify`: 5 respostas integradas (tela própria, colisão só avisa, ímã de 50 mm configurável, item fora da face avisa, migração automática como "elemento filho") | reversa |

## Pendências de Qualidade

- Q-010 (parcial): RF-09, RF-10, RF-13, RF-22 e RF-26 têm critério de aceite verificável na tabela da
  seção 5, sem cenário Gherkin próprio; os cenários completos ficam para o `onboarding.md` do `/reversa-plan`.
- Q-018: o documento cita caminhos de código do legado na seção 2 (rastreabilidade exigida pelo Reversa), não como
  solução prescrita.
