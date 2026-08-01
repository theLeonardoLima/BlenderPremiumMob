# Módulo Cutting, Design Técnico

## Interface

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `optimize_nesting` | `(parts, sheet_width, sheet_height, refilo, kerf)` | `dict` | Retorna lista de chapas organizadas, itens unplaced e estatísticas. |
| `can_fit_in_shelf` | `(part, shelf, usable_width, remaining_height, kerf)` | `(bool, bool)` | Retorna (cabe, rotacionada). Verifica grão de madeira. |

## Fluxo Principal — Otimização de Chapas
1. Subtrai o refilo bidimensional da chapa para definir a área de corte disponível (`usable_width` e `usable_height`).
2. Filtra peças cujo tamanho exceda as dimensões úteis.
3. Desmembra quantidades em itens únicos (`flat_parts`).
4. Ordena os itens por área (`width * height`) de forma decrescente.
5. Para cada item:
   - Tenta posicioná-lo horizontalmente nas prateleiras existentes das chapas ativas (`can_fit_in_shelf`).
   - Se não couber, tenta criar uma nova prateleira horizontal no topo da chapa ativa (`can_create_shelf_in_sheet`).
   - Se não couber na chapa ativa, inicializa uma nova chapa física de MDF e inicia uma prateleira nela.
6. Agrupa as coordenadas de cada chapa e calcula a eficiência percentual de aproveitamento de matéria-prima.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Organização por faixas horizontais de prateleiras | `nesting.py:82` | 🟢 |
| Ordenação prévia por área decrescente | `nesting.py:78` | 🟢 |

## Estado Interno
O módulo é stateless, recebendo dados puros por parâmetro e retornando estruturas de dados limpas em formato de dicionário Python.

## Riscos e Lacunas
- 🟡 A limitação de cortes guilhotinados simplifica a execução, porém reduz a eficiência de aproveitamento em cerca de 5-10% se comparada a algoritmos de empacotamento livre bidimensional.
