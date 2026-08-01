# Módulo Cutting

## Visão Geral
O módulo **cutting** é uma engine algorítmica em Python puro responsável por otimizar a distribuição de peças retangulares de mobiliário sobre chapas de MDF comerciais, minimizando sobras de material e respeitando restrições físicas de corte e textura.

## Responsabilidades
- Otimizar a disposição bidimensional de peças amadeiradas em chapas ($2750 \times 1830$ mm).
- Respeitar a orientação do veio da madeira (`grain_direction`) impedindo rotações inválidas.
- Descontar as larguras de corte da serra circular (kerf) e margens de limpeza (refilo).

## Regras de Negócio
- **R-01 (Margem de Refilo)**: Toda chapa nova recebe um desconto de refilo (padrão 10mm) em suas 4 bordas antes do cálculo de área útil. 🟢
- **R-02 (Perda por Kerf)**: Cada linha de corte consome uma largura fixa correspondente à serra (padrão 4mm). 🟢
- **R-03 (Alinhamento de Fibra)**: Peças com `grain_direction` igual a `VERTICAL` ou `HORIZONTAL` são proibidas de rotacionar fora do eixo correspondente. 🟢
- **R-04 (Corte Guilhotinado)**: Os cortes devem ser transversais contínuos de ponta a ponta na chapa (organização por prateleiras/shelves). 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Otimização de chapa via Next-Fit Decreasing | Must | Peças de área maior são empacotadas primeiro nas prateleiras. |
| RF-02 | Filtro de dimensões limites da peça | Must | Peças que excedem a chapa útil são rejeitadas e listadas como unplaced. |
| RF-03 | Controle de rotação condicional pela fibra | Must | Se grain_direction for travado, impede rotação de 90° no encaixe. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | Encaixe de sub-segundo para lotes de até 500 peças | `nesting.py:78` | 🟡 |
| Portabilidade | Lógica pura Python sem dependência de APIs externas | `nesting.py:1` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que há chapas livres e uma lista de peças amadeiradas ordenadas
Quando o algoritmo processa uma peça com grain_direction = VERTICAL
Então o algoritmo nunca a rotaciona horizontalmente nas prateleiras da chapa
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| `optimize_nesting` | Must | Função central do algoritmo de nesting. |
| `can_fit_in_shelf` | Must | Regra crítica de validação de rotação e fibra por prateleira. |
| `grain_direction` | Should | Importante para estética, mas pode rodar sem textura. |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `blendertomob/cutting/nesting.py` | `NestingPart` | 🟢 |
| `blendertomob/cutting/nesting.py` | `optimize_nesting` | 🟢 |
