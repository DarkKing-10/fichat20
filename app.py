import streamlit as st
import json
import base64
from PIL import Image
import io
import os

# Configuração da página
st.set_page_config(
    page_title="Ficha T20",
    page_icon="🎲",
    layout="wide"
)

# Função para converter imagem para base64
def image_to_base64(image):
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        st.error(f"Erro ao converter imagem: {str(e)}")
        return None

# Função para converter base64 para imagem
def base64_to_image(base64_string):
    try:
        if base64_string:
            image_data = base64.b64decode(base64_string)
            return Image.open(io.BytesIO(image_data))
        return None
    except Exception as e:
        st.error(f"Erro ao converter base64 para imagem: {str(e)}")
        return None

# Função para calcular modificador
def calcular_modificador(valor):
    return (valor - 10) // 2

# Função para calcular bônus de perícia
def calcular_bonus_pericia(atributo, treinada, nivel):
    bonus = calcular_modificador(atributo)
    if treinada:
        bonus += (nivel // 2)+2  # Bônus de treinamento é metade do nível
    return bonus

# Função para atualizar o nível da classe
def atualizar_nivel_classe(index):
    # Preservar o estado atual da ficha
    ficha_atual = st.session_state.ficha.copy()
    
    # Atualizar o nível da classe
    ficha_atual["classes"][index]["nivel"] = st.session_state[f"classe_nivel_{index}"]
    
    # Recalcular o nível total
    ficha_atual["nivel"] = sum(classe["nivel"] for classe in ficha_atual["classes"])
    
    # Atualizar o estado da sessão com a ficha completa
    st.session_state.ficha = ficha_atual

# Função para calcular defesa
def calcular_defesa(atributos, bonus_equipamento=0, usar_atributo=True, atributo="destreza", bonus_reflexo=0):
    defesa = 10
    if usar_atributo:
        defesa += calcular_modificador(atributos[atributo])
    defesa += bonus_equipamento
    defesa += bonus_reflexo
    return defesa

# Função para calcular deslocamento
def calcular_deslocamento(atributos, armadura=None, raca=None):
    deslocamento = 9  # Base padrão
    if raca:
        # Ajuste baseado na raça (exemplo)
        if raca.lower() in ["humano", "elfo", "meio-elfo"]:
            deslocamento = 9
        elif raca.lower() in ["anão", "meio-orc"]:
            deslocamento = 6
        elif raca.lower() == "halfling":
            deslocamento = 6
    
    # Ajuste por armadura
    if armadura:
        if armadura.get("tipo", "").lower() == "pesada":
            deslocamento = max(6, deslocamento - 3)
        elif armadura.get("tipo", "").lower() == "média":
            deslocamento = max(6, deslocamento - 2)
        elif armadura.get("tipo", "").lower() == "leve":
            deslocamento = max(6, deslocamento - 1)
    
    return deslocamento

# Função para calcular carga máxima
def calcular_carga_maxima(forca):
    return forca * 3

# Função para calcular penalidade de carga
def calcular_penalidade_carga(carga_atual, carga_maxima):
    if carga_atual <= carga_maxima * 0.5:
        return 0, "Sem penalidade"
    elif carga_atual <= carga_maxima:
        return -2, "Sobrecarregado (-2 em testes de Força e Destreza)"
    elif carga_atual <= carga_maxima * 1.5:
        return -4, "Sobrecarregado (-4 em testes de Força e Destreza)"
    elif carga_atual <= carga_maxima * 2:
        return -6, "Sobrecarregado (-6 em testes de Força e Destreza)"
    else:
        return -8, "Sobrecarregado (-8 em testes de Força e Destreza)"

# Função para atualizar carga total
def atualizar_carga_total():
    # Preservar o estado atual da ficha
    ficha_atual = st.session_state.ficha.copy()
    
    # Calcular carga total dos itens
    carga_total = sum(item["peso"] * item["quantidade"] for item in ficha_atual["inventario"]["itens"])
    
    # Atualizar carga atual
    ficha_atual["inventario"]["carga"]["atual"] = carga_total
    
    # Atualizar o estado da sessão com a ficha completa
    st.session_state.ficha = ficha_atual

# Função para atualizar item
def atualizar_item(index):
    # Preservar o estado atual da ficha
    ficha_atual = st.session_state.ficha.copy()
    
    # Atualizar o item
    ficha_atual["inventario"]["itens"][index] = st.session_state[f"item_{index}"]
    
    # Recalcular carga total
    carga_total = sum(item["peso"] * item["quantidade"] for item in ficha_atual["inventario"]["itens"])
    ficha_atual["inventario"]["carga"]["atual"] = carga_total
    
    # Atualizar o estado da sessão com a ficha completa
    st.session_state.ficha = ficha_atual

# Lista de perícias do T20
PERICIAS = {
    "Acrobacia": {"atributo_padrao": "destreza", "penalidade_armadura": True},
    "Adestramento": {"atributo_padrao": "carisma", "penalidade_armadura": False},
    "Atletismo": {"atributo_padrao": "forca", "penalidade_armadura": True},
    "Atuação": {"atributo_padrao": "carisma", "penalidade_armadura": False},
    "Cavalgar": {"atributo_padrao": "destreza", "penalidade_armadura": True},
    "Conhecimento": {"atributo_padrao": "inteligencia", "penalidade_armadura": False},
    "Cura": {"atributo_padrao": "sabedoria", "penalidade_armadura": False},
    "Diplomacia": {"atributo_padrao": "carisma", "penalidade_armadura": False},
    "Enganação": {"atributo_padrao": "carisma", "penalidade_armadura": False},
    "Fortitude": {"atributo_padrao": "constituicao", "penalidade_armadura": False},
    "Furtividade": {"atributo_padrao": "destreza", "penalidade_armadura": True},
    "Guerra": {"atributo_padrao": "inteligencia", "penalidade_armadura": False},
    "Iniciativa": {"atributo_padrao": "destreza", "penalidade_armadura": False},
    "Intimidação": {"atributo_padrao": "carisma", "penalidade_armadura": False},
    "Investigação": {"atributo_padrao": "inteligencia", "penalidade_armadura": False},
    "Intuição": {"atributo_padrao": "sabedoria", "penalidade_armadura": False},
    "Jogatina": {"atributo_padrao": "carisma", "penalidade_armadura": False},
    "Ladinagem": {"atributo_padrao": "destreza", "penalidade_armadura": True},
    "Luta": {"atributo_padrao": "forca", "penalidade_armadura": True},
    "Misticismo": {"atributo_padrao": "inteligencia", "penalidade_armadura": False},
    "Nobreza": {"atributo_padrao": "inteligencia", "penalidade_armadura": False},
    "Ofício": {"atributo_padrao": "inteligencia", "penalidade_armadura": False},
    "Percepção": {"atributo_padrao": "sabedoria", "penalidade_armadura": False},
    "Pilotagem": {"atributo_padrao": "destreza", "penalidade_armadura": True},
    "Pontaria": {"atributo_padrao": "destreza", "penalidade_armadura": True},
    "Reflexos": {"atributo_padrao": "destreza", "penalidade_armadura": False},
    "Religião": {"atributo_padrao": "sabedoria", "penalidade_armadura": False},
    "Sobrevivência": {"atributo_padrao": "sabedoria", "penalidade_armadura": False},
    "Vontade": {"atributo_padrao": "sabedoria", "penalidade_armadura": False}
}

# Lista de atributos disponíveis
ATRIBUTOS = ["forca", "destreza", "constituicao", "inteligencia", "sabedoria", "carisma"]

# Estruturas de dados para T20
MAGIAS = {
    "Arcana": [],
    "Divina": []
}

TIPOS_ITEM = [
    "Arma", "Armadura", "Escudo", "Item Mágico", "Poção", "Varinha", 
    "Cajado", "Varinha", "Anel", "Amuleto", "Botas", "Manto", "Vestimenta",
    "Consumível", "Material", "Outro"
]

# Função para salvar ficha
def salvar_ficha(ficha):
    ficha_json = json.dumps(ficha, ensure_ascii=False, indent=4)
    return ficha_json

# Função para carregar ficha
def carregar_ficha(json_string):
    try:
        ficha = json.loads(json_string)
        # Garantir que todos os campos necessários existam
        if "inventario" not in ficha:
            ficha["inventario"] = {
                "itens": [],
                "dinheiro": {"T$": 0, "PP": 0, "PO": 0, "PE": 0, "PC": 0},
                "carga": {"atual": 0.0, "maxima": 0.0}
            }
        if "magias" not in ficha:
            ficha["magias"] = {
                "arcana": [],
                "divina": []
            }
        if "poderes" not in ficha:
            ficha["poderes"] = []
        if "habilidades" not in ficha:
            ficha["habilidades"] = []
        if "pericias" not in ficha:
            ficha["pericias"] = {pericia: {"treinada": False, "bonus": 0, "atributo": info["atributo_padrao"]} for pericia, info in PERICIAS.items()}
        if "classes" not in ficha:
            ficha["classes"] = [{"nome": "", "nivel": 1}]
        if "recursos" not in ficha:
            ficha["recursos"] = {
                "vida": {"atual": 0, "maximo": 0},
                "mana": {"atual": 0, "maximo": 0},
                "prana": {"atual": 0, "maximo": 0}
            }
        if "recursos_adicionais" not in ficha:
            ficha["recursos_adicionais"] = []
        if "atributos" not in ficha:
            ficha["atributos"] = {
                "forca": 10,
                "destreza": 10,
                "constituicao": 10,
                "inteligencia": 10,
                "sabedoria": 10,
                "carisma": 10
            }
        if "oficios" not in ficha:
            ficha["oficios"] = []
        if "origem" not in ficha:
            ficha["origem"] = ""
        return ficha
    except:
        st.error("Erro ao carregar a ficha. Verifique se o JSON é válido.")
        return None

# Função para criar barra de recursos
def criar_barra_recursos(nome, valor_atual, valor_maximo, cor):
    if valor_maximo == 0:
        porcentagem = 0
    else:
        porcentagem = (valor_atual / valor_maximo) * 100
    
    # Estilo CSS melhorado para as barras
    st.markdown(f"""
        <style>
        .{nome.lower().replace(' ', '_')} {{
            background-color: #2e2e2e;
            border-radius: 10px;
            padding: 8px;
            margin: 8px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .{nome.lower().replace(' ', '_')} .bar {{
            background-color: {cor};
            height: 24px;
            border-radius: 8px;
            width: {porcentagem}%;
            transition: width 0.3s ease;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        }}
        .{nome.lower().replace(' ', '_')} .label {{
            color: white;
            font-weight: bold;
            margin-bottom: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        </style>
        <div class="{nome.lower().replace(' ', '_')}">
            <div class="label">
                <span>{nome}</span>
                <span>{valor_atual}/{valor_maximo}</span>
            </div>
            <div class="bar"></div>
        </div>
    """, unsafe_allow_html=True)

# Função para adicionar novo ofício
def adicionar_oficio():
    # Preservar o estado atual da ficha
    ficha_atual = st.session_state.ficha.copy()
    
    # Adicionar novo ofício
    novo_oficio = st.session_state["novo_oficio"]
    if novo_oficio and novo_oficio not in ficha_atual["oficios"]:
        ficha_atual["oficios"].append(novo_oficio)
        # Inicializar a perícia para o novo ofício
        ficha_atual["pericias"][f"Ofício ({novo_oficio})"] = {
            "treinada": False,
            "bonus": 0,
            "atributo": "inteligencia",
            "outros_bonus": 0,
            "penalidade": 0
        }
        st.session_state["novo_oficio"] = ""  # Limpar o campo
    
    # Atualizar o estado da sessão com a ficha completa
    st.session_state.ficha = ficha_atual

# Inicialização do estado da sessão
if 'ficha' not in st.session_state:
    st.session_state.ficha = {
        "nome": "",
        "nivel": 1,
        "raca": "",
        "classes": [{"nome": "", "nivel": 1}],
        "divindade": "",
        "tendencia": "",
        "origem": "",
        "atributos": {
            "forca": 10,
            "destreza": 10,
            "constituicao": 10,
            "inteligencia": 10,
            "sabedoria": 10,
            "carisma": 10
        },
        "recursos": {
            "vida": {"atual": 0, "maximo": 0},
            "mana": {"atual": 0, "maximo": 0},
            "prana": {"atual": 0, "maximo": 0}
        },
        "recursos_adicionais": [],
        "pv": 0,
        "pm": 0,
        "defesa": 10,
        "deslocamento": 9,
        "pericias": {pericia: {"treinada": False, "bonus": 0, "atributo": info["atributo_padrao"]} for pericia, info in PERICIAS.items()},
        "imagem": None,
        "inventario": {
            "itens": [],
            "dinheiro": {
                "T$": 0,
                "PP": 0,
                "PO": 0,
                "PE": 0,
                "PC": 0
            },
            "carga": {
                "atual": 0.0,
                "maxima": 0.0
            }
        },
        "magias": {
            "arcana": [],
            "divina": []
        },
        "poderes": [],
        "habilidades": [],
        "oficios": []  # Lista de ofícios adicionais
    }

if 'novo_oficio' not in st.session_state:
    st.session_state.novo_oficio = ""

if 'show_file_uploader' not in st.session_state:
    st.session_state.show_file_uploader = False

# Interface principal
st.title("Ficha de Personagem - Tormenta 20")

# Colunas para layout
col1, col2 = st.columns([1, 2])

with col1:
    # Exibir imagem existente
    if st.session_state.ficha.get("imagem"):
        try:
            imagem = base64_to_image(st.session_state.ficha["imagem"])
            if imagem:
                st.image(imagem, caption="Imagem do Personagem", width=300)
        except Exception as e:
            st.error(f"Erro ao exibir imagem: {str(e)}")
            st.session_state.ficha["imagem"] = None
    
    # Upload de nova imagem
    uploaded_file = st.file_uploader("Escolha uma imagem para o personagem", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            # Converter para RGB se necessário
            if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
                image = image.convert('RGB')
            st.session_state.ficha["imagem"] = image_to_base64(image)
            st.image(image, caption="Imagem do Personagem", width=300)
        except Exception as e:
            st.error(f"Erro ao processar imagem: {str(e)}")

    # Botão para carregar ficha
    if st.button("Carregar Ficha"):
        st.session_state.show_file_uploader = True

    # Upload de ficha
    if st.session_state.show_file_uploader:
        uploaded_json = st.file_uploader("Selecione o arquivo da ficha", type=['json'], key="json_uploader")
        if uploaded_json is not None:
            try:
                json_string = uploaded_json.getvalue().decode()
                nova_ficha = carregar_ficha(json_string)
                if nova_ficha:
                    # Preservar a imagem se existir
                    imagem_atual = st.session_state.ficha.get("imagem")
                    st.session_state.ficha = nova_ficha
                    if imagem_atual:
                        st.session_state.ficha["imagem"] = imagem_atual
                    st.success("Ficha carregada com sucesso!")
                    st.session_state.show_file_uploader = False
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao carregar ficha: {str(e)}")

with col2:
    # Informações básicas
    st.subheader("Informações Básicas")
    st.session_state.ficha["nome"] = st.text_input("Nome", st.session_state.ficha["nome"], on_change=lambda: None)
    
    # Calcular nível total baseado nas classes
    nivel_total = sum(classe["nivel"] for classe in st.session_state.ficha["classes"])
    st.session_state.ficha["nivel"] = nivel_total
    
    # Exibir nível total como métrica (somente leitura)
    st.metric("Nível Total", nivel_total)
    
    st.session_state.ficha["raca"] = st.text_input("Raça", st.session_state.ficha["raca"], on_change=lambda: None)
    st.session_state.ficha["origem"] = st.text_input("Origem", st.session_state.ficha.get("origem", ""), on_change=lambda: None)
    
    # Sistema de Multiclasse
    st.subheader("Classes")
    
    # Botão para adicionar nova classe
    if st.button("Adicionar Classe"):
        st.session_state.ficha["classes"].append({"nome": "", "nivel": 1})
    
    # Exibir e editar classes
    for i, classe in enumerate(st.session_state.ficha["classes"]):
        col_classe1, col_classe2, col_classe3 = st.columns([3, 1, 1])
        with col_classe1:
            classe["nome"] = st.text_input(f"Nome da Classe {i+1}", classe["nome"], key=f"classe_nome_{i}", on_change=lambda: None)
        with col_classe2:
            st.number_input(
                "Nível",
                1, 20,
                classe["nivel"],
                key=f"classe_nivel_{i}",
                on_change=atualizar_nivel_classe,
                args=(i,)
            )
        with col_classe3:
            if len(st.session_state.ficha["classes"]) > 1:
                if st.button("Remover", key=f"remover_classe_{i}"):
                    st.session_state.ficha["classes"].pop(i)
                    # Recalcular nível total após remover classe
                    st.session_state.ficha["nivel"] = sum(classe["nivel"] for classe in st.session_state.ficha["classes"])
                    st.rerun()
    
    st.session_state.ficha["divindade"] = st.text_input("Divindade", st.session_state.ficha["divindade"], on_change=lambda: None)
    st.session_state.ficha["tendencia"] = st.text_input("Tendência", st.session_state.ficha["tendencia"], on_change=lambda: None)

    # Atributos
    st.subheader("Atributos")
    
    # Força
    col_forca1, col_forca2 = st.columns([3, 1])
    with col_forca1:
        st.session_state.ficha["atributos"]["forca"] = st.number_input("Força", 1, None, st.session_state.ficha["atributos"]["forca"], on_change=lambda: None)
    with col_forca2:
        st.metric("Mod", calcular_modificador(st.session_state.ficha["atributos"]["forca"]))
    
    # Destreza
    col_des1, col_des2 = st.columns([3, 1])
    with col_des1:
        st.session_state.ficha["atributos"]["destreza"] = st.number_input("Destreza", 1, None, st.session_state.ficha["atributos"]["destreza"], on_change=lambda: None)
    with col_des2:
        st.metric("Mod", calcular_modificador(st.session_state.ficha["atributos"]["destreza"]))
    
    # Constituição
    col_con1, col_con2 = st.columns([3, 1])
    with col_con1:
        st.session_state.ficha["atributos"]["constituicao"] = st.number_input("Constituição", 1, None, st.session_state.ficha["atributos"]["constituicao"], on_change=lambda: None)
    with col_con2:
        st.metric("Mod", calcular_modificador(st.session_state.ficha["atributos"]["constituicao"]))
    
    # Inteligência
    col_int1, col_int2 = st.columns([3, 1])
    with col_int1:
        st.session_state.ficha["atributos"]["inteligencia"] = st.number_input("Inteligência", 1, None, st.session_state.ficha["atributos"]["inteligencia"], on_change=lambda: None)
    with col_int2:
        st.metric("Mod", calcular_modificador(st.session_state.ficha["atributos"]["inteligencia"]))
    
    # Sabedoria
    col_sab1, col_sab2 = st.columns([3, 1])
    with col_sab1:
        st.session_state.ficha["atributos"]["sabedoria"] = st.number_input("Sabedoria", 1, None, st.session_state.ficha["atributos"]["sabedoria"], on_change=lambda: None)
    with col_sab2:
        st.metric("Mod", calcular_modificador(st.session_state.ficha["atributos"]["sabedoria"]))
    
    # Carisma
    col_car1, col_car2 = st.columns([3, 1])
    with col_car1:
        st.session_state.ficha["atributos"]["carisma"] = st.number_input("Carisma", 1, None, st.session_state.ficha["atributos"]["carisma"], on_change=lambda: None)
    with col_car2:
        st.metric("Mod", calcular_modificador(st.session_state.ficha["atributos"]["carisma"]))

    # Defesa e Deslocamento
    st.subheader("Defesa e Deslocamento")
    col_def1, col_def2 = st.columns(2)

    with col_def1:
        st.write("Defesa")
        # Campos para cálculo de defesa
        usar_atributo = st.checkbox("Usar modificador de atributo", value=True, key="usar_atributo_defesa")
        if usar_atributo:
            atributo_defesa = st.selectbox(
                "Atributo para Defesa",
                options=ATRIBUTOS,
                index=ATRIBUTOS.index("destreza"),
                key="atributo_defesa"
            )
        
        bonus_equipamento = st.number_input("Bônus de Equipamento", -10, 20, 0, key="bonus_equipamento_defesa")
        bonus_reflexo = st.number_input("Bônus de Reflexos", -10, 20, 0, key="bonus_reflexo_defesa")
        
        # Calcular defesa
        defesa = calcular_defesa(
            st.session_state.ficha["atributos"],
            bonus_equipamento,
            usar_atributo,
            atributo_defesa if usar_atributo else "destreza",
            bonus_reflexo
        )
        st.metric("Defesa Total", defesa)

    with col_def2:
        st.write("Deslocamento")
        # Campo editável para deslocamento
        deslocamento_atual = st.session_state.ficha.get("deslocamento", 9)  # Valor padrão se não existir
        novo_deslocamento = st.number_input(
            "Deslocamento (metros)",
            min_value=0,
            max_value=30,
            value=deslocamento_atual,
            step=1,
            key="deslocamento_input"
        )
        st.session_state.ficha["deslocamento"] = novo_deslocamento
        st.metric("Deslocamento", f"{novo_deslocamento}m")

# Perícias
st.subheader("Perícias")
st.write("Marque as perícias treinadas e escolha o atributo base. O bônus total é calculado automaticamente.")

# Estilo CSS para as perícias
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .pericia-container {
            margin: 10px 0;
        }
        .pericia-nome {
            font-size: 1.1em;
        }
        .pericia-atributo {
            font-size: 0.8em;
        }
        .pericia-bonus {
            font-size: 1.2em;
        }
    }
    
    .pericia-container {
        background-color: #2e2e2e;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .pericia-container:hover {
        background-color: #363636;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    .pericia-nome {
        color: white;
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 4px;
    }
    .pericia-atributo {
        color: #a0a0a0;
        font-size: 0.9em;
    }
    .pericia-bonus {
        color: #4CAF50;
        font-weight: bold;
        font-size: 1.3em;
    }
    .pericia-treinada {
        color: #FFC107;
    }
    .pericia-controls {
        display: flex;
        gap: 10px;
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Função para determinar o número de colunas baseado no tamanho da tela
def get_column_count():
    # Streamlit não tem uma maneira direta de detectar o tamanho da tela
    # Vamos usar uma heurística baseada no tamanho da janela do navegador
    # que é passado para o Streamlit
    try:
        # Tenta obter o tamanho da tela do session state
        if 'screen_width' not in st.session_state:
            st.session_state.screen_width = 1200  # valor padrão
        
        if st.session_state.screen_width < 768:
            return 1
        elif st.session_state.screen_width < 1024:
            return 2
        else:
            return 3
    except:
        return 3  # valor padrão

# Criar colunas para organizar as perícias
num_columns = get_column_count()
columns = st.columns(num_columns)

# Dividir as perícias em colunas de forma mais eficiente
pericias_lista = list(PERICIAS.items())
pericias_por_coluna = (len(pericias_lista) + num_columns - 1) // num_columns  # Arredonda para cima
pericias_colunas = []
for i in range(0, len(pericias_lista), pericias_por_coluna):
    pericias_colunas.append(pericias_lista[i:i + pericias_por_coluna])

# Garantir que temos o número correto de colunas
while len(pericias_colunas) < num_columns:
    pericias_colunas.append([])

# Função para atualizar o estado da perícia quando treinada é alterada
def atualizar_pericia_treinada(pericia):
    # Preservar o estado atual da ficha
    ficha_atual = st.session_state.ficha.copy()
    
    # Atualizar apenas o campo treinada da perícia específica
    ficha_atual["pericias"][pericia]["treinada"] = st.session_state[f"pericia_{pericia}"]
    
    # Atualizar o bônus da perícia
    atributo = ficha_atual["atributos"][ficha_atual["pericias"][pericia]["atributo"]]
    treinada = ficha_atual["pericias"][pericia]["treinada"]
    bonus = calcular_bonus_pericia(atributo, treinada, ficha_atual["nivel"])
    ficha_atual["pericias"][pericia]["bonus"] = bonus + ficha_atual["pericias"][pericia].get("outros_bonus", 0)
    
    # Atualizar o estado da sessão com a ficha completa
    st.session_state.ficha = ficha_atual

# Função para atualizar o atributo da perícia
def atualizar_atributo_pericia(pericia):
    # Preservar o estado atual da ficha
    ficha_atual = st.session_state.ficha.copy()
    
    # Atualizar o atributo da perícia
    ficha_atual["pericias"][pericia]["atributo"] = st.session_state[f"atributo_{pericia}"]
    
    # Recalcular o bônus
    atributo = ficha_atual["atributos"][ficha_atual["pericias"][pericia]["atributo"]]
    treinada = ficha_atual["pericias"][pericia]["treinada"]
    bonus = calcular_bonus_pericia(atributo, treinada, ficha_atual["nivel"])
    ficha_atual["pericias"][pericia]["bonus"] = bonus + ficha_atual["pericias"][pericia].get("outros_bonus", 0)
    
    # Atualizar o estado da sessão com a ficha completa
    st.session_state.ficha = ficha_atual

# Função para atualizar outros bônus da perícia
def atualizar_outros_bonus_pericia(pericia):
    # Preservar o estado atual da ficha
    ficha_atual = st.session_state.ficha.copy()
    
    # Atualizar outros bônus
    ficha_atual["pericias"][pericia]["outros_bonus"] = st.session_state[f"outros_bonus_{pericia}"]
    
    # Recalcular o bônus total
    atributo = ficha_atual["atributos"][ficha_atual["pericias"][pericia]["atributo"]]
    treinada = ficha_atual["pericias"][pericia]["treinada"]
    bonus = calcular_bonus_pericia(atributo, treinada, ficha_atual["nivel"])
    ficha_atual["pericias"][pericia]["bonus"] = bonus + ficha_atual["pericias"][pericia]["outros_bonus"]
    
    # Atualizar o estado da sessão com a ficha completa
    st.session_state.ficha = ficha_atual

# Função para atualizar penalidade da perícia
def atualizar_penalidade_pericia(pericia):
    # Preservar o estado atual da ficha
    ficha_atual = st.session_state.ficha.copy()
    
    # Atualizar penalidade
    ficha_atual["pericias"][pericia]["penalidade"] = st.session_state[f"penalidade_{pericia}"]
    
    # Recalcular o bônus total
    atributo = ficha_atual["atributos"][ficha_atual["pericias"][pericia]["atributo"]]
    treinada = ficha_atual["pericias"][pericia]["treinada"]
    bonus = calcular_bonus_pericia(atributo, treinada, ficha_atual["nivel"])
    ficha_atual["pericias"][pericia]["bonus"] = bonus + ficha_atual["pericias"][pericia]["outros_bonus"] + ficha_atual["pericias"][pericia]["penalidade"]
    
    # Atualizar o estado da sessão com a ficha completa
    st.session_state.ficha = ficha_atual

# Exibir perícias em cada coluna
for col, pericias_col in zip(columns, pericias_colunas):
    with col:
        for pericia, info in pericias_col:
            # Tratamento especial para Ofício
            if pericia == "Ofício":
                # Exibir ofícios existentes
                for oficio in st.session_state.ficha["oficios"]:
                    pericia_oficio = f"Ofício ({oficio})"
                    if pericia_oficio not in st.session_state.ficha["pericias"]:
                        st.session_state.ficha["pericias"][pericia_oficio] = {
                            "treinada": False,
                            "bonus": 0,
                            "atributo": "inteligencia",
                            "outros_bonus": 0,
                            "penalidade": 0
                        }
                    
                    # Calcular bônus total incluindo penalidades
                    atributo = st.session_state.ficha["atributos"][st.session_state.ficha["pericias"][pericia_oficio]["atributo"]]
                    treinada = st.session_state.ficha["pericias"][pericia_oficio]["treinada"]
                    bonus = calcular_bonus_pericia(atributo, treinada, st.session_state.ficha["nivel"])
                    bonus_total = bonus + st.session_state.ficha["pericias"][pericia_oficio]["outros_bonus"] + st.session_state.ficha["pericias"][pericia_oficio]["penalidade"]
                    
                    # Criar container para o ofício
                    st.markdown(f"""
                        <div class="pericia-container">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div class="pericia-nome">{pericia_oficio}</div>
                                    <div class="pericia-atributo">Atributo: {st.session_state.ficha["pericias"][pericia_oficio]["atributo"].capitalize()}</div>
                                </div>
                                <div class="pericia-bonus">{bonus_total:+d}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Controles do ofício
                    st.markdown('<div class="pericia-controls">', unsafe_allow_html=True)
                    col_controls1, col_controls2, col_controls3, col_controls4, col_controls5 = st.columns([1, 1, 1, 1, 1])
                    with col_controls1:
                        st.checkbox(
                            "Treinada",
                            value=st.session_state.ficha["pericias"][pericia_oficio]["treinada"],
                            key=f"pericia_{pericia_oficio}",
                            on_change=atualizar_pericia_treinada,
                            args=(pericia_oficio,)
                        )
                    with col_controls2:
                        st.selectbox(
                            "Atributo",
                            options=ATRIBUTOS,
                            index=ATRIBUTOS.index(st.session_state.ficha["pericias"][pericia_oficio]["atributo"]),
                            key=f"atributo_{pericia_oficio}",
                            label_visibility="collapsed",
                            on_change=atualizar_atributo_pericia,
                            args=(pericia_oficio,)
                        )
                    with col_controls3:
                        st.number_input(
                            "Outros Bônus",
                            -10, 10,
                            st.session_state.ficha["pericias"][pericia_oficio]["outros_bonus"],
                            key=f"outros_bonus_{pericia_oficio}",
                            label_visibility="collapsed",
                            on_change=atualizar_outros_bonus_pericia,
                            args=(pericia_oficio,)
                        )
                    with col_controls4:
                        st.number_input(
                            "Penalidade",
                            -10, 10,
                            st.session_state.ficha["pericias"][pericia_oficio]["penalidade"],
                            key=f"penalidade_{pericia_oficio}",
                            label_visibility="collapsed",
                            on_change=atualizar_penalidade_pericia,
                            args=(pericia_oficio,)
                        )
                    with col_controls5:
                        if st.button("Remover", key=f"remover_oficio_{oficio}"):
                            st.session_state.ficha["oficios"].remove(oficio)
                            del st.session_state.ficha["pericias"][pericia_oficio]
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Campo para adicionar novo ofício
                col_novo_oficio1, col_novo_oficio2 = st.columns([3, 1])
                with col_novo_oficio1:
                    st.text_input(
                        "Novo Ofício",
                        value=st.session_state.novo_oficio,
                        key="novo_oficio",
                        placeholder="Digite o nome do ofício"
                    )
                with col_novo_oficio2:
                    st.button("Adicionar Ofício", on_click=adicionar_oficio)
                
                continue  # Pular a exibição padrão do Ofício
            
            # Exibição padrão para outras perícias
            # Garantir que outros_bonus e penalidade existem
            if "outros_bonus" not in st.session_state.ficha["pericias"][pericia]:
                st.session_state.ficha["pericias"][pericia]["outros_bonus"] = 0
            if "penalidade" not in st.session_state.ficha["pericias"][pericia]:
                st.session_state.ficha["pericias"][pericia]["penalidade"] = 0
            
            # Calcular bônus total incluindo penalidades
            atributo = st.session_state.ficha["atributos"][st.session_state.ficha["pericias"][pericia]["atributo"]]
            treinada = st.session_state.ficha["pericias"][pericia]["treinada"]
            bonus = calcular_bonus_pericia(atributo, treinada, st.session_state.ficha["nivel"])
            bonus_total = bonus + st.session_state.ficha["pericias"][pericia]["outros_bonus"] + st.session_state.ficha["pericias"][pericia]["penalidade"]
            
            # Criar container para a perícia
            st.markdown(f"""
                <div class="pericia-container">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div class="pericia-nome">{pericia}</div>
                            <div class="pericia-atributo">Atributo: {st.session_state.ficha["pericias"][pericia]["atributo"].capitalize()}</div>
                        </div>
                        <div class="pericia-bonus">{bonus_total:+d}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Controles da perícia
            st.markdown('<div class="pericia-controls">', unsafe_allow_html=True)
            col_controls1, col_controls2, col_controls3, col_controls4 = st.columns([1, 1, 1, 1])
            with col_controls1:
                st.checkbox(
                    "Treinada",
                    value=st.session_state.ficha["pericias"][pericia]["treinada"],
                    key=f"pericia_{pericia}",
                    on_change=atualizar_pericia_treinada,
                    args=(pericia,)
                )
            with col_controls2:
                st.selectbox(
                    "Atributo",
                    options=ATRIBUTOS,
                    index=ATRIBUTOS.index(st.session_state.ficha["pericias"][pericia]["atributo"]),
                    key=f"atributo_{pericia}",
                    label_visibility="collapsed",
                    on_change=atualizar_atributo_pericia,
                    args=(pericia,)
                )
            with col_controls3:
                st.number_input(
                    "Outros Bônus",
                    -10, 10,
                    st.session_state.ficha["pericias"][pericia]["outros_bonus"],
                    key=f"outros_bonus_{pericia}",
                    label_visibility="collapsed",
                    on_change=atualizar_outros_bonus_pericia,
                    args=(pericia,)
                )
            with col_controls4:
                st.number_input(
                    "Penalidade",
                    -10, 10,
                    st.session_state.ficha["pericias"][pericia]["penalidade"],
                    key=f"penalidade_{pericia}",
                    label_visibility="collapsed",
                    on_change=atualizar_penalidade_pericia,
                    args=(pericia,)
                )
            st.markdown('</div>', unsafe_allow_html=True)

# Recursos
st.subheader("Recursos")
col_rec1, col_rec2, col_rec3 = st.columns(3)

with col_rec1:
    # Vida
    st.write("Vida")
    col_vida1, col_vida2 = st.columns(2)
    with col_vida1:
        st.session_state.ficha["recursos"]["vida"]["atual"] = st.number_input("Atual", 0, 1000, st.session_state.ficha["recursos"]["vida"]["atual"], key="vida_atual", on_change=lambda: None)
    with col_vida2:
        st.session_state.ficha["recursos"]["vida"]["maximo"] = st.number_input("Máximo", 0, 1000, st.session_state.ficha["recursos"]["vida"]["maximo"], key="vida_max", on_change=lambda: None)

with col_rec2:
    # Mana
    st.write("Mana")
    col_mana1, col_mana2 = st.columns(2)
    with col_mana1:
        st.session_state.ficha["recursos"]["mana"]["atual"] = st.number_input("Atual", 0, 1000, st.session_state.ficha["recursos"]["mana"]["atual"], key="mana_atual", on_change=lambda: None)
    with col_mana2:
        st.session_state.ficha["recursos"]["mana"]["maximo"] = st.number_input("Máximo", 0, 1000, st.session_state.ficha["recursos"]["mana"]["maximo"], key="mana_max", on_change=lambda: None)

with col_rec3:
    # Prana
    st.write("Prana")
    col_prana1, col_prana2 = st.columns(2)
    with col_prana1:
        st.session_state.ficha["recursos"]["prana"]["atual"] = st.number_input("Atual", 0, 1000, st.session_state.ficha["recursos"]["prana"]["atual"], key="prana_atual", on_change=lambda: None)
    with col_prana2:
        st.session_state.ficha["recursos"]["prana"]["maximo"] = st.number_input("Máximo", 0, 1000, st.session_state.ficha["recursos"]["prana"]["maximo"], key="prana_max", on_change=lambda: None)

# Exibir barras de recursos
criar_barra_recursos("Vida", st.session_state.ficha["recursos"]["vida"]["atual"], st.session_state.ficha["recursos"]["vida"]["maximo"], "#ff0000")
criar_barra_recursos("Mana", st.session_state.ficha["recursos"]["mana"]["atual"], st.session_state.ficha["recursos"]["mana"]["maximo"], "#0000ff")
criar_barra_recursos("Prana", st.session_state.ficha["recursos"]["prana"]["atual"], st.session_state.ficha["recursos"]["prana"]["maximo"], "#00ff00")

# Recursos Adicionais
st.subheader("Recursos Adicionais")
if st.button("Adicionar Recurso"):
    st.session_state.ficha["recursos_adicionais"].append({
        "nome": "",
        "atual": 0,
        "maximo": 0,
        "cor": "#808080"
    })

# Exibir e editar recursos adicionais
for i, recurso in enumerate(st.session_state.ficha["recursos_adicionais"]):
    col_rec_add1, col_rec_add2, col_rec_add3 = st.columns([2, 1, 1])
    with col_rec_add1:
        recurso["nome"] = st.text_input(f"Nome do Recurso {i+1}", recurso["nome"], key=f"nome_rec_{i}", on_change=lambda: None)
    with col_rec_add2:
        recurso["maximo"] = st.number_input("Máximo", 0, 1000, recurso["maximo"], key=f"max_rec_{i}", on_change=lambda: None)
        recurso["atual"] = st.number_input("Atual", 0, recurso["maximo"], recurso["atual"], key=f"atual_rec_{i}", on_change=lambda: None)
    with col_rec_add3:
        recurso["cor"] = st.color_picker("Cor", recurso["cor"], key=f"cor_rec_{i}")
        if st.button("Remover", key=f"remover_rec_{i}"):
            st.session_state.ficha["recursos_adicionais"].pop(i)
            st.rerun()
    
    if recurso["nome"]:  # Só mostra a barra se o recurso tiver um nome
        criar_barra_recursos(recurso["nome"], recurso["atual"], recurso["maximo"], recurso["cor"])

# Inventário
st.subheader("Inventário")

# Dinheiro
st.write("Dinheiro")
col_din1, col_din2, col_din3, col_din4, col_din5 = st.columns(5)
with col_din1:
    st.session_state.ficha["inventario"]["dinheiro"]["T$"] = st.number_input("T$", 0, 1000000, st.session_state.ficha["inventario"]["dinheiro"]["T$"])
with col_din2:
    st.session_state.ficha["inventario"]["dinheiro"]["PP"] = st.number_input("PP", 0, 1000000, st.session_state.ficha["inventario"]["dinheiro"]["PP"])
with col_din3:
    st.session_state.ficha["inventario"]["dinheiro"]["PO"] = st.number_input("PO", 0, 1000000, st.session_state.ficha["inventario"]["dinheiro"]["PO"])
with col_din4:
    st.session_state.ficha["inventario"]["dinheiro"]["PE"] = st.number_input("PE", 0, 1000000, st.session_state.ficha["inventario"]["dinheiro"]["PE"])
with col_din5:
    st.session_state.ficha["inventario"]["dinheiro"]["PC"] = st.number_input("PC", 0, 1000000, st.session_state.ficha["inventario"]["dinheiro"]["PC"])

# Carga
st.write("Carga")
col_carga1, col_carga2, col_carga3 = st.columns(3)
with col_carga1:
    carga_maxima = calcular_carga_maxima(st.session_state.ficha["atributos"]["forca"])
    st.session_state.ficha["inventario"]["carga"]["maxima"] = carga_maxima
    st.metric("Carga Máxima", f"{st.session_state.ficha['inventario']['carga']['atual']:.1f}/{carga_maxima:.1f}")

with col_carga2:
    # Calcular e exibir penalidade de carga
    penalidade, descricao = calcular_penalidade_carga(
        st.session_state.ficha["inventario"]["carga"]["atual"],
        carga_maxima
    )
    st.metric("Penalidade de Carga", f"{penalidade:+d}")
    st.write(descricao)

with col_carga3:
    # Exibir porcentagem de carga
    porcentagem = (st.session_state.ficha["inventario"]["carga"]["atual"] / carga_maxima) * 100
    st.metric("Porcentagem de Carga", f"{porcentagem:.1f}%")

# Itens
st.write("Itens")
if st.button("Adicionar Item"):
    st.session_state.ficha["inventario"]["itens"].append({
        "nome": "",
        "tipo": TIPOS_ITEM[0],
        "quantidade": 1,
        "peso": 0.0,
        "valor": 0,
        "descricao": "",
        "propriedades": "",
        "dano": "",
        "alcance": "",
        "duracao": "",
        "tipo_dano": "",
        "critico": "",
        "especial": "",
        "efeitos": "",
        "bonus_atributos": {
            "forca": 0,
            "destreza": 0,
            "constituicao": 0,
            "inteligencia": 0,
            "sabedoria": 0,
            "carisma": 0
        },
        "outros_bonus": {
            "ataque": 0,
            "dano": 0,
            "defesa": 0,
            "iniciativa": 0,
            "pericias": {}
        }
    })

# Lista de itens
for i, item in enumerate(st.session_state.ficha["inventario"]["itens"]):
    with st.expander(f"Item {i+1}: {item['nome'] or 'Novo Item'}"):
        col_item1, col_item2 = st.columns(2)
        with col_item1:
            item["nome"] = st.text_input("Nome", item["nome"], key=f"item_nome_{i}")
            item["tipo"] = st.selectbox("Tipo", TIPOS_ITEM, index=TIPOS_ITEM.index(item["tipo"]), key=f"item_tipo_{i}")
            item["quantidade"] = st.number_input("Quantidade", 1, 1000, item["quantidade"], key=f"item_qtd_{i}")
            item["peso"] = st.number_input("Peso", min_value=0.0, max_value=1000.0, value=float(item["peso"]), step=0.1, key=f"item_peso_{i}")
            item["valor"] = st.number_input("Valor", 0, 1000000, item["valor"], key=f"item_valor_{i}")
        
        # Atualizar carga total quando o item é modificado
        if st.button("Atualizar", key=f"atualizar_item_{i}"):
            atualizar_item(i)
            st.rerun()
        
        # Descrições detalhadas
        st.write("Descrições")
        item["descricao"] = st.text_area("Descrição do Item", item["descricao"], height=100, key=f"item_desc_{i}")
        item["propriedades"] = st.text_area("Propriedades", item["propriedades"], height=100, key=f"item_prop_{i}")
        item["efeitos"] = st.text_area("Efeitos Especiais", item["efeitos"], height=100, key=f"item_efeitos_{i}")
        
        # Campos específicos para armas
        if item["tipo"] == "Arma":
            st.write("Propriedades da Arma")
            col_arma1, col_arma2 = st.columns(2)
            with col_arma1:
                item["dano"] = st.text_input("Dano", item["dano"], key=f"item_dano_{i}")
                item["alcance"] = st.text_input("Alcance", item["alcance"], key=f"item_alcance_{i}")
            with col_arma2:
                item["tipo_dano"] = st.text_input("Tipo de Dano", item["tipo_dano"], key=f"item_tipo_dano_{i}")
                item["critico"] = st.text_input("Crítico", item["critico"], key=f"item_critico_{i}")
        
        # Campos específicos para itens mágicos
        if item["tipo"] in ["Item Mágico", "Poção", "Varinha", "Cajado", "Varinha", "Anel", "Amuleto"]:
            st.write("Propriedades Mágicas")
            item["duracao"] = st.text_input("Duração", item["duracao"], key=f"item_duracao_{i}")
            item["especial"] = st.text_area("Efeitos Mágicos", item["especial"], height=100, key=f"item_especial_{i}")
        
        # Bônus de Atributos
        st.write("Bônus de Atributos")
        col_bonus1, col_bonus2, col_bonus3 = st.columns(3)
        with col_bonus1:
            item["bonus_atributos"]["forca"] = st.number_input("Força", -10, 10, item["bonus_atributos"]["forca"], key=f"item_bonus_forca_{i}")
            item["bonus_atributos"]["destreza"] = st.number_input("Destreza", -10, 10, item["bonus_atributos"]["destreza"], key=f"item_bonus_des_{i}")
        with col_bonus2:
            item["bonus_atributos"]["constituicao"] = st.number_input("Constituição", -10, 10, item["bonus_atributos"]["constituicao"], key=f"item_bonus_con_{i}")
            item["bonus_atributos"]["inteligencia"] = st.number_input("Inteligência", -10, 10, item["bonus_atributos"]["inteligencia"], key=f"item_bonus_int_{i}")
        with col_bonus3:
            item["bonus_atributos"]["sabedoria"] = st.number_input("Sabedoria", -10, 10, item["bonus_atributos"]["sabedoria"], key=f"item_bonus_sab_{i}")
            item["bonus_atributos"]["carisma"] = st.number_input("Carisma", -10, 10, item["bonus_atributos"]["carisma"], key=f"item_bonus_car_{i}")
        
        # Outros Bônus
        st.write("Outros Bônus")
        col_outros1, col_outros2 = st.columns(2)
        with col_outros1:
            item["outros_bonus"]["ataque"] = st.number_input("Bônus de Ataque", -10, 10, item["outros_bonus"]["ataque"], key=f"item_bonus_ataque_{i}")
            item["outros_bonus"]["dano"] = st.number_input("Bônus de Dano", -10, 10, item["outros_bonus"]["dano"], key=f"item_bonus_dano_{i}")
        with col_outros2:
            item["outros_bonus"]["defesa"] = st.number_input("Bônus de Defesa", -10, 10, item["outros_bonus"]["defesa"], key=f"item_bonus_defesa_{i}")
            item["outros_bonus"]["iniciativa"] = st.number_input("Bônus de Iniciativa", -10, 10, item["outros_bonus"]["iniciativa"], key=f"item_bonus_iniciativa_{i}")
        
        # Bônus em Perícias
        st.write("Bônus em Perícias")
        pericias_selecionadas = st.multiselect(
            "Selecione as perícias que recebem bônus",
            options=list(PERICIAS.keys()),
            default=list(item["outros_bonus"]["pericias"].keys()),
            key=f"item_pericias_{i}"
        )
        
        # Atualizar bônus de perícias
        for pericia in pericias_selecionadas:
            if pericia not in item["outros_bonus"]["pericias"]:
                item["outros_bonus"]["pericias"][pericia] = 0
        # Remover perícias não selecionadas
        for pericia in list(item["outros_bonus"]["pericias"].keys()):
            if pericia not in pericias_selecionadas:
                del item["outros_bonus"]["pericias"][pericia]
        
        # Exibir campos de bônus para perícias selecionadas
        if pericias_selecionadas:
            col_per1, col_per2 = st.columns(2)
            for j, pericia in enumerate(pericias_selecionadas):
                with col_per1 if j % 2 == 0 else col_per2:
                    item["outros_bonus"]["pericias"][pericia] = st.number_input(
                        f"Bônus em {pericia}",
                        -10, 10,
                        item["outros_bonus"]["pericias"][pericia],
                        key=f"item_bonus_pericia_{i}_{pericia}"
                    )
        
        if st.button("Remover Item", key=f"remover_item_{i}"):
            st.session_state.ficha["inventario"]["itens"].pop(i)
            atualizar_carga_total()
            st.rerun()

# Atualizar carga total inicial
atualizar_carga_total()

# Magias
st.subheader("Magias")

# Barra de pesquisa para magias
pesquisa_magia = st.text_input("🔍 Pesquisar Magia", key="pesquisa_magia")

# Função para adicionar nova magia
def adicionar_magia():
    nova_magia = {
        "nome": "",
        "tipo": "Arcana",  # Tipo padrão
        "nivel": 1,        # Nível padrão
        "escola": "",
        "execucao": "",
        "alcance": "",
        "alvo": "",
        "duracao": "",
        "resistencia": "",
        "descricao": ""
    }
    
    # Verificar se as magias estão organizadas por nível
    if isinstance(st.session_state.ficha["magias"][nova_magia["tipo"].lower()], dict):
        # Se for um dicionário, adicionar ao nível apropriado
        nivel_key = f"{nova_magia['nivel']}º"
        if nivel_key not in st.session_state.ficha["magias"][nova_magia["tipo"].lower()]:
            st.session_state.ficha["magias"][nova_magia["tipo"].lower()][nivel_key] = []
        st.session_state.ficha["magias"][nova_magia["tipo"].lower()][nivel_key].append(nova_magia)
    else:
        # Se for uma lista, adicionar diretamente
        st.session_state.ficha["magias"][nova_magia["tipo"].lower()].append(nova_magia)

# Botão para adicionar nova magia
if st.button("Adicionar Nova Magia"):
    adicionar_magia()

# Agrupar magias por nível
def agrupar_magias_por_nivel(magias):
    niveis = {}
    for magia in magias:
        nivel = magia["nivel"]
        if nivel not in niveis:
            niveis[nivel] = []
        niveis[nivel].append(magia)
    return dict(sorted(niveis.items()))

# Exibir magias por tipo e nível
for tipo in ["Arcana", "Divina"]:
    # Filtrar magias do tipo atual
    magias_tipo = []
    
    # Verificar se as magias estão organizadas por nível
    if isinstance(st.session_state.ficha["magias"][tipo.lower()], dict):
        # Se for um dicionário, coletar todas as magias de todos os níveis
        for nivel_magias in st.session_state.ficha["magias"][tipo.lower()].values():
            if isinstance(nivel_magias, list):
                magias_tipo.extend(nivel_magias)
    else:
        # Se for uma lista, usar diretamente
        magias_tipo = st.session_state.ficha["magias"][tipo.lower()]
    
    # Filtrar magias baseado na pesquisa
    magias_tipo = [
        magia for magia in magias_tipo
        if pesquisa_magia.lower() in magia.get("nome", "").lower() or pesquisa_magia.lower() in magia.get("descricao", "").lower()
    ]
    
    if magias_tipo:  # Só mostra a seção se houver magias do tipo
        st.write(f"### {tipo}")
        
        # Agrupar magias por nível
        magias_por_nivel = agrupar_magias_por_nivel(magias_tipo)
        
        # Exibir magias por nível
        for nivel, magias in magias_por_nivel.items():
            with st.expander(f"Magias de {nivel}º Nível", expanded=True):
                for i, magia in enumerate(magias):
                    st.write(f"#### {magia.get('nome', 'Nova Magia')}")
                    
                    col_magia1, col_magia2 = st.columns(2)
                    with col_magia1:
                        magia["nome"] = st.text_input("Nome", magia.get("nome", ""), key=f"magia_nome_{tipo}_{nivel}_{i}")
                        magia["tipo"] = st.selectbox("Tipo", ["Arcana", "Divina"], index=0 if magia.get("tipo", "Arcana") == "Arcana" else 1, key=f"magia_tipo_{tipo}_{nivel}_{i}")
                        magia["nivel"] = st.number_input("Nível", 1, None, magia.get("nivel", 1), key=f"magia_nivel_{tipo}_{nivel}_{i}")
                        magia["escola"] = st.text_input("Escola", magia.get("escola", ""), key=f"magia_escola_{tipo}_{nivel}_{i}")
                        magia["execucao"] = st.text_input("Execução", magia.get("execucao", ""), key=f"magia_exec_{tipo}_{nivel}_{i}")
                        magia["alcance"] = st.text_input("Alcance", magia.get("alcance", ""), key=f"magia_alcance_{tipo}_{nivel}_{i}")
                    with col_magia2:
                        magia["alvo"] = st.text_input("Alvo", magia.get("alvo", ""), key=f"magia_alvo_{tipo}_{nivel}_{i}")
                        magia["duracao"] = st.text_input("Duração", magia.get("duracao", ""), key=f"magia_duracao_{tipo}_{nivel}_{i}")
                        magia["resistencia"] = st.text_input("Resistência", magia.get("resistencia", ""), key=f"magia_resist_{tipo}_{nivel}_{i}")
                    
                    magia["descricao"] = st.text_area("Descrição", magia.get("descricao", ""), height=100, key=f"magia_desc_{tipo}_{nivel}_{i}")
                    
                    if st.button("Remover Magia", key=f"remover_magia_{tipo}_{nivel}_{i}"):
                        # Encontrar e remover a magia da estrutura correta
                        if isinstance(st.session_state.ficha["magias"][tipo.lower()], dict):
                            for nivel_key in st.session_state.ficha["magias"][tipo.lower()]:
                                if magia in st.session_state.ficha["magias"][tipo.lower()][nivel_key]:
                                    st.session_state.ficha["magias"][tipo.lower()][nivel_key].remove(magia)
                                    break
                        else:
                            st.session_state.ficha["magias"][tipo.lower()].remove(magia)
                        st.rerun()
                    
                    st.markdown("---")  # Separador entre magias

# Poderes
st.subheader("Poderes")

# Barra de pesquisa para poderes
pesquisa_poder = st.text_input("🔍 Pesquisar Poder", key="pesquisa_poder")

if st.button("Adicionar Poder"):
    st.session_state.ficha["poderes"].append({
        "nome": "",
        "tipo": "",
        "custo": "",
        "requisito": "",
        "descricao": ""
    })

# Filtrar poderes
poderes_filtrados = [
    poder for poder in st.session_state.ficha["poderes"]
    if pesquisa_poder.lower() in poder["nome"].lower() or pesquisa_poder.lower() in poder["descricao"].lower()
]

for i, poder in enumerate(poderes_filtrados):
    with st.expander(f"{poder['nome'] or 'Novo Poder'}", expanded=True):
        col_poder1, col_poder2 = st.columns(2)
        with col_poder1:
            poder["nome"] = st.text_input("Nome", poder["nome"], key=f"poder_nome_{i}")
            poder["tipo"] = st.text_input("Tipo", poder["tipo"], key=f"poder_tipo_{i}")
        with col_poder2:
            poder["custo"] = st.text_input("Custo", poder["custo"], key=f"poder_custo_{i}")
            poder["requisito"] = st.text_input("Requisito", poder["requisito"], key=f"poder_req_{i}")
        
        poder["descricao"] = st.text_area("Descrição", poder["descricao"], height=100, key=f"poder_desc_{i}")
        
        if st.button("Remover Poder", key=f"remover_poder_{i}"):
            st.session_state.ficha["poderes"].pop(i)
            st.rerun()

# Habilidades
st.subheader("Habilidades")

# Barra de pesquisa para habilidades
pesquisa_habilidade = st.text_input("🔍 Pesquisar Habilidade", key="pesquisa_habilidade")

if st.button("Adicionar Habilidade"):
    st.session_state.ficha["habilidades"].append({
        "nome": "",
        "tipo": "",
        "custo": "",
        "requisito": "",
        "descricao": ""
    })

# Filtrar habilidades
habilidades_filtradas = [
    habilidade for habilidade in st.session_state.ficha["habilidades"]
    if pesquisa_habilidade.lower() in habilidade["nome"].lower() or pesquisa_habilidade.lower() in habilidade["descricao"].lower()
]

for i, habilidade in enumerate(habilidades_filtradas):
    with st.expander(f"{habilidade['nome'] or 'Nova Habilidade'}", expanded=True):
        col_hab1, col_hab2 = st.columns(2)
        with col_hab1:
            habilidade["nome"] = st.text_input("Nome", habilidade["nome"], key=f"hab_nome_{i}")
            habilidade["tipo"] = st.text_input("Tipo", habilidade["tipo"], key=f"hab_tipo_{i}")
        with col_hab2:
            habilidade["custo"] = st.text_input("Custo", habilidade["custo"], key=f"hab_custo_{i}")
            habilidade["requisito"] = st.text_input("Requisito", habilidade["requisito"], key=f"hab_req_{i}")
        
        habilidade["descricao"] = st.text_area("Descrição", habilidade["descricao"], height=100, key=f"hab_desc_{i}")
        
        if st.button("Remover Habilidade", key=f"remover_hab_{i}"):
            st.session_state.ficha["habilidades"].pop(i)
            st.rerun()

# Botão para salvar ficha
if st.button("Salvar Ficha"):
    ficha_json = salvar_ficha(st.session_state.ficha)
    nome_arquivo = f"{st.session_state.ficha['nome']}.json" if st.session_state.ficha['nome'] else "ficha_t20.json"
    st.download_button(
        label="Baixar Ficha",
        data=ficha_json,
        file_name=nome_arquivo,
        mime="application/json"
    )
