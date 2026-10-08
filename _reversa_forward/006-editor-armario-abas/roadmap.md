# Roadmap: Editor de armário reformulado em abas (Estrutura e Divisão)

> Identificador: `006-editor-armario-abas`
> Data: `2026-10-08`
> Requirements: `_reversa_forward/006-editor-armario-abas/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Quatro incrementos, cada um com teste fora do Blender (núcleos puros) e teste de fumaça no Blender:

- **I1. Núcleos puros.** Dois módulos sem `bpy`, que fazem toda a conta da feature e são testados com `pytest`:
  - `cabinet_editor/divisions.py`: árvore de subvãos com corte guilhotinado, medidas da chapa, recuos, posição e
    validação;
  - `cabinet_editor/structure.py`: componentes externos, os três modos de remoção e a conta das medidas.
- **I2. Abas e Divisão.**
  - O editor ganha uma linha de abas (`UILayout.prop_tabs_enum`) e os painéis da 004 passam a aparecer conforme a aba.
  - As divisões são **objetos nossos**: uma chapa (`CabinetPart`, a mesma peça das bibliotecas) filha da raiz, com
    os dados em `Object.btm_division`. Isso vale igual para as quatro bibliotecas, não depende do interior de cada uma
    e entra no plano de corte pelo caminho que já existe.
- **I3. Estrutura.** Lista dos componentes externos com material, espessura, Remover e Restaurar:
  - o modo **Manter tudo** vale para as quatro bibliotecas;
  - **Estender as vizinhas** e **Reduzir o armário** valem onde a biblioteca permite e aparecem desabilitados, com o
    motivo, onde não permite (RN-07).
- **I4. Produção e persistência.**
  - Plano de corte: divisões entram e componentes removidos saem, inclusive no módulo `btm`, cuja lista hoje é
    sintética.
  - "Salvar como módulo" passa a levar Estrutura e Divisão.
  - Depois de qualquer reconstrução da biblioteca, as divisões são reposicionadas.

Antes de codificar os painéis do I2 e do I3, roda-se uma passada de desenho com `/impeccable`, restrita a `UILayout`.

## 2. Princípios aplicados

`.reversa/principles.md` não existe. Valem as regras do `CLAUDE.md` e os princípios do `PRODUCT.md`:

| Princípio | Como a feature se relaciona | Status |
|---|---|---|
| Consultar o RAG 5.2 | Abas com `UILayout.prop_tabs_enum` (`docs/rag/blender-api/corpus/bpy.types.UILayout.md#bpy.types.UILayout.prop_tabs_enum`). Handler `depsgraph_update_post` a confirmar na codificação | respeita |
| Handlers com remoção em todos os caminhos; `@persistent` | O handler de reposicionamento (D-09) é removido no `unregister()` | respeita |
| Propriedades por atributo; `# type: ignore` | `Object.btm_division` e `Object.btm_structure` | respeita |
| Textos pt-BR + en-US | Abas, rótulos e mensagens novas (RF-17) | respeita |
| Só `caffmob_draw/` | Bibliotecas tocadas apenas em ganchos pontuais (D-07, D-08) | respeita |
| PRODUCT 2: convenções do Blender | Abas nativas do `UILayout`, sem desenho próprio de interface | respeita |
| PRODUCT 3: cada função num lugar | A aba Divisão também recebe "Distribuir por quantidade" (o "Divisões internas…" da 003), para que divisões fiquem num só lugar (D-02) | respeita |
| PRODUCT 5: do projeto à produção | **Conflito herdado:** módulos face frame **não entram no plano de corte hoje** (`cutting/part_sources.py:17-18, 74-90`). Divisões e remoções em face frame aparecem no 3D mas não chegam à produção. A feature não corrige essa lacuna e avisa na aba (D-12) | conflita |
| Acessibilidade: estado em texto | "Removido", "alterado neste armário" e subvão escolhido aparecem em texto, não só em cor | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Abas = `WindowManager.btm_cabinet_editor.tab` (Enum `STRUCTURE`, `DIVISIONS`, `FINISH`) desenhada com `prop_tabs_enum` num painel cabeçalho (`bl_order` 0). Os painéis existentes testam a aba no `poll` | Abas nativas do Blender, sem modal novo | Categorias separadas no N-panel (o usuário perde o contexto); um painel único com `if` gigante | 🟢 |
| D-02 | Distribuição das funções. **Estrutura:** Medidas, Componentes externos. **Divisão:** opções e Adicionar, lista de divisões, "Distribuir por quantidade" (o antigo "Divisões internas…"). **Acabamento:** lista de componentes da 004, Frentes, Puxadores, Materiais. **Sempre visíveis:** Mensagens (resumo), Ajustes automáticos (recolhido), Desfazer/Refazer, Confirmar/Cancelar/Fechar, Salvar como módulo | RF-02, RF-03 e PRODUCT 3. O nome "Acabamento" é provisório e fica para o `/impeccable` | Deixar Frentes etc. fora das abas | 🟡 |
| D-03 | Divisão = objeto `CabinetPart` (`hb_types.GeoNodeCutpart`) filho da raiz do módulo, nome "Divisória N", com `Object.btm_division` e `btm_component='DIV'` | Mesmo objeto de peça das bibliotecas: aparece no editor, no 3D e no plano de corte. Nenhuma biblioteca tem divisão com recuo nem por subvão (frameless e closets dividem sem recuo; o face frame ignora alturas) | Usar o interior de cada biblioteca (quatro implementações e sem recuo); agregado da 003 (preso à face **externa**, não ao vão) | 🟢 |
| D-04 | Subvãos = árvore guilhotinada pura. Cada **espaço-raiz** vem do adaptador (`inner_spaces(root)`): frameless = jaulas de bay; closets = jaulas de abertura por bay; face frame = `bay_cage_dims`; `btm` = caixa interna implícita. Cada divisão corta um subvão-folha em dois, e o caminho estável é `s0`, `s0.a`, `s0.b`… | Atende RN-09: a divisão ocupa o subvão inteiro. A posição fica relativa à face esquerda ou de baixo (RN-11, RN-16) | Calcular o vão subtraindo as peças da caixa (frágil com rodapé, travessas e quinas) | 🟡 |
| D-05 | Medidas da chapa (puro): vertical = altura do subvão × (profundidade − recuo frente − recuo trás) × espessura; horizontal = largura × (profundidade − recuos) × espessura. A posição nova é o meio do subvão. Valida subvão ≥ 50 mm (`DIV-001`) e profundidade ≥ 50 mm (`DIV-002`), as duas como erro | RN-09, RN-11, RN-13, RN-14 | — | 🟢 |
| D-06 | Material e espessura da divisão: `standards.api.get_value(scene, sheet_key(line, 'DIV', 'material'/'thickness'))`, com `line = root['btm_line']` (padrão por biblioteca, `standards/sync.py:_tag_lines`). O acabamento visual segue o grupo `INTERNO` (`customize/adapters/common.apply_group_materials`). O plano de corte já pega material e fitas do padrão por componente (`cutting/part_extractor.py:44-69`) | RN-10: o que está ativo no Configurador vale sozinho | Material próprio da biblioteca | 🟢 |
| D-07 | Remoção (modo **Manter tudo**) = esconder a peça (`hide_viewport` + `hide_render`) e gravar `removed` em `Object.btm_structure` da raiz. Onde a biblioteca já dirige o esconder por driver (frameless: Bottom, Top, Toe Kick, travessas), a expressão ganha `or btm_removed`. Closets e face frame reescrevem o esconder no recálculo, então a remoção é reafirmada em `after_rebuild` | O plano de corte já ignora peça escondida (`cutting/part_sources.py:104-108`) | Apagar o objeto (a biblioteca o recria); `make_part_editable` do face frame (tira a peça do recálculo para sempre) | 🟡 |
| D-08 | Modos **Estender** e **Reduzir** por capacidade do adaptador (`structure_caps(root)`). **`btm`:** os três modos em todas as peças, com `generate_cabinet_mesh` recebendo quais painéis gerar e as espessuras por componente. **Frameless:** base com "Estender" = `Remove Bottom` nativo, que já baixa o bay e alonga o fundo. **Demais casos:** desabilitado com o motivo | Só o `btm` (malha gerada por código) e a base do frameless têm conta de vizinhança. Fazer isso nas outras exige mexer no solver de cada biblioteca | Implementar Estender e Reduzir genérico movendo peças (quebra os drivers e o solver no próximo recálculo) | 🔴 |
| D-09 | Espessura por componente. **`btm`:** campos por componente novos. **Frameless, closets e face frame:** a sobrescrita grava no `Thickness` da peça (tirando o driver no frameless) e é reafirmada em `after_rebuild`. A face externa fica parada e a peça cresce para dentro; o vão interno é recalculado pelas peças e as divisões são reposicionadas. Material por componente usa o `btm_custom.material` da 003 (já existe) | RN-05: o valor vale só para este armário. As bibliotecas grandes têm uma espessura só para a caixa | Mudar a espessura geral da caixa (afeta todas as peças) | 🟡 |
| D-10 | Reposicionar divisões: `divisions.reflow(root)` roda (a) no editor após cada mudança, (b) em `customize/reapply.after_rebuild` (já chamado pelas quatro bibliotecas) e (c) num `depsgraph_update_post` `@persistent` que compara a assinatura dos espaços-raiz dos módulos com divisões (o frameless muda medidas por driver, sem `after_rebuild`) | RN-16: as divisões acompanham o vão | Drivers em cada divisão (subvão aninhado vira expressão gigante) | 🟡 |
| D-11 | Rascunho: `EditorState` ganha `structure` e `divisions` (dicionários). `bridge.read_state` e `apply_state` leem e reaplicam os dois, e `signature` os inclui. Cancelar, desfazer e um único passo de desfazer continuam iguais | RN-02 e 004 RN-01 | Desfazer próprio para a aba Divisão | 🟢 |
| D-12 | Plano de corte. `part_roles.classify` respeita `btm_component` antes do nome. `cutpart_records` já pega as divisões de frameless e closets. No `btm`, `synthetic_records` deixa de listar componente removido, usa as espessuras por componente e soma as divisões filhas. Face frame continua fora (lacuna herdada) e a aba mostra "Face frame ainda não entra no plano de corte" | RF-15 e PRODUCT 5 | Incluir o face frame no plano de corte (outra feature) | 🟢 |
| D-13 | Escolher o subvão: clique na vista frontal sobre a área livre (o subvão é destacado e o nome aparece em texto) ou lista suspensa na aba Divisão. Com um subvão só, ele vem escolhido | RN-09; clique já existe na vista (`ops_editor._handle_click`) | Só lista (pouco visual) | 🟡 |
| D-14 | Opções da próxima divisão (`orientation`, `use_front`, `front`, `use_back`, `back`, com 20 mm de padrão) em `WindowManager.btm_cabinet_editor`, lembradas enquanto o editor está aberto (RN-08) | Não são dado do módulo | Guardar no módulo | 🟢 |
| D-15 | "Salvar como módulo": o manifesto ganha `structure` e `divisions` como campos **opcionais**, e `schema_version` vai a `1.1.0`. Leitores 1.0 ignoram o que não conhecem | Compatível com arquivos já salvos (`interfaces/user-module-file.md`) | Versão 2.0 (quebraria arquivos existentes) | 🟢 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| Recuo padrão = 20 mm | §10 Lacunas (RN-13) | Baixo: é uma constante |
| Subvão mínimo = 50 mm | §10 Lacunas (RN-14) | Baixo: constante em `divisions.py` |
| Estender e Reduzir só no `btm` e na base do frameless; nas demais peças e bibliotecas aparecem desabilitados com o motivo | Pedido do titular "3C com opção para A e B" + RN-07 | **Médio:** o titular pode esperar os três modos em todas as bibliotecas. Isso precisa de aval antes do `/reversa-to-do` ou de uma feature seguinte por biblioteca |
| Divisões e remoções em face frame não chegam ao plano de corte | RF-15 | Médio: limitação herdada, avisada na interface |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Editor de armário: painéis | `caffmob_draw/cabinet_editor/panels.py` | regra-alterada | Linha de abas e `poll` por aba; painéis novos Componentes externos, Divisão e Distribuir por quantidade |
| Editor de armário: núcleo de divisões | `caffmob_draw/cabinet_editor/divisions.py` | componente-novo | Árvore de subvãos, medidas, recuos, validação (puro) |
| Editor de armário: núcleo da estrutura | `caffmob_draw/cabinet_editor/structure.py` | componente-novo | Componentes externos e modos de remoção (puro) |
| Editor de armário: cena | `caffmob_draw/cabinet_editor/bridge.py`, `scene_divisions.py` (novo) | regra-alterada / componente-novo | Ler, criar, mover e apagar objetos de divisão; aplicar remoção e espessura |
| Editor de armário: estado e operadores | `cabinet_editor/state.py`, `props.py`, `ops_actions.py`, `ops_editor.py`, `window.py` | regra-alterada | Estado com estrutura e divisões; pedidos novos; clique escolhe subvão; desenho do subvão |
| Adaptadores da 003 | `caffmob_draw/customize/adapters/*.py` | contrato-alterado (interno) | Novos `inner_spaces`, `structure_parts`, `structure_caps`, `remove_part`, `restore_part`, `set_part_thickness` |
| Reaplicar | `caffmob_draw/customize/reapply.py` | regra-alterada | `has_custom` considera estrutura e divisões; `after_rebuild` reafirma remoções e chama `reflow` |
| Módulo `btm` | `caffmob_draw/geometry/mesh_gen.py`, `data/properties.py` | regra-alterada | Painéis opcionais e espessura por componente |
| Plano de corte | `caffmob_draw/cutting/part_roles.py`, `part_sources.py` | regra-alterada | `btm_component` explícito; registros do `btm` com remoções e divisões |
| Manifesto do módulo salvo | `caffmob_draw/customize/manifest.py`, `library_io.py` | contrato-alterado | Campos opcionais `structure` e `divisions` (1.1.0) |
| Traduções | `caffmob_draw/data/translations/` | regra-alterada | Textos novos pt-BR/en-US |

## 6. Delta no modelo de dados

- Resumo das mudanças:
  - `Object.btm_structure` na raiz: um item por componente externo, com removido, modo, espessura e material
    sobrescritos;
  - `Object.btm_division` em cada objeto de divisão: subvão, orientação, posição, recuos e sobrescritas;
  - campos da aba no `WindowManager`;
  - `EditorState` com `structure` e `divisions`;
  - `BTM_PG_CabinetProperties` com painéis opcionais e espessuras por componente;
  - manifesto 1.1.0.
- Detalhe completo em: `_reversa_forward/006-editor-armario-abas/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Arquivo de módulo do usuário (`caffmob_draw.user-module`) | arquivo | `_reversa_forward/006-editor-armario-abas/interfaces/user-module-file.md` |

## 8. Plano de migração

1. Projetos antigos: sem `btm_structure` nem divisões. Ler a ausência como "nada removido, nenhuma divisão". Nenhuma
   migração ativa.
2. Módulo `btm` antigo: os campos novos têm padrão "todos os painéis presentes" e espessura por componente vazia (vale
   `thickness`), então a malha sai idêntica.
3. Manifestos 1.0.0 continuam válidos. Os de 1.1.0 abertos numa versão antiga perdem só a estrutura e as divisões.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| O recálculo das bibliotecas desfaz a remoção ou a espessura sobrescrita | alto | médio | Reafirmar em `after_rebuild` e no handler de D-10. A fumaça muda a largura, recalcula e confere |
| Divisão nossa sobrepõe o interior próprio da biblioteca (prateleiras, divisórias da 003, cubbies) | médio | alto | `GEO-002` já acusa sobreposição. A aba Divisão avisa quando o subvão tem interior da biblioteca |
| Handler `depsgraph_update_post` pesado em cena grande | médio | médio | Só módulos com divisão; assinatura barata (caixas dos espaços-raiz); sem trabalho quando a assinatura não muda |
| Espessura maior empurra a peça para dentro e colide com peças internas | médio | médio | Mensagem `STR-002` (aviso) e Ajustes automáticos mostram o que mudou |
| Expressão de driver do frameless editada por nós quebrar em versão futura da biblioteca | baixo | baixo | Teste de fumaça com Remove Bottom + remoção nossa na mesma peça |
| Face frame sem plano de corte confundir o usuário | médio | alto | Aviso fixo na aba Divisão e na Estrutura para módulos face frame |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] `pytest` dos núcleos `divisions` e `structure` passando; `ruff` e `check_api.py` sem erro
- [ ] Fumaça no Blender com as quatro bibliotecas: abas, adicionar/mover/remover divisão, remover/restaurar componente,
      Cancelar, Confirmar = um desfazer, plano de corte e reabrir o `.blend`
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-08 | Versão inicial gerada por `/reversa-plan` | reversa |
