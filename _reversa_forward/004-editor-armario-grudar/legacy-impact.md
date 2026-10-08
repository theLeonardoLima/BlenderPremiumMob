# Legacy impact — 004-editor-armario-grudar

> Gerado por `/reversa-coding` em 2026-10-07 (rodada única: T001–T060, todas concluídas).
> Base: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`, as specs por unidade em `_reversa_sdd/<unidade>/` e
> as features 002 e 003.

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `caffmob_draw/stick/` (frame, props, apply, settle, link, magnet, migrate, ops_stick, panels) | Grudar / elemento filho (novo) | componente-novo | MEDIUM | Bloco B: vínculo item → face plana, handler que mantém o item na face, ímã, migração dos módulos que já estão na parede (D-01 a D-11) |
| `caffmob_draw/collision/` (obb, rules, props, scan, stale, overlay, ops_collision, panels) | Colisão de corpo (novo) | componente-novo | MEDIUM | Bloco C: verificação, painel, destaque, desatualizado, afastar até encostar (D-12 a D-19) |
| `caffmob_draw/cabinet_editor/` (elevation, validate, state, props, bridge, window, ops_editor, ops_actions, panels) | Editor de Armário (novo) | componente-novo | MEDIUM | Bloco A: janela própria, vista frontal, rascunho com instantâneos, validação, Confirmar com um passo de desfazer (D-20 a D-27) |
| `caffmob_draw/canvas2d/window.py`, `caffmob_draw/walls2d/window.py` | Editor de Paredes (janela 2D) | regra-alterada | LOW | Mecânica da janela extraída para o comum; `walls2d/window.py` mantém a mesma API pública (D-20) |
| `caffmob_draw/walls2d/history.py` | Editor de Paredes (histórico do rascunho) | regra-alterada | LOW | `History` recebe a função de assinatura; padrão `plan_signature` preservado (D-21) |
| `caffmob_draw/aggregates/limits.py` | Agregados (003) | regra-alterada | LOW | `box_for(..., clamp_to_face=True)`; padrão preservado |
| `caffmob_draw/aggregates/ops_aggregate.py`, `aggregates/convert.py` | Agregados (003): apagar e converter | regra-alterada | MEDIUM | Apagar um hospedeiro solta os elementos filhos no lugar com aviso; converter recusa item grudado (D-07) |
| `caffmob_draw/data/properties.py` | Dados da cena | delta-de-dados | LOW | `btm_settings.stick_migrated`; `collision_override` e `collision_global` passam a ser lidos pela colisão (D-08, D-18) |
| `caffmob_draw/__init__.py` | Registro, preferências, abertura de arquivo | regra-alterada / delta-de-dados | MEDIUM | Preferências `stick_magnet` e `stick_magnet_distance`; registro de `stick`, `collision`, `cabinet_editor`; `load_file_post` chama a migração (D-06, D-08) |
| `caffmob_draw/ui/object_properties.py` | Painel de propriedades (002) | regra-nova | LOW | Botão "Abrir editor de armário" na caixa de dimensões dos módulos (D-27) |
| `caffmob_draw/ui/save_feedback.py` | Aviso ao salvar (003 D-27) | regra-alterada | LOW | `show()` público para avisos de handlers; aviso de colisões pendentes ou não verificadas ao salvar (D-10, D-15) |
| `caffmob_draw/data/translations/editor_grudar.json` | Tradução da interface | regra-nova | LOW | 136 textos novos em pt_BR e en_US |
| `tests/_bootstrap.py`, `tests/test_walls2d_history.py` | Testes | regra-alterada | LOW | Pacotes novos na lista `_stub`; teste do histórico com assinatura própria |

## Diff conceitual por componente

**Grudar (novo).** Um item (módulo, geometria ou malha) pode ser elemento filho de uma face plana de outro objeto. O
vínculo é o parentesco do Blender mais `Object.btm_stick`: o hospedeiro, a face (um lado da caixa local, que acompanha a
medida do hospedeiro, ou um plano fixo para face inclinada), a posição no plano, a distância e o giro. Um handler
`depsgraph_update_post` reposiciona os itens quando a caixa do hospedeiro muda; isso corrige o defeito de espessura de
parede sem tocar no editor de paredes nem nos outros pontos que mudam a espessura. Os movimentos (G nativo,
posicionamento das bibliotecas, mover do plugin) são tratados ao assentar, quando nenhum modal de movimento está
rodando: o item grudado volta ao plano, o módulo novo posto na parede vira elemento filho dela, o ímã gruda módulos e
geometrias soltos perto de uma face e a colisão de quem se moveu é verificada. Ao abrir um arquivo, os módulos filhos
de parede ganham o vínculo na face em que já estão, sem mover nada.

**Colisão de corpo (novo).** Núcleo puro (caixas orientadas, regras de pares, classificação e ordem estável) e uma
varredura que confirma pela malha avaliada os pares com parede, obstáculo, abertura ou malha solta (os vãos de porta e
janela não geram falsa colisão). Resultado em `WindowManager.btm_collision`, com marca de desatualizado, painel com Ir
para e Afastar até encostar, destaque na viewport e aviso ao salvar. A interferência de frentes da 001 continua igual e
cobre a área de abertura.

**Editor de Armário (novo).** Janela própria no molde do editor de paredes. O módulo é editado ao vivo pelos adaptadores
da 003; o rascunho é uma pilha de instantâneos (medidas + personalização + valores crus de `btm_custom`). As edições
rodam dentro do modal com `UNDO`, então os operadores das bibliotecas não criam passos próprios; Confirmar cria um único
passo e Cancelar reaplica o instantâneo inicial.

**Editor de Paredes, agregados, interface (alterações pequenas).** Extração da janela comum e do histórico genérico,
sem mudança visível; apagar hospedeiro e converter passam a respeitar os elementos filhos; botão do editor de armário
no painel de propriedades; aviso de colisões ao salvar.

## Preservadas

Regras 🟢 de `_reversa_sdd/domain.md` que continuam intactas:

- R-01 Dependência do Piso; R-02 Ajuste Conformal de Piso; R-03 Sentido de Orientação de Paredes.
- R-04 Aderência ao Segmento (aberturas); R-05 Movimento Constrangido; R-06 Clamping de Limites; R-07 Transição entre
  Segmentos; R-08 Sill Fixo de Portas.
- R-09 Precedência de Área; R-10 Corte Guilhotinado.

E das specs por unidade: `_reversa_sdd/hb_placement/requirements.md` RN-09..RN-25 (vão livre, encosto
gabinete-a-gabinete, snap de ponto) não foram tocadas; o posicionamento das bibliotecas continua igual.

## Modificadas

Nenhuma regra 🟢 de `_reversa_sdd/domain.md` foi alterada ou removida. A feature amplia comportamentos confirmados de
features anteriores e do código, acompanhados em `regression-watch.md`:

- Módulo posto na parede: antes, filho da parede com Y local fixo; agora também elemento filho com vínculo à face, que
  acompanha espessura e comprimento (`product_libraries/*/operators/ops_placement.py`, `walls2d/apply.py`).
- Apagar o pai (003 RF-12): agora também solta os elementos filhos grudados no lugar.
- "Evitar Sobreposição" (`btm_settings.collision_global`): agora também liga e desliga a verificação de colisão.
- Tolerância de contato de 1 mm (`inspection/interference.py`): agora vale também para a colisão de corpo.
- Aviso ao salvar (003 D-27): agora inclui as colisões pendentes.
