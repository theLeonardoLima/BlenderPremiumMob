# Roadmap: Janela importada (OBJ) com folhas de correr, agregados por grupo e colisão coerente

> Identificador: `007-janela-obj-folhas-colisao`
> Data: `2026-10-08`
> Requirements: `_reversa_forward/007-janela-obj-folhas-colisao/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A feature é um delta sobre o pacote `caffmob_draw/aggregates/` da 003, em cinco incrementos:

- **I1. Núcleos puros** (sem `bpy`, testados com `unittest`):
  - unidade sugerida pelo tamanho;
  - grupos sugeridos pelo prefixo dos nomes;
  - os limites 1D da folha de correr: posição do arquivo, montante da outra folha, sentido padrão e curso livre.
- **I2. Importação.** `caffmob.import_model` ganha **unidade** (Automática/mm/cm/m/pol) e **eixo vertical** (Z/Y),
  repassados a `wm.obj_import(global_scale, up_axis, forward_axis)`. Na Automática, o modelo entra em escala 1, é
  medido e, se a maior medida passar de 50, é reescalado para mm.
- **I3. Grupo de peças.** Um **objeto de grupo** (Empty com `Object.btm_group`) recebe as peças como filhas. A folha
  da 003 passa a aceitar o grupo: caixa, eixo, trilho e teste de contato saem da **união** das peças. O operador
  **Montar esquadria** sugere os grupos pelo nome, o projetista confirma e o plugin cria a esquadria e as folhas de
  correr num passo.
- **I4. Colisão coerente.**
  - A esquadria da própria janela deixa de ser excluída do teste de contato.
  - A varredura passa a valer nos **dois** sentidos.
  - Ao fechar, a folha também respeita dois batentes calculados: a posição do arquivo e o montante da outra folha.
  - O aviso diz "bateu em" ou "encostou em".
- **I5. Parede.** **Instalar na parede** cria a mesma jaula de janela das janelas de ambiente (`IS_WINDOW_BP`) com as
  medidas da esquadria, corta o vão com `cut_wall` e prende a esquadria nela. **Desinstalar** desfaz.

## 2. Princípios aplicados

`.reversa/principles.md` não existe. Valem as regras do `CLAUDE.md` e os princípios do `PRODUCT.md`:

| Princípio | Como a feature se relaciona | Status |
|---|---|---|
| Consultar o RAG 5.2 | `wm.obj_import(global_scale, up_axis, forward_axis)` (`docs/rag/blender-api/corpus/bpy.ops.wm.md#bpy.ops.wm.obj_import`); Empty como raiz de grupo | respeita |
| Operadores com `UNDO`; handlers com remoção | Montar esquadria, criar/desfazer grupo, instalar/desinstalar: `{'REGISTER', 'UNDO'}`. Nenhum handler novo | respeita |
| Propriedades por atributo; `# type: ignore` | `Object.btm_group`, `Object.btm_window` | respeita |
| Textos pt-BR + en-US | RF-12 | respeita |
| PRODUCT 1: a viewport é o lugar principal | Barra de abertura e contato destacado na vista (overlay da 003) | respeita |
| PRODUCT 3: cada função num lugar | "Montar esquadria" fica junto de Importar e Converter (Inserir/Selecionado da 005), sem duplicar | respeita |
| PRODUCT 5: do projeto à produção | Janela é acessório: fora do plano de corte (RN-11) | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Importação: novas propriedades `unit` (`AUTO`, `MM`, `CM`, `M`, `IN`) e `up_axis` (`Z`, `Y`) em `BTM_OT_ImportModel`. Para OBJ, `global_scale` e `up_axis`/`forward_axis` vão ao `wm.obj_import`. Em `AUTO`, importa em escala 1, mede a caixa e reescala para 0,001 se a maior medida passar de 50 (RN-01). O relatório diz a unidade usada | Medido: hoje entra 1400 m e deitado. O padrão do importador é Y para cima | Ler o LEIA-ME (não é padrão); reescalar só a janela | 🟢 |
| D-02 | Eixo vertical padrão = **Z** | O arquivo de teste e os exportadores de móveis (Promob, SketchUp) usam Z para cima. O Y continua disponível | Padrão Y do Blender | 🟡 |
| D-03 | Grupo de peças = **Empty** "<nome do grupo>" com `Object.btm_group` (`kind`: `FRAME`/`LEAF`/`PLAIN`). As peças viram filhas com a matriz do mundo preservada. Desfazer o grupo devolve cada peça ao pai e à matriz guardados (RN-04) | Mantém nomes, materiais e o vidro à parte, como decidido no clarify (Q4). Pivô e folha da 003 já funcionam com hierarquia | Juntar as malhas (perde as peças, descartado no clarify); coleção (não se move como uma coisa só) | 🟢 |
| D-04 | Sugestão de grupos (puro): agrupa pelo prefixo de **dois tokens** separados por `_` que começa com `Folha`/`Leaf`/`Sash`. O resto vira a esquadria. Resultado no arquivo de teste: 15/15/16 | RN-05; nomes medidos no OBJ | Agrupar por material (o vidro e o perfil da folha ficariam separados); por proximidade (frágil) | 🟡 |
| D-05 | Folha de grupo: `leaf.leaf_box`, `rebuild_pivot` e `collision.Tester` usam a caixa da **união** das peças do grupo (`group_box`). `convert.can_convert` aceita um Empty de grupo `LEAF`. Abrir continua sem tocar em malha | RN-06; hoje tudo lê o `bound_box` de **um** objeto | Converter cada peça em folha (15 pivôs dessincronizados) | 🟢 |
| D-06 | **Montar esquadria** (`caffmob.window_assemble`) num diálogo: lista os grupos sugeridos com a quantidade de peças e o papel (Esquadria, Folha de correr, Folha de giro, Ignorar), editáveis. Ao confirmar: cria o grupo da esquadria, cria as folhas como filhas dela, converte com `motion='SLIDE'`, aplica o sentido padrão (D-08) e o curso livre (D-09) | "Facilmente" (meta de 5 ações, §6 do requirements) | Fazer grupo a grupo à mão (continua possível: "Criar grupo" com a seleção) | 🟡 |
| D-07 | Colisão: em `collision._excluded`, quando o pai da folha é um grupo `FRAME`, as peças da esquadria **não** são excluídas. Saem do teste só a própria folha, o pivô e as **outras folhas** do mesmo grupo (tratadas por D-10) (RN-08) | Hoje pai e filhos do pai nunca são alvo, por isso a folha atravessa a esquadria | Exceção por nome de peça | 🟢 |
| D-08 | Sentido padrão da folha de correr = **para o próprio lado**: o centro da folha comparado ao centro da esquadria (RN-07a). Quando a folga nesse lado for menor que 10% da largura da folha, o painel avisa "Pouco curso para este lado: inverta o sentido" e não muda nada sozinho | Respeita a resposta do titular (Q3) e torna visível o risco medido (2 mm no arquivo) | Trocar o padrão automaticamente (decisão do titular pendente; ver §4) | 🟡 |
| D-09 | Curso = **distância livre** até a esquadria no sentido de abrir, medida pela própria varredura de contato com curso máximo igual à largura da esquadria. O campo `travel` ganha teto dinâmico: valor maior é gravado no máximo (RN-07) | Reaproveita `sweep.sweep` e `Tester` | Calcular pela caixa do marco (depende da forma do perfil) | 🟡 |
| D-10 | Fechar (RN-09): `sweep` ganha o sentido de fechar. A folha para no primeiro de três limites: (a) fração 0, que é a pose do arquivo; (b) o **montante da outra folha**, um limite 1D puro (`slide_limits.close_stop`) que mantém a sobreposição entre os montantes no máximo igual à do arquivo, relativa à posição **atual** da outra folha; (c) contato real com a esquadria do lado oposto, pela varredura | As folhas estão em trilhos distintos e não se tocam em 3D. A sobreposição dos montantes (32 mm no arquivo) é o batente real de uma janela de correr | Colisão 3D entre folhas (nunca acontece); fixar só em (a) | 🟡 |
| D-11 | Aviso e destaque: `contact_name` ganha `contact_kind` (`OPEN`/`CLOSE`). O painel mostra "Folha bateu em <peça>" ou "Folha encostou em <folha>". O overlay da 003 destaca a caixa da peça de contato, que hoje destaca só a folha (RN-10) | 003 RF-17 já desenha o contato | Só texto | 🟢 |
| D-12 | **Instalar na parede** (`caffmob.window_install`): o projetista escolhe a parede (seleção ou clique). O plugin cria `hb_types.GeoNodeCage` com `IS_WINDOW_BP`, Dim X/Z = largura/altura da esquadria e Dim Y = espessura da parede, filho da parede em `(x, 0, peitoril)`. Corta com `cut_wall` (`operators/doors_windows.py:430`, extraído para função de módulo). O grupo da esquadria vira filho da jaula, centrado na espessura. Peitoril padrão = 1,0 m, o mesmo da janela BTM | A jaula `IS_WINDOW_BP` já recebe da parede: deslizar no plano com limite (`set_position_on_wall`), espessura no editor de paredes (`walls2d/apply.py:152`), apagar com a parede (`KEEP_WITH_WALL`) e a colisão de cena da 004 (`collision/scan.py:77`) | Grudar com a 004 (não corta o vão nem limita ao segmento); camada BTM de parede (convertida em HB pelo editor de paredes) | 🟢 |
| D-13 | **Desinstalar** (`caffmob.window_uninstall`): solta o grupo da esquadria na posição do mundo, remove o boolean e apaga a jaula (o mesmo caminho de `delete_door_window`, sem apagar o grupo) | RN-03 | Apagar e reimportar | 🟢 |
| D-14 | Só paredes HB (`IS_WALL_BP`). Parede BTM antiga mostra "Converta a parede pelo editor de paredes" | `walls2d/convert.py` já converte BTM → HB | Suportar as duas | 🟡 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| Sentido padrão "para o próprio lado" mantido; folga < 10% só gera aviso (D-08) | §10 Lacunas (risco físico de RN-07a) | Médio: no arquivo de teste a folha abre 2 mm até o projetista inverter. Se o titular escolher trocar o padrão, muda uma linha em `slide_limits.default_direction` |
| Grupos pelo prefixo de dois tokens (`Folha_Esquerda`) | §10 (RN-05) | Baixo: o diálogo deixa corrigir |
| Peitoril padrão de 1,0 m ao instalar | Inferência (opening_builder) | Baixo: editável |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Importar modelo | `caffmob_draw/aggregates/ops_import.py` | regra-alterada | Unidade e eixo; escala automática |
| Núcleos puros | `caffmob_draw/aggregates/import_units.py`, `grouping.py`, `slide_limits.py` | componente-novo | Unidade sugerida, grupos sugeridos, limites da folha de correr |
| Grupo de peças | `caffmob_draw/aggregates/group.py`, `ops_group.py` | componente-novo | Criar/desfazer grupo, caixa do grupo, Montar esquadria |
| Folha | `caffmob_draw/aggregates/leaf.py`, `convert.py`, `props.py` | regra-alterada | Folha de grupo; fechar com batentes; `contact_kind`; teto do curso |
| Colisão da folha | `caffmob_draw/aggregates/collision.py`, `sweep.py` | regra-alterada | Esquadria conta; varredura nos dois sentidos |
| Overlay e painel | `caffmob_draw/aggregates/overlay.py`, `panels.py` | regra-alterada | Destaque da peça de contato; aviso de sentido; botões novos |
| Janela na parede | `caffmob_draw/aggregates/install.py`; `caffmob_draw/operators/doors_windows.py` (`cut_wall` vira função de módulo) | componente-novo / regra-alterada | Instalar e desinstalar |
| Traduções | `caffmob_draw/data/translations/` | regra-alterada | Textos novos |

## 6. Delta no modelo de dados

- Resumo das mudanças:
  - `Object.btm_group` no Empty de grupo (tipo, peças, matrizes de origem);
  - `Object.btm_window` na jaula instalada (grupo da esquadria, parede);
  - `BTM_PG_Aggregate` ganha `contact_kind`, `free_travel` e `rest_overlap`;
  - `BTM_OT_ImportModel` ganha `unit` e `up_axis`.
- Detalhe completo em: `_reversa_forward/007-janela-obj-folhas-colisao/data-delta.md`

## 7. Delta de contratos externos

Nenhum. O arquivo de módulo do usuário (003/006) não muda: grupos e folhas viajam no `.blend` do módulo salvo.

## 8. Plano de migração

1. Folhas da 003 (uma malha só) continuam funcionando: sem `btm_group`, a caixa é a do próprio objeto.
2. A colisão de fechar só usa os batentes novos (b) e (c) quando o pai é um grupo `FRAME`. Folhas antigas continuam
   com "fechar livre", que era a regra da 003.
3. A importação sem mudar as opções usa `AUTO` + Z. Um arquivo em metros e Z continua entrando igual.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Varredura com 15 peças fica lenta | médio | baixo | A folha é testada como **uma** caixa (a do grupo); os alvos ficam no cache da 003 |
| Falso contato com trilho/guia (1 mm de folga no arquivo) | médio | médio | Encolhimento de 1 mm da 003 mantido; teste de fumaça com o OBJ real (folha a 0% sem contato) |
| Padrão "para o próprio lado" abre 2 mm nesta janela | médio | alto | Aviso visível (D-08) e decisão do titular registrada em §4 |
| `cut_wall` com boolean EXACT fica lento em parede longa | baixo | baixo | Mesmo caminho das janelas de ambiente já em uso |
| Editor de paredes trata a jaula como janela HB e muda `Dim Y` | baixo | alto (desejado) | A esquadria é filha da jaula e centrada por driver/recálculo na espessura; testar no editor de paredes |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] `unittest` dos núcleos novos; `ruff`, `check_api.py` e `test_i18n_coverage` sem erro
- [ ] Fumaça com `inputs/janela_preta_1400mm.obj`:
  - importar em escala e em pé;
  - Montar esquadria com grupos 15/15/16;
  - abrir parando na esquadria;
  - fechar parando na posição do arquivo e no montante da outra folha aberta;
  - instalar e desinstalar numa parede;
  - um passo de desfazer por operação.
- [ ] Fumaças da 003 (agregados e folhas) sem regressão

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-08 | Versão inicial gerada por `/reversa-plan` | reversa |
