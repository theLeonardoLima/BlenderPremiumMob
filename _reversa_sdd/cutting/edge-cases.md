# Módulo Cutting, Casos de Borda

Este documento cataloga comportamentos extremos e limites do algoritmo de otimização de corte no **BlenderToMob**, no nível **Detalhado**.

---

## 1. Casos Extremos Catalogados

### 1.1 Peça Única Excedendo a Chapa Útil
* **Cenário**: O usuário adiciona um painel de móvel com comprimento de 2800mm (MDF padrão é 2750mm).
* **Comportamento Esperado**: O algoritmo detecta que a peça excede o espaço útil `usable_width` ou `usable_height` mesmo sob rotação de 90°.
* **Impacto**: O item é imediatamente rejeitado no início de `optimize_nesting` e adicionado à lista `unplaced` com o motivo `"Exceeds usable sheet size"`.
* **Mitigação**: O sistema funciona perfeitamente sem travar, retornando a lista de não-alocados para visualização do usuário no relatório. 🟢

### 1.2 Peça Estreita com Margem Grande de Serra (Kerf)
* **Cenário**: Lote com muitas peças de tamanho inferior a 20mm, em chapa com kerf de 4mm.
* **Comportamento Esperado**: A perda acumulada pelo consumo do corte da serra circular será extremamente alta em relação à área total de MDF utilizada.
* **Impacto**: A eficiência geral de aproveitamento cai drasticamente. Se a largura da peça for inferior ou igual ao kerf, pode haver falhas de precisão na modelagem de faixas.
* **Mitigação Recomendada**: Adicionar um limite mínimo de largura de peça no modelo (ex: mínimo de 15mm) impedindo a tentativa de nesting de tiras degeneradas. 🟡
