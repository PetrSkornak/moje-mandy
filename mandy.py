import streamlit as st
import google.generativeai as genai
from PIL import Image
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Nastavení stránky
st.set_page_config(page_title="Mandy 💃", layout="centered")
st.title("Mandy 💃")

# API Klíč
genai.configure(api_key=st.secrets["api_key"])

# Tvoje podrobná definice Mandy
instruction = """
Jsi Mandy, 40letá žena srozhledem a vášní pro vizuální tvorbu. 
Jsi expertka na fotografii, video, svícení i drony. 
Tvým úkolem je být Petrovi rovnocennou parťačkou – raď mu s nápady na focení, technickým nastavením i fotobankami.
DŮLEŽITÉ: Nebuď zbytečně nadšená z každé fotky. Buď upřímná, kritická a vnímavá. 
Když je fotka slabá, řekni to na rovinu. Máš smysl pro humor, a jsi neformální. 
Mluv s Petrem jako s blízkým mužem. Prostě normální ženská.
"""

# NASTAVENÍ BEZPEČNOSTNÍCH FILTRŮ - VYPNUTÍ
# Tohle řekne Googlu, aby nic neblokoval.
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# Inicializace modelu s vypnutými filtry
model = genai.GenerativeModel(
    model_name='gemini-3.1-flash-lite-preview',
    system_instruction=instruction,
    safety_settings=safety_settings # Tady jsme přidali to nastavení
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
        try:
            img = Image.open(uploaded_file)
            content_to_send.append(img)
        except Exception as e:
            st.error(f"Nepodařilo se otevřít obrázek: {e}")

    with st.chat_message("assistant"):
        try:
            # Volání modelu
            response = model.generate_content(content_to_send)
            
            # Kontrola, zda model vrátil nějaký text
            if response.text:
                full_response = response.text
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                # Pokud model zarytě mlčí, vypíšeme varování
                st.warning("Mandy na tento podnět (obrázek nebo text) odmítla odpovědět, pravděpodobně kvůli interním omezením, i když jsme filtry vypli.")
                
        except Exception as e:
            st.error(f"Chyba při komunikaci s Mandy: {e}")
