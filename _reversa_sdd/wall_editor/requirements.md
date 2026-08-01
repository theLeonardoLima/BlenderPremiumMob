# Módulo Wall Editor (Editor de Parede 🧱)

## Visão Geral
O módulo **wall_editor** implementa o Editor de Parede interativo com visualização GPU, snapping magnético, indicação angular, medição dinâmica em múltiplas unidades (`mm`, `cm`, `m`, `in`, `ft`), alternância de foco por tecla `TAB` e painel de propriedades editável com persistência de configurações globais.

## Botão e Menu Suspenso (Viewport UI & Header)
- **Ícone e Botão Principal**: Aparece na tela quando uma parede visível é selecionada ou ao clicar no botão **Editor de Parede** (`🧱`).
- **Menu Suspenso**:
  1. `🛠️ 1. CONSTRUIR PAREDE (MODO DE DESENHO INTERATIVO)`
  2. `🎛️ 2. PAINEL GRÁFICO DE PROPRIEDADES`

---

## Requisitos Funcionais

### 1. Construir Parede (Modo de Desenho Interativo)
- **RF-WE-01 (Snap Automático)**: Trava na aresta/extremidade mais próxima com tolerância magnética.
- **RF-WE-02 (Cota Dinâmica em Tempo Real)**: Exibe a distância em tempo real com unidade selecionável dinamicamente (`mm`, `cm`, `m`, `in`, `ft`).
- **RF-WE-03 (Indicador Angular Vetorizado)**: Exibe direção e inclinação (0°, 90°, 180°, 270°, 360°) com trava magnética configurável (padrão 45°).
- **RF-WE-04 (Transição Flexível de Aresta)**: Apaga a cota atual e fixa na nova aresta ao aproximar o cursor de outro vértice/parede.
- **RF-WE-05 (Digitação Direta de Comprimento)**: Permite digitação direta de valores numéricos na unidade padrão selecionada.
- **RF-WE-06 (Navegação Ciclicamente via Tecla TAB)**: A tecla `TAB` alterna ciclicamente entre os campos do Painel Gráfico durante o modo interativo.

### 2. Painel Gráfico de Propriedades (Editável em Qualquer Unidade)
- **RF-WE-07 (Dimensões da Parede)**:
  - Comprimento (Length - ex: 1700 mm / 170 cm / 1,70 m)
  - Altura (Height - ex: 2600 mm / 260 cm / 2,60 m)
  - Espessura (Thickness - ex: 150 mm / 15 cm / 0,15 m)
  - Afastamento / Nível (Elevation - ex: 0 mm / nível do chão)
  - Seletor de Unidades Linear: `['mm', 'cm', 'm', 'in', 'ft']`
- **RF-WE-08 (Ângulos e Posicionamento)**:
  - Ângulo Absoluto (Padrão 270° - aponta para baixo no plano)
  - Ângulo Relativo (Padrão 270° - em relação à parede anterior)
  - Orientação: `Direita` / `Esquerda` (lado da espessura no eixo)
- **RF-WE-09 (Incrementos e Comportamento)**:
  - Incremento Linear (Passo de ajuste: padrão 50 mm / 5 cm)
  - Incremento Angular (Trava magnética de rotação: padrão 45°)
  - Tipo da Parede: `Normal` / `Drywall`
- **RF-WE-10 (Definições Globais)**:
  - Checkbox `☑️ Utilizar valores como padrão`: Salva as configurações atuais em `scene.hb_wall_defaults` para as próximas paredes criadas.

---

## Critérios de Aceitação (Gherkin)

```gherkin
Cenário: Ativação do Construir Parede via Menu Suspenso 🧱
  Dado que o usuário clica no botão "Editor de Parede" 🧱 na 3D Viewport
  Quando seleciona a opção "1. CONSTRUIR PAREDE"
  Então o operador modal de desenho é ativado, exibindo a cota dinâmica em tempo real e o indicador angular vetorizado.

Cenário: Snap magnético e troca de unidade de medida
  Dado que o operador de desenho interativo de parede está ativo
  Quando o usuário aproxima o mouse de uma extremidade de parede e seleciona a unidade "cm"
  Então a cota dinâmica trava no vértice mais próximo e exibe o valor em centímetros (ex: "170 cm").

Cenário: Alternância de campos via tecla TAB
  Dado que o painel gráfico de propriedades da parede está visível no modal
  Quando o usuário pressiona a tecla TAB
  Então o foco do campo de entrada altera ciclicamente entre Comprimento, Altura, Espessura, Afastamento e Ângulo.

Cenário: Salvamento de valores padrão globais
  Dado que o usuário alterou a Espessura para 200 mm e o Tipo para Drywall
  Quando marca a opção "Utilizar valores como padrão" e clica em Salvar
  Então as próximas paredes iniciam automaticamente com 200 mm de espessura e Tipo Drywall.
```
