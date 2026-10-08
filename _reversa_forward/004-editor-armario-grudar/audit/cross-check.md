# Cross-check — 004-editor-armario-grudar

> Data: 2026-10-07
> Gerado por `/reversa-audit` (somente leitura; nenhum artefato da feature foi alterado).
> Artefatos analisados: [`requirements.md`](../requirements.md), [`roadmap.md`](../roadmap.md),
> [`actions.md`](../actions.md) e, por ser auditoria pós-codificação, as notas de execução, o
> [`data-delta.md`](../data-delta.md) e o [`onboarding.md`](../onboarding.md).
> Eixo extra a pedido do titular: **interface** (ótica do `/impeccable`, registro *product* e *distill*: só o útil,
> sem repetição, sem tirar capacidade, conversando com a viewport). O projeto não tem `PRODUCT.md`; o `/impeccable init`
> não foi rodado porque esta auditoria só pode escrever este arquivo.

## Resumo

| Severidade | Quantidade |
|---|---|
| CRITICAL | 0 |
| HIGH | 4 |
| MEDIUM | 9 |
| LOW | 4 |

Os três artefatos estão coerentes entre si e com o legado. Os achados HIGH são de **interface** (duplicação herdada
entre o painel novo com abas e os painéis legados do Home Builder) e um critério de aceite (RF-12) que a implementação
cumpriu só em parte.

## Achados

| ID | Severidade | Eixo | Descrição | Onde está |
|---|---|---|---|---|
| A001 | HIGH | Interface | A galeria de produtos é desenhada duas vezes na mesma aba: a aba **GALERIA** do painel "CAFFMob Draw" e o painel **Product Library** usam o mesmo seletor (`home_builder.product_tab`) e o mesmo `draw_library_ui` das três bibliotecas | `caffmob_draw/ui/panels.py:241-255`; `caffmob_draw/ui/view3d_sidebar.py:613-646` |
| A002 | HIGH | Interface | Duas navegações paralelas na mesma aba: o painel "CAFFMob Draw" com 4 abas internas (Construtor, Galeria, Configurações, Plano de Corte) e 11 painéis de topo legados (Project, Room Layout, Product Library, Layout Views, 2D Details, Annotations, Plano de Corte, Colisões, Face Frame Cabinet…). É a causa raiz das repetições A001, A003, A004, A005 | `caffmob_draw/ui/panels.py:178-330`; `caffmob_draw/ui/view3d_sidebar.py` (painéis `HOME_BUILDER_PT_*`) |
| A003 | HIGH | Interface | A aba **Construtor** repete os botões do painel **Room Layout**: Desenhar Paredes, Criar Teto, Porta Simples, Porta Dupla, Janela, Vão Livre, Luzes do Quarto, Inserir Obstáculo (8 operadores em dois painéis) | `ui/panels.py:209-231` × `ui/view3d_sidebar.py:380, 437-442, 486, 504, 554` |
| A004 | HIGH | Cobertura (requirements × código) | RF-12 pede "o ímã mostra a prévia encostada" ao mover/inserir; a implementação gruda **ao soltar**, sem prévia (desvio registrado nas notas de T030/T032). A ação está `[X]`, mas o critério de aceite do RF-12 não é atendido como escrito | `requirements.md#5` (RF-12); `actions.md` (notas de execução); `stick/settle.py` |
| A005 | MEDIUM | Interface | Gerenciador de ambientes em dois painéis: aba Configurações (trocar/criar/renomear/apagar) e painel **Project › Rooms** (as mesmas ações + reordenar) | `ui/panels.py:296-320` × `ui/view3d_sidebar.py:254-280, 766-768` |
| A006 | MEDIUM | Interface | Plano de corte em dois lugares: aba **Plano de Corte** e painel **Plano de Corte (Nesting)**, ambos com `draw_cut_plan` | `ui/panels.py:327-330` × `ui/panels.py:335-347` |
| A007 | MEDIUM | Interface | Três "bibliotecas do usuário": "User" do frameless (grupos de gabinetes), a do face frame e a **Biblioteca de módulos** (003). A última fica dentro de **Propriedades** (painel do objeto selecionado), sem `poll`, embora não dependa da seleção | `customize/panels.py:130-139`; `props_hb_frameless.py` (`show_user_library`); `props_hb_face_frame.py` (`draw_user_library_ui`) |
| A008 | MEDIUM | Interface | Propriedades de um módulo abrem 8 subpainéis (Arranjo, Dimensões e limites, Movimentação, Personalizar módulo, Biblioteca de módulos, Agregados e folhas, **Elemento filho**, **Colisão**). Há sobreposição: "Dimensões e limites" repete as medidas da caixa Dimensões; "Movimentação" e "Elemento filho" tratam de posição; "Colisão" (do item) e o painel de topo "Colisões" tratam do mesmo assunto. O painel "Elemento filho" (004) vem aberto por padrão e aparece para todo item, só com o botão Grudar | `ui/object_properties.py:362-460`; `stick/panels.py`; `collision/panels.py` |
| A009 | MEDIUM | Interface | "Evitar Sobreposição" (`collision_global`) aparece na aba Configurações e no painel Colisões (quando desligada); o mesmo controle em dois lugares | `ui/panels.py:269`; `collision/panels.py` (`draw_collisions`) |
| A010 | MEDIUM | Consistência (roadmap × código) | O roadmap descreve D-06 (ímã no `PlacementMixin` com prévia) e D-16 (sem aviso no G nativo); a implementação seguiu o "assentar" por `Window.modal_operators` e avisa também no G nativo. O roadmap ficou desatualizado em relação ao código | `roadmap.md#3` (D-06, D-16); `actions.md` (notas) |
| A011 | MEDIUM | Consistência (data-delta × código) | `data-delta.md` descreve `BTM_PG_Collision.axis` (enum) e não cita `push`, `checked_names` nem `BTM_PG_Stick.applied_spin`, que existem no código | `data-delta.md#1.1, #1.4`; `collision/props.py`; `stick/props.py` |
| A012 | MEDIUM | Consistência (onboarding × código) | O onboarding I1 passo 5 diz "a prévia deve encostar na lateral"; com o assentar, o item encosta ao soltar | `onboarding.md` (I1, passo 5) |
| A013 | MEDIUM | Cobertura (rastreabilidade) | O roadmap cobre todos os RF, mas cita explicitamente só parte deles por ID (faltam, entre outros, RF-01, RF-03, RF-05, RF-06, RF-08..RF-11, RF-13..RF-18, RF-20, RF-21, RF-25, RF-27). A cobertura foi conferida à mão (lista em "Itens que passaram") | `roadmap.md#3` |
| A014 | LOW | Interface | Código morto: o pacote `catalog/` (painel **Catalog**, uma terceira galeria) não é registrado por `caffmob_draw/__init__.py` | `caffmob_draw/catalog/` |
| A015 | LOW | Interface | Controles de abrir frentes em dois lugares: caixa de inspeção da aba Construtor (Abrir/Fechar tudo) e grupo **Abrir** em Propriedades (frente selecionada). Escopos diferentes (cena × seleção), mas a mesma função visual em dois painéis | `ui/panels.py:72-101`; `ui/object_properties.py:224` |
| A016 | LOW | Cobertura (roadmap × actions) | D-09 (faces da parede frente/trás e espessura) não tem ação própria; está coberta por T024/T029 | `roadmap.md#3` (D-09); `actions.md` |
| A017 | LOW | Interface | A integração com a viewport é pouco usada como caminho principal: o HUD de controles vem desligado (`use_viewport_hud = False`) e as ações frequentes da 004 (Grudar, Mover no plano, Abrir editor, Verificar colisões) dependem da barra lateral ou do menu do botão direito | `caffmob_draw/__init__.py` (`BTM_AddonPreferences.use_viewport_hud`); `stick/ops_stick.py` (`draw_context_menu`) |

## Impacto e direção (CRITICAL e HIGH)

**A001 — galeria duplicada.** O usuário vê a mesma galeria em dois lugares, com o mesmo seletor de biblioteca;
abrir as duas duplica a altura da barra e confunde qual é a "certa". Pelo princípio *distill* ("se já está em outro
lugar, não repita"), deve existir **uma** galeria. Direção: manter uma só entrada (a aba GALERIA ou o painel Product
Library, não os dois) e decidir isso com o titular. É mudança de interface fora do escopo da 004: abrir uma feature ou
bug próprio (`/reversa-requirements` para uma feature de "faxina da barra lateral", ou `/reversa-debugger` se tratado
como defeito) e depois `/reversa-coding`.

**A002 — duas navegações.** Um usuário fluente em ferramentas do ramo espera uma hierarquia: o que construir, o que
inserir, o que está selecionado, o que configurar, o que produzir. Hoje há abas dentro de um painel **e** painéis de
topo com o mesmo conteúdo. Direção sugerida (a validar com o titular, sem remover capacidade):
1. **Construir** (paredes, aberturas, obstáculos, teto, luzes): um lugar só;
2. **Inserir** (galeria de produtos + bibliotecas do usuário, numa seção "Meus módulos");
3. **Selecionado** (Propriedades, contextual: só o que vale para o tipo do objeto, em menos subpainéis);
4. **Verificar** (inspeção de frentes e colisões juntas);
5. **Produção** (plano de corte) e **Projeto/Configurações** (ambientes, unidades, chapas, padrões).
Os painéis 2D (Layout Views, 2D Details, Annotations) já somem com "Ocultar Painéis 2D". Caminho: `/reversa-clarify`
numa feature nova de reorganização, seguida de `/reversa-plan`.

**A003 — Construtor × Room Layout.** Oito botões repetidos. Direção: a mesma de A002; o painel que ficar com
"Construir" concentra os botões e o outro é removido ou recolhido, mantendo atalhos no menu do botão direito e no
HUD da viewport.

**A004 — RF-12 sem prévia.** O critério de aceite não é atendido literalmente. Direção: ou o titular aceita "gruda ao
soltar" e o `requirements.md` é atualizado por `/reversa-clarify`, ou abre-se uma ação para desenhar a prévia do
ímã durante o arraste (um overlay `POST_VIEW` com a face-alvo destacada, que também "conversa com a viewport", A017).

## Itens que passaram

**Cobertura**
- Todos os 27 RF têm decisão no roadmap: RF-01/D-27; RF-02/D-23; RF-03, RF-06, RF-10/D-24; RF-04, RF-05/D-21, D-22;
  RF-07/D-25; RF-08/D-21, D-26; RF-09/D-27; RF-11/D-05; RF-12/D-06; RF-13/D-04, D-07; RF-14/D-04, D-09; RF-15/D-07,
  D-10; RF-16/D-07; RF-17/D-11; RF-18/D-03; RF-19/D-08; RF-20/D-12, D-13; RF-21/D-14; RF-22/D-17; RF-23/D-16;
  RF-24/D-18; RF-25/D-15; RF-26/D-19; RF-27/D-15.
- Todas as decisões D-01..D-27 têm ação, exceto D-09 sem ação própria (A016).
- Os 18 cenários Gherkin do requirements estão cobertos por ações e por um dos três testes de fumaça
  (`blender_004_stick_smoke.py`, `blender_004_collision_smoke.py`, `blender_004_cabinet_editor_smoke.py`), todos
  passando na última rodada.

**Consistência**
- Termos estáveis nos três documentos: "elemento filho", "hospedeiro", "Grudar/Desgrudar", "Verificar colisões",
  "desatualizado", "Editor de Armário", "instantâneo".
- Nenhum identificador fantasma: os RF e RN citados no roadmap e no actions existem no requirements.
- Sem contratos externos: `interfaces/` ausente, coerente com o roadmap §7.

**Coerência com o legado**
- Nenhuma decisão contradiz as regras 🟢 de `_reversa_sdd/domain.md` (R-01..R-10 preservadas, conforme
  `legacy-impact.md`).
- Os componentes citados existem: `hb_placement`, `walls2d`, `inspection/interference.py`, `aggregates`,
  `customize`, `selection/classify`, `data/properties.py`.

**Sanidade do actions**
- 60 ações, todas com dependências apontando para IDs existentes.
- Nenhuma tarefa `[//]` compartilha arquivo alvo.
- Sem ciclo de dependência (maior cadeia: 10).

**Interface: o que já está bem**
- A 004 não acrescentou botões duplicados no mesmo painel. As entradas repetidas que ela criou (Abrir editor de
  armário na caixa Dimensões e no menu do botão direito; Grudar no painel e no menu) são **caminhos de contexto**:
  painel + menu da viewport. Isso é descoberta, não repetição.
- O Editor de Armário segue uma hierarquia limpa: uma ação primária (Confirmar), estados de erro em texto, faixa
  visível em cada medida e a vista frontal como centro.
- Os overlays de colisão e da folha usam texto além de cor (estado legível sem depender só do vermelho).
