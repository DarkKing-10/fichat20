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

# Função para calcular bônus de perícia - CORRIGIDA
def calcular_bonus_pericia(atributo, treinada, nivel, bonus_adicional=0, penalidade=0):
    bonus = calcular_modificador(atributo)
    if treinada:
        bonus += (nivel // 2) + 2  # Bônus de treinamento é metade do nível
    bonus += bonus_adicional  # Adiciona bônus extra
    bonus -= penalidade  # Subtrai penalidade
    return bonus

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
    "Intuição": {"atributo_padrao": "sabedoria", "penalidade_armadura": False},
    "Investigação": {"atributo_padrao": "inteligencia", "penalidade_armadura": False},
    "Jogatina": {"atributo_padrao": "carisma", "penalidade_armadura": False},
    "Ladinagem": {"atributo_padrao": "destreza", "penalidade_armadura": True},
    "Luta": {"atributo_padrao": "forca", "penalidade_armadura": True},
    "Misticismo": {"atributo_padrao": "inteligencia", "penalidade_armadura": False},
    "Nobreza": {"atributo_padrao": "inteligencia", "penalidade_armadura": False},
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
    "Arcana": ["1º", "2º", "3º", "4º", "5º"],
    "Divina": ["1º", "2º", "3º", "4º", "5º"]
}

TIPOS_ITEM = [
    "Arma", "Armadura", "Escudo", "Item Mágico", "Poção", "Varinha", "Cajado",
    "Anel", "Amuleto", "Botas", "Manto", "Vestimenta", "Consumível", "Material", "Outro"
]

# Função para salvar ficha
def salvar_ficha(ficha):
    ficha_json = json.dumps(ficha, ensure_ascii=False, indent=4)
    return ficha_json

# Função para carregar ficha - CORRIGIDA
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
                "arcana": {nivel: [] for nivel in MAGIAS["Arcana"]},
                "divina": {nivel: [] for nivel in MAGIAS["Divina"]}
            }

        if "poderes" not in ficha:
            ficha["poderes"] = []

        if "habilidades" not in ficha:
            ficha["habilidades"] = []

        # Inicializar perícias com os novos campos
        if "pericias" not in ficha:
            ficha["pericias"] = {}

        for pericia, info in PERICIAS.items():
            if pericia not in ficha["pericias"]:
                ficha["pericias"][pericia] = {
                    "treinada": False,
                    "bonus": 0,
                    "penalidade": 0,
                    "atributo": info["atributo_padrao"]
                }
            else:
                # Garantir que campos novos existam
                if "bonus" not in ficha["pericias"][pericia]:
                    ficha["pericias"][pericia]["bonus"] = 0
                if "penalidade" not in ficha["pericias"][pericia]:
                    ficha["pericias"][pericia]["penalidade"] = 0
                if "atributo" not in ficha["pericias"][pericia]:
                    ficha["pericias"][pericia]["atributo"] = info["atributo_padrao"]

        # Adicionar suporte para múltiplos ofícios
        if "oficios_customizados" not in ficha:
            ficha["oficios_customizados"] = []

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

        return ficha
    except Exception as e:
        st.error(f"Erro ao carregar a ficha: {str(e)}")
        return None

# Função para criar barra de recursos
def criar_barra_recursos(nome, valor_atual, valor_maximo, cor):
    if valor_maximo == 0:
        porcentagem = 0
    else:
        porcentagem = (valor_atual / valor_maximo) * 100

    # Estilo CSS melhorado para as barras
    st.markdown(f"""
        <div style="margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <span style="font-weight: bold; color: white;">{nome}</span>
                <span style="color: {cor}; font-weight: bold;">{valor_atual}/{valor_maximo}</span>
            </div>
            <div style="background-color: #333; border-radius: 10px; height: 20px; overflow: hidden;">
                <div style="background-color: {cor}; height: 100%; width: {porcentagem}%; transition: width 0.3s ease; border-radius: 10px;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Inicializar session state
if "ficha" not in st.session_state:
    st.session_state.ficha = {
        "nome": "",
        "nivel": 1,
        "raca": "",
        "classes": [{"nome": "", "nivel": 1}],
        "divindade": "",
        "tendencia": "",
        "atributos": {
            "forca": 10,
            "destreza": 10,
            "constituicao": 10,
            "inteligencia": 10,
            "sabedoria": 10,
            "carisma": 10
        },
        "pericias": {pericia: {"treinada": False, "bonus": 0, "penalidade": 0, "atributo": info["atributo_padrao"]} for pericia, info in PERICIAS.items()},
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
            "arcana": {nivel: [] for nivel in MAGIAS["Arcana"]},
            "divina": {nivel: [] for nivel in MAGIAS["Divina"]}
        },
        "poderes": [],
        "habilidades": [],
        "recursos": {
            "vida": {"atual": 0, "maximo": 0},
            "mana": {"atual": 0, "maximo": 0},
            "prana": {"atual": 0, "maximo": 0}
        },
        "recursos_adicionais": [],
        "oficios_customizados": []
    }

# Título principal
st.title("Ficha de Personagem - Tormenta 20")

# Colunas para layout
col1, col2 = st.columns([1, 2])

with col1:
    # Exibir imagem existente - CORRIGIDO
    if st.session_state.ficha.get("imagem"):
        try:
            imagem = base64_to_image(st.session_state.ficha["imagem"])
            if imagem:
                st.image(imagem, caption="Imagem do Personagem", width=300)
        except Exception as e:
            st.error(f"Erro ao exibir imagem: {str(e)}")
            st.session_state.ficha["imagem"] = None

    # Upload de nova imagem - CORRIGIDO
    uploaded_file = st.file_uploader("Escolha uma imagem para o personagem", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            # Converter para RGB se necessário
            if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
                image = image.convert('RGB')
            st.session_state.ficha["imagem"] = image_to_base64(image)
            st.image(image, caption="Imagem do Personagem", width=300)
            st.success("Imagem carregada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao carregar imagem: {str(e)}")

    # Botão para remover imagem
    if st.session_state.ficha.get("imagem") and st.button("Remover Imagem"):
        st.session_state.ficha["imagem"] = None
        st.rerun()

with col2:
    # Informações básicas
    st.subheader("Informações Básicas")
    st.session_state.ficha["nome"] = st.text_input("Nome do Personagem", value=st.session_state.ficha["nome"])
    st.session_state.ficha["nivel"] = st.number_input("Nível", min_value=1, max_value=20, value=st.session_state.ficha["nivel"])
    st.session_state.ficha["raca"] = st.text_input("Raça", value=st.session_state.ficha["raca"])
    st.session_state.ficha["divindade"] = st.text_input("Divindade", value=st.session_state.ficha["divindade"])
    st.session_state.ficha["tendencia"] = st.text_input("Tendência", value=st.session_state.ficha["tendencia"])

# Seção de atributos
st.subheader("Atributos")
col_atr1, col_atr2, col_atr3 = st.columns(3)

with col_atr1:
    st.session_state.ficha["atributos"]["forca"] = st.number_input("Força", min_value=1, max_value=30, value=st.session_state.ficha["atributos"]["forca"])
    st.session_state.ficha["atributos"]["destreza"] = st.number_input("Destreza", min_value=1, max_value=30, value=st.session_state.ficha["atributos"]["destreza"])

with col_atr2:
    st.session_state.ficha["atributos"]["constituicao"] = st.number_input("Constituição", min_value=1, max_value=30, value=st.session_state.ficha["atributos"]["constituicao"])
    st.session_state.ficha["atributos"]["inteligencia"] = st.number_input("Inteligência", min_value=1, max_value=30, value=st.session_state.ficha["atributos"]["inteligencia"])

with col_atr3:
    st.session_state.ficha["atributos"]["sabedoria"] = st.number_input("Sabedoria", min_value=1, max_value=30, value=st.session_state.ficha["atributos"]["sabedoria"])
    st.session_state.ficha["atributos"]["carisma"] = st.number_input("Carisma", min_value=1, max_value=30, value=st.session_state.ficha["atributos"]["carisma"])

# Seção de perícias - IMPLEMENTAÇÃO CORRIGIDA
st.subheader("🎯 Perícias")
st.write("Marque as perícias treinadas, escolha o atributo base e defina bônus/penalidades adicionais.")

# Estilo CSS para as perícias
st.markdown("""
    <style>
    .pericia-container {
        background-color: #2e2e2e;
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
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
    </style>
""", unsafe_allow_html=True)

# Seção de Ofícios Customizados
with st.expander("🔧 Ofícios Customizados"):
    st.write("Adicione ofícios específicos (ex: Ferreiro, Carpinteiro, etc.)")

    # Interface para adicionar novos ofícios
    col_oficio1, col_oficio2 = st.columns([3, 1])
    with col_oficio1:
        novo_oficio = st.text_input("Nome do Ofício", placeholder="Ex: Ferreiro, Carpinteiro, etc.")
    with col_oficio2:
        if st.button("➕ Adicionar Ofício"):
            if novo_oficio and f"Ofício ({novo_oficio})" not in st.session_state.ficha["oficios_customizados"]:
                st.session_state.ficha["oficios_customizados"].append(f"Ofício ({novo_oficio})")
                # Adicionar à estrutura de perícias
                oficio_nome = f"Ofício ({novo_oficio})"
                st.session_state.ficha["pericias"][oficio_nome] = {
                    "treinada": False,
                    "bonus": 0,
                    "penalidade": 0,
                    "atributo": "inteligencia"
                }
                st.rerun()

    # Listar ofícios customizados existentes
    if st.session_state.ficha["oficios_customizados"]:
        st.write("**Ofícios Cadastrados:**")
        for i, oficio in enumerate(st.session_state.ficha["oficios_customizados"]):
            col_off1, col_off2 = st.columns([4, 1])
            with col_off1:
                st.write(f"• {oficio}")
            with col_off2:
                if st.button("🗑️", key=f"remove_oficio_{i}"):
                    # Remove do session_state
                    if oficio in st.session_state.ficha["pericias"]:
                        del st.session_state.ficha["pericias"][oficio]
                    st.session_state.ficha["oficios_customizados"].remove(oficio)
                    st.rerun()

# Criar lista de todas as perícias (padrão + ofícios customizados)
todas_pericias = dict(PERICIAS)
for oficio in st.session_state.ficha["oficios_customizados"]:
    todas_pericias[oficio] = {"atributo_padrao": "inteligencia", "penalidade_armadura": False}

# Criar colunas para organizar as perícias
columns = st.columns(3)
pericias_lista = list(todas_pericias.items())
pericias_por_coluna = len(pericias_lista) // 3 + (1 if len(pericias_lista) % 3 else 0)

# Função para atualizar o estado da perícia
def atualizar_pericia(pericia, field, value):
    if pericia in st.session_state.ficha["pericias"]:
        st.session_state.ficha["pericias"][pericia][field] = value

# Exibir perícias em cada coluna
for col_idx, col in enumerate(columns):
    with col:
        inicio = col_idx * pericias_por_coluna
        fim = min((col_idx + 1) * pericias_por_coluna, len(pericias_lista))

        for i in range(inicio, fim):
            if i < len(pericias_lista):
                pericia, info = pericias_lista[i]

                # Garantir que a perícia existe na ficha
                if pericia not in st.session_state.ficha["pericias"]:
                    st.session_state.ficha["pericias"][pericia] = {
                        "treinada": False,
                        "bonus": 0,
                        "penalidade": 0,
                        "atributo": info["atributo_padrao"]
                    }

                # Calcular bônus atual
                atributo_valor = st.session_state.ficha["atributos"][st.session_state.ficha["pericias"][pericia]["atributo"]]
                treinada = st.session_state.ficha["pericias"][pericia]["treinada"]
                bonus_adicional = st.session_state.ficha["pericias"][pericia]["bonus"]
                penalidade = st.session_state.ficha["pericias"][pericia]["penalidade"]

                bonus_total = calcular_bonus_pericia(atributo_valor, treinada, st.session_state.ficha["nivel"], bonus_adicional, penalidade)

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
                # Checkbox para treinada
                st.session_state.ficha["pericias"][pericia]["treinada"] = st.checkbox(
                    "Treinada",
                    value=st.session_state.ficha["pericias"][pericia]["treinada"],
                    key=f"pericia_treinada_{pericia}"
                )

                # Selectbox para atributo
                atributo_atual = st.session_state.ficha["pericias"][pericia]["atributo"]
                if atributo_atual in ATRIBUTOS:
                    index_atual = ATRIBUTOS.index(atributo_atual)
                else:
                    index_atual = 0

                st.session_state.ficha["pericias"][pericia]["atributo"] = st.selectbox(
                    "Atributo",
                    options=ATRIBUTOS,
                    index=index_atual,
                    key=f"pericia_atributo_{pericia}"
                )

                # Controles para bônus e penalidade
                col_bonus, col_penalidade = st.columns(2)
                with col_bonus:
                    st.session_state.ficha["pericias"][pericia]["bonus"] = st.number_input(
                        "Bônus",
                        min_value=-10,
                        max_value=20,
                        value=st.session_state.ficha["pericias"][pericia]["bonus"],
                        key=f"pericia_bonus_{pericia}"
                    )
                with col_penalidade:
                    st.session_state.ficha["pericias"][pericia]["penalidade"] = st.number_input(
                        "Penalidade",
                        min_value=0,
                        max_value=20,
                        value=st.session_state.ficha["pericias"][pericia]["penalidade"],
                        key=f"pericia_penalidade_{pericia}"
                    )

                st.markdown("---")

# Seção de Recursos
st.subheader("⚡ Recursos")
col_vida, col_mana, col_prana = st.columns(3)

with col_vida:
    st.session_state.ficha["recursos"]["vida"]["maximo"] = st.number_input(
        "Pontos de Vida Máximos", 
        min_value=0, 
        value=st.session_state.ficha["recursos"]["vida"]["maximo"]
    )
    st.session_state.ficha["recursos"]["vida"]["atual"] = st.number_input(
        "Pontos de Vida Atuais", 
        min_value=0, 
        max_value=st.session_state.ficha["recursos"]["vida"]["maximo"],
        value=min(st.session_state.ficha["recursos"]["vida"]["atual"], st.session_state.ficha["recursos"]["vida"]["maximo"])
    )
    criar_barra_recursos("Vida", st.session_state.ficha["recursos"]["vida"]["atual"], st.session_state.ficha["recursos"]["vida"]["maximo"], "#FF4444")

with col_mana:
    st.session_state.ficha["recursos"]["mana"]["maximo"] = st.number_input(
        "Pontos de Mana Máximos", 
        min_value=0, 
        value=st.session_state.ficha["recursos"]["mana"]["maximo"]
    )
    st.session_state.ficha["recursos"]["mana"]["atual"] = st.number_input(
        "Pontos de Mana Atuais", 
        min_value=0, 
        max_value=st.session_state.ficha["recursos"]["mana"]["maximo"],
        value=min(st.session_state.ficha["recursos"]["mana"]["atual"], st.session_state.ficha["recursos"]["mana"]["maximo"])
    )
    criar_barra_recursos("Mana", st.session_state.ficha["recursos"]["mana"]["atual"], st.session_state.ficha["recursos"]["mana"]["maximo"], "#4444FF")

with col_prana:
    st.session_state.ficha["recursos"]["prana"]["maximo"] = st.number_input(
        "Pontos de Prana Máximos", 
        min_value=0, 
        value=st.session_state.ficha["recursos"]["prana"]["maximo"]
    )
    st.session_state.ficha["recursos"]["prana"]["atual"] = st.number_input(
        "Pontos de Prana Atuais", 
        min_value=0, 
        max_value=st.session_state.ficha["recursos"]["prana"]["maximo"],
        value=min(st.session_state.ficha["recursos"]["prana"]["atual"], st.session_state.ficha["recursos"]["prana"]["maximo"])
    )
    criar_barra_recursos("Prana", st.session_state.ficha["recursos"]["prana"]["atual"], st.session_state.ficha["recursos"]["prana"]["maximo"], "#44FF44")

# Seção de Defesas
st.subheader("🛡️ Defesas")
col_def1, col_def2 = st.columns(2)

with col_def1:
    st.write("**Defesa**")
    usar_atributo = st.checkbox("Usar modificador de atributo", value=True, key="usar_atributo_defesa")
    if usar_atributo:
        atributo_defesa = st.selectbox(
            "Atributo para Defesa",
            options=ATRIBUTOS,
            index=ATRIBUTOS.index("destreza"),
            key="atributo_defesa"
        )
    else:
        atributo_defesa = "destreza"

    bonus_equipamento = st.number_input("Bônus de Equipamento", -10, 20, 0, key="bonus_equipamento_defesa")
    bonus_reflexo = st.number_input("Bônus de Reflexos", -10, 20, 0, key="bonus_reflexos_defesa")

    defesa_total = calcular_defesa(
        st.session_state.ficha["atributos"],
        bonus_equipamento,
        usar_atributo,
        atributo_defesa,
        bonus_reflexo
    )

    st.markdown(f"**Defesa Total: {defesa_total}**")

with col_def2:
    st.write("**Deslocamento**")
    deslocamento = calcular_deslocamento(
        st.session_state.ficha["atributos"],
        raca=st.session_state.ficha["raca"]
    )
    st.markdown(f"**Deslocamento: {deslocamento}m**")

# Seção de Importação/Exportação - CORRIGIDA
st.subheader("💾 Importar/Exportar Ficha")

col_import, col_export = st.columns(2)

with col_import:
    st.write("**Importar Ficha**")

    # Upload de arquivo JSON
    uploaded_json = st.file_uploader("Selecione um arquivo JSON", type=['json'], key="import_json")
    if uploaded_json is not None:
        try:
            json_content = uploaded_json.read().decode('utf-8')
            ficha_importada = carregar_ficha(json_content)

            if ficha_importada:
                if st.button("Confirmar Importação"):
                    st.session_state.ficha = ficha_importada
                    st.success("Ficha importada com sucesso!")
                    st.rerun()
                else:
                    st.info("Clique em 'Confirmar Importação' para carregar a ficha")
        except Exception as e:
            st.error(f"Erro ao importar ficha: {str(e)}")

    # Campo de texto para colar JSON
    json_text = st.text_area("Ou cole o JSON aqui:", height=100, key="json_paste")
    if json_text and st.button("Importar do Texto"):
        try:
            ficha_importada = carregar_ficha(json_text)
            if ficha_importada:
                st.session_state.ficha = ficha_importada
                st.success("Ficha importada com sucesso!")
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao importar ficha: {str(e)}")

with col_export:
    st.write("**Exportar Ficha**")

    # Botão para salvar ficha
    if st.button("Gerar JSON da Ficha"):
        ficha_json = salvar_ficha(st.session_state.ficha)
        nome_arquivo = f"{st.session_state.ficha['nome']}.json" if st.session_state.ficha['nome'] else "ficha_t20.json"

        st.download_button(
            label="📥 Baixar Ficha",
            data=ficha_json,
            file_name=nome_arquivo,
            mime="application/json"
        )

        # Mostrar o JSON em um campo de texto para copiar
        st.text_area("JSON da Ficha (para copiar):", value=ficha_json, height=200, key="json_output")

# Seção de Classes
st.subheader("🎓 Classes")
if st.button("Adicionar Classe"):
    st.session_state.ficha["classes"].append({"nome": "", "nivel": 1})
    st.rerun()

for i, classe in enumerate(st.session_state.ficha["classes"]):
    col_classe1, col_classe2, col_classe3 = st.columns([3, 1, 1])

    with col_classe1:
        st.session_state.ficha["classes"][i]["nome"] = st.text_input(
            f"Nome da Classe {i+1}", 
            value=classe["nome"], 
            key=f"classe_nome_{i}"
        )

    with col_classe2:
        st.session_state.ficha["classes"][i]["nivel"] = st.number_input(
            f"Nível {i+1}", 
            min_value=1, 
            max_value=20, 
            value=classe["nivel"], 
            key=f"classe_nivel_{i}"
        )

    with col_classe3:
        if st.button("🗑️", key=f"remove_classe_{i}"):
            if len(st.session_state.ficha["classes"]) > 1:
                st.session_state.ficha["classes"].pop(i)
                st.rerun()
            else:
                st.error("Deve ter pelo menos uma classe!")

# Seção de Poderes
st.subheader("✨ Poderes")
novo_poder = st.text_input("Adicionar Poder")
if st.button("Adicionar Poder") and novo_poder:
    st.session_state.ficha["poderes"].append({"nome": novo_poder, "descricao": ""})
    st.rerun()

for i, poder in enumerate(st.session_state.ficha["poderes"]):
    with st.expander(f"Poder: {poder['nome']}"):
        st.session_state.ficha["poderes"][i]["nome"] = st.text_input(
            "Nome do Poder", 
            value=poder["nome"], 
            key=f"poder_nome_{i}"
        )
        st.session_state.ficha["poderes"][i]["descricao"] = st.text_area(
            "Descrição", 
            value=poder["descricao"], 
            key=f"poder_desc_{i}"
        )
        if st.button("Remover Poder", key=f"remove_poder_{i}"):
            st.session_state.ficha["poderes"].pop(i)
            st.rerun()

# Seção de Habilidades
st.subheader("🏹 Habilidades")
nova_habilidade = st.text_input("Adicionar Habilidade")
if st.button("Adicionar Habilidade") and nova_habilidade:
    st.session_state.ficha["habilidades"].append({"nome": nova_habilidade, "descricao": ""})
    st.rerun()

for i, habilidade in enumerate(st.session_state.ficha["habilidades"]):
    with st.expander(f"Habilidade: {habilidade['nome']}"):
        st.session_state.ficha["habilidades"][i]["nome"] = st.text_input(
            "Nome da Habilidade", 
            value=habilidade["nome"], 
            key=f"habilidade_nome_{i}"
        )
        st.session_state.ficha["habilidades"][i]["descricao"] = st.text_area(
            "Descrição", 
            value=habilidade["descricao"], 
            key=f"habilidade_desc_{i}"
        )
        if st.button("Remover Habilidade", key=f"remove_habilidade_{i}"):
            st.session_state.ficha["habilidades"].pop(i)
            st.rerun()

# Footer
st.markdown("---")
st.markdown("**Ficha T20** - Criada com Streamlit 🎲")
