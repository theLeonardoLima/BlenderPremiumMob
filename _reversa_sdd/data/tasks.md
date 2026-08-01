# Módulo Data, Tarefas de Implementação

## Pré-requisitos
- Nenhum (módulo base de persistência).

## Tarefas

- [ ] T-01, Definir e registrar PropertyGroups paramétricos
  - Origem no legado: `data/properties.py:43`
  - Critério de pronto: Propriedades de parede, vãos, armários e cena expostas na API `bpy`.
  - Confiança: 🟢
- [ ] T-02, Implementar callbacks de reatividade de malhas
  - Origem no legado: `data/properties.py:9`
  - Critério de pronto: Alterações de propriedades invocam mesh generators correspondentes e regeneram malhas.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Validar registro e desregistro (register/unregister) sem erros ou vazamento de classes na API do Blender
- [ ] TT-02, Testar persistência de valores de propriedades customizadas salvando e reabrindo um arquivo `.blend`
