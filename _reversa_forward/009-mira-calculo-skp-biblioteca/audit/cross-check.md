# Cross-check: 009-mira-calculo-skp-biblioteca (3ª rodada, depois do coding)

> Data: 2026-10-09. Auditoria só de leitura; nenhum artefato foi alterado.
> Artefatos analisados:
> - [`requirements.md`](../requirements.md)
> - [`roadmap.md`](../roadmap.md)
> - [`actions.md`](../actions.md)
>
> Entrada do titular nesta rodada:
> - (1) visualização "Textura com linha" na viewport;
> - (2) a porta nativa do addon cria "um bloco esquisito" e deve ser uma porta real, como os exemplos baixados do
>   3D Warehouse: `docs/porta_75x200x3,5cm.skp` e `docs/PORTA+0_80X2_10.skp`.
>
> Verificação feita: os dois `.skp` foram lidos pelo OpenSKP e importados num Blender temporário pelo
> `caffmob.import_model`; o código da porta de parede legada também foi lido.

## Resumo

| Severidade | Findings |
|---|---|
| CRITICAL | 0 |
| HIGH | 4 |
| MEDIUM | 3 |
| LOW | 1 |

## Findings

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| A001 | HIGH | Cobertura | A porta de parede do addon (Construir › Aberturas, `caffmob_doors_windows.place_door`) é uma caixa `GeoNodeCage` do tamanho do vão, com o texto "DOOR" e o arco de abertura: o "bloco 3D caixa com nome de porta" que o titular aponta. Nenhum RF, decisão ou ação da 009 trata dela; a 009 só cobre a biblioteca de objetos (Inserir › Objetos) | `caffmob_draw/operators/doors_windows.py` (`_PlaceWallObjectBase.create_placement_object`, ~l. 739); ausente em requirements §4-§5, roadmap §3, actions |
| A002 | HIGH | Cobertura | Não há requisito, decisão nem ação para o modo de visualização "Textura com linha" (sólido com textura + arestas). O legado só liga `overlay.show_wireframes` dentro das configurações recomendadas (`ops.py`, `show_wireframes`), sem um botão próprio | ausente em requirements, roadmap e actions; legado em `caffmob_draw/ops.py` l. 51 e 93-96 |
| A003 | HIGH | Consistência | O pedido de usar como porta nativa "portas reais obtidas do 3D Warehouse" contradiz a RN-09 da 009 (🟢): a licença do 3D Warehouse proíbe juntar esses modelos numa biblioteca redistribuída, e o `build.py` recusa um item embutido com origem "3D Warehouse". Os dois arquivos podem entrar na biblioteca **do usuário**, não no pacote | requirements RN-09, RF-07; roadmap D-13; actions T035; `build.py` (`package_problems`) |
| A004 | HIGH | Cobertura | A RN-14 ("componentes e grupos do SketchUp viram grupos de peças") não vale para componentes **aninhados**. Em `porta_75x200x3,5cm.skp`, a folha `Component_810` e as dobradiças e a maçaneta que estão dentro dela (`Component_1055`, `_1624`, `_1651`, duas de cada) chegam como 7 grupos soltos na raiz, sem a hierarquia. O `skp_core.plan` agrupa por caminho completo e cria tudo no topo. A fixture de teste (T046) e a fumaça (T039) só têm instâncias de primeiro nível, por isso não pegaram | requirements RN-14; roadmap D-16; actions T044, T045, T039, T046 |
| A005 | MEDIUM | Cobertura | Modelos do 3D Warehouse costumam trazer a figura de escala do SketchUp: `porta_75x200x3,5cm.skp` importa também o grupo `2D_Woman_Standing_Sandra` (660 × 83 × 1702 mm, 883 faces). Nenhuma regra diz se figuras de escala, câmeras ou textos do SketchUp devem ser ignorados na importação | requirements RN-14; roadmap D-16 |
| A006 | MEDIUM | Consistência | A Porta lisa 80 embutida (RF-07: "geometria simples e limpa") é uma folha lisa em caixa com um cilindro de maçaneta. O titular espera portas "reais", com detalhe comparável ao dos exemplos (batente com guarnição, maçaneta modelada, dobradiças). O critério de aceite do RF-07 não define nível de detalhe | requirements RF-07; roadmap D-13; actions T021 |
| A007 | MEDIUM | Consistência | `PORTA+0_80X2_10.skp` não tem material próprio (só `Layer_Layer0`, cor da camada). Cada importação gera um material novo com sufixo (`Layer_Layer0.002`): reimportar o mesmo arquivo duplica materiais. A D-16 não define o reaproveitamento de material com o mesmo nome do SketchUp | roadmap D-16; `aggregates/skp_build.py` (`_material`) |
| A008 | LOW | Coerência com o legado | A porta de parede legada tem `display_type = 'WIRE'` quando "mostrar caixas de portas e janelas" está desligado, e `'TEXTURED'` com `show_in_front` quando ligado. Um modo "Textura com linha" global precisa decidir como ele convive com esse ajuste por objeto | `operators/doors_windows.py` l. 749-753 |

## Impacto e direção (HIGH)

- **A001 (porta de parede em caixa).** Hoje o projetista vê um bloco com o texto "DOOR" no vão, e não uma porta. Isso
  está fora do escopo da 009. A direção é uma feature nova (`/reversa-requirements`): o vão continua sendo o
  `GeoNodeCage` que corta a parede (R-04 a R-08 do `_reversa_sdd/domain.md` dependem dele), mas ganha dentro dele uma
  porta real, que pode ser um item de porta da biblioteca de objetos da 009 (embutido ou do usuário), com batente e
  folha de giro (003/007).
- **A002 (Textura com linha).** É um pedido de visualização sem cobertura. A direção é incluí-lo na mesma feature
  nova: um botão de modo de vista (por exemplo Sólido · Textura · Textura com linha), com o efeito sobre a viewport e
  o convívio com o ajuste das caixas (A008) definidos no requirements.
- **A003 (3D Warehouse como porta nativa).** É conflito direto com a RN-09 e com a licença. A direção, para
  `/reversa-clarify` na feature nova, é escolher entre:
  - (a) portas reais **modeladas pelo projeto**, com o nível de detalhe dos exemplos, vindo com o plugin;
  - (b) a porta de parede usar **qualquer** item de porta da biblioteca, inclusive os que o usuário trouxe do 3D
    Warehouse para a biblioteca dele;
  - (a) e (b) juntas.

  Os dois `.skp` de exemplo servem como referência de forma e medidas e como teste local, e não devem ir para o
  pacote.
- **A004 (hierarquia do SketchUp).** É defeito da 009 frente à RN-14: uma porta com ferragens vira vários grupos
  soltos, e converter a folha em folha de porta deixa as dobradiças e a maçaneta para trás. A direção é corrigir na
  009 ou na feature nova (`/reversa-clarify` para decidir): montar os grupos com a mesma árvore do SketchUp (filho
  dentro do pai) e acrescentar à fixture uma instância aninhada, para a fumaça cobrir o caso.

## Itens verificados que passaram

**Cobertura**
- RF-01 a RF-13 da 009 têm decisão (D-01 a D-17) e ação concluída (43 de 43 `[X]`, T004, T009 e T017 removidas
  com motivo).
- Os dois `.skp` de exemplo **são lidos** pelo OpenSKP (SketchUp 21.0, VFF) e importados sem erro: a folha de
  `porta_75x200x3,5cm.skp` sai com 750 × 35 × 2000 mm e o material `<Wood-cherry>`. `PORTA+0_80X2_10.skp` sai com
  batente e guarnição (1000 × 210 × 2200), folha (840 × 30 × 2120) e maçaneta. A RN-13 vale para arquivos reais do
  3D Warehouse.

**Consistência**
- Os IDs citados (RN-01 a RN-14, RF-01 a RF-13, D-01 a D-17, T001 a T046) existem.
- O contrato `interfaces/object-library-item.md` está no roadmap §7 e é o formato gravado pelo `item_io`.

**Coerência com o legado**
- Nenhuma decisão da 009 contradiz as regras 🟢 do `_reversa_sdd/domain.md`. R-04 a R-08 (aberturas) não foram
  tocadas: a porta de parede continua a mesma, e é isso que o A001 aponta.

**Sanidade do actions**
- As dependências apontam para IDs existentes, não há ciclo, e nenhum par `[//]` compartilha arquivo.
