# Módulo Overlays, Casos de Borda

Este documento cataloga comportamentos extremos e limites operacionais dos desenhos gráficos acelerados na GPU no **BlenderToMob**, no nível **Detalhado**.

---

## 1. Casos Extremos Catalogados

### 1.1 Fechamento Repentino do 3D Viewport com Handler Ativo
* **Cenário**: O usuário fecha a aba ou janela do Viewport 3D enquanto o operador modal ou desenhador global de grade está ativo na fila de renderização.
* **Comportamento Esperado**: O Blender desvincula o escopo do painel, mas o handler permanece registrado na fila `draw_handler_add`.
* **Impacto**: Ao tentar desenhar, referências de contexto (`context.space_data` ou `context.region`) serão resolvidas como `None` ou do tipo inválido, disparando exceções Python contínuas no console (excluindo logs da viewport).
* **Mitigação**: O callback do handler valida de forma defensiva no início de cada execução: `if not context.space_data or context.space_data.type != 'VIEW_3D': return`. 🟢

### 1.2 Tamanho do Grid Zerado ou Negativo
* **Cenário**: O usuário altera o espaçamento da grade (`grid_spacing_x` ou `grid_spacing_y`) nas configurações globais da cena para $0.0$.
* **Comportamento Esperado**: O loop de repetição de linhas de grade tentará dividir por zero ou iterar infinitamente se o passo de incremento for nulo.
* **Impacto**: O Blender trava por loop infinito ou lança exceção `ZeroDivisionError`.
* **Mitigação**: Os campos na interface possuem limite mínimo configurado para $10.0$ mm na API `bpy.props`, impedindo a inserção de valores nulos ou negativos. 🟢
