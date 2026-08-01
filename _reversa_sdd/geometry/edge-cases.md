# Módulo Geometry, Casos de Borda

Este documento cataloga comportamentos extremos e limites operacionais da modelagem poligonal paramétrica no **BlenderToMob**, no nível **Detalhado**.

---

## 1. Casos Extremos Catalogados

### 1.1 Vértices Colineares ou Coincidentes (Graham Scan do Piso)
* **Cenário**: O usuário desenha paredes em linha reta perfeita ou coincidentes, resultando em múltiplos vértices de base alinhados (colineares).
* **Comportamento Esperado**: O Graham Scan tenta calcular a curvatura polar. Vértices colineares geram produto vetorial nulo ($\le 0$).
* **Impacto**: O algoritmo remove pontos intermediários. Se restarem menos de 3 vértices únicos e não-colineares, `bm.faces.new` falhará lançando uma exceção de faces inválidas.
* **Mitigação**: O código captura `ValueError` ao tentar criar a face, limpa e libera o bmesh e retorna `False` silenciosamente sem travar o Blender. 🟢

### 1.2 Espessura de MDF Maior que as Dimensões do Armário
* **Cenário**: O usuário configura a largura do armário para 100mm e a espessura da chapa para 50mm.
* **Comportamento Esperado**: As duas laterais ocupam $50 + 50 = 100$ mm de espaço.
* **Impacto**: A largura interna do armário é comprimida para 0. Tampo, base e fundo serão gerados com largura zero ou invertida (negativa).
* **Mitigação Recomendada**: Adicionar regras de restrição na interface limitando a espessura máxima da chapa a um terço da largura total do módulo. 🟡
