# Onboarding: editor no modelo do Construtor de Armários (008)

Pré-requisito: `python3 build.py`, instalar o `caffmob_draw.zip` no Blender 5.2 e inserir um balcão frameless e um
módulo paramétrico (`btm`) de 800 × 2250 × 550.

## 1. Fluxo

1. Abra o editor do `btm`. Confira:
   - as 7 abas, na ordem;
   - Estrutura aberta;
   - na barra da vista, "Selecionado: (nenhum)";
   - a cota interna de 770.
2. Clique numa área livre. O vão fica destacado e a barra diz "Selecionado: Vão 1".
3. Na Estrutura, desmarque "Lateral Direita 15mm". Ela some; marque de novo e ela volta.
4. Clique **Aplicar**. O editor continua aberto e Aplicar fica desabilitado. Faça outra mudança e clique **Cancelar**:
   o armário volta ao estado do Aplicar.

## 2. Abas reaproveitadas

1. **Divisões:** escolha Inserção múltipla, 3 verticais e Inserir. Surgem 4 subvãos iguais.
2. **Gavetas:** com um vão selecionado, escolha 4 e Inserir. As gavetas ocupam o vão da biblioteca.
3. **Portas:** escolha Ambas e um estilo e clique Inserir. A vista mostra as linhas de abertura. Com "Esquerda" +
   Inserir invertido, a porta sai com a dobradiça à direita.
4. **Fundos:** escolha Inteiro Recuado. O fundo recua 20 mm e as divisões encurtam junto.

## 3. Abas novas

1. **Internos:** com o vão de cima selecionado, escolha "Painel Forno Externo" e clique Inserir. Aparecem o painel com
   o recorte e o forno de referência.
2. **Deslizantes:** escolha Madeira › Gola Vertical 2L, 2 folhas, e clique Inserir. Mova a barra de abertura de uma
   folha: ela para na lateral e, ao fechar, no montante da outra.
3. **Estrutura completa:** marque Rodapés › Frontal e Pés Plásticos. Mude Número de vãos para 2. Selecione a divisória
   e use as setas: ela anda 10 mm por toque.

## 3a. Itens da sessão 2

1. Sem vão selecionado, o Inserir de todas as abas fica desabilitado com "Selecione um vão na vista".
2. Em Divisões, insira "Distanciador Duplo 30mm" num vão de 768: o vão fica com 738 livres, sem virar dois.
   Insira uma Divisória Móvel e confira a furação nas peças vizinhas, no plano de corte.
3. Em Gavetas › Internas, num balcão frameless, a gaveta sai atrás da porta, sem puxador. Em Gavetas, escolha um
   puxador e insira: as frentes saem com ele.

## 4. Produção

Gere o plano de corte. Devem aparecer o rodapé, os painéis, as folhas deslizantes e as divisões. Não devem aparecer
os pés nem o eletro de referência. A caixa **Ferragens** lista os pés, os pistões, as corrediças e os trilhos.
Exporte o JSON: `schema_version` é `2.2.0`, há a seção `hardware`, e a peça vizinha da divisória móvel traz `drilling`.

## 5. Testes automáticos

```bash
cd tests && python3 -m unittest test_cabinet_catalog test_cabinet_extras test_cabinet_bays test_cabinet_slides \
    test_cabinet_appliances test_cabinet_editor_divisions test_cabinet_hardware test_production_contracts \
    test_i18n_coverage && cd ..
ruff check caffmob_draw/ && python3 docs/rag/tools/check_api.py
xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_008_construtor_smoke.py
```
