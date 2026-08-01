# Glossário e Regras de Domínio — BlenderToMob

Este documento apresenta o mapeamento do domínio de negócio e regras implícitas do sistema **BlenderToMob**, conduzido pelo agente **Detective** na fase de Interpretação.

---

## 1. Glossário de Domínio

### 1.1 Entidades do Ambiente 3D
* **Ambiente (Scene)**: O espaço tridimensional onde o layout do projeto de marcenaria é construído (cômodo).
* **Parede (Wall)**: Entidade estrutural que delimita o ambiente. Pode ser composta por um único segmento retilíneo ou por uma polilinha contínua de múltiplos segmentos.
* **Segmento de Parede (Wall Segment)**: Um trecho reto individual de parede, caracterizado por ponto inicial, ponto final, espessura e pé-direito.
* **Piso (Floor)**: O plano horizontal de referência do ambiente. Adapta-se dinamicamente ao perímetro interno definido pelas paredes.
* **Abertura (Opening)**: Vão recortado na parede para permitir a passagem de luz ou tráfego. Subdivide-se em:
  * **Porta (Door)**: Abertura que inicia no nível do piso (peitoril fixo em 0.0).
  * **Janela (Window)**: Abertura suspensa na parede com peitoril configurável.
* **Peitoril (Sill Height)**: Distância vertical do piso até a base inferior do vão de uma janela.
* **Plano de Inserção (Insertion Plane)**: Qualquer face plana de um objeto existente (piso, paredes ou faces de outros módulos) que serve como base de alinhamento e ancoragem para a inserção de novos itens. Identificado visualmente por um sombreamento amarelo.
* **Módulo (Furniture Module / Cabinet)**: Armário de marcenaria paramétrico (balcões, aéreos ou paneleiros) composto por painéis de MDF/MDP.

### 1.2 Entidades de Produção (Plano de Corte)
* **Plano de Corte (Nesting)**: Processo algorítmico de otimização de arranjo bidimensional que organiza as peças retangulares de MDF em chapas padronizadas para minimizar a sobra de material.
* **Chapa (Sheet)**: Painel de matéria-prima (MDF/MDP) nas dimensões nominais de produção (padrão $2750 \times 1830$ mm).
* **Refilo (Sheet Margins)**: Faixa de margem de segurança cortada nas quatro bordas de uma chapa de MDF para esquadrejar a placa (padrão 10mm). A área de nesting útil é reduzida por esta margem.
* **Kerf (Saw Blade Thickness)**: A espessura da lâmina da serra de corte que é consumida (virando pó) a cada divisão de peças na chapa (padrão 4mm).
* **Sentido da Fibra/Veio (Wood Grain Direction)**: Orientação das texturas ou fibras da madeira no MDF:
  * `NONE`: Peça lisa ou sem veio definido; pode ser rotacionada em 90° livremente para otimizar o encaixe.
  * `VERTICAL` / `HORIZONTAL`: Exige que as dimensões da peça permaneçam alinhadas à fibra da chapa para manter a estética visual.

---

## 2. Regras de Negócio e Domínio

### 2.1 Regras de Paredes e Piso
* **Dependência do Piso (R-01)**: O piso do ambiente é uma entidade opcional no menu de interface, que **somente** é exibido se houver ao menos um segmento de parede ativo na cena (poll: `any(WALL)`).
* **Ajuste Conformal de Piso (R-02)**: O piso deve se ajustar automaticamente ao perímetro interno delimitado pelos vértices inferiores das paredes. Isso é computado via fecho convexo Graham Scan.
* **Sentido de Orientação de Paredes (R-03)**: A construção de paredes no sentido horário (`RIGHT`) ou anti-horário (`LEFT`) determina o lado para o qual a espessura da parede será extrudada em relação à linha guia desenhada pelo cursor do mouse.

### 2.2 Regras de Snapping e Movimentação de Aberturas
* **Aderência ao Segmento (R-04)**: Uma porta ou janela está vinculada fisicamente a um segmento de parede hospedeiro. Ela herda a rotação Z e a espessura do segmento de parede. O cortador boolean possui largura igual à espessura da parede multiplicada por 3 para garantir transpasse completo e furo limpo.
* **Movimento Constrangido (R-05)**: Durante o arrasto de uma abertura no modo de inserção, a sua posição é projetada e travada no plano vertical da parede ativa. O usuário só consegue alterar a coordenada ao longo do comprimento da parede (comprimento X local) e a altura vertical (peitoril Z local).
* **Clamping de Limites (R-06)**: A abertura não pode se deslocar para fora do segmento de parede ativo. Sua posição de deslocamento local no eixo X é limitada entre $0.0$ (início do segmento) e o comprimento máximo do segmento.
* **Transição entre Segmentos (R-07)**: Caso o usuário mova o cursor em direção a um segmento de parede vizinho ou quina, o sistema recalcula a menor distância 2D e transfere a abertura para a parede adjacente, rotacionando e readequando o preview à espessura da nova parede.
* **Sill Fixo de Portas (R-08)**: Portas de ambiente possuem peitoril fixado em `0.0 mm`, impedindo deslocamento vertical. Janelas podem deslizar verticalmente entre `0.0 mm` e a altura total da parede subtraída da altura do vão.

### 2.3 Regras de Otimização de Plano de Corte
* **Precedência de Área (R-09)**: O algoritmo de nesting prioriza o encaixe de peças maiores no início das prateleiras (shelves) da chapa de MDF para evitar que o espaço útil seja fragmentado por retalhos pequenos.
* **Corte Guilhotinado (R-10)**: O arranjo das peças na prateleira da chapa respeita cortes transversais completos de ponta a ponta (guilhotina), dividindo a chapa em faixas horizontais de altura equivalente à peça mais alta contida na fileira.

---

## 3. Matriz de Certeza e Escala de Confiança

Como o projeto é executado localmente sem repositório Git inicializado para análise de commits históricos, a escala de confiança apoia-se estritamente na engenharia reversa do código-fonte Python:

* **Conexão Convexa do Piso (R-02)**: 🟢 CONFIRMADO (Lógica geométrica explícita implementada em `mesh_gen.py` via `_convex_hull_2d`).
* **Snapping de Portas/Janelas (R-04 a R-08)**: 🟢 CONFIRMADO (Máquina de estado e cálculos de distância e projeção de planos codados em `opening_builder.py`).
* **Lógica de Guilhotina e Refilo (R-09 e R-10)**: 🟢 CONFIRMADO (Algoritmo Next-Fit Decreasing e espaçamento kerf implementados em `nesting.py`).
