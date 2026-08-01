# Módulo UI

## Visão Geral
O módulo **ui** provê a interface gráfica de usuário (painéis e layouts) integrada à barra lateral da Viewport 3D do Blender (Sidebar), permitindo a edição paramétrica intuitiva de paredes, aberturas, móveis e o acionamento de nesting.

## Responsabilidades
- Organizar ferramentas e opções na aba lateral `BlenderToMob` da Viewport 3D.
- Exibir propriedades paramétricas dinamicamente de acordo com o objeto selecionado (painel reativo de propriedades).
- Oferecer botões para disparo dos operadores de desenho CAD, construção de piso e plano de corte.

## Regras de Negócio
- **R-01 (Condicionalidade de Piso e Abertura)**: Os painéis de "Ajustar Limites do Piso" e "Inserir Porta/Janela" só devem ser exibidos se houver ao menos uma parede registrada na cena. 🟢
- **R-02 (Reatividade de Contexto)**: O painel de propriedades do add-on se ajusta automaticamente ao tipo do objeto ativo (`WALL`, `CABINET`, `OPENING`), exibindo apenas as propriedades relevantes àquela entidade. 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Renderização de painéis Sidebar na categoria "BlenderToMob" | Must | Aba é exposta corretamente na lateral ao pressionar a tecla N. |
| RF-02 | Polling dinâmico do objeto ativo para exibição de propriedades | Must | Selecionar um armário mostra apenas tamanho e chapa de MDF. |
| RF-03 | Ocultação automática de aberturas/pisos caso não existam paredes | Must | Se a contagem de paredes for zero, esconde os botões e exibe aviso. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Portabilidade | Layout 100% aderente ao guia de estilo visual nativo do Blender UI | `panels.py:42` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que a cena está vazia (sem paredes)
Quando o usuário abre a aba "BlenderToMob" na barra lateral
Então ele não vê os painéis "Piso" e "Aberturas", apenas "Paredes" e configurações globais
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| `PT_EnvironmentBuilder` | Must | Contém os botões primários de desenho de ambiente. |
| `PT_ContextProperties` | Must | Exibe os inputs de edição paramétrica de tamanho dos objetos. |
| `PT_NestingPanel` | Should | Permite disparar e visualizar o relatório de nesting. |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `blendertomob/ui/panels.py` | `BTM_PT_Environment` | 🟢 |
| `blendertomob/ui/panels.py` | `BTM_PT_ContextProperties` | 🟢 |
| `blendertomob/ui/panels.py` | `BTM_PT_Nesting` | 🟢 |
