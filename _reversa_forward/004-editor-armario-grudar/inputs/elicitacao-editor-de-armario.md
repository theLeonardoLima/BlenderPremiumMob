# Elicitação de Requisitos — Editor de Armário

**Produto observado no artefato de origem:** Promob Plus Enterprise 5.60.46.6  
**Contexto nominal:** ELÊ DE AMBIENTES  
**Evidência de origem:** `Editor de armário - ELÊDE AMBIENTES - Promob Plus Enterprise - 5.60.46.6 2026-10-07 11-04-56.mp4`  
**Data/hora indicada no nome:** 07/10/2026 às 11:04:56  
**Versão do documento:** 1.0  
**Objetivo:** especificar, em linguagem textual suficiente para implementação e homologação, o comportamento de um editor paramétrico de armários/móveis planejados.

> **Nota de evidência.** O arquivo MP4 foi localizado e possui aproximadamente 352 MB. Neste ambiente, a decodificação/captura de quadros do vídeo não foi autorizada pelos recursos locais disponíveis. Assim, este documento não afirma como “confirmado” nenhum detalhe de pixel, rótulo, atalho ou sequência que não possa ser sustentado pelo artefato nominal. A especificação foi estruturada para ser implementável e para explicitar as validações pendentes, sem transformar suposições em fatos.

## 1. Legenda de confiança

- 🟢 **CONFIRMADO** — sustentado diretamente pelo nome do arquivo, pelo contexto fornecido ou por uma propriedade explicitamente informada.
- 🟡 **INFERIDO** — comportamento esperado de um editor paramétrico de móveis planejados, útil para projetar a solução, mas sujeito a confirmação.
- 🔴 **LACUNA** — não determinável sem revisão quadro a quadro, entrevista com usuário ou acesso ao sistema.

As marcas acompanham requisitos e decisões para evitar que uma implementação trate hipótese como regra.

---

## 2. Visão do produto

### 2.1 Propósito

O sistema deve permitir que um projetista crie ou edite um armário paramétrico, informe dimensões e componentes, visualize o resultado e preserve uma configuração reutilizável para orçamento, detalhamento ou continuidade do projeto.

- 🟢 O contexto é um **“Editor de armário”**.
- 🟢 O produto nominal é **Promob Plus Enterprise**, versão **5.60.46.6**.
- 🟡 O editor deve manter coerência entre medidas, composição, visualização 3D/2D e dados de produção.
- 🟡 O fluxo principal é um CRUD paramétrico: abrir/criar → configurar → validar → visualizar → confirmar/salvar.
- 🔴 Não foi possível confirmar se o fluxo observado começa em um catálogo, em uma planta, em um ambiente ou em uma janela independente.

### 2.2 Resultado de negócio

Ao concluir a edição, deve existir uma definição de armário que:

1. possua identidade e contexto de projeto;
2. tenha dimensões válidas;
3. contenha uma composição interna e externa coerente;
4. esteja associada a materiais/acabamentos quando exigidos;
5. seja visualizável;
6. possa ser salva, reaberta e alterada sem perda silenciosa de dados;
7. possa alimentar etapas posteriores, como orçamento, detalhamento ou fabricação, se essas integrações fizerem parte do produto.

### 2.3 Fora de escopo desta elicitação

- 🟡 Não especifica cálculo industrial de ferragens, otimização de corte, CNC ou orçamento final sem evidência de que tais funcionalidades estejam no vídeo.
- 🔴 Não especifica nomes exatos de botões, ícones, abas, cores, atalhos ou posições.
- 🔴 Não especifica perfis de acesso, integrações externas, formatos de exportação ou regras fiscais.

---

## 3. Atores e permissões

| Ator | Responsabilidade | Permissão mínima | Confiança |
|---|---|---|---|
| Projetista | Criar e configurar o armário | Criar, editar, validar, visualizar e salvar | 🟡 |
| Revisor | Conferir medidas e composição | Visualizar, validar e aprovar/reprovar, se existir | 🔴 |
| Orçamentista | Usar a composição para preço | Consultar itens e quantidades, se existir integração | 🔴 |
| Produção | Consumir detalhamento técnico | Consultar itens, medidas, materiais e ferragens, se existir integração | 🔴 |
| Administrador | Manter catálogos e regras | Configurar limites, componentes, materiais e permissões | 🔴 |

**Regra geral:** toda ação de alteração deve ser autorizada pelo contexto de usuário atual. Se o produto não possuir controle de acesso, o sistema deve ao menos identificar o autor e a data da última alteração.

---

## 4. Modelo mental da tela, descrito sem imagem

A tela deve ser compreensível somente pela estrutura textual abaixo, independentemente da tecnologia visual usada.

### 4.1 Regiões funcionais

1. **Cabeçalho de contexto**
   - nome do projeto/ambiente;
   - identificação do móvel selecionado;
   - estado de edição: novo, alterado, salvo, inválido ou somente leitura;
   - ações de salvar, cancelar, desfazer e refazer, quando disponíveis.

2. **Seletor de categoria/tipo**
   - tipo do armário ou módulo;
   - eventual modelo/base de catálogo;
   - ação para trocar o modelo sem destruir dados sem confirmação.

3. **Painel de dimensões**
   - largura;
   - altura;
   - profundidade;
   - espessuras, folgas, recuos e alturas de referência, quando aplicáveis;
   - unidade de medida explícita;
   - indicação de valor padrão, mínimo, máximo e valor atualmente aplicado.

4. **Painel de composição**
   - divisões/vãos;
   - laterais, tampo, base e fundo;
   - prateleiras;
   - portas;
   - gavetas;
   - cabideiros, colunas, nichos e acessórios;
   - ferragens e componentes dependentes do catálogo.

5. **Painel de materiais e acabamentos**
   - material estrutural;
   - acabamento externo/interno;
   - bordas;
   - puxadores/perfis;
   - cor/textura;
   - herança de material do ambiente ou sobrescrita local.

6. **Área de visualização**
   - prévia do móvel;
   - seleção de componente;
   - atualização após alteração paramétrica;
   - modos 2D, 3D, frontal, superior ou explodido, somente se disponíveis;
   - indicação visual ou textual de erros de geometria.

7. **Rodapé de mensagens**
   - validações;
   - quantidade de alterações não salvas;
   - progresso de processamento;
   - conflitos e avisos não bloqueantes.

> Os nomes acima são nomes canônicos da especificação. A interface pode exibir rótulos diferentes, desde que preserve o significado e a acessibilidade.

---

## 5. Fluxo principal de usuário

### 5.1 Fluxo feliz

1. O usuário abre o editor.
2. O sistema carrega o contexto do projeto e o armário selecionado, ou oferece a criação de um novo.
3. O sistema apresenta os valores atuais e o estado de cada componente.
4. O usuário escolhe ou confirma o tipo/modelo do armário.
5. O usuário informa ou altera largura, altura e profundidade.
6. O sistema normaliza a entrada segundo unidade, precisão e limites do catálogo.
7. O usuário adiciona, remove ou configura componentes internos/externos.
8. O sistema recalcula a geometria dependente.
9. O usuário define ou confirma materiais e acabamentos.
10. O usuário examina a visualização.
11. O sistema executa validação completa.
12. Se não houver erro bloqueante, o usuário salva/confirma.
13. O sistema persiste a configuração, atualiza o estado do projeto e informa sucesso.

### 5.2 Fluxo de edição de item existente

1. Carregar o snapshot salvo.
2. Reidratar parâmetros, componentes, materiais e metadados.
3. Exibir diferenças somente após alteração.
4. Marcar o documento como alterado na primeira mutação efetiva.
5. Permitir desfazer/refazer dentro do escopo da sessão.
6. Ao salvar, validar novamente; nunca confiar apenas na validação feita durante a digitação.

### 5.3 Fluxo de cancelamento

- Se não houver alteração, cancelar fecha ou retorna sem diálogo.
- Se houver alteração não salva, o sistema deve oferecer **continuar editando**, **descartar alterações** ou **salvar antes de sair**.
- O descarte deve ser explícito e não pode ocorrer por clique acidental em navegação.

---

## 6. Requisitos funcionais

### RF-001 — Abrir o editor

🟢 O sistema deve abrir o editor associado ao armário/contexto selecionado.  
🟡 Se não houver seleção, deve oferecer criação de um novo armário ou solicitar seleção válida.  
**Aceite:** ao abrir, o usuário consegue identificar o contexto, o item editado e o estado atual.

### RF-002 — Criar configuração nova

🟡 O sistema deve criar um rascunho com valores padrão provenientes do tipo/modelo escolhido.  
**Aceite:** nenhum dado do projeto é alterado antes da confirmação do usuário.

### RF-003 — Selecionar tipo ou modelo

🟡 O sistema deve permitir escolher um tipo/modelo de armário a partir de catálogo permitido.  
**Regra:** mudar de modelo deve recalcular parâmetros dependentes e identificar dados incompatíveis.  
**Aceite:** dados que não possam ser preservados são listados antes da confirmação.

### RF-004 — Editar dimensões

🟡 O sistema deve aceitar largura, altura e profundidade com unidade explícita.  
**Regras:**

- valores vazios, não numéricos, negativos ou fora dos limites são inválidos;
- separador decimal deve ser tratado de forma consistente com a localidade;
- precisão e arredondamento devem ser definidos pelo catálogo;
- entrada equivalente em unidades diferentes deve resultar no mesmo valor normalizado;
- a tela deve distinguir valor digitado, valor normalizado e valor efetivamente aplicado.

### RF-005 — Gerenciar componentes

🟡 O sistema deve permitir adicionar, selecionar, editar, duplicar, mover e remover componentes suportados pelo modelo.  
**Componentes candidatos:** prateleira, porta, gaveta, nicho, divisão, fundo, acessório e ferragem.  
**Aceite:** cada componente selecionado possui propriedades editáveis e referência inequívoca na visualização e no painel textual.

### RF-006 — Manter restrições geométricas

🟡 O sistema deve impedir ou sinalizar componentes que excedam o espaço disponível, colidam ou violem dependências do modelo.  
**Aceite:** o usuário recebe mensagem que identifica componente, parâmetro causador, valor atual e ação corretiva sugerida.

### RF-007 — Editar materiais e acabamentos

🟡 O sistema deve permitir aplicar material por escopo: móvel inteiro, grupo, peça ou face, conforme capacidade do catálogo.  
**Regra:** uma sobrescrita local deve indicar que deixou de herdar a configuração superior.

### RF-008 — Atualizar visualização

🟡 A alteração de um parâmetro deve refletir-se na visualização após a conclusão da operação ou durante a edição, conforme desempenho definido.  
**Aceite:** a visualização nunca pode permanecer silenciosamente divergente dos parâmetros persistidos; se estiver defasada, deve exibir estado de processamento.

### RF-009 — Selecionar por painel ou visualização

🟡 A seleção feita no painel deve selecionar o mesmo componente na visualização e vice-versa.  
**Aceite:** existe uma identidade única de componente, não apenas uma posição visual.

### RF-010 — Desfazer e refazer

🟡 O sistema deve permitir desfazer/refazer alterações relevantes na sessão.  
**Regra:** salvar não deve apagar o histórico de forma que torne o estado inconsistente; a política exata de agrupamento de ações é lacuna.

### RF-011 — Validar configuração

🟡 O sistema deve executar validação de campo, modelo, geometria, catálogo e persistência.  
A validação deve classificar mensagens como erro bloqueante, aviso e informação.

### RF-012 — Salvar

🟡 O sistema deve salvar somente uma configuração válida ou permitir salvar rascunho explicitamente identificado.  
**Aceite:** após salvar, o estado muda para salvo, a versão/data/autor são atualizados e uma reabertura reproduz a configuração.

### RF-013 — Impedir perda de dados

🟡 Ao fechar, navegar ou trocar de item com alterações não salvas, o sistema deve proteger o usuário com decisão explícita.  
**Aceite:** nenhum caminho normal descarta mutações sem aviso.

### RF-014 — Reabrir sem alteração semântica

🟡 Uma configuração salva e reaberta deve conservar medidas, ordem, componentes, materiais, vínculos e estado de validação, salvo regras de migração documentadas.

### RF-015 — Registrar diagnóstico

🟡 Erros de cálculo, catálogo, carregamento ou persistência devem gerar mensagem acionável e registro técnico correlacionável, sem expor segredos.

---

## 7. Regras de negócio

### RN-001 — Identidade

Cada armário deve ter um identificador estável. O identificador não pode mudar quando o usuário altera apenas medidas ou acabamento.

### RN-002 — Unidade e precisão

A unidade exibida deve ser explícita e a conversão deve ser determinística. O sistema deve evitar o problema “valor visualmente igual, valor interno diferente” por arredondamento oculto.

### RN-003 — Limites

Limites mínimo/máximo devem ser definidos por tipo, componente, material e eventual ferragem. O sistema não deve aplicar limite genérico quando existir limite mais específico.

### RN-004 — Dependências

Alterações de dimensões devem recalcular componentes dependentes. O recálculo deve indicar o que foi alterado automaticamente e não pode sobrescrever ajuste manual sem política explícita.

### RN-005 — Preservação

Ao redimensionar, o sistema deve preservar posições e proporções apenas quando geometricamente possível. Itens afetados devem ser marcados para revisão.

### RN-006 — Compatibilidade de catálogo

Só podem ser usados componentes e materiais compatíveis com o modelo, ambiente, fabricante e regras de negócio vigentes.

### RN-007 — Conflitos

Conflitos devem ser determinísticos: mesma entrada e mesmo catálogo devem produzir os mesmos erros/avisos e a mesma geometria.

### RN-008 — Estado de validade

A configuração deve manter pelo menos os estados `RASCUNHO`, `VÁLIDA`, `INVÁLIDA`, `ALTERADA`, `PROCESSANDO`, `SALVA` e `SOMENTE_LEITURA`, conforme aplicável.

### RN-009 — Salvamento atômico

Uma falha no salvamento não pode produzir uma configuração parcialmente persistida ou declarar sucesso sem confirmação do armazenamento.

### RN-010 — Concorrência

Se o mesmo item puder ser editado por mais de um usuário/processo, o sistema deve detectar versão desatualizada e oferecer comparação, recarga ou criação de nova versão. 🔴

### RN-011 — Regras silenciosas proibidas

Toda alteração automática de dimensão, posição, componente, material ou quantidade deve ser visível em mensagem, histórico ou diferencial antes da confirmação.

---

## 8. Máquina de estados

```text
NÃO_CARREGADO
  -> CARREGANDO
  -> PRONTO_SEM_ALTERAÇÃO
  -> EDITANDO
  -> VALIDANDO
  -> VÁLIDO
  -> SALVANDO
  -> SALVO

EDITANDO -> INVÁLIDO              quando houver erro bloqueante
EDITANDO -> VALIDANDO             ao solicitar validação ou salvar
VALIDANDO -> EDITANDO             se houver aviso não bloqueante ou erro
VALIDANDO -> VÁLIDO               se não houver erro bloqueante
SALVANDO -> SALVO                 após confirmação de persistência
SALVANDO -> EDITANDO              em falha recuperável
QUALQUER_ESTADO -> SOMENTE_LEITURA se o contexto não permitir edição
QUALQUER_ESTADO -> ERRO_CARREGAMENTO em falha irrecuperável
```

### Invariantes

- Não é permitido salvar como configuração definitiva quando há erro bloqueante.
- `SALVO` implica que a versão persistida corresponde ao estado exibido no momento da confirmação.
- `EDITANDO` implica que existe diferença entre o estado corrente e o último snapshot persistido.
- `PROCESSANDO` impede ações concorrentes que poderiam produzir ordem de atualização indefinida, ou deve usar fila/versionamento.

---

## 9. Contrato de dados conceitual

```text
Projeto
 └── Ambiente
      └── Armário
           ├── Modelo
           ├── Dimensões
           ├── Componentes[*]
           │    ├── tipo
           │    ├── posição
           │    ├── dimensões
           │    ├── propriedades
           │    ├── material
           │    └── dependências[*]
           ├── Materiais/Acabamentos
           ├── Validações[*]
           └── Auditoria/Versão
```

### 9.1 Campos mínimos recomendados

| Entidade | Campos | Obrigatório | Confiança |
|---|---|---:|---|
| Armário | `id`, `projetoId`, `nome`, `modeloId`, `status`, `versão` | Sim | 🟡 |
| Dimensões | `largura`, `altura`, `profundidade`, `unidade`, `precisão` | Sim | 🟡 |
| Componente | `id`, `tipo`, `ordem`, `posição`, `dimensões`, `estado` | Sim | 🟡 |
| Material | `id`, `escopo`, `catálogoId`, `acabamento`, `herdado` | Conforme modelo | 🟡 |
| Validação | `código`, `severidade`, `mensagem`, `entidadeId`, `parâmetro`, `resolvido` | Sim durante validação | 🟡 |
| Auditoria | `autor`, `criadoEm`, `alteradoEm`, `versão`, `origem` | Recomendido | 🟡 |

### 9.2 Exemplo textual de payload

```json
{
  "id": "armario-<id-estavel>",
  "projetoId": "projeto-<id>",
  "nome": "<nome do armário>",
  "modeloId": "<modelo do catálogo>",
  "status": "EDITANDO",
  "dimensoes": {
    "largura": {"valor": 0, "unidade": "mm"},
    "altura": {"valor": 0, "unidade": "mm"},
    "profundidade": {"valor": 0, "unidade": "mm"}
  },
  "componentes": [],
  "materiais": [],
  "validacoes": [],
  "versao": 1
}
```

Os zeros são placeholders e não valores de negócio.

---

## 10. Validações e mensagens

### 10.1 Formato de mensagem

Toda mensagem deve conter:

1. severidade;
2. código estável;
3. texto humano;
4. entidade/componente afetado;
5. parâmetro causador, quando aplicável;
6. valor atual e faixa permitida, quando seguro;
7. ação corretiva;
8. indicação se bloqueia salvamento.

### 10.2 Catálogo inicial de códigos

| Código | Situação | Severidade |
|---|---|---|
| `DIM-001` | Dimensão obrigatória ausente | Erro |
| `DIM-002` | Dimensão não numérica | Erro |
| `DIM-003` | Dimensão fora do limite do modelo | Erro |
| `DIM-004` | Precisão incompatível | Aviso/erro conforme regra |
| `GEO-001` | Componente fora do volume do armário | Erro |
| `GEO-002` | Colisão entre componentes | Erro |
| `GEO-003` | Folga insuficiente | Aviso ou erro |
| `CAT-001` | Componente incompatível com o modelo | Erro |
| `CAT-002` | Material indisponível | Erro |
| `MAT-001` | Material herdado sobrescrito | Informação |
| `SAVE-001` | Falha ao persistir | Erro |
| `SAVE-002` | Versão desatualizada/conflito | Erro |
| `UX-001` | Alterações não salvas | Aviso |

---

## 11. Requisitos não funcionais

### RNF-001 — Clareza

O usuário deve conseguir descobrir o que editar, qual valor está vigente e por que uma operação não foi aceita sem depender de imagem externa ou conhecimento oculto.

### RNF-002 — Desempenho

Após uma edição simples, a confirmação visual/textual deve ocorrer em tempo compatível com uso interativo. O alvo exato em milissegundos é 🔴 lacuna e deve ser definido por perfil de hardware e complexidade do modelo.

### RNF-003 — Determinismo

Mesma versão de catálogo, mesma configuração e mesmas entradas devem produzir a mesma validação e geometria.

### RNF-004 — Recuperação

Falhas de cálculo, catálogo ou persistência devem permitir repetir, corrigir ou recuperar o último estado seguro.

### RNF-005 — Acessibilidade

Todos os controles devem possuir nome acessível, foco navegável, estado anunciado e mensagem associada ao campo. Não depender somente de cor ou ícone.

### RNF-006 — Observabilidade

Registrar duração de carregamento, cálculo, validação e salvamento; códigos de erro; versão do catálogo; identificador do armário; sem registrar dados sensíveis desnecessários.

### RNF-007 — Compatibilidade

A versão do catálogo e do motor geométrico deve ser persistida com a configuração ou ser recuperável por referência imutável.

### RNF-008 — Integridade

Salvar deve ser transacional ou equivalente: ou a nova versão é confirmada, ou o último estado íntegro permanece disponível.

### RNF-009 — Internacionalização

Unidade, separador decimal, idioma, formato de data e terminologia devem ser configuráveis sem alterar os valores internos.

### RNF-010 — Segurança

Validar no cliente e no servidor, se houver servidor. Nunca confiar em limites ou permissões vindos apenas da interface.

---

## 12. Cenários de uso e critérios de aceite

### CA-01 — Criar um armário válido

**Dado** um contexto de projeto editável, **quando** o usuário escolher um modelo e informar dimensões dentro dos limites, **então** o sistema deve gerar a configuração, atualizar a prévia, informar estado válido e permitir salvar.

### CA-02 — Rejeitar dimensão inválida

**Dado** um campo de dimensão, **quando** o usuário informar texto inválido, valor negativo, zero proibido ou valor fora da faixa, **então** o campo deve indicar erro específico, não aplicar silenciosamente a entrada e bloquear o salvamento definitivo.

### CA-03 — Redimensionar com dependências

**Dado** um armário com componentes, **quando** a largura/altura/profundidade mudar, **então** o sistema deve recalcular dependências, preservar o que for possível, marcar afetados e apresentar conflitos antes de salvar.

### CA-04 — Adicionar componente incompatível

**Dado** um modelo sem suporte a determinado componente, **quando** o usuário tentar adicioná-lo, **então** a ação deve ser impedida ou explicitamente convertida em aviso conforme regra do catálogo, sempre com motivo identificável.

### CA-05 — Detectar colisão

**Dado** dois componentes que ocupem o mesmo volume proibido, **quando** a validação ocorrer, **então** o sistema deve localizar ambos, informar a colisão e impedir o salvamento definitivo.

### CA-06 — Material indisponível

**Dado** um material removido ou incompatível, **quando** o item for carregado, **então** o sistema deve preservar a referência original para diagnóstico, marcar o item como pendente e oferecer substituição controlada.

### CA-07 — Cancelar alterações

**Dado** um item alterado, **quando** o usuário tentar sair e escolher descartar, **então** o sistema deve restaurar exatamente o último snapshot persistido, sem alterar projeto ou histórico indevidamente.

### CA-08 — Falha de salvamento

**Dado** uma falha de persistência, **quando** o usuário salvar, **então** o sistema deve informar falha, manter a edição local recuperável, não declarar sucesso e permitir nova tentativa.

### CA-09 — Reabrir configuração

**Dado** uma configuração salva, **quando** ela for reaberta com a mesma versão de catálogo, **então** dimensões, componentes, materiais e estados devem ser semanticamente equivalentes ao snapshot salvo.

### CA-10 — Concorrência

**Dado** que outra versão tenha sido salva antes, **quando** o usuário tentar salvar uma versão antiga, **então** o sistema deve impedir sobrescrita silenciosa e oferecer recarregar, comparar ou salvar como nova versão.

### CA-11 — Desfazer/refazer

**Dado** uma sequência de alterações, **quando** o usuário desfizer e refizer, **então** o modelo, os parâmetros, a visualização e o estado de validade devem permanecer sincronizados.

### CA-12 — Acessibilidade

**Dado** uso por teclado/leitor de tela, **quando** o usuário percorrer os campos, **então** cada campo deve ser identificável, ter unidade/erro/limite anunciados e permitir concluir o fluxo sem depender do mouse.

---

## 13. Matriz de rastreabilidade

| Objetivo | Requisitos | Critérios |
|---|---|---|
| Configurar móvel | RF-001 a RF-008 | CA-01, CA-03, CA-04, CA-05 |
| Preservar integridade | RF-009 a RF-015, RN-009 | CA-07, CA-08, CA-09, CA-10 |
| Evitar erro de fabricação | RF-004 a RF-007, RN-003 a RN-007 | CA-02 a CA-06 |
| Oferecer experiência operável | RNF-001, RNF-005, RNF-009 | CA-11, CA-12 |
| Permitir evolução técnica | RNF-003, RNF-006, RNF-007, RNF-008 | CA-08 a CA-10 |

---

## 14. Lacunas que precisam ser resolvidas

1. 🔴 Quais telas, abas e controles aparecem exatamente no vídeo?
2. 🔴 Qual é a ordem temporal real das interações?
3. 🔴 O editor opera sobre um armário selecionado em planta, sobre um módulo isolado ou sobre um catálogo?
4. 🔴 Quais componentes estão realmente disponíveis?
5. 🔴 Quais são os nomes exatos e os limites dos campos?
6. 🔴 Qual unidade, precisão e política de arredondamento são usadas?
7. 🔴 A visualização é 2D, 3D, ambas ou apenas uma prévia esquemática?
8. 🔴 Existem abas para estrutura, portas, gavetas, acessórios, materiais ou orçamento?
9. 🔴 Há confirmação explícita ao fechar, excluir, trocar modelo ou alterar dimensões?
10. 🔴 O sistema permite salvar rascunho inválido?
11. 🔴 Há undo/redo, histórico, versionamento ou autosave?
12. 🔴 Quais regras de colisão, folga, alinhamento e distribuição automática existem?
13. 🔴 Quais cálculos são feitos automaticamente e quais dependem de entrada manual?
14. 🔴 Há integração com orçamento, lista de peças, corte, ferragens, renderização ou fabricação?
15. 🔴 Quais perfis e permissões existem?
16. 🔴 O catálogo é local, remoto, versionado ou configurável pelo usuário?
17. 🔴 Qual comportamento ocorre quando o catálogo muda depois que o armário foi salvo?
18. 🔴 Existe suporte a múltiplos usuários, bloqueio ou resolução de conflito?
19. 🔴 Quais formatos de importação/exportação são necessários?
20. 🔴 Quais métricas de desempenho são aceitáveis em projetos pequenos e grandes?

---

## 15. Plano de validação contra o vídeo

Quando o vídeo puder ser decodificado, a revisão deve ser feita nesta ordem:

1. registrar duração, resolução, taxa de quadros e áudio;
2. criar uma linha do tempo com eventos e timestamps;
3. transcrever literalmente rótulos, valores, mensagens e títulos;
4. para cada interação, registrar pré-condição, ação, reação, persistência e estado;
5. separar comportamento repetido de comportamento excepcional;
6. comparar o fluxo observado com RF-001–RF-015;
7. substituir 🟡 por 🟢 somente quando houver evidência direta;
8. converter cada 🔴 em decisão, requisito confirmado ou item fora de escopo;
9. adicionar casos de teste para toda mensagem e transição observada;
10. revisar se a especificação ainda consegue reconstruir a interface sem imagem.

### Registro de observação a preencher

| Tempo | Contexto | Ação do usuário | Resposta do sistema | Dados/valor | Estado antes/depois | Confiança |
|---|---|---|---|---|---|---|
| `mm:ss` | `<tela/seleção>` | `<ação>` | `<feedback>` | `<valor>` | `<antes> → <depois>` | 🟢/🟡/🔴 |

---

## 16. Decisões recomendadas para implementação

1. Implementar o domínio como um modelo paramétrico versionado, não como desenho solto.
2. Manter uma função de validação pura e determinística, separada da camada visual.
3. Identificar componentes por ID estável e não por índice de lista.
4. Persistir unidade, precisão e versão de catálogo.
5. Representar avisos e erros como objetos estruturados, não como textos espalhados pela interface.
6. Fazer recálculos com origem rastreável: usuário, regra de modelo ou migração.
7. Usar snapshot e diff para cancelamento, undo/redo e auditoria.
8. Aplicar salvamento transacional e controle de versão otimista quando houver armazenamento compartilhado.
9. Testar a mesma configuração em modo visual, textual e persistido para provar convergência.
10. Não usar imagem como requisito: toda informação necessária para construir, validar e operar o editor deve estar expressa nos contratos, estados, regras e critérios deste documento.

---

## 17. Definição de pronto da elicitação

A elicitação pode ser considerada pronta para implementação somente quando:

- todos os 🔴 críticos tiverem uma decisão humana;
- cada controle visível tiver requisito, estado e critério de aceite;
- cada alteração automática tiver regra e mensagem;
- dimensões, unidades, limites e precisão estiverem fechados;
- o modelo de dados estiver versionado;
- os fluxos feliz, inválido, cancelamento, falha e reabertura estiverem testados;
- houver rastreabilidade entre objetivo, requisito e teste;
- a inspeção quadro a quadro do vídeo tiver atualizado a matriz de evidências;
- nenhum detalhe importante depender de uma imagem para ser compreendido.

**Conclusão:** este documento é uma especificação textual robusta e implementável para o domínio do editor de armário, mas não deve ser apresentado como transcrição confirmada do vídeo enquanto a limitação de decodificação permanecer. A substituição das lacunas por evidência observável é o único passo necessário para transformá-lo em uma especificação de paridade do comportamento original.
