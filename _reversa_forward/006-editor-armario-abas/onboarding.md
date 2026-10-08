# Onboarding: testar o editor de armário em abas (006)

Pré-requisito: `python3 build.py`, instalar `caffmob_draw.zip` no Blender 5.2 e abrir um projeto vazio.

## 1. Abas

1. Insira um balcão frameless (Inserir › Frameless).
2. Selecione-o e use botão direito › Abrir editor de armário.
3. Confira o cabeçalho com o nome do módulo e as abas **Estrutura**, **Divisão** e **Acabamento**, com Estrutura aberta
   e Confirmar/Cancelar visíveis.
4. Troque de aba e confira que Confirmar, Cancelar e as mensagens continuam na tela.

## 2. Estrutura

1. Na Estrutura, digite uma largura nova e veja a prévia mudar.
2. Na lista, mude a espessura do **Tampo** para 18 mm. A linha passa a mostrar "alterado".
3. Clique no ✕ da **Lateral direita**: abre a janela com os três modos. Escolha "Manter tudo" e Remover. Ela some e
   fica marcada como removida. Clique em Restaurar.
4. Num módulo frameless, os modos "Estender as vizinhas" e "Reduzir o armário" da lateral aparecem desabilitados com
   o motivo. Na **Base**, "Estender as vizinhas" funciona.
5. Repita com um módulo `btm`: os três modos funcionam em todas as peças.

## 3. Divisão

1. Confira, no topo da aba Divisão, o material e a espessura da Divisória do Configurador para a linha do módulo.
   Altere-os no Configurador de Dimensões (por exemplo, MDP 15 mm) e volte.
2. Escolha Vertical, marque recuo na frente (20 mm) e clique em Adicionar. A chapa entra no meio do vão.
3. Clique na área livre à esquerda da chapa, na vista. O subvão é destacado e o nome aparece na aba.
4. Escolha Horizontal sem recuos e adicione. A chapa fica só no subvão esquerdo.
5. Na lista, digite 20 mm na posição da primeira chapa. Deve aparecer o erro `DIV-001`, e Confirmar fica bloqueado.
6. Corrija o valor, Confirme e dê Ctrl+Z. Tudo volta num passo só.

## 4. Produção e persistência

1. Confirme de novo e gere o plano de corte. As divisórias aparecem com a profundidade descontada do recuo, e a
   lateral removida não aparece.
2. Salve, feche e reabra o `.blend`. Remoções e divisões continuam lá.
3. Mude a largura do módulo pela barra lateral (fora do editor). As divisões acompanham o vão.
4. Use "Salvar como módulo", insira o módulo salvo e confira estrutura e divisões.

## 5. Testes automáticos

```bash
cd tests && python3 -m unittest test_cabinet_editor_divisions test_cabinet_editor_structure test_cabinet_editor_state \
    test_module_manifest test_i18n_coverage && cd ..
ruff check caffmob_draw/ && python3 docs/rag/tools/check_api.py
# precisa de janela; sem tela, use xvfb-run
xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_006_cabinet_editor_tabs_smoke.py
```
