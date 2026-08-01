# Módulo Operators, Tarefas de Implementação

## Pré-requisitos
- As classes PropertyGroup de `data/properties.py` e `hb_props.py` devem estar registradas na cena.
- Os utilitários de compatibilidade `hb_utils.py` e `blendertomob/compat.py` devem estar ativos.

## Tarefas

- [x] T-01, Implementar operador de paredes modal interativo
  - Origem no legado: `operators/wall_builder.py:12`
  - Critério de pronto: Loop de clicks gera segmentos corretos na Viewport; Enter e loop fechado gravam no JSON.
  - Confiança: 🟢
- [x] T-02, Implementar snapping interativo e transição de aberturas
  - Origem no legado: `operators/opening_builder.py:48`
  - Critério de pronto: Vão segue a rotação da parede mais próxima e transiciona para vizinhas nos cantos; Z do mouse controla peitoril de janelas.
  - Confiança: 🟢
- [x] T-03, Implementar ajuste de piso automático
  - Origem no legado: `operators/floor_builder.py:30`
  - Critério de pronto: Graham Scan gera malha de piso conforme o perímetro das paredes na cena.
  - Confiança: 🟢

## Tarefas de Correção e Auditoria (Reversa)

- [x] T-FIX-01, Garantir aplicação universal de medidas (largura, altura, profundidade) em todos os móveis
  - Origem no legado: `hb_props.py`, `hb_types.py`, `ops_placement.py`
  - Critério de pronto: Alterações de dimensão na UI/modal aplicam-se a armários, eletros, partes soltas e itens do catálogo sem perdas.
  - Confiança: 🟢
- [x] T-FIX-02, Aplicar configurações globais de montagem de armário nos móveis da galeria do catálogo
  - Origem no legado: `catalog/catalog_data.py`, `catalog/ops_catalog.py`, `ops_placement.py`
  - Critério de pronto: Móveis instanciados a partir da galeria herdam estilo ativo, materiais, recuos e perfis globais da cena.
  - Confiança: 🟢
- [x] T-FIX-03, Garantir compatibilidade total com versões do Blender (5.0.2, 4.x, 3.6+)
  - Origem no legado: `hb_utils.py`, `blendertomob/compat.py`, `__init__.py`, `blender_manifest.toml`
  - Critério de pronto: Leitura/escrita de entradas GN funciona via `mod[ident]` em Blender < 5.2 (incluindo 5.0.2) e via `properties.inputs` em 5.2+; shaders GPU possuem fallback para 3.6/4.x/5.x.
  - Confiança: 🟢

## Tarefas de Teste

- [x] TT-01, Testar feliz caminho do Construtor de Paredes (iniciar, mousemove, clicks, fechar loop)
- [x] TT-02, Testar feliz caminho da Abertura Modal (arrastar sobre parede, transição na quina, confirmar corte)
- [x] TT-03, Testar comportamento do buffer de digitação para cotas numéricas exatas
- [x] TT-04, Testar alteração de dimensões em móveis da galeria e verificar propagação das configurações globais de montagem
- [x] TT-05, Testar execução do add-on no Blender 5.0.2 sem exceções de API

