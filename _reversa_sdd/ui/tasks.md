# Módulo UI, Tarefas de Implementação

## Pré-requisitos
- Módulo `data` e `operators` registrados e funcionais.

## Tarefas

- [ ] T-01, Criar estrutura base de abas Sidebar do Blender
  - Origem no legado: `ui/panels.py:12`
  - Critério de pronto: Aba "BlenderToMob" aparece na barra lateral VIEW_3D.
  - Confiança: 🟢
- [ ] T-02, Implementar painel de propriedades de contexto reativo
  - Origem no legado: `ui/panels.py:82`
  - Critério de pronto: Selecionar objeto atualiza e exibe somente os campos de edição paramétrica correspondentes.
  - Confiança: 🟢
- [ ] T-03, Adicionar ocultação de aberturas e pisos baseada em paredes
  - Origem no legado: `ui/panels.py:58`
  - Critério de pronto: Sem paredes, esconde botões de portas/janelas e piso e exibe mensagem informativa de aviso.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Validar transição de exibição de painéis selecionando alternadamente paredes, armários e lâmpadas
- [ ] TT-02, Validar ocultação dinâmica excluindo todas as paredes da cena e verificando se os painéis de Piso/Abertura somem da Sidebar
