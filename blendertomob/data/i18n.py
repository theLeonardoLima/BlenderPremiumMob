import bpy  # type: ignore

# Dicionário de traduções nativo do Blender
translations_dict = {
    "pt_BR": {
        ("*", "Construir Parede"): "Construir Parede",
        ("*", "Inserir Abertura"): "Inserir Abertura",
        ("*", "Remover Abertura"): "Remover Abertura",
        ("*", "Inserir Armário"): "Inserir Armário",
        ("*", "Largura"): "Largura",
        ("*", "Altura"): "Altura",
        ("*", "Profundidade"): "Profundidade",
        ("*", "Espessura"): "Espessura",
        ("*", "Espessura MDF"): "Espessura MDF",
        ("*", "Comprimento"): "Comprimento",
        ("*", "Afastamento"): "Afastamento",
        ("*", "Flecha"): "Flecha",
        ("*", "Peitoril"): "Peitoril",
        ("*", "Porta"): "Porta",
        ("*", "Janela"): "Janela",
        ("*", "Basculante"): "Basculante",
        ("*", "Configurações"): "Configurações",
        ("*", "Piso"): "Piso",
        ("*", "Módulos"): "Módulos",
        ("*", "Otimizar Plano de Corte"): "Otimizar Plano de Corte",
        ("*", "Plano de Corte (Nesting)"): "Plano de Corte (Nesting)",
        ("*", "Abertura Porta"): "Abertura Porta",
        ("*", "Sentido Abertura"): "Sentido Abertura",
        ("*", "Configurador de Dimensões"): "Configurador de Dimensões",
        ("*", "Material"): "Material",
        ("*", "Largura Máxima da Chapa"): "Largura Máxima da Chapa",
        ("*", "Comprimento Máximo da Chapa"): "Comprimento Máximo da Chapa",
        ("*", "Espessura da Chapa"): "Espessura da Chapa",
        ("*", "Fita Borda 1 (Superior)"): "Fita Borda 1 (Superior)",
        ("*", "Fita Borda 2 (Inferior)"): "Fita Borda 2 (Inferior)",
        ("*", "Fita Borda 3 (Direita/Traseira)"): "Fita Borda 3 (Direita/Traseira)",
        ("*", "Fita Borda 4 (Esquerda/Frontal)"): "Fita Borda 4 (Esquerda/Frontal)",
    },
    "en_US": {
        ("*", "Construir Parede"): "Build Wall",
        ("*", "Inserir Abertura"): "Insert Opening",
        ("*", "Remover Abertura"): "Remove Opening",
        ("*", "Inserir Armário"): "Insert Cabinet",
        ("*", "Largura"): "Width",
        ("*", "Altura"): "Height",
        ("*", "Profundidade"): "Depth",
        ("*", "Espessura"): "Thickness",
        ("*", "Espessura MDF"): "MDF Thickness",
        ("*", "Comprimento"): "Length",
        ("*", "Afastamento"): "Offset",
        ("*", "Flecha"): "Sagitta",
        ("*", "Peitoril"): "Sill Height",
        ("*", "Porta"): "Door",
        ("*", "Janela"): "Window",
        ("*", "Basculante"): "Flip Up",
        ("*", "Configurações"): "Settings",
        ("*", "Piso"): "Floor",
        ("*", "Módulos"): "Modules",
        ("*", "Otimizar Plano de Corte"): "Optimize Cut Plan",
        ("*", "Plano de Corte (Nesting)"): "Cut Plan (Nesting)",
        ("*", "Abertura Porta"): "Door Opening",
        ("*", "Sentido Abertura"): "Swing Direction",
        ("*", "Configurador de Dimensões"): "Dimension Configurator",
        ("*", "Material"): "Material",
        ("*", "Largura Máxima da Chapa"): "Max Sheet Width",
        ("*", "Comprimento Máximo da Chapa"): "Max Sheet Length",
        ("*", "Espessura da Chapa"): "Sheet Thickness",
        ("*", "Fita Borda 1 (Superior)"): "Edge Band 1 (Top)",
        ("*", "Fita Borda 2 (Inferior)"): "Edge Band 2 (Bottom)",
        ("*", "Fita Borda 3 (Direita/Traseira)"): "Edge Band 3 (Right/Back)",
        ("*", "Fita Borda 4 (Esquerda/Frontal)"): "Edge Band 4 (Left/Front)",
    }
}


def register():
    try:
        # Registra o dicionário de traduções no Blender
        bpy.app.translations.register(__name__, translations_dict)
    except Exception as e:
        print(f"Erro ao registrar traduções: {e}")


def unregister():
    try:
        bpy.app.translations.unregister(__name__)
    except Exception as e:
        print(f"Erro ao desregistrar traduções: {e}")
