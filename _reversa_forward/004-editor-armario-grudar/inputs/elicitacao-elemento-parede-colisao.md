# Elicitação de Requisitos — Elemento Preso à Parede e Colisão

**Produto nominal:** Promob Plus Enterprise 5.60.46.6  
**Contexto:** ELÊ DE AMBIENTES  
**Arquivo analisado:** `elemento grudado na parede e colisãoELÊDE AMBIENTES - Promob Plus Enterprise - 5.60.46.6 2026-10-07 14-13-48.mp4`  
**Tamanho identificado:** aproximadamente 129,31 MB  
**Versão:** 1.0  
**Escopo:** especificar o comportamento de elementos posicionados junto a paredes e o tratamento de colisões em um ambiente de móveis planejados.

> **Nota de evidência.** O arquivo foi localizado, mas a decodificação quadro a quadro continua indisponível neste ambiente. Portanto, apenas o tema nominal do vídeo e o contexto do produto são tratados como evidência direta. Os comportamentos geométricos descritos abaixo são requisitos de engenharia e hipóteses de paridade, marcados como **CONFIRMADO**, **INFERIDO** ou **LACUNA**. Nenhum rótulo, ícone, atalho, coordenada ou mensagem visual é inventado como fato observado.

---

## 1. Legenda de confiança

- 🟢 **CONFIRMADO** — consta diretamente no nome do arquivo ou no contexto fornecido.
- 🟡 **INFERIDO** — comportamento necessário/esperado para implementar o domínio de forma consistente.
- 🔴 **LACUNA** — depende de inspeção do vídeo, teste no Promob ou decisão do responsável pelo produto.

---

## 2. Fatos disponíveis e hipótese central

### 2.1 Evidências confirmadas

- 🟢 O vídeo trata de um **elemento grudado na parede**.
- 🟢 O vídeo trata de **colisão**.
- 🟢 O contexto é o Promob Plus Enterprise 5.60.46.6.
- 🟢 O contexto empresarial é ELÊ DE AMBIENTES.
- 🔴 Não foi possível confirmar se “grudado” significa encaixe automático, restrição de movimento, alinhamento visual, vínculo topológico ou apenas proximidade.
- 🔴 Não foi possível confirmar se a colisão é apenas exibida, bloqueia a operação, corrige automaticamente a posição ou gera uma mensagem.

### 2.2 Hipótese de produto

🟡 O sistema permite inserir ou mover um componente em um ambiente com paredes e deve decidir, a cada alteração geométrica, se o elemento:

1. está livre;
2. está apoiado/encostado em uma parede;
3. está vinculado a uma parede;
4. está penetrando uma parede;
5. está colidindo com outro objeto;
6. está simultaneamente encostado e em conflito;
7. pode ser reposicionado automaticamente;
8. deve permanecer inválido até correção manual.

---

## 3. Objetivo de negócio

O usuário deve conseguir posicionar móveis e componentes no ambiente com previsibilidade espacial, mantendo o relacionamento desejado com paredes e evitando que objetos ocupem o mesmo espaço físico de forma silenciosa.

O sistema deve:

- preservar a intenção de posicionamento do usuário;
- reconhecer paredes como elementos geométricos de referência;
- distinguir contato válido de penetração inválida;
- detectar colisões entre objetos relevantes;
- informar a causa e os envolvidos;
- evitar correções automáticas inesperadas;
- permitir corrigir, ignorar quando permitido ou revisar o conflito;
- manter a visualização, o modelo geométrico e os dados persistidos sincronizados.

---

## 4. Conceitos e definições

| Conceito | Definição operacional |
|---|---|
| Elemento | Objeto posicionável: armário, módulo, eletrodoméstico, acessório, painel, porta, prateleira ou componente de catálogo. |
| Parede | Superfície ou entidade arquitetônica que delimita o ambiente e pode servir como referência de posicionamento. |
| Contato | Relação entre volumes/superfícies com distância dentro da tolerância permitida, sem penetração proibida. |
| Elemento grudado | Elemento com posição ajustada à parede e, possivelmente, vínculo persistente que mantém o alinhamento durante alterações. 🟡 |
| Snap | Ajuste automático do elemento para uma posição/alinhamento de referência. 🟡 |
| Colisão | Interseção proibida entre volumes ou superfícies de entidades. |
| Penetração | Interseção de um elemento com a geometria da parede ou de outro elemento. |
| Folga | Distância mínima requerida entre elementos, parede, piso, teto ou área de circulação. |
| Tolerância | Margem numérica usada para não classificar como colisão diferenças decorrentes de precisão computacional. |
| Colisão ignorável | Interseção permitida por regra de catálogo, grupo ou contexto. 🟡 |
| Colisão bloqueante | Interseção que impede confirmação/salvamento ou uma operação específica. 🟡 |
| Resolver | Ação que elimina o conflito por deslocamento, redimensionamento, remoção, alteração de regra ou decisão explícita. |

---

## 5. Atores

| Ator | Ações | Confiança |
|---|---|---|
| Projetista | Inserir, mover, girar, encostar, afastar, editar e validar elementos | 🟡 |
| Revisor | Conferir conflitos, folgas e aderência à parede | 🔴 |
| Administrador de catálogo | Definir faces de encaixe, tolerâncias, regras e exceções | 🔴 |
| Motor geométrico | Calcular contatos, interseções, folgas e atualizações | 🟡 |

---

## 6. Modelo textual da experiência

A interface deve ser compreensível sem imagem por meio de quatro áreas funcionais:

1. **Canvas/ambiente**
   - paredes, piso, teto e objetos;
   - seleção do elemento;
   - manipuladores de mover/girar;
   - indicação de contato e colisão;
   - atualização após cada operação.

2. **Propriedades do elemento**
   - posição X, Y, Z;
   - rotação;
   - largura, altura, profundidade;
   - referência de parede, se houver;
   - distância/folga à parede;
   - estado de colisão;
   - modo de posicionamento: livre, alinhado, grudado ou bloqueado.

3. **Painel de conflitos**
   - severidade;
   - elemento principal;
   - elemento conflitante;
   - tipo de conflito;
   - medida da interseção/folga;
   - ação sugerida;
   - status resolvido/não resolvido.

4. **Ações de posicionamento**
   - mover;
   - alinhar à parede;
   - fixar/desfixar vínculo;
   - aplicar snap;
   - manter distância;
   - desfazer/refazer;
   - validar ambiente;
   - salvar.

Os nomes exatos permanecem 🔴 lacuna; os significados são os contratos funcionais desta especificação.

---

## 7. Requisitos funcionais

### RF-PAREDE-001 — Reconhecer paredes

🟡 O sistema deve identificar paredes válidas no ambiente e disponibilizar suas superfícies, faces e orientação para operações de posicionamento.

**Aceite:** uma parede possui identidade estável, geometria consultável e normal/orientação determinística.

### RF-PAREDE-002 — Inserir elemento no ambiente

🟡 Ao inserir um elemento, o sistema deve determinar sua posição inicial e validar sua relação com paredes, piso, teto e objetos existentes.

**Aceite:** o elemento não pode aparecer em posição semântica desconhecida; seu estado geométrico deve ser calculável imediatamente ou permanecer como “processando”.

### RF-PAREDE-003 — Mover elemento

🟡 O usuário deve poder mover um elemento por manipulação direta e/ou por campos numéricos.

**Regras:**

- a operação deve preservar a identidade do elemento;
- a posição final deve ser normalizada conforme precisão do motor;
- o sistema deve recalcular contatos e colisões;
- o sistema deve informar se o objeto foi ajustado automaticamente.

### RF-PAREDE-004 — Encostar elemento na parede

🟡 O sistema deve permitir posicionar um elemento encostado ou alinhado a uma parede quando o tipo de elemento e o catálogo permitirem.

**Aceite:** o contato deve respeitar a face configurada, a orientação e a folga mínima aplicável.

### RF-PAREDE-005 — Fixar vínculo à parede

🟡 O usuário deve poder transformar um contato momentâneo em vínculo persistente, se essa função existir.

O vínculo deve registrar:

- `elementoId`;
- `paredeId`;
- face de referência;
- offset lateral/vertical;
- distância da face;
- orientação relativa;
- política diante de alteração da parede.

🔴 Confirmar no vídeo se “grudado” é vínculo persistente ou somente snap.

### RF-PAREDE-006 — Desfazer vínculo

🟡 O usuário deve poder liberar um elemento grudado, retornando-o ao modo livre sem perder sua posição atual, salvo regra explícita diferente.

### RF-PAREDE-007 — Ajustar automaticamente ao mover a parede

🟡 Se houver vínculo persistente, mover, girar ou redimensionar a parede deve atualizar o elemento segundo a política do vínculo.

Possíveis políticas a configurar:

- manter contato;
- manter offset;
- manter coordenada absoluta;
- desacoplar e gerar aviso;
- impedir alteração da parede.

A política real é 🔴 lacuna.

### RF-PAREDE-008 — Detectar contato válido

🟡 O sistema deve distinguir contato válido de penetração. Um contato válido não pode ser classificado como colisão apenas por erro de arredondamento.

### RF-COL-001 — Detectar colisão entre elementos

🟢 O domínio do vídeo inclui colisão. 🟡 O sistema deve calcular interseção entre elementos sujeitos à regra de colisão.

O resultado deve identificar:

- elementos envolvidos;
- volume ou região de interseção;
- instante da detecção;
- regra violada;
- severidade;
- resolvido/não resolvido.

### RF-COL-002 — Detectar penetração em parede

🟡 O sistema deve verificar se o volume do elemento penetra a parede além da tolerância permitida.

### RF-COL-003 — Classificar colisões

🟡 Cada ocorrência deve ser classificada, no mínimo, como:

- colisão entre elementos;
- penetração em parede;
- folga insuficiente;
- contato permitido;
- sobreposição intencional;
- conflito de área de abertura;
- conflito de circulação;
- conflito com piso/teto;
- conflito desconhecido.

A lista efetivamente usada pelo produto é 🔴 lacuna.

### RF-COL-004 — Indicar conflito

🟡 O sistema deve indicar o conflito no canvas, no painel textual ou em ambos, sem depender exclusivamente de cor.

A indicação deve permitir localizar o elemento e compreender a causa.

### RF-COL-005 — Impedir ação inválida

🟡 Quando a regra for bloqueante, o sistema deve impedir confirmação/salvamento ou concluir a operação mantendo o item em estado inválido, conforme política definida.

O produto deve escolher uma política consistente; não pode bloquear silenciosamente.

### RF-COL-006 — Resolver por afastamento

🟡 O usuário deve poder afastar um elemento da parede ou de outro objeto, informando distância ou usando manipulação direta.

### RF-COL-007 — Resolver por snap

🟡 Se houver snap, o sistema deve oferecer uma posição candidata e mostrar o deslocamento aplicado antes de confirmar ou tornar a alteração efetiva.

### RF-COL-008 — Resolver por deslocamento automático

🟡 Uma correção automática só pode ocorrer se estiver configurada e deve registrar:

- posição original;
- posição corrigida;
- motivo;
- regra usada;
- possibilidade de desfazer.

### RF-COL-009 — Aceitar exceção controlada

🟡 Se certas colisões forem permitidas, o usuário deve conseguir distingui-las de erros e visualizar a justificativa da exceção.

### RF-COL-010 — Validar ambiente completo

🟡 O sistema deve oferecer validação global de todas as paredes, elementos, aberturas e regras geométricas do ambiente.

### RF-COL-011 — Validar elemento selecionado

🟡 O sistema deve permitir validar somente o elemento selecionado e suas relações relevantes para resposta rápida.

### RF-COL-012 — Persistir estado de colisão

🟡 O estado da colisão deve ser recalculável e, quando necessário, persistido com a versão do motor geométrico e do catálogo.

### RF-COL-013 — Desfazer e refazer

🟡 Mover, grudar, desgrudar, snap, resolver colisão e alteração automática devem ser operações reversíveis.

### RF-COL-014 — Evitar perda de dados

🟡 Alterações de posição ou vínculo não salvas devem ser protegidas no fechamento, troca de ambiente ou troca de seleção.

### RF-COL-015 — Salvar configuração

🟡 O salvamento deve informar se existem conflitos bloqueantes, avisos ou exceções aceitas. Nunca deve declarar uma configuração “sem colisões” se a validação estiver desatualizada.

---

## 8. Regras de negócio geométricas

### RN-GEO-001 — Identidade estável

Cada parede e elemento deve ter ID estável. Posição, rotação e vínculo não podem ser associados apenas à ordem visual ou ao índice da lista.

### RN-GEO-002 — Sistema de coordenadas

🟡 Deve existir um sistema de coordenadas documentado para ambiente, parede e elemento. Posição e orientação devem informar o referencial utilizado.

🔴 Confirmar origem, eixos, unidade e convenção angular do produto observado.

### RN-GEO-003 — Faces de parede

Uma parede deve expor ao menos uma face de referência; paredes com espessura devem distinguir face interna, face externa e plano central quando aplicável.

### RN-GEO-004 — Tolerância

A classificação deve usar tolerância configurável e versionada. A tolerância não pode variar de modo imprevisível entre visualização, validação e salvamento.

### RN-GEO-005 — Contato não é colisão

Encostar exatamente na face de uma parede não deve ser reportado como penetração, desde que a folga mínima e a regra do elemento permitam contato.

### RN-GEO-006 — Penetração proibida

Se o volume do elemento atravessar a parede além da tolerância, deve existir conflito identificável e o elemento não pode ser considerado validamente grudado.

### RN-GEO-007 — Folga mínima

A distância mínima deve ser específica por elemento, face, ferragem, abertura e contexto quando necessário. Uma tolerância numérica não substitui uma folga de uso.

### RN-GEO-008 — Área de abertura

Portas, gavetas e componentes móveis devem ser avaliados também em sua área de abertura, não apenas no volume fechado.

🔴 Confirmar se o vídeo mostra portas/gavetas ou somente caixas/módulos.

### RN-GEO-009 — Colisão entre elementos

Dois elementos devem gerar conflito quando suas geometrias válidas se sobrepõem além da tolerância e a combinação não estiver explicitamente permitida.

### RN-GEO-010 — Colisão com a própria estrutura

Componentes pertencentes ao mesmo conjunto podem ter sobreposições de fabricação intencionais. O catálogo deve declarar pares permitidos e não permitir que a regra genérica os marque como erro.

### RN-GEO-011 — Prioridade de conflitos

Quando vários conflitos ocorrerem, a ordenação deve ser determinística. Recomenda-se: erro de geometria estrutural → penetração em parede → colisão física → folga insuficiente → aviso visual.

A prioridade real é 🔴 lacuna.

### RN-GEO-012 — Uma causa, uma mensagem

O sistema deve evitar dezenas de mensagens duplicadas para a mesma causa geométrica. Deve agrupar a ocorrência e listar entidades envolvidas.

### RN-GEO-013 — Alteração automática transparente

Nenhum deslocamento, giro, recorte, redimensionamento ou des vínculo automático pode ocorrer sem registro visível ou histórico consultável.

### RN-GEO-014 — Persistência de vínculo

Um elemento só deve continuar “grudado” após reabrir o projeto se o vínculo tiver sido persistido; proximidade visual isolada não deve ser interpretada como vínculo.

### RN-GEO-015 — Mudança de parede

Se uma parede for apagada, dividida, unida, invertida ou redimensionada, os elementos vinculados devem ser reavaliados e apresentados em estado de conflito quando a relação não puder ser preservada.

---

## 9. Estados do elemento

```text
LIVRE
  -> SELECIONADO
  -> MOVENDO
  -> EM_CONTATO
  -> GRUDADO
  -> EM_CONFLITO
  -> VALIDADO

MOVENDO -> EM_CONTATO       quando alcança a face dentro da tolerância
MOVENDO -> EM_CONFLITO      quando invade parede ou outro elemento
EM_CONTATO -> GRUDADO       ao confirmar vínculo persistente
GRUDADO -> LIVRE            ao desfazer vínculo
GRUDADO -> EM_CONFLITO      se parede/elemento relacionado mudar
EM_CONFLITO -> VALIDADO     após correção e nova validação
EM_CONFLITO -> EXCEÇÃO      se regra permitir aceitar a ocorrência
EXCEÇÃO -> EM_CONFLITO      se a condição da exceção deixar de ser válida
```

### Estados da ocorrência

- `NÃO_AVALIADA`
- `EM_PROCESSAMENTO`
- `SEM_CONFLITO`
- `CONTATO_PERMITIDO`
- `AVISO`
- `CONFLITO_NÃO_BLOQUEANTE`
- `CONFLITO_BLOQUEANTE`
- `EXCEÇÃO_ACEITA`
- `RESOLVIDA`
- `OBSOLETA`
- `ERRO_DE_CÁLCULO`

---

## 10. Contrato de dados

### 10.1 Parede

```json
{
  "id": "parede-<id>",
  "ambienteId": "ambiente-<id>",
  "geometria": {
    "tipo": "plano_ou_volume",
    "origem": {"x": 0, "y": 0, "z": 0},
    "normal": {"x": 0, "y": 0, "z": 1},
    "espessura": 0,
    "unidade": "mm"
  },
  "faces": [],
  "versao": 1
}
```

### 10.2 Elemento

```json
{
  "id": "elemento-<id>",
  "tipo": "<tipo-catalogo>",
  "geometria": {
    "largura": 0,
    "altura": 0,
    "profundidade": 0,
    "unidade": "mm"
  },
  "transformacao": {
    "posicao": {"x": 0, "y": 0, "z": 0},
    "rotacao": {"x": 0, "y": 0, "z": 0}
  },
  "posicionamento": {
    "modo": "LIVRE",
    "paredeId": null,
    "faceId": null,
    "offset": 0,
    "folga": 0
  },
  "estadoGeometrico": "NÃO_AVALIADO",
  "versaoCatalogo": "<versao>"
}
```

### 10.3 Ocorrência de colisão

```json
{
  "id": "conflito-<id>",
  "tipo": "PENETRACAO_PAREDE",
  "elementoIds": ["elemento-1", "parede-1"],
  "severidade": "BLOQUEANTE",
  "estado": "CONFLITO_BLOQUEANTE",
  "interseccao": {
    "profundidadeMaxima": 0,
    "volumeEstimado": 0,
    "unidade": "mm"
  },
  "regraId": "RN-GEO-006",
  "mensagem": "<mensagem localizada>",
  "geradoPor": "motor-geometrico",
  "versaoMotor": "<versao>",
  "criadoEm": "<timestamp>"
}
```

Os valores zero são placeholders e não dados observados.

---

## 11. Algoritmo comportamental recomendado

### 11.1 Ao mover um elemento

1. Capturar snapshot anterior.
2. Aplicar transformação provisória.
3. Identificar paredes e elementos candidatos por região espacial.
4. Calcular distância às faces de parede.
5. Avaliar snap e candidatos de contato, se habilitado.
6. Aplicar a política de snap somente se a intenção do usuário e a regra permitirem.
7. Calcular penetrações e colisões.
8. Calcular folgas requeridas.
9. Classificar ocorrências.
10. Atualizar visualização, propriedades e painel de conflitos.
11. Permitir confirmar, corrigir ou desfazer.
12. Persistir apenas após validação/salvamento.

### 11.2 Regra de prioridade de intenção

🟡 Recomenda-se a seguinte prioridade:

1. edição numérica explícita do usuário;
2. vínculo persistente já confirmado;
3. snap explicitamente ativado;
4. correção automática configurada;
5. sugestão não aplicada.

O sistema nunca deve deslocar um elemento por uma sugestão silenciosa que contradiga um valor numérico explícito.

### 11.3 Ao validar

1. invalidar resultados geométricos anteriores afetados pela alteração;
2. recalcular contatos, colisões e folgas;
3. agrupar ocorrências equivalentes;
4. atualizar estados;
5. marcar resultados obsoletos;
6. bloquear ou liberar salvamento conforme severidade;
7. registrar versão do catálogo e do motor.

---

## 12. Mensagens e diagnósticos

Toda mensagem deve informar **o que ocorreu**, **onde**, **por quê** e **como corrigir**.

| Código | Mensagem canônica | Severidade |
|---|---|---|
| `WALL-001` | Elemento encostado na parede | Informação |
| `WALL-002` | Elemento vinculado à parede | Informação |
| `WALL-003` | Parede de referência não encontrada | Erro |
| `WALL-004` | Elemento penetra a parede além da tolerância | Erro |
| `WALL-005` | Folga mínima em relação à parede não atendida | Aviso/erro |
| `WALL-006` | Vínculo à parede foi perdido após alteração da geometria | Erro |
| `COL-001` | Elemento colide com outro elemento | Erro |
| `COL-002` | Elementos possuem sobreposição permitida pelo catálogo | Informação |
| `COL-003` | Área de abertura colide com outro elemento | Erro |
| `COL-004` | Elemento colide com piso ou teto | Erro |
| `COL-005` | Conflito detectado, mas a análise está desatualizada | Aviso |
| `COL-006` | Não foi possível calcular a colisão | Erro técnico |
| `SNAP-001` | Elemento alinhado automaticamente à parede | Informação |
| `SNAP-002` | Nenhuma posição de snap válida encontrada | Aviso |
| `SAVE-001` | Não é possível salvar enquanto houver conflitos bloqueantes | Erro |
| `SAVE-002` | Existem conflitos aceitos que devem ser revisados | Aviso |

Os textos reais da aplicação são 🔴 lacuna e devem ser transcritos quando o vídeo puder ser visualizado.

---

## 13. Critérios de aceite

### CA-01 — Elemento livre sem conflito

**Dado** um ambiente com paredes e espaço livre, **quando** o usuário inserir um elemento em posição válida, **então** o sistema deve classificá-lo como livre ou validado, sem criar colisão falsa.

### CA-02 — Encostar na parede

**Dado** um elemento compatível com instalação junto à parede, **quando** o usuário o mover até a face válida, **então** o sistema deve reconhecer contato e respeitar a folga/offset configurado.

### CA-03 — Grudar com vínculo

**Dado** que o produto suporte vínculo persistente, **quando** o usuário confirmar o encaixe, **então** a parede de referência, face, offset e orientação devem ser armazenados e reconstituídos ao reabrir.

### CA-04 — Desgrudar

**Dado** um elemento vinculado, **quando** o usuário desfizer o vínculo, **então** o elemento deve continuar em posição previsível, mudar para modo livre e deixar de acompanhar alterações futuras da parede.

### CA-05 — Penetração da parede

**Dado** um elemento que atravesse a parede além da tolerância, **quando** a validação ocorrer, **então** o sistema deve criar ocorrência específica, apontar elemento e parede e impedir salvamento definitivo se a regra for bloqueante.

### CA-06 — Colisão entre elementos

**Dado** que dois elementos ocupem o mesmo espaço proibido, **quando** o usuário terminar o movimento ou solicitar validação, **então** ambos devem ser identificados em uma ocorrência agrupada.

### CA-07 — Falsa colisão por precisão

**Dado** um elemento exatamente encostado na parede dentro da tolerância, **quando** a validação ocorrer, **então** o sistema não deve classificá-lo como penetração por erro de ponto flutuante.

### CA-08 — Folga insuficiente

**Dado** um elemento que não penetre outro, mas não possua a folga mínima operacional, **quando** a validação ocorrer, **então** o sistema deve distinguir folga insuficiente de colisão volumétrica.

### CA-09 — Porta ou gaveta

**Dado** um elemento com área de abertura, **quando** a abertura invadir outro elemento ou área proibida, **então** o sistema deve registrar conflito de abertura mesmo que os volumes fechados não se intersectem.

### CA-10 — Resolução automática transparente

**Dado** que snap/correção automática esteja habilitado, **quando** o sistema deslocar o elemento, **então** deve exibir ou registrar posição anterior, posição nova e regra aplicada, com possibilidade de desfazer.

### CA-11 — Colisão permitida

**Dado** um par de componentes cuja sobreposição seja prevista pelo catálogo, **quando** a validação ocorrer, **então** a relação não deve ser tratada como erro genérico e a permissão deve ser rastreável.

### CA-12 — Alteração da parede

**Dado** um elemento vinculado a uma parede, **quando** a parede for alterada, **então** o sistema deve manter o vínculo ou criar conflito explícito conforme a política definida.

### CA-13 — Parede excluída

**Dado** um elemento vinculado, **quando** a parede for excluída, **então** o elemento não pode permanecer com referência inválida silenciosa; deve ser desacoplado, removido ou marcado para decisão.

### CA-14 — Salvamento com conflito

**Dado** que exista conflito bloqueante, **quando** o usuário tentar salvar, **então** o sistema deve impedir a confirmação definitiva e listar os conflitos pendentes.

### CA-15 — Exceção aceita

**Dado** que uma colisão tenha sido explicitamente aceita, **quando** o usuário salvar, **então** a exceção deve manter motivo, autor, data, regra e escopo; não pode mascarar novas colisões.

### CA-16 — Reabertura

**Dado** um ambiente salvo, **quando** ele for reaberto com as mesmas versões de catálogo e motor, **então** os contatos, vínculos e conflitos devem ser semanticamente equivalentes.

### CA-17 — Desfazer/refazer

**Dado** um movimento que gere conflito, **quando** o usuário desfizer e refizer, **então** posição, vínculo, visualização e estado de colisão devem convergir em cada etapa.

### CA-18 — Falha do motor geométrico

**Dado** que o cálculo falhe, **quando** o usuário tentar salvar, **então** o sistema não deve afirmar que o ambiente está livre de colisões; deve exibir erro técnico e manter o estado recuperável.

---

## 14. Requisitos não funcionais

### RNF-001 — Determinismo

A mesma geometria, catálogo, tolerância e versão do motor devem produzir o mesmo resultado.

### RNF-002 — Responsividade

O sistema deve informar processamento quando o cálculo não for imediato. O tempo máximo aceitável é 🔴 lacuna e deve ser definido por quantidade de objetos e complexidade geométrica.

### RNF-003 — Precisão

O motor deve evitar inconsistências entre coordenadas exibidas, geometria renderizada e validação.

### RNF-004 — Rastreabilidade

Cada conflito deve ser explicável por uma regra e pelas entidades que a violaram.

### RNF-005 — Recuperação

Falhas de cálculo ou salvamento não devem apagar a última configuração válida nem a edição local recuperável.

### RNF-006 — Acessibilidade

Conflitos devem ser comunicados por texto e não somente por cor, brilho, transparência ou contorno.

### RNF-007 — Observabilidade

Registrar duração de cálculo, quantidade de objetos candidatos, quantidade de conflitos, versão do motor, tolerância e resultado.

### RNF-008 — Compatibilidade

Mudanças de catálogo ou motor devem declarar estratégia de revalidação de configurações existentes.

### RNF-009 — Segurança de integridade

Validações críticas devem ocorrer na camada confiável de domínio/servidor quando houver persistência compartilhada.

### RNF-010 — Escalabilidade

A detecção deve usar filtragem espacial ou estratégia equivalente para não comparar indiscriminadamente todos os pares em ambientes grandes.

---

## 15. Perguntas de validação do vídeo

1. 🔴 O elemento é um armário, módulo, painel, eletrodoméstico ou outro componente?
2. 🔴 O “grudado” acontece por clique, arraste, comando, proximidade ou alinhamento automático?
3. 🔴 Existe indicador visual/textual de que o elemento está grudado?
4. 🔴 Há diferença entre encostar e fixar?
5. 🔴 O elemento acompanha a parede quando ela se move?
6. 🔴 A parede possui espessura real ou é apenas um plano?
7. 🔴 A colisão ocorre com parede, outro móvel, piso, teto ou abertura?
8. 🔴 A colisão é apresentada em tempo real ou somente após validação?
9. 🔴 A colisão bloqueia o movimento, o salvamento ou apenas gera aviso?
10. 🔴 O sistema reposiciona automaticamente o elemento?
11. 🔴 O sistema mostra o elemento conflitante e a medida da interseção?
12. 🔴 Existe opção para ignorar/aceitar a colisão?
13. 🔴 Existem tolerâncias ou folgas editáveis?
14. 🔴 Há manipulação por eixo, coordenadas e rotação?
15. 🔴 A colisão considera portas/gavetas abertas?
16. 🔴 Quais mensagens, códigos, rótulos e botões aparecem exatamente?
17. 🔴 O estado de conflito é salvo no projeto?
18. 🔴 O vídeo mostra desfazer/refazer ou apenas uma operação única?
19. 🔴 O comportamento muda conforme o tipo de elemento?
20. 🔴 Qual é o fluxo após detectar a colisão?

---

## 16. Matriz de rastreabilidade

| Objetivo | Requisitos | Critérios |
|---|---|---|
| Posicionar elemento junto à parede | RF-PAREDE-001 a 008, RN-GEO-002 a 007 | CA-01 a CA-04 |
| Detectar colisões | RF-COL-001 a 005, RN-GEO-008 a 012 | CA-05 a CA-09 |
| Resolver conflitos | RF-COL-006 a 010, RN-GEO-013 | CA-10 a CA-15 |
| Preservar integridade | RF-COL-011 a 015, RN-GEO-014 e 015 | CA-14 a CA-18 |
| Operar com previsibilidade | RNF-001 a RNF-010 | CA-07, CA-10, CA-16 a CA-18 |

---

## 17. Plano de testes

### Testes unitários do motor

- ponto exatamente na face da parede;
- ponto dentro da tolerância;
- ponto além da tolerância;
- elemento paralelo e perpendicular à parede;
- parede com espessura;
- rotação de 90°, 180° e valores fracionários;
- colisão volumétrica parcial e total;
- dois objetos apenas tangentes;
- sobreposição permitida pelo catálogo;
- objeto sem geometria válida;
- unidade mm/cm/m;
- arredondamento próximo do limite.

### Testes de integração

- mover elemento e atualizar painel;
- snap e persistência;
- parede alterada com elemento vinculado;
- exclusão de parede referenciada;
- atualização da renderização após resolver;
- salvamento com ocorrência bloqueante;
- salvamento com exceção aceita;
- reabertura e revalidação;
- undo/redo de contato e colisão.

### Testes de aceitação

Executar CA-01 a CA-18 com captura textual de entrada, regra acionada, saída, estado anterior, estado posterior e versão do motor.

---

## 18. Decisões recomendadas

1. Separar **contato**, **vínculo**, **snap**, **folga** e **colisão** como conceitos distintos.
2. Nunca derivar “grudado” apenas de distância visual no momento da reabertura.
3. Identificar as entidades envolvidas em cada conflito.
4. Persistir regra, tolerância, catálogo e versão do motor usados na avaliação.
5. Exibir deslocamentos automáticos e permitir desfazê-los.
6. Diferenciar colisão física, penetração, folga insuficiente e abertura conflitante.
7. Tratar paredes com ID, faces, orientação e espessura, não como uma textura visual.
8. Invalidar resultados geométricos quando qualquer entidade relacionada mudar.
9. Não declarar o ambiente válido quando o motor falhar ou o resultado estiver obsoleto.
10. Manter o fluxo textual suficientemente completo para reconstrução sem screenshots.

---

## 19. Definição de pronto

Esta especificação estará pronta para implementação de paridade quando:

- o significado real de “grudado” estiver confirmado;
- os tipos de colisão observados estiverem enumerados;
- o comportamento de bloqueio, aviso ou correção automática estiver decidido;
- tolerâncias e folgas estiverem definidas;
- a relação entre parede, face, elemento e vínculo estiver fechada;
- todas as mensagens do vídeo forem transcritas;
- cada evento observado tiver timestamp, pré-condição, ação, reação e estado;
- os critérios CA-01 a CA-18 forem executáveis;
- a implementação não depender de uma imagem para entender a regra.

**Conclusão:** o documento fornece o contrato completo para implementar um sistema robusto de posicionamento junto a paredes e tratamento de colisões. Os itens marcados como 🔴 devem ser confirmados antes da alegação de equivalência exata ao comportamento mostrado no vídeo.
