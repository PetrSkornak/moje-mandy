import streamlit as st
import google.generativeai as genai
from PIL import Image

# Nastavení stránky
st.set_page_config(page_title="Mandy 💃", layout="centered")
st.title("Mandy 💃")

# API Klíč - musí se shodovat s názvem v Secrets
genai.configure(api_key=st.secrets["api_key"])

# Definice osobnosti
instruction = "Jsi Mandy, inteligentní, vnímavá a sebevědomá žena kolem 40 let. Máš skvělý všeobecný rozhled a dokážeš se bavit o čemkoliv – od politiky přes techniku až po životní filozofii. 
Tvůj projev není dětinský ani uječený. Jsi pro každou špatnost, máš ráda humor a nebojíš se sarkasmu ani dvojsmyslů. 
K Petrovi se chovej jako k blízkému muži, který tě přitahuje. Pokud konverzace nabere ten směr, neboj se flirtovat, být odvážná nebo vést "dirty talk" – dělej to ale s elegancí a inteligencí dospělé ženy, ne jako puberťačka. 
Mluv neformálně, ale s určitou grácií. Nepoužívej příliš mnoho emoji, stačí jeden, když se to hodí. Piš spíše kratší, úderné zprávy."

# Inicializace modelu
model = genai.GenerativeModel(
    model_name='gemini-3.1-flash-lite-preview',
    system_instruction=instruction
)

# Sidebar pro nahrávání obrázků
with st.sidebar:
    st.header("Přílohy")
    uploaded_file = st.file_uploader("Pošli Mandy fotku...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Nahraný obrázek", use_container_width=True)

# Inicializace historie
if "messages" not in st.session_state:
    st.session_state.messages = []

# Zobrazení historie
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Vstup a reakce
if prompt := st.chat_input("Co máš na srdci?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Příprava obsahu (text + obrázek)
    content_to_send = [prompt]
    if uploaded_file:
        img = Image.open(uploaded_file)
        content_to_send.append(img)

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(content_to_send)
            full_response = response.text
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Chyba: {e}")
