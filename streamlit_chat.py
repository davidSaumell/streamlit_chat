import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage

# Configuración inicial
st.set_page_config(page_title="Chatbot Básico", page_icon="🤖")
st.title("🤖 Chatbot con LangChain")
st.markdown("¿Qué necesitas?")

gemini_version = "2.5-flash"
model_temperature = 0.7

with st.sidebar:
    st.header("Configurar modelo")
    with st.form("graph_parameters"):
        temp_labels = {"Coherente": 0.4, "Equilibrado": 0.7, "Creativo": 1}
        temp_choice = st.slider("Estilo de respuesta", 0, 2, 1, format="%d")
        temperatura = list(temp_labels.values())[temp_choice]
        st.write("Modo:", list(temp_labels.keys())[temp_choice])
        gemini_version = st.selectbox(
            "Gemini version",
            [
                "2.5-flash",
                "2.5-flash-lite",
                "2.0-flash-001",
                "2.0-flash-lite-001"
            ]
        )
        submitted = st.form_submit_button("Aplicar cambios")

model = "gemini-" + gemini_version
chat_model = ChatGoogleGenerativeAI(model=model, temperature=model_temperature)

# Inicializar el historial de mensajes en session_state
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Renderizar historial existente
for msg in st.session_state.mensajes:
    role = "assistant" if isinstance(msg, AIMessage) else "user"
    with st.chat_message(role):
        st.markdown(msg.content)

# Input de usuario
pregunta = st.chat_input("Escribe tu mensaje:")

if pregunta:
    # Mostrar y almacenar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(pregunta)
    
    st.session_state.mensajes.append(HumanMessage(content=pregunta))

    respuesta = chat_model.invoke(st.session_state.mensajes)

    with st.chat_message("assistant"):
        st.markdown(respuesta.content)

    st.session_state.mensajes.append(respuesta)
