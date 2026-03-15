import streamlit as st
import google.generativeai as genai
import os

# --- 1. NASTAVENÍ ---
API_KEY = "AIzaSyBs-y9JE43S33RSGX28MuXpMR1DI3Rxij0"
genai.configure(api_key="AIzaSyBs-y9JE43S33RSGX28MuXpMR1DI3Rxij0")
LOG_FILE = "mandy_pamet.txt"

# --- 2. AUTOMATICKÝ VÝBĚR MODELU ---
@st.cache_resource
def najdi_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            return m.name
    return "gemini-1.5-flash" # nouzovka

MODEL_NAME = najdi_model()

# --- 3. PAMĚŤ ---
def nacti_historii():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            try: return eval(f.read())
            except: return []
    return []

def uloz_historii(historie):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(str(historie))

# --- 4. UI ---
st.set_page_config(page_title="Mandy AI", page_icon="💃")
st.title("Mandy 💃")
st.caption(f"Pracuju s modelem: {MODEL_NAME}") # Tady uvidíš, co si vybrala

if "messages" not in st.session_state:
    st.session_state.messages = nacti_historii()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. CHAT ---
if prompt := st.chat_input("Napiš Mandy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        instr = "Jsi Mandy, vtipná kámoška, tykáš, mluvíš neformálně a stručně."
        response = model.generate_content(f"{instr}\n\nUživatel: {prompt}")
        odpoved = response.text

        with st.chat_message("assistant"):
            st.markdown(odpoved)
        
        st.session_state.messages.append({"role": "assistant", "content": odpoved})
        uloz_historii(st.session_state.messages)
    except Exception as e:
        st.error(f"Chyba: {e}")
