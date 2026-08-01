# Módulo Cutting, Tarefas de Implementação

## Pré-requisitos
- Lógica de modelagem paramétrica do armário deve estar pronta para fornecer a lista de peças ao nesting.

## Tarefas

- [ ] T-01, Implementar modelo de dados NestingPart e NestingSheet
  - Origem no legado: `cutting/nesting.py:1`
  - Critério de pronto: Permite instanciar peças com ID, tamanho, quantidade e direção do veio.
  - Confiança: 🟢
- [ ] T-02, Implementar algoritmo de encaixe em prateleiras guilhotinadas
  - Origem no legado: `cutting/nesting.py:26`
  - Critério de pronto: Distribui as peças respeitando kerf, refilo e restrições do veio amadeirado.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Testar com lote de 50 peças amadeiradas e verificar orientação do veio de madeira
- [ ] TT-02, Validar se as cotas de corte geradas respeitam o alinhamento de corte transversal completo (guilhotina)
