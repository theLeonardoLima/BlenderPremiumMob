# Análise de Código — BlenderToMob

Este documento apresenta a análise técnica aprofundada da estrutura, lógica e algoritmos do add-on **BlenderToMob**, conduzida pelo agente **Archaeologist** na fase de Escavação.

---

## 1. Dicionário de Dados do Sistema

O add-on registra propriedades customizadas em tipos internos do Blender (usando a API `bpy.props`). A tabela abaixo cataloga a estrutura de dados paramétrica utilizada na cena.

### 1.1 Parâmetros de Parede (`BTM_PG_WallSegment`)
Registrado em `bpy.types.Object.btm_wall`. Controla a geometria paramétrica das paredes.

| Propriedade | Tipo | Descrição | Padrão / Limites | Certeza |
|-------------|------|-----------|-------------------|----------|
| `length` | Float | Comprimento do segmento de parede em milímetros | 2000.0 (10.0 a 100000.0) | 🟢 CONFIRMADO |
| `absolute_angle`| Float | Ângulo do segmento em relação ao sistema global | 0.0° (-360.0° a 360.0°) | 🟢 CONFIRMADO |
| `relative_angle`| Float | Ângulo em relação ao segmento anterior da polilinha | 0.0° (-360.0° a 360.0°) | 🟢 CONFIRMADO |
| `thickness` | Float | Espessura da parede em milímetros | 150.0 (10.0 a 2000.0) | 🟢 CONFIRMADO |
| `height_start` | Float | Altura da parede no ponto inicial (Pé-Direito) | 2700.0 (100.0 a 10000.0) | 🟢 CONFIRMADO |
| `height_end` | Float | Altura da parede no ponto final | 2700.0 (100.0 a 10000.0) | 🟢 CONFIRMADO |
| `offset` | Float | Afastamento vertical da base da parede em relação ao piso | 0.0 mm | 🟢 CONFIRMADO |
| `sagitta` | Float | Flecha do arco para paredes curvas (0 para retas) | 0.0 mm | 🟢 CONFIRMADO |
| `linear_increment`| Float| Passo do salto do cursor durante a construção do comprimento | 50.0 mm (1.0 a 1000.0) | 🟢 CONFIRMADO |
| `angular_increment`| Float| Passo do salto do ângulo ao mover o mouse | 5.0° (0.5° a 90.0°) | 🟢 CONFIRMADO |
| `orientation` | Enum | Lado da parede que recebe o comprimento (`RIGHT` / `LEFT`) | `RIGHT` | 🟢 CONFIRMADO |
| `wall_type` | Enum | Estilo e material da parede (`NORMAL` / `DRYWALL` / `GLASS`) | `NORMAL` | 🟢 CONFIRMADO |
| `use_as_default`| Bool | Salvar as propriedades atuais como padrão para novas paredes | `False` | 🟢 CONFIRMADO |

### 1.2 Parâmetros de Plano de Inserção (`BTM_PG_InsertionPlane`)
Registrado em `bpy.types.Object.btm_plane`. Mapeia o tipo de entidade CAD do objeto na hierarquia espacial.

| Propriedade | Tipo | Descrição | Valores Possíveis | Certeza |
|-------------|------|-----------|-------------------|----------|
| `object_kind` | Enum | Tipo de elemento de ambiente | `WALL`, `FLOOR`, `MODULE`, `GEOMETRY`, `OPENING` | 🟢 CONFIRMADO |
| `parent_plane`| Pointer | Referência ao objeto hospedeiro | `bpy.types.Object` | 🟢 CONFIRMADO |
| `layer_id` | String | ID da camada (Camada do Promob para isolamento) | `"Default"` | 🟢 CONFIRMADO |
| `collision_override`| Enum| Controle de colisão específico do objeto | `INHERIT` (padrão), `ON`, `OFF` | 🟢 CONFIRMADO |

### 1.3 Parâmetros de Abertura (`BTM_PG_OpeningProperties`)
Registrado em `bpy.types.Object.btm_opening`. Utilizado para portas e janelas que realizam corte boolean nas paredes.

| Propriedade | Tipo | Descrição | Padrão / Limites | Certeza |
|-------------|------|-----------|-------------------|----------|
| `opening_type` | Enum | Tipo de abertura de vão (`DOOR` / `WINDOW`) | `DOOR` | 🟢 CONFIRMADO |
| `width` | Float | Largura útil da abertura em milímetros | 800.0 (100.0 a 5000.0) | 🟢 CONFIRMADO |
| `height` | Float | Altura útil da abertura em milímetros | 2100.0 (100.0 a 5000.0) | 🟢 CONFIRMADO |
| `sill_height` | Float | Altura do peitoril a partir da base (0.0 para portas) | 0.0 (0.0 a 5000.0) | 🟢 CONFIRMADO |
| `parent_wall` | Pointer | Referência ao objeto de parede que hospeda o vão | `bpy.types.Object` | 🟢 CONFIRMADO |

### 1.4 Parâmetros de Módulos de Mobiliário (`BTM_PG_CabinetProperties`)
Registrado em `bpy.types.Object.btm_cabinet`. Controla as dimensões da caixa estrutural de MDF/MDP.

| Propriedade | Tipo | Descrição | Padrão / Limites | Certeza |
|-------------|------|-----------|-------------------|----------|
| `width` | Float | Largura total do módulo (mm) | 800.0 (100.0 a 3000.0) | 🟢 CONFIRMADO |
| `height` | Float | Altura total do módulo (mm) | 700.0 (100.0 a 3000.0) | 🟢 CONFIRMADO |
| `depth` | Float | Profundidade total do módulo (mm) | 550.0 (100.0 a 2000.0) | 🟢 CONFIRMADO |
| `thickness` | Float | Espessura das chapas de MDF (laterais/base/topo) | 18.0 mm (6.0 a 50.0) | 🟢 CONFIRMADO |
| `cabinet_type` | Enum | Categoria do módulo (`BASE` / `WALL` / `TALL`) | `BASE` | 🟢 CONFIRMADO |

---

## 2. Fluxo de Controle e Interações

### 2.1 Construtor de Parede Modal (`BTM_OT_WallBuilder`)
Este operador implementa uma máquina de estado modal para a modelagem interativa de polilinhas de paredes no plano:

```
[Iniciar Operador] ──> [Aguardar Clique no Piso (Z=0)] 
                             │
                             ▼
                    [Registrar Início]
                             │
                             ▼
     ┌───────────> [Aguardar Input do Mouse/Teclado] <──────────┐
     │                       │                                  │
     │                       ├─> [MOUSEMOVE] ──> Atualiza preview/snap
     │                       │
     │                       ├─> [Dígito 0-9] ─> Adiciona ao buffer numérico
     │                       │
     │                       ├─> [TAB] ────────> Alterna campo ativo (Length/Angle)
     │                       │
     │                       ├─> [ENTER] ──────> _confirm_segment()
     │                       │                     │
     │                       │                     ├─> Fecha loop? ─> [Finaliza e reconstrói]
     │                       │                     └─> Continua? ───> Salva segmento e move origem
     │                       │
     │                       └─> [RMB / ESC] ──> [Cancela / Limpa Tudo]
```

### 2.2 Inserção de Aberturas com Snapping (`BTM_OT_InsertOpening`)
Implementa o comportamento interativo de arrasto e deslizamento de portas e janelas nas paredes:
1. **Ativação**: O operador é invocado abrindo uma janela de propriedades iniciais (Largura/Altura/Peitoril).
2. **Ciclo Modal**:
   - **Mapeamento Tridimensional**: Realiza raycast a partir da posição 2D do cursor no plano de projeção 3D do Blender.
   - **Cálculo da Distância de Snapping**: Projeta a coordenada de impacto em todos os segmentos das paredes existentes na cena (usando o algoritmo de menor distância ponto-segmento 2D).
   - **Transição Automática**: Se a distância até um segmento adjacente se torna menor do que a do segmento atual (ex: ao contornar quinas), a abertura altera seu pai para o novo segmento de parede, adotando instantaneamente sua rotação, espessura e direção.
   - **Movimentação Travada**: A abertura é travada localmente nos eixos X (comprimento) e Z (altura do peitoril). Não é possível arrastá-la para fora da parede.
   - **Cálculo de Cotas Visuais**: Calcula as distâncias do centro do preview até o início ($d_1$) e o fim ($d_2$) do segmento ativo e renderiza como linhas de extensão e dimensões em tempo real.
   - **Confirmação**: Cria o objeto cortador (`BTM_Porta_Cut` / `BTM_Janela_Cut`), realiza o parentesco e aplica o modificador `Boolean` em modo de diferença exata na parede-alvo.

---

## 3. Algoritmos Relevantes

### 3.1 Geração de Piso a partir do Contorno das Paredes (`_convex_hull_2d`)
Para ajustar o piso automaticamente, o sistema utiliza o algoritmo de **Graham Scan** para encontrar o fecho convexo dos vértices inferiores das paredes:
1. Encontra o ponto com menor coordenada Y (e menor X em caso de empate) como ponto inicial.
2. Ordena os demais pontos pelo ângulo polar em relação ao ponto inicial.
3. Filtra pontos duplicados ou excessivamente próximos.
4. Percorre os pontos ordenados mantendo uma pilha (hull) de vértices. Para cada ponto, realiza o produto vetorial 2D (cruzamento) para garantir que a curva continue no sentido anti-horário (ângulo à esquerda). Se o produto for $\le 0$, remove o topo da pilha (curva à direita/colinear).
5. Cria a malha poligonal plana conectando os vértices finais do fecho convexo em um único loop fechado.

### 3.2 Otimização de Plano de Corte (`optimize_nesting`)
Para planejar a produção do mobiliário na chapa de MDF de $2750 \times 1830$ mm, o add-on implementa um otimizador de nesting 2D baseado em **Guilhotina Híbrida com Shelf-Packing (Next-Fit Decreasing)**:
- **Pré-filtragem**: Verifica se cada peça cabe no espaço útil descontando a margem de refilo (padrão 10mm).
- **Ordenação**: Ordena todas as peças por área de corte decrescente.
- **Shelf Packing**:
  - Tenta colocar a peça nas prateleiras (shelves) existentes das chapas ativas, respeitando o sentido da fibra de madeira (grain direction). Se a rotação violar a fibra horizontal/vertical, ela é descartada.
  - Se a peça cabe em uma prateleira, ela é colocada adjacente às outras. O espaçamento da serra (kerf, padrão 4mm) é adicionado após cada peça.
  - Se a prateleira cresce em altura, a altura da prateleira é reajustada e a altura restante da chapa é reduzida.
  - Se não couber em nenhuma prateleira de nenhuma chapa existente, cria uma nova prateleira na chapa que possuir espaço vertical suficiente.
  - Se nenhuma chapa existente tiver espaço vertical, inicializa uma nova chapa de MDF e inicia uma prateleira com a peça.
- **Métricas**: Retorna a eficiência percentual de aproveitamento das chapas, número de chapas utilizadas e a lista de coordenadas exatas $(x, y)$ de cada peça.
