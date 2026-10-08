# Requirements: Barra lateral em 5 seções, sem repetição, conversando com a viewport

> Identificador: `005-barra-lateral-viewport`
> Data: `2026-10-07`
> Pasta da extração reversa: `_reversa_sdd/`
> Origem: pedido do titular depois do `/reversa-audit` da 004 (achados A001–A017 em
> `_reversa_forward/004-editor-armario-grudar/audit/cross-check.md`) e decisões de 2026-10-07: painel "Inserir" único,
> prévia do ímã, 5 seções contextuais. Princípios de produto em `PRODUCT.md`.
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

A aba CAFFMob Draw tem hoje duas navegações ao mesmo tempo. Uma é o painel novo com 4 abas internas; a outra são 11
painéis de topo herdados do Home Builder. Por isso a galeria aparece duas vezes, 8 botões de construção se repetem, o
gerenciador de ambientes e o plano de corte aparecem em dobro e há três "bibliotecas do usuário". Esta feature entrega
ao projetista **uma navegação só, em 5 seções** (Construir · Inserir · Selecionado · Verificar · Produção/Projeto), com
cada função num lugar e **nenhuma capacidade a menos**. Ela também leva as ações frequentes para a **viewport** (menu
do botão direito e HUD ligado por padrão) e desenha a **prévia do ímã** durante o arraste, o que cumpre o RF-12 da 004.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/ui/requirements.md#Regras de Negócio` (R-01, R-02) | Aberturas e ajuste de piso só aparecem com ao menos uma parede; o painel de propriedades se ajusta ao tipo do objeto ativo | 🟢 |
| `_reversa_sdd/domain.md#2.1 Regras de Paredes e Piso` (R-01) | O piso só é oferecido se houver ao menos um segmento de parede | 🟢 |
| `_reversa_forward/004-editor-armario-grudar/audit/cross-check.md` (A001) | A galeria de produtos é desenhada duas vezes: aba GALERIA (`ui/panels.py:241-255`) e painel Product Library (`ui/view3d_sidebar.py:613-646`) | 🟢 |
| idem (A002, A003) | Duas navegações paralelas; a aba Construtor repete 8 operadores do painel Room Layout | 🟢 |
| idem (A005, A006, A009) | Gerenciador de ambientes, plano de corte e "Evitar Sobreposição" em dois lugares cada | 🟢 |
| idem (A007, A014) | Três bibliotecas do usuário (frameless "User", face frame, "Biblioteca de módulos" da 003), esta dentro de Propriedades sem `poll`; pacote `catalog/` não registrado | 🟢 |
| idem (A008) | Um módulo abre 8 subpainéis em Propriedades, com sobreposições (dimensões, posição, colisão) | 🟢 |
| idem (A004, A017) | O ímã gruda ao soltar, sem prévia; o HUD da viewport vem desligado (`use_viewport_hud = False`) | 🟢 |
| `caffmob_draw/operators/viewport_hud.py` | HUD desenhado na viewport, com botões de modo (Grab, Abrir Portas e Gavetas, Mover Sobre) e um navegador de cenas; não usa modal persistente para não travar o salvamento automático | 🟢 |
| `caffmob_draw/product_libraries/face_frame/ui_face_frame.py:1498` | Painel "Face Frame Cabinet" (7 subpainéis) aparece com um módulo face frame selecionado, separado de Propriedades | 🟢 |
| `PRODUCT.md#Product Principles` | Viewport como lugar principal; convenções do Blender; cada função num lugar só; contextual ao selecionado | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de loja/marcenaria (`PRODUCT.md#Users`) | Achar cada ferramenta sem procurar | Abre a aba CAFFMob Draw e vê 5 seções na ordem do trabalho; a galeria aparece uma vez só |
| Projetista de loja/marcenaria | Inserir um módulo próprio salvo | Em Inserir › Meus módulos encontra juntos os módulos salvos, os grupos frameless e os do face frame |
| Projetista de loja/marcenaria | Ajustar o módulo selecionado | Selecionado mostra só o que vale para aquele módulo, em poucos grupos; o resto fica recolhido |
| Projetista de loja/marcenaria | Trabalhar sem ir à barra lateral | Clica com o botão direito no módulo e acha Grudar, Mover Sobre, Abrir editor, Verificar colisões; o HUD mostra os modos ativos |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** A aba CAFFMob Draw tem **uma navegação só**, em 5 painéis empilhados e recolhíveis nesta ordem:
   **Construir**, **Inserir**, **Selecionado**, **Verificar**, **Produção/Projeto**. Selecionado abre sozinho quando há
   algo selecionado. Nenhum outro painel de topo do plugin fica visível na aba. 🟢 (Esclarecimentos 2026-10-07, Q1)
   - Tipo: alterada (substitui o painel com 4 abas e os painéis de topo legados)
2. **RN-02:** Cada operador e cada controle aparece **uma vez** na barra lateral. Outros caminhos fora da barra lateral
   (menu do botão direito, HUD, menus do cabeçalho) podem repetir uma ação, mas nunca outro painel. 🟢 (`PRODUCT.md`,
   princípio 3)
   - Tipo: nova
3. **RN-03:** **Nenhuma capacidade é removida.** Toda ação hoje acessível pela aba continua acessível depois, em um
   único lugar da barra lateral ou num caminho de contexto. 🟢 (pedido do titular)
   - Tipo: nova
4. **RN-04:** **Inserir** tem uma galeria só, com o seletor de biblioteca (frameless, face frame, closets). Abaixo dela
   fica **Meus módulos**, que junta os módulos salvos (003), os grupos do usuário do frameless e os do face frame numa
   lista com a origem de cada item. 🟢 (decisão de 2026-10-07)
   - Tipo: alterada
5. **RN-05:** **Selecionado** é contextual (preserva R-02 da UI). Mostra no máximo **4 grupos abertos** por tipo de
   objeto; o restante fica recolhido. Para módulo, os grupos são Medidas e cotas, Personalizar, Posição e vínculo e
   Abrir. As opções próprias da biblioteca (face frame: construção, padrões, vãos) entram como grupo recolhido dentro de
   Selecionado, e não como painel separado. 🟡
   - Origem no legado: `_reversa_sdd/ui/requirements.md#Regras de Negócio` (R-02)
   - Tipo: alterada
6. **RN-06:** **Verificar** junta a inspeção de frentes (abrir/fechar, interferência) e as colisões. **Produção/Projeto**
   junta o plano de corte, os ambientes, as configurações (unidade, chapa, padrões, Evitar Sobreposição), os dados do
   projeto e o grupo recolhido "Desenhos 2D". 🟡 (Desenhos 2D: Esclarecimentos 2026-10-07, Q3)
   - Tipo: alterada
7. **RN-07:** Em **Construir**, aberturas, piso e teto só ficam disponíveis quando há ao menos uma parede. Sem parede,
   os botões aparecem desabilitados e uma linha explica "Desenhe uma parede primeiro". 🟢
   - Origem no legado: `_reversa_sdd/ui/requirements.md#Regras de Negócio` (R-01); `_reversa_sdd/domain.md#2.1` (R-01)
   - Tipo: preservada (hoje a aba Construtor mostra os botões sempre)
8. **RN-08:** O **HUD da viewport vem ligado** para instalações novas (quem já tem o plugin mantém a escolha) e continua
   desligável nas preferências. Ele mostra os modos ativos (Mover Sobre, Abrir frentes, Grudar) e, com algo
   selecionado, as 3 ou 4 ações principais do item. 🟢 (Esclarecimentos 2026-10-07, Q2 e Q4)
   - Origem no legado: `caffmob_draw/operators/viewport_hud.py`
   - Tipo: alterada (padrão era desligado)
9. **RN-09:** O **menu do botão direito** de um módulo, geometria ou item grudado traz as ações frequentes: Grudar ou
   Desgrudar, Mover no plano, Mover Sobre, Abrir editor de armário, Verificar colisões do item e Abrir/Fechar frentes.
   🟡
   - Tipo: alterada
10. **RN-10:** Durante um arraste (G nativo ou posicionamento do plugin) com o ímã ligado, a viewport mostra a **face-alvo
    destacada** e o **contorno de onde o item vai encostar** quando ele está a até a distância do ímã de uma face plana.
    Ao soltar, ele gruda ali. Sem face ao alcance, nada é desenhado. 🟢 (decisão de 2026-10-07)
    - Origem: `_reversa_forward/004-editor-armario-grudar/requirements.md#5` (RF-12)
    - Tipo: alterada (cumpre o critério do RF-12 da 004)
11. **RN-11:** Painéis e código que não são registrados nem usados (pacote `catalog/`) ficam fora do pacote ou são
    removidos, sem efeito para o usuário. 🟡
    - Tipo: removida

## 5. Requisitos Funcionais

**A. Navegação única**

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | As 5 seções de RN-01 na aba CAFFMob Draw, como **5 painéis empilhados e recolhíveis** (padrão do Blender), na ordem do trabalho; **Selecionado abre sozinho** quando há algo selecionado; as outras seções lembram se estavam abertas ou recolhidas | Must | Abrir a aba mostra só os 5 painéis; selecionar um módulo abre Selecionado; recolher Construir e trocar de seleção mantém Construir recolhido; nenhum painel legado de topo aparece | 🟢 |
| RF-02 | **Construir**: paredes (desenhar, editor de paredes), piso, teto, aberturas (porta simples, dupla, janela, vão livre), obstáculos, luzes, escadas, imagem de referência e as geometrias Placa/Caixa, cada um uma vez | Must | Os 8 operadores hoje repetidos entre a aba Construtor e o painel Room Layout aparecem uma vez cada | 🟢 |
| RF-03 | **Inserir**: uma galeria com o seletor de biblioteca e, abaixo, **Meus módulos** com as três origens do usuário e um filtro por origem (RN-04) | Must | A galeria é desenhada uma vez; um módulo salvo, um grupo frameless e um grupo face frame aparecem na mesma lista, com a origem indicada | 🟢 |
| RF-04 | **Selecionado**: grupos por tipo de objeto, no máximo 4 abertos (RN-05); as opções do face frame passam a ser um grupo recolhido dentro dele | Must | Selecionar um balcão frameless mostra 4 grupos; selecionar um face frame mostra os mesmos 4 e "Opções do face frame" recolhido; não há painel "Face Frame Cabinet" separado | 🟡 |
| RF-05 | **Verificar**: abrir/fechar frentes, interferência e colisões numa seção, com um único controle de "Evitar Sobreposição" (em Produção/Projeto) | Must | Inspeção e colisões aparecem juntas; a chave Evitar Sobreposição aparece uma vez na barra lateral | 🟡 |
| RF-06 | **Produção/Projeto**: plano de corte (uma vez), ambientes (uma vez, com reordenar), unidade, chapa, padrões e dados do projeto | Must | O plano de corte e o gerenciador de ambientes aparecem uma vez cada | 🟡 |
| RF-07 | Painéis de desenho 2D (vistas de layout, detalhes, anotações) viram o grupo recolhido **"Desenhos 2D" dentro de Produção/Projeto** e somem com a preferência "Ocultar Painéis 2D" | Should | Com "Ocultar Painéis 2D" ligado, nada do 2D aparece; desligado, o grupo "Desenhos 2D" aparece recolhido em Produção/Projeto | 🟢 |
| RF-08 | Inventário de capacidade: lista de todos os operadores acessíveis pela aba antes e depois, conferida por teste | Must | O teste falha se algum operador acessível antes deixar de ter um caminho depois (RN-03) | 🟢 |
| RF-09 | Teste de não repetição: nenhum operador aparece em dois painéis da barra lateral | Must | O teste falha se um `bl_idname` for desenhado por dois painéis da aba (RN-02) | 🟢 |
| RF-10 | Pacote `catalog/` não registrado sai do pacote gerado (RN-11) | Could | `build.py` não inclui `catalog/`; nenhuma função muda | 🟡 |

**B. Conversa com a viewport**

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-11 | HUD ligado por padrão **só em instalações novas**; quem já tem o plugin mantém a escolha atual; desligável nas preferências (RN-08) | Must | Instalar em perfil novo mostra o HUD; atualizar num perfil com o HUD desligado mantém desligado; desligar a preferência some com ele | 🟢 |
| RF-12 | O HUD mostra os modos ativos (Mover Sobre, Abrir frentes, Grudar/Mover no plano) e, com um item selecionado, as **3 ou 4 ações principais dele** (mesmo rótulo e ícone do menu do botão direito) | Must | Com um módulo selecionado, o HUD mostra até 4 ações dele; sem seleção, só os modos; com o Mover Sobre ligado, o HUD mostra o modo ativo e como sair | 🟢 |
| RF-13 | Menu do botão direito com as ações frequentes de RN-09, só as que valem para o objeto | Must | Botão direito num módulo frameless mostra as 6 ações; numa parede, só as da parede | 🟡 |
| RF-14 | Prévia do ímã durante o arraste: face-alvo destacada e contorno do item encostado, com o nome do hospedeiro em texto (RN-10) | Must | Arrastar um aéreo a 30 mm de uma lateral mostra a face destacada e o contorno; soltar gruda ali; a 80 mm (ímã de 50 mm) nada aparece | 🟢 |
| RF-15 | A prévia não atrapalha o arraste: some ao soltar, ao cancelar (Esc ou botão direito) e quando o ímã está desligado | Must | Cancelar um G nativo não deixa desenho nem vínculo; ímã desligado não desenha nada | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Desenhar a aba (qualquer seção aberta) em até 16 ms numa cena com 200 módulos; a prévia do ímã acompanha o mouse sem queda perceptível (até 16 ms por quadro) | Uso interativo; o desenho de painel roda a cada redesenho | 🟡 |
| Consistência | Mesmo vocabulário de botões em todas as seções: um rótulo e um ícone por ação, iguais onde quer que a ação apareça (painel, menu, HUD) | `.claude/skills/impeccable/reference/product.md` ("inconsistent component vocabulary") | 🟢 |
| Usabilidade | Cada seção mostra primeiro a ação principal; estados vazios explicam o próximo passo ("Desenhe uma parede primeiro", "Selecione um objeto") | `PRODUCT.md#Product Principles`; ótica *distill* | 🟢 |
| Acessibilidade | Estados sempre em texto além da cor (desatualizado, colisão, grudado, desabilitado com motivo) | `PRODUCT.md#Accessibility & Inclusion` | 🟢 |
| Compatibilidade | Blender 5.2; arquivos antigos abrem sem perder preferências; textos novos em pt-BR e en-US | CLAUDE.md; `data/i18n.py` | 🟢 |
| Manutenção | Os painéis legados deixam de se registrar na aba, sem apagar a lógica das bibliotecas; o código de desenho de cada biblioteca é chamado de um lugar só | Fork do Home Builder 5 (`_reversa_sdd/soul.md#1`) | 🟡 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Uma navegação só (RF-01)
  Dado o add-on instalado e a aba CAFFMob Draw aberta
  Quando nada está selecionado
  Então vejo só as seções Construir, Inserir, Selecionado, Verificar e Produção/Projeto
  E nenhum painel legado de topo

Cenário: Selecionado abre sozinho e as outras seções lembram o estado (RF-01)
  Dado Construir recolhido e nada selecionado
  Quando seleciono um módulo
  Então Selecionado se abre com os grupos do módulo
  E Construir continua recolhido

Cenário: Atualização não liga o HUD de quem o desligou (RF-11)
  Dado um perfil com o plugin instalado e o HUD desligado
  Quando atualizo o plugin
  Então o HUD continua desligado

Cenário: Galeria uma vez (RF-03)
  Dado a seção Inserir aberta
  Quando procuro a galeria de produtos
  Então ela aparece uma única vez, com o seletor de biblioteca
  E Meus módulos lista juntos um módulo salvo, um grupo frameless e um grupo face frame, com a origem

Cenário: Nenhuma capacidade a menos (RF-08)
  Dado a lista de operadores acessíveis pela aba antes da mudança
  Quando o teste de inventário roda depois da mudança
  Então todo operador da lista tem um caminho na barra lateral ou no menu de contexto

Cenário: Nenhum botão repetido (RF-09)
  Dado a barra lateral reorganizada
  Quando o teste de não repetição roda
  Então nenhum operador é desenhado por dois painéis da aba

Cenário: Construir sem parede (RF-02)
  Dado uma cena sem paredes
  Quando abro Construir
  Então os botões de aberturas, piso e teto aparecem desabilitados
  E leio "Desenhe uma parede primeiro"

Cenário: Selecionado enxuto (RF-04)
  Dado um módulo face frame selecionado
  Quando abro Selecionado
  Então vejo no máximo 4 grupos abertos e "Opções do face frame" recolhido
  E não existe painel "Face Frame Cabinet" separado

Cenário: Ações no botão direito (RF-13)
  Dado um balcão frameless selecionado
  Quando clico com o botão direito sobre ele na viewport
  Então vejo Grudar, Mover no plano, Mover Sobre, Abrir editor de armário, Verificar colisões e Abrir/Fechar frentes

Cenário: HUD ligado por padrão (RF-11)
  Dado um perfil novo do Blender com o add-on instalado
  Quando abro a viewport
  Então o HUD aparece
  E ao desligar a preferência ele some

Cenário: Prévia do ímã (RF-14)
  Dado o ímã ligado a 50 mm e um aéreo sendo arrastado com G
  Quando o fundo do aéreo chega a 30 mm da lateral de um roupeiro
  Então a lateral fica destacada e vejo o contorno do aéreo encostado e o nome do roupeiro
  E ao soltar o aéreo fica grudado ali

Cenário: Prévia some ao cancelar (RF-15)
  Dado a prévia do ímã visível durante um arraste
  Quando aperto Esc
  Então a prévia some, o aéreo volta ao lugar e nenhum vínculo é criado
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01..RF-06, RF-08, RF-09 | Must | Pedido central: uma navegação, nada repetido, nada perdido; os dois testes são a garantia |
| RF-11, RF-13..RF-15 | Must | "Conversando com a viewport" e a prévia do ímã foram decididos pelo titular |
| RF-12 | Must | O HUD com as ações do item é parte do "conversar com a viewport" (Esclarecimentos Q2) |
| RF-07 | Should | Desenhos 2D seguem a preferência existente; há alternativa (painéis 2D já ocultáveis) |
| RF-10 | Could | Limpeza sem efeito visível |
| Mudar o tema ou as cores do Blender, ícones próprios | Won't | `PRODUCT.md` (convenções do Blender) |
| Integração com a conta CAFF DIGITAL | Won't (nesta feature) | Em aberto em `PRODUCT.md#Capabilities and Constraints`; feature própria |

**Orçamento de esforço.** São 15 RF em dois blocos. O plano deve entregar primeiro o inventário de capacidade e o teste
de não repetição (RF-08, RF-09), que viram a rede de segurança; depois a navegação única (A); por último a viewport (B).
Cada incremento tem o próprio teste de fumaça com captura da barra lateral.

## 9. Esclarecimentos

### Sessão 2026-10-07

- **Q:** Forma das 5 seções? **R:** 5 painéis empilhados e recolhíveis (padrão do Blender); Selecionado abre sozinho quando há seleção e os outros lembram se estavam abertos. → RN-01, RF-01.
- **Q:** O que o HUD mostra? **R:** Os modos ativos e, com algo selecionado, as 3 ou 4 ações principais do item. → RN-08, RF-12 (passa a Must).
- **Q:** Onde ficam os painéis de desenho 2D? **R:** Grupo "Desenhos 2D" recolhido dentro de Produção/Projeto, sumindo com "Ocultar Painéis 2D". → RN-06, RF-07.
- **Q:** HUD ligado por padrão para quem já tem o plugin? **R:** Só instalações novas ligam; quem já tem mantém a escolha. → RN-08, RF-11.

## 10. Lacunas

- 🟡 A lista exata de grupos de Selecionado para parede, abertura, geometria, obstáculo e piso será fechada no plano, a
  partir do que o painel de propriedades da 002 já mostra por tipo.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-07 | Versão inicial gerada por `/reversa-requirements` a partir do cross-check da 004, das decisões do titular e do `PRODUCT.md` | reversa |
| 2026-10-07 | `/reversa-clarify`: 4 respostas integradas (painéis empilhados, HUD com ações do item, Desenhos 2D em Produção/Projeto, HUD ligado só em instalações novas) | reversa |
