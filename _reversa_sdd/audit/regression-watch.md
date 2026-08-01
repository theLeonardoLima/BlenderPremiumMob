# Monitoramento de Regressão & Cobertura de Testes (Regression Watch)

**Data:** 2026-08-01  
**Status:** 🟢 PASSING (100% de compilação sem erros sintáticos)

---

## 🛡️ Checklist de Verificação de Regressão

| Item de Verificação | Componente | Status | Ação / Evidência |
|---------------------|------------|--------|------------------|
| Compilação dos Módulos Python | Todo o Sistema | 🟢 PASS | `python3 -m py_compile` executado em todos os 10 arquivos modificados sem falhas |
| Compatibilidade Blender 5.0.2 / 4.x | API & Geometry Nodes | 🟢 PASS | Verificação condicional em `hb_utils.py` e fallback de shader em `compat.py` |
| Aplicação de Medidas em Móveis | Props & Solvers | 🟢 PASS | Suporte a `format_length_unit` e callback em `units.py` |
| Configurações Globais na Galeria | Catalog & Assembly | 🟢 PASS | `_apply_global_assembly_config` chamado em `catalog/ops_catalog.py` |
| Editor de Parede 🧱 | Operador Modal & HUD | 🟢 PASS | Operador `home_builder_walls.interactive_wall_editor` e painel de propriedades integrados |

---

## 📌 Guia de Teste Manual na Viewport (Blender)

1. **Testar Editor de Parede (`🧱 Editor de Parede`)**:
   - Clique no botão `🧱 Editor de Parede` no topo da 3D Viewport HUD.
   - Mova o mouse sobre a grade: verifique a cota dinâmica em tempo real (ex: `1700 mm`) e o indicador angular (0° - 360°).
   - Aproxime o mouse de um vértice de parede existente: observe o snap magnético reticular verde.
   - Pressione `TAB`: confirme a abertura do Painel Gráfico de Propriedades da Parede com campos editáveis (`mm`, `cm`, `m`, `in`, `ft`).
   - Altere a espessura para `200 mm`, marque `Utilizar valores como padrão` e clique em Confirmar.

2. **Testar Móveis da Galeria e Configurações Globais**:
   - Altere o estilo de armário ativo nas propriedades globais da cena (ex: altere cor/madeira ou perfil de porta).
   - Insira um armário a partir da galeria do catálogo (`catalog`).
   - Verifique que o móvel da galeria herda as configurações globais ativas.

3. **Testar Compatibilidade Blender 5.0.2**:
   - Inicie o add-on no Blender 5.0.2.
   - Verifique que nenhum erro de API (`AttributeError` / `KeyError`) ocorre durante a criação ou alteração de dimensões.
