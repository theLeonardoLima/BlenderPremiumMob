# Módulo UI, Casos de Borda

Este documento cataloga comportamentos extremos e limites operacionais da interface gráfica Sidebar no **BlenderToMob**, no nível **Detalhado**.

---

## 1. Casos Extremos Catalogados

### 1.1 Múltiplos Objetos de Tipos Diferentes Selecionados Concorrentemente
* **Cenário**: O usuário seleciona uma parede e um armário paramétrico ao mesmo tempo usando Shift+Click.
* **Comportamento Esperado**: O painel reativo `PT_ContextProperties` recupera `context.active_object` para definir quais campos desenhar.
* **Impacto**: O Blender define apenas um objeto como o "Ativo" (normalmente o último selecionado, com contorno amarelo mais claro), enquanto o outro é considerado "Selecionado" (contorno laranja).
* **Mitigação**: O painel reativo desenhará apenas as propriedades do objeto Ativo correspondente. Isso é o comportamento padrão e esperado na usabilidade do Blender. 🟢

### 1.2 Viewport com Resolução Muito Baixa ou Painel Sidebar Estreito
* **Cenário**: O usuário encolhe a largura da barra lateral (Sidebar) para o tamanho mínimo ou utiliza um monitor de resolução muito baixa.
* **Comportamento Esperado**: Os rótulos de texto e campos numéricos serão espremidos horizontalmente.
* **Impacto**: Textos longos de propriedades paramétricas (ex: `"Espaçamento de Snap do Grid"`) serão truncados, impossibilitando a leitura completa.
* **Mitigação Recomendada**: Utilizar abreviações claras e layout em duas colunas verticais (`layout.column(align=True)`) com rótulos compactados para melhor aproveitamento do espaço de tela. 🟡
