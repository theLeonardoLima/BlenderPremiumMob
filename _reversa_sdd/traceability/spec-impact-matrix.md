# Matriz de Impacto de Componentes — BlenderToMob

Este documento apresenta a matriz de impacto cruzada entre as especificações e os componentes técnicos do add-on **BlenderToMob**, conduzido pelo agente **Architect** no nível de documentação **Detalhado**.

---

## 1. Matriz de Impacto

A tabela abaixo cruza os componentes do sistema (colunas) com os demais componentes do add-on (linhas), indicando o grau de impacto que mudanças em um exercem sobre o outro:

* 🔴 **Forte Impacto**: Mudanças estruturais exigem refatoração completa do componente impactado.
* 🟡 **Médio Impacto**: Requer alteração pontual de assinaturas ou lógica de consumo.
* ⚪ **Sem Impacto / Baixo**: Mudanças são transparentes e não afetam o componente.

| Componente de Origem | data (Properties) | geometry (mesh_gen) | operators (Wall/Opening) | overlays (draw_handlers) | ui (panels) | cutting (nesting) |
|----------------------|:-----------------:|:-------------------:|:------------------------:|:------------------------:|:-----------:|:-----------------:|
| **data (Properties)** | - | 🔴 Forte | 🔴 Forte | 🟡 Médio | 🔴 Forte | ⚪ Baixo |
| **geometry (mesh_gen)**| ⚪ Baixo | - | 🔴 Forte | ⚪ Baixo | ⚪ Baixo | ⚪ Baixo |
| **operators** | 🟡 Médio | ⚪ Baixo | - | 🔴 Forte | 🟡 Médio | ⚪ Baixo |
| **overlays** | ⚪ Baixo | ⚪ Baixo | ⚪ Baixo | - | 🟡 Médio | ⚪ Baixo |
| **ui (panels)** | ⚪ Baixo | ⚪ Baixo | 🟡 Médio | ⚪ Baixo | - | 🟡 Médio |
| **cutting (nesting)** | ⚪ Baixo | ⚪ Baixo | ⚪ Baixo | ⚪ Baixo | 🟡 Médio | - |

---

## 2. Descrição das Relações de Dependência Críticas

1. **data → geometry, operators, ui (Forte Impacto 🔴)**:
   - Os dados paramétricos armazenados no módulo `data` servem como a única fonte de verdade para a engine de geometria e as janelas da interface lateral. Se uma propriedade de `properties.py` for renomeada, removida ou tiver seu tipo modificado:
     - O `mesh_gen.py` falhará em ler os argumentos de tamanho, gerando geometrias corrompidas ou zeradas.
     - Os operadores modais e painéis da UI lançarão erros de atributo (`AttributeError`) imediatos ao tentar renderizar ou atualizar valores no painel lateral.
2. **geometry → operators (Forte Impacto 🔴)**:
   - Mudanças nas funções de modelagem `generate_*` (especialmente assinaturas de parâmetros) impactam diretamente os operadores de criação de paredes, pisos e vãos. Se `generate_wall_from_segments` for modificada, o operador modal de paredes quebrará no método `_finish`.
3. **operators → overlays (Forte Impacto 🔴)**:
   - Os operadores modais interativos (`WallBuilder` e `InsertOpening`) dependem dos draw handlers em tempo real para pintar as cotas na viewport. Se a estrutura ou referências do `draw_handlers.py` mudarem, os builders modal falharão em iniciar ou deixarão de desenhar cotas, invalidando o feedback visual do usuário.
