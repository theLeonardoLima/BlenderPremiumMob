# Módulo Data, Casos de Borda

Este documento cataloga comportamentos extremos e limites do módulo de dados no **BlenderToMob**, no nível **Detalhado**.

---

## 1. Casos Extremos Catalogados

### 1.1 JSON corrompido em `btm_wall_segments`
* **Cenário**: O usuário altera o valor da propriedade customizada `"btm_wall_segments"` de forma manual (digitando caractere inválido ou quebrando a sintaxe JSON).
* **Comportamento Esperado**: O parser `json.loads` lança uma exceção `json.JSONDecodeError` no callback `update_wall_geom`.
* **Impacto**: O callback captura a exceção no bloco `except Exception: pass` e executa a ramificação de fallback.
* **Mitigação**: O add-on reconstrói a parede como um segmento reto simples baseado nos parâmetros individuais (`length`, `thickness`, `height_start`), garantindo que não haja falha fatal no Blender. 🟢

### 1.2 Registro Concorrente em Objetos Não-Malha (Curvas, Luzes)
* **Cenário**: O ponteiro `bpy.types.Object.btm_wall` é registrado de forma global em todos os objetos da cena. O usuário altera a espessura da parede em uma lâmpada ou câmera.
* **Comportamento Esperado**: A propriedade está disponível no objeto de lâmpada, mas ao alterar o valor, o callback `update_wall_geom` verifica `if obj and obj.type == 'MESH'`.
* **Impacto**: Como a lâmpada é tipo `'LIGHT'`, a mutação geométrica é ignorada e nada acontece.
* **Mitigação**: Validação explícita de tipo de objeto no início de todos os callbacks reativos, mantendo a consistência dos dados da cena. 🟢
