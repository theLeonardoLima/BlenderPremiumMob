# Cross-check: 008-editor-armario-construtor (2ª rodada)

> Data: 2026-10-08. 2ª auditoria, depois da sessão 2 do clarify, do `/reversa-plan` revisado e da revisão do
> `actions.md`.
>
> Artefatos analisados:
> - [requirements.md](../requirements.md)
> - [roadmap.md](../roadmap.md)
> - [actions.md](../actions.md)
>
> Apoio: `data-delta.md`, `interfaces/cut-plan-json.md`, `_reversa_sdd/domain.md`, `_reversa_sdd/architecture.md`.
> Auditoria só de leitura: nenhum artefato foi alterado.

## Resumo

| Severidade | Quantidade |
|------------|-----------|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 3 |
| LOW | 2 |

Situação dos achados da 1ª rodada:

| Achado anterior | Situação |
|---|---|
| A001 Inserir sem vão | **fechado** (D-21; T032, T039, T040) |
| A002 itens de catálogo sem regra | **fechado** (RN-10a, RN-12; D-22, D-23; T053, T055–T057) |
| A003 cenário com 5 abas | **fechado** (cenário com as 7 abas) |
| A004 nomes em inglês | **fechado** (RF-14 com 7 nomes) |
| A005 lista de ferragens | **fechado** (RN-16; D-14, D-24; T054, T059–T062; contrato 2.2.0) |
| A006 RF-05 e RF-07 sem decisão | **parcial**: RF-07 fechado (D-25); RF-05 continua sem decisão (ver A101) |
| A007 `[//]` com o mesmo arquivo | **fechado** (T020 sem `[//]`) |
| A008 ação em 4 arquivos | **fechado** (T023 + T063) |
| A009 puxador nas gavetas | **fechado** (D-03, RN-12; T040, T056) |

## Findings

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| A101 | MEDIUM | Cobertura (1.1) | RF-05 (painel de propriedades com "Não há propriedades disponíveis") ainda não tem decisão no roadmap: quando o painel mostra propriedades, de quais itens, e quando mostra o estado vazio. A implementação está só em T037 | requirements RN-06, RF-05; actions T037; ausente no roadmap |
| A102 | MEDIUM | Consistência requirements × roadmap | A RN-10a diz que a divisória móvel tem "marcação de furação **na peça**"; a D-22 e o contrato põem a furação nas **duas peças vizinhas** (laterais/divisórias), em `drilling`. A D-22 é a leitura física correta (furo para pino fica nas laterais), mas o texto do requirements não foi alinhado | requirements RN-10a; roadmap D-22; interfaces `cut-plan-json.md` |
| A103 | MEDIUM | Cobertura data-delta × actions | O campo `btm_custom.slide_kind` (data-delta §1.3a) precisa ser acrescentado ao `BTM_PG_CustomSpec` (`customize/props.py`), mas nenhuma ação tem esse arquivo como alvo; T056 e T059 só o usam | data-delta §1.3a; actions T056, T059 |
| A104 | LOW | Sanidade | O ID T058 não existe (pulado na revisão). Não fere a regra de não reciclar, mas o leitor pode estranhar; a nota de execução registra | actions (resumo e notas) |
| A105 | LOW | Organização | T057 (furação) e T059 (lista de ferragens) são núcleo (cálculo puro + coletor) e estão na Fase 4, Integração. As dependências estão certas, então não muda a ordem de execução | actions T057, T059 |

Não há achado CRITICAL nem HIGH nesta rodada.

## Itens verificados que passaram

### Cobertura
- Os 23 RF do requirements (RF-01 a RF-16, com 07a–c, 09a, 10a, 11a, 11b) têm decisão no roadmap, exceto RF-05
  (A101). Os novos estão cobertos:
  - RF-04 → D-21;
  - RF-09a → D-22;
  - RF-10a → D-23;
  - RF-16 → D-24;
  - RF-07 → D-25.
- As 25 decisões (D-01 a D-25) têm ação. As novas:
  - D-21 → T032, T039, T040;
  - D-22 → T002, T053, T055, T057;
  - D-23 → T040, T056;
  - D-24 → T054, T059–T062;
  - D-25 → T038.
- Os cenários novos estão cobertos: "Distanciador duplo" (D-22, T053, T055) e "Lista de ferragens" (D-24, T054, T059,
  T062). O cenário "Inserir sem vão" agora tem dono (D-21, T032).

### Consistência
- O roadmap cita só identificadores que existem no requirements: RF-01, 11, 14; RN-01, 03–05, 07, 07a–c, 08–10,
  10a, 11–13, 13a, 13b, 14–16.
- O contrato `interfaces/cut-plan-json.md` (2.2.0) aparece no roadmap §7 e em D-24, com ações T060 e T061.
- Termos estáveis: "lista de ferragens", "Distanciador", "Divisória Móvel", "Gavetões/Internas/Blum", "vão alvo",
  "Aplicar". Os nomes em inglês das abas são iguais em RF-14 e D-02.

### Coerência com o legado
- Nenhuma decisão contradiz as regras 🟢 R-01 a R-10 de `_reversa_sdd/domain.md`. O nesting (R-09, R-10) não muda;
  a lista de ferragens é à parte.
- A mudança de contrato é menor e compatível (2.1 → 2.2, major 2, campos opcionais): nenhum contrato externo é
  quebrado.
- Os arquivos citados existem: `cutting/json_exporter.py`, `ui/sidebar_project.py` (005), `customize/props.py`,
  `aggregates/perforate.py`, `standards/previews.py`, `catalog/render_thumbnails.py`. `cutting/hardware.py` e
  `cutting/drilling.py` são novos, declarados no roadmap §5.

### Sanidade do actions
- 62 ações, sem dependência para ID inexistente e sem ciclo.
- Nenhum par `[//]` com o mesmo arquivo alvo.
- Maior cadeia: 11 (T001 → … → T052).
