# Módulo Operators, Casos de Borda

Este documento cataloga comportamentos extremos e limites operacionais dos operadores modais no **BlenderToMob**, documentado no nível **Detalhado**.

---

## 1. Casos Extremos Catalogados

### 1.1 Inserção de Aberturas em Segmentos de Parede Curtos
* **Cenário**: O usuário tenta inserir uma porta com largura de 800mm em uma parede que possui comprimento total de 600mm.
* **Comportamento Esperado**: O fator de projeção $t$ é calculado em relação ao comprimento do segmento. Como o vão é maior que o segmento, a largura do vão sobressairá em relação às quinas da parede.
* **Impacto**: O modificador `Boolean` em modo `EXACT` ainda conseguirá realizar a diferença geométrica, porém criará faces degeneradas/órfãs nas laterais da parede.
* **Mitigação Recomendada**: Adicionar uma validação no operador modal para exibir um aviso vermelho de aviso ("Abertura excede o comprimento da parede") e travar a confirmação. 🟡

### 1.2 Fecho Convexo com Paredes Paralelas Afastadas (Piso)
* **Cenário**: O usuário constrói duas paredes retas paralelas sem fechá-las e aciona o "Ajustar Limites do Piso".
* **Comportamento Esperado**: O algoritmo de Convex Hull (`_convex_hull_2d`) coletará os vértices das bases de ambas as paredes e gerará um fecho convexo abrangendo o espaço entre elas.
* **Impacto**: Isso gera um piso retangular conectando as duas extremidades externas. Se houver concavidades no layout do cômodo (ex: formato em L), o Convex Hull ignorará as reentrâncias e gerará um piso estendido (passando por cima das paredes internas).
* **Mitigação Recomendada**: Implementar um algoritmo de geração por contorno poligonal (seguindo a conectividade dos vértices) em vez de um fecho convexo puro para suportar cômodos não-convexos. 🔴
