# Máquinas de Estado do Sistema — BlenderToMob

Este documento apresenta a especificação detalhada das máquinas de estado dos operadores modais e comportamentos dinâmicos do add-on **BlenderToMob**, conduzido pelo agente **Detective** no nível de documentação **Detalhado**.

---

## 1. Construtor de Parede Modal (`BTM_OT_WallBuilder`)

Esta máquina de estado gerencia a captura de coordenadas do cursor, buffer de entrada numérica via teclado e confirmação de segmentos polilinhas para geração geométrica final.

### 1.1 Diagrama de Estados (Mermaid)

```mermaid
stateDiagram-v2
    [*] --> Inativo
    
    Inativo --> AguardandoPrimeiroClick : Invoke (chamar operador)
    AguardandoPrimeiroClick --> Inativo : ESC ou RMB (Cancelar)
    
    AguardandoPrimeiroClick --> DesenhandoSegmento : Mouse Click (Z=0)
    note right of DesenhandoSegmento
        Marca vértice inicial da polilinha
    end note
    
    state DesenhandoSegmento {
        [*] --> EditandoMouse
        
        EditandoMouse --> DigitandoValor : Qualquer dígito numérico (0-9, ., -)
        note right of DigitandoValor
            buffer de string 'typed_value' ativo
        end note
        
        DigitandoValor --> DigitandoValor : Digitar mais caracteres
        DigitandoValor --> EditandoMouse : Backspace (apaga último caractere)
        
        DigitandoValor --> EditandoMouse : ENTER (Aplica valor digitado no campo ativo)
        
        EditandoMouse --> EditandoMouse : MOUSEMOVE (Atualiza preview de comprimento/ângulo)
        EditandoMouse --> EditandoMouse : TAB (Alterna campo ativo: Length, Angle, Thickness, Height)
        
        DigitandoValor --> EditandoMouse : TAB (Commit temporário e muda campo ativo)
    }
    
    DesenhandoSegmento --> DesenhandoSegmento : Mouse Click ou ENTER (sem digitação)
    note right of DesenhandoSegmento
        _confirm_segment(): Grava segmento em JSON local
        Reseta comprimento do mouse e move origem
    end note
    
    DesenhandoSegmento --> Finalizado : Click próximo ao ponto de partida (fecha loop)
    DesenhandoSegmento --> Finalizado : RMB (Finaliza polilinha aberta)
    DesenhandoSegmento --> Inativo : ESC (Cancela e descarta todos os segmentos)
    
    Finalizado --> Inativo : _finish(): Limpa draw handler e reconstrói malhas
```

---

## 2. Inserção de Aberturas interativa (`BTM_OT_InsertOpening`)

Esta máquina de estado controla o arrasto de portas e janelas nas paredes da cena, aplicando lógica de snapping 2D e peitoril vertical.

### 2.1 Diagrama de Estados (Mermaid)

```mermaid
stateDiagram-v2
    [*] --> Inativo
    
    Inativo --> ConfigurandoVao : Invoke (Janela de propriedades iniciais)
    ConfigurandoVao --> Inativo : Fechar caixa de diálogo
    ConfigurandoVao --> DeslizandoAbertura : Confirmar diálogo (OK)
    
    state DeslizandoAbertura {
        [*] --> TravadoNoSegmento
        
        TravadoNoSegmento --> TravadoNoSegmento : MOUSEMOVE (Busca parede mais próxima e snappa)
        TravadoNoSegmento --> TransicaoDeParede : MOUSEMOVE (Distância até parede adjacente é menor)
        TransicaoDeParede --> TravadoNoSegmento : Adota nova rotação, normal e espessura
        
        TravadoNoSegmento --> EditandoDimensoes : Qualquer dígito numérico
        EditandoDimensoes --> EditandoDimensoes : Digitar caracteres adicionais
        EditandoDimensoes --> TravadoNoSegmento : ENTER (Aplica cota de afastamento ou peitoril)
        
        TravadoNoSegmento --> TravadoNoSegmento : TAB (Alterna entre cota de Afastamento e Peitoril)
    }
    
    DeslizandoAbertura --> Inativo : ESC ou RMB (Cancela e remove preview_obj)
    DeslizandoAbertura --> Aplicado : Mouse Click ou ENTER (Confirma inserção)
    
    Aplicado --> Inativo : _confirm_insertion(): Cria cortador real, aplica Boolean e finaliza
```
