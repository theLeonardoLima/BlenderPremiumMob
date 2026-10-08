# Regression watch — 005-barra-lateral-viewport

> Criado por `/reversa-coding` em 2026-10-08 (rodada única, T001–T038).

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|---|---|---|---|---|
| W001 | `_reversa_sdd/ui/requirements.md#Requisitos Funcionais` (RF-01) | A aba CAFFMob Draw tem um único painel registrado (`BTM_PT_sidebar`) com 5 seções recolhíveis; os painéis legados são desenhados dentro delas | redação | Spec regenerada lista os painéis `HOME_BUILDER_PT_*`/`BTM_PT_EnvironmentBuilder` como painéis da aba |
| W002 | `_reversa_sdd/ui/requirements.md#Regras de Negócio` (R-01) e `_reversa_sdd/domain.md#2.1` (R-01) | Em Construir, aberturas e piso e teto ficam indisponíveis sem parede, com "Desenhe uma parede primeiro" | presença | Botões de aberturas/piso ativos numa cena sem paredes |
| W003 | `_reversa_sdd/ui/requirements.md#Regras de Negócio` (R-02) | Selecionado mostra só os grupos do tipo do objeto ativo, no máximo 4 abertos, e abre sozinho quando algo é selecionado | presença | Painel de propriedades separado volta, ou mais de 4 grupos abertos por padrão |
| W004 | `tests/fixtures/sidebar_inventory_baseline.json` (RN-03 da 005) | Toda ação da linha de base continua alcançável pela barra lateral, pelo menu do botão direito ou pelo HUD | presença | `tests/blender_005_sidebar_inventory.py` falha com "capacidade perdida" |
| W005 | RN-02 da 005 | Nenhum operador é desenhado por duas seções da barra lateral | ausência | `tests/blender_005_sidebar_inventory.py` falha com "repetido" |
| W006 | `_reversa_forward/004-editor-armario-grudar/roadmap.md` (D-04, assentar) | O ímã age ao soltar e não age quando o movimento termina onde o item já estava (cancelar um G não gruda) | presença | Cancelar um G perto de uma face deixa o item grudado |

## Histórico de re-extrações

<!-- Preenchido pelo agente reverso em cada `/reversa` futuro: data, veredito 🟢/🟡/🔴 por item. -->

## Arquivadas

<!-- Itens que deixaram de ser relevantes, com data e motivo. -->

## Observações

Itens sem peso de regressão (decisão nova desta feature, origem 🟡):

- Meus módulos em três blocos com filtro, cada um com os operadores da própria biblioteca. 🟡
- Linha de ações do item no HUD sem Mover Sobre (já na linha dos modos). 🟡
- HUD ligado por padrão: quem nunca salvou a preferência passa a vê-lo; quem a desligou e salvou continua sem. 🟡
- Prévia do ímã só desenha (`POST_VIEW`/`POST_PIXEL`) e não mexe no objeto; não aparece para módulo em parede da
  biblioteca nem para item já grudado. 🟡
- `catalog/` continua no repositório, fora do pacote. 🟡
