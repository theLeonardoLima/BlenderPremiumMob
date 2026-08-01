# Dicionário de Dados Completo — BlenderToMob

Este documento apresenta o dicionário de dados formal e completo do add-on **BlenderToMob**, mapeado pelo agente **Archaeologist** no nível de documentação **Detalhado**.

---

## 1. Mapeamento das Entidades Paramétricas

### 1.1 Segmento de Parede (`BTM_PG_WallSegment`)
Esta estrutura de dados gerencia a definição paramétrica de um segmento de parede individual na cena. É registrada como um pointer property em `bpy.types.Object.btm_wall`.

| Propriedade | Tipo | Subtipo | Padrão | Mínimo | Máximo | Callback de Update | Descrição | Certeza |
|-------------|------|---------|--------|--------|--------|--------------------|-----------|----------|
| `length` | Float | - | 2000.0 | 10.0 | 100000.0 | `update_wall_geom` | Comprimento linear do segmento de parede em milímetros. | 🟢 CONFIRMADO |
| `absolute_angle` | Float | `ANGLE` | 0.0 | -360.0 | 360.0 | - | Ângulo absoluto em relação ao sistema global de coordenadas do Blender (em graus). | 🟢 CONFIRMADO |
| `relative_angle` | Float | `ANGLE` | 0.0 | -360.0 | 360.0 | - | Ângulo do segmento medido em relação ao segmento anterior da polilinha (em graus). | 🟢 CONFIRMADO |
| `thickness` | Float | - | 150.0 | 10.0 | 2000.0 | `update_wall_geom` | Espessura física da extrusão lateral da parede em milímetros. | 🟢 CONFIRMADO |
| `height_start` | Float | - | 2700.0 | 100.0 | 10000.0 | `update_wall_geom` | Altura vertical da parede no ponto inicial em milímetros (Pé-Direito inicial). | 🟢 CONFIRMADO |
| `height_end` | Float | - | 2700.0 | 100.0 | 10000.0 | `update_wall_geom` | Altura vertical da parede no ponto final em milímetros (Pé-Direito final). | 🟢 CONFIRMADO |
| `offset` | Float | - | 0.0 | - | - | - | Afastamento vertical (elevação) da base da parede em relação ao plano de piso Z=0. | 🟢 CONFIRMADO |
| `sagitta` | Float | - | 0.0 | - | - | - | Flecha do arco de curvatura para modelagem de paredes redondas em milímetros. | 🟢 CONFIRMADO |
| `linear_increment` | Float | - | 50.0 | 1.0 | 1000.0 | - | Intervalo de incremento linear (passo de snap) em milímetros para o cursor de desenho. | 🟢 CONFIRMADO |
| `angular_increment` | Float | `ANGLE` | 5.0 | 0.5 | 90.0 | - | Passo de incremento angular em graus para o ajuste de inclinação via cursor. | 🟢 CONFIRMADO |
| `orientation` | Enum | - | `RIGHT` | - | - | - | Lado do alinhamento da espessura em relação ao eixo da parede (`RIGHT` = Direita/Horário, `LEFT` = Esquerda/Anti-horário). | 🟢 CONFIRMADO |
| `wall_type` | Enum | - | `NORMAL` | - | - | - | Preset de estilo e materialização da parede (`NORMAL` = Alvenaria, `DRYWALL` = Gesso, `GLASS` = Divisória de Vidro). | 🟢 CONFIRMADO |
| `use_as_default` | Bool | - | `False` | - | - | - | Salva as propriedades atuais para serem usadas como default em novos segmentos. | 🟢 CONFIRMADO |

### 1.2 Plano de Inserção (`BTM_PG_InsertionPlane`)
Registrado em `bpy.types.Object.btm_plane`. Mapeia metadados espaciais e físicos necessários para as regras de snapping e colisão de arrasto de mobiliário.

| Propriedade | Tipo | Padrão | Valores Válidos | Descrição | Certeza |
|-------------|------|--------|-----------------|-----------|----------|
| `object_kind` | Enum | `WALL` | `WALL`, `FLOOR`, `MODULE`, `GEOMETRY`, `OPENING` | Classificação da entidade no add-on para identificação na hierarquia espacial. | 🟢 CONFIRMADO |
| `parent_plane` | Pointer | - | `bpy.types.Object` | Referência direta ao objeto pai na árvore espacial (hospedeiro). | 🟢 CONFIRMADO |
| `layer_id` | String | `"Default"` | - | Nome ou ID da camada à qual o plano pertence (usado no Promob para ocultar/isolar). | 🟢 CONFIRMADO |
| `collision_override` | Enum | `INHERIT` | `INHERIT`, `ON`, `OFF` | Permite ligar ou desligar colisões de física localmente por objeto, ignorando a configuração global da cena. | 🟢 CONFIRMADO |

### 1.3 Propriedades de Vãos de Abertura (`BTM_PG_OpeningProperties`)
Registrado em `bpy.types.Object.btm_opening`. Controla vãos de portas e janelas associados a paredes.

| Propriedade | Tipo | Padrão | Mínimo | Máximo | Descrição | Certeza |
|-------------|------|--------|--------|--------|-----------|----------|
| `opening_type` | Enum | `DOOR` | `DOOR`, `WINDOW` | Categoria da abertura que define o comportamento de movimentação vertical (Porta ou Janela). | 🟢 CONFIRMADO |
| `width` | Float | 800.0 | 100.0 | 5000.0 | Largura física em milímetros do vão que será subtraído da parede. | 🟢 CONFIRMADO |
| `height` | Float | 2100.0 | 100.0 | 5000.0 | Altura física em milímetros do vão que será subtraído da parede. | 🟢 CONFIRMADO |
| `sill_height` | Float | 0.0 | 0.0 | 5000.0 | Altura do peitoril a partir da base em milímetros (janelas). Obrigatoriamente zero para portas. | 🟢 CONFIRMADO |
| `parent_wall` | Pointer | - | `bpy.types.Object` | Referência ao objeto de parede correspondente que hospeda e é recortado pela abertura. | 🟢 CONFIRMADO |

### 1.4 Propriedades de Módulos de Armário (`BTM_PG_CabinetProperties`)
Registrado em `bpy.types.Object.btm_cabinet`. Controla as dimensões paramétricas dos armários modulares de MDF.

| Propriedade | Tipo | Padrão | Mínimo | Máximo | Callback de Update | Descrição | Certeza |
|-------------|------|--------|--------|--------|--------------------|-----------|----------|
| `width` | Float | 800.0 | 100.0 | 3000.0 | `update_cabinet_geom` | Largura externa total do módulo em milímetros. | 🟢 CONFIRMADO |
| `height` | Float | 700.0 | 100.0 | 3000.0 | `update_cabinet_geom` | Altura externa total do módulo em milímetros. | 🟢 CONFIRMADO |
| `depth` | Float | 550.0 | 100.0 | 2000.0 | `update_cabinet_geom` | Profundidade externa total do módulo em milímetros. | 🟢 CONFIRMADO |
| `thickness` | Float | 18.0 | 6.0 | 50.0 | `update_cabinet_geom` | Espessura das placas de MDF/MDP (laterais, base, tampo, prateleiras) em milímetros. | 🟢 CONFIRMADO |
| `cabinet_type` | Enum | `BASE` | `BASE`, `WALL`, `TALL` | Categoria do módulo (`BASE` = Balcão Inferior, `WALL` = Aéreo, `TALL` = Paneleiro/Torre). | 🟢 CONFIRMADO |

### 1.5 Configurações Globais da Cena (`BTM_PG_SceneSettings`)
Registrado em `bpy.types.Scene.btm_settings`. Controla os ajustes ambientais, snaps e overlays visuais ativos na Viewport.

| Propriedade | Tipo | Padrão | Mínimo | Máximo | Descrição | Certeza |
|-------------|------|--------|--------|--------|-----------|----------|
| `snap_grid` | Bool | `True` | - | - | Ativa globalmente o snap posicional para movimentação de módulos. | 🟢 CONFIRMADO |
| `snap_increment` | Float | 50.0 | 1.0 | 1000.0 | Tamanho da grade de snap em milímetros. | 🟢 CONFIRMADO |
| `collision_global` | Bool | `True` | - | - | Liga/desliga o cálculo de prevenção de colisões físicas entre os objetos de marcenaria. | 🟢 CONFIRMADO |
| `show_grid` | Bool | `True` | - | - | Controla a exibição visual da grade de orientação no plano de piso Z=0. | 🟢 CONFIRMADO |
| `grid_spacing_x` | Float | 500.0 | 50.0 | 5000.0 | Intervalo horizontal das linhas da grade de piso em milímetros. | 🟢 CONFIRMADO |
| `grid_spacing_y` | Float | 500.0 | 50.0 | 5000.0 | Intervalo vertical das linhas da grade de piso em milímetros. | 🟢 CONFIRMADO |
| `grid_snap_enabled`| Bool | `True` | - | - | Se ativo, os módulos serão atraídos para as linhas do grid do piso ao serem movidos. | 🟢 CONFIRMADO |
| `grid_snap_gap` | Float | 50.0 | 5.0 | 500.0 | Distância limite em milímetros na qual o snap de atração magnética do grid é ativado. | 🟢 CONFIRMADO |
| `show_insertion_plane`| Bool | `True`| - | - | Exibe o realce visual (sombreamento amarelo) no plano de inserção sob o cursor. | 🟢 CONFIRMADO |
| `show_dimensions` | Bool | `True` | - | - | Ativa a renderização de linhas de cota e dimensões na viewport. | 🟢 CONFIRMADO |

---

## 2. Dicionário de Persistência Interna (Custom Properties)

O add-on utiliza propriedades internas do Blender (armazenadas em dicionários `IDPropertyGroup` nos próprios objetos) para persistir estruturas mais complexas que não possuem correspondência direta na API nativa `bpy.props`:

### 2.1 Polilinha de Parede (`btm_wall_segments`)
Armazenado como propriedade dinâmica no objeto de parede (ex: `obj["btm_wall_segments"]`).
* **Tipo:** String contendo um dump JSON serializado.
* **Schema JSON:**
  ```json
  [
    {
      "start": [float, float],     // Coordenada X, Y inicial em mm
      "end": [float, float],       // Coordenada X, Y final em mm
      "thickness": float,          // Espessura do segmento em mm
      "height": float,             // Altura do segmento em mm
      "offset": float              // Elevação em mm
    }
  ]
  ```
* **Uso:** Preserva a estrutura de polilinhas gerada pelo operador modal de parede, permitindo a atualização dos parâmetros sem colapsar os segmentos em uma única parede retilínea simples.
