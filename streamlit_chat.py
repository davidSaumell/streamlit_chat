import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage
import time

st.set_page_config(page_title="Davo-Bot", page_icon="🤖")
st.markdown("""
    <div style="
        font-size:32px; 
        font-weight:700; 
        line-height:1.2; 
        color:#4A90E2; 
        margin-bottom:5px;
    ">
        🤖 Davo-Bot
    </div>
    <div style="
        font-size:18px; 
        color:#666666; 
        line-height:1.5; 
        margin-bottom:20px;
    ">
        ¿En que estás trabajando?
    </div>
""", unsafe_allow_html=True)

st.divider()
st.markdown("""
    <style>
        .stChatMessage {
            padding: 10px;
            border: 1px solid #444;
        }
    </style>
""", unsafe_allow_html=True)

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if "ultima_pregunta" not in st.session_state:
    st.session_state.ultima_pregunta = None

def export_md():
    md_text = "# Conversación Chatbot Gemini\n\n"
    for msg in st.session_state.mensajes:
        if isinstance(msg, HumanMessage):
            md_text += f"**Usuario:** {msg.content}\n\n"
        elif isinstance(msg, AIMessage):
            md_text += f"**Asistente:** {msg.content}\n\n"
    return md_text

with st.sidebar:
    st.header("⚙️ Configuraciones")

    tema_oscuro = st.toggle("🌙 Tema oscuro")

    if tema_oscuro:
        st.markdown("""
        <style>

        .stApp {
            background-color: #0f0f0f;
            color: #fafafa;
        }

        section[data-testid="stSidebar"] {
            background-color: #1a1a1a;
            color: white;
        }

        .stMarkdown, .stText, .stHeader, p, div, label, span {
            color: #B9B9B9;
        }

        input[type="text"], textarea, .stTextInput input {
            background-color: #333333;
            color: white;
            border: 1px solid #555;
        }

        .stChatMessage {
            background-color: #1c1c1c;
            border-radius: 10px;
            padding: 10px;
            border: 1px solid #444;
        }
                    
        </style>
        """, unsafe_allow_html=True)

    usar_color_personalizado = st.sidebar.toggle("🖌️ Cambiar color de letra")

    if usar_color_personalizado:
        color_letra = st.sidebar.color_picker("Elige el color de letra", "#FFFFFF")
        st.markdown(f"""
        <style>
        .stApp, .stMarkdown, .stText, .stHeader, p, div, span, label, input {{
            color: {color_letra};
        }}

        .stChatMessage {{
            color: {color_letra};
        }}

        input[type="text"], textarea, .stTextInput input {{
            color: {color_letra};
        }}
        </style>
        """, unsafe_allow_html=True)

    st.divider()

    preset = st.selectbox(
        "Modo rápido",
        [
            "Normal",
            "Explicación técnica",
            "Tono amistoso",
            "Resumir",
            "Responder como experto",
            "Responder como profesor"
        ]
    )

    st.divider()

    st.header("Modelo Gemini")
    temp_labels = {"Coherente": 0.4, "Equilibrado": 0.7, "Creativo": 1}
    temp_choice = st.slider("Estilo de respuesta", 0, 2, 1, format="%d")
    model_temperature = list(temp_labels.values())[temp_choice]
    st.write("Modo:", list(temp_labels.keys())[temp_choice])

    gemini_version = st.selectbox(
        "Gemini versión",
        [
            "2.5-flash",
            "2.5-flash-lite",
            "2.0-flash-001",
            "2.0-flash-lite-001"
        ]
    )

model = "gemini-" + gemini_version
chat_model = ChatGoogleGenerativeAI(model=model, temperature=model_temperature)

for msg in st.session_state.mensajes:
    role = "assistant" if isinstance(msg, AIMessage) else "user"
    avatar = "🤖" if isinstance(msg, AIMessage) else "👤"
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg.content)

pregunta = st.chat_input("Escribe tu mensaje:")

def aplicar_preset(texto, modo):
    if modo == "Normal":
        return texto
    if modo == "Explicación técnica":
        return "Explica de forma técnica y detallada: " + texto
    if modo == "Tono amistoso":
        return "Responde con un tono amistoso y cercano: " + texto
    if modo == "Resumir":
        return "Resume claramente: " + texto
    if modo == "Responder como experto":
        return "Responde como un experto en el tema: " + texto
    if modo == "Responder como profesor":
        return "Explícalo como un profesor paciente: " + texto
    return texto

if pregunta:
    texto_modificado = aplicar_preset(pregunta, preset)

    st.session_state.ultima_pregunta = texto_modificado

    st.session_state.mensajes.append(HumanMessage(content=texto_modificado))
    with st.chat_message("user", avatar="👤"):
        st.markdown(texto_modificado)

    with st.spinner("🤖 Pensando..."):
        time.sleep(1)
        respuesta = chat_model.invoke(st.session_state.mensajes)
        st.session_state.mensajes.append(respuesta)

    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(respuesta.content)

if st.session_state.ultima_pregunta:
    col1, col2, col3 = st.columns([4, 1, 1])

    with col1:
        if st.button("🔄 Regenerar respuesta"):
            st.session_state.mensajes.append(HumanMessage(content=st.session_state.ultima_pregunta))
            with st.spinner("♻️ Repensando..."):
                respuesta = chat_model.invoke(st.session_state.mensajes)
                st.session_state.mensajes.append(respuesta)
            st.rerun()

    with col2:
        if st.button("🧹", help="Limpiar conversación"):
            st.session_state.mensajes = []
            st.success("Conversación limpiada")
            st.rerun()

    with col3:
        st.download_button(
            label="⬇️",
            data=export_md(),
            file_name="conversacion.md",
            mime="text/markdown",
            help="Exportar conversación"
    )
