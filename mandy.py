import streamlit as st
import google.generativeai as genai
from PIL import Image

# Nastavení stránky
st.set_page_config(page_title="Mandy 💃", layout="centered")
st.title("Mandy 💃")

# API Klíč (ten už máš v Secrets na Streamlitu)
genai.configure(api_key=st.secrets["api_key"])

# Inicializace modelu
model = genai.GenerativeModel(model_name='gemini-3.1-flash-lite-preview')

# Sidebar pro nahrávání obrázků
with st.sidebar:
    st.header("Přílohy")
    uploaded_file = st.file_uploader("Pošli Mandy fotku...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Nahraný obrázek", use_container_width=True)

# Inicializace historie chatu
if "messages" not in st.session_state:
    st.session_state.messages = []

# Zobrazení historie chatu
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Vstup od uživatele
if prompt := st.chat_input("Co máš na srdci?"):
    # Zobrazení zprávy uživatele
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Uložení do historie
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Příprava obsahu pro model (text + případný obrázek)
    content_to_send = [prompt]
    if uploaded_file:
        img = Image.open(uploaded_file)
        content_to_send.append(img)

    # Odpověď modelu
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # Tady posíláme text i fotku najednou
            response = model.generate_content(content_to_send)
            full_response = response.text
            message_placeholder.markdown(full_response)
            
            # Uložení odpovědi do historie
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Chyba: {e}")
