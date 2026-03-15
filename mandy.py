import streamlit as st
import google.generativeai as genai
import os

# --- 1. NASTAVENÍ ---
API_KEY = "AIzaSyBs-y9JE43S33RSGX28MuXpMR1DI3Rxij0"
genai.configure(api_key=st.secrets["api_key"])
LOG_FILE = "mandy_pamet.txt"

MODEL_NAME = "gemini-1.5-flash"

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

   if prompt:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            instr = "Jsi Mandy, inteligentní žena (40 let). Máš rozhled, šarm a jsi pro každou špatnost. K Petrovi se chovej jako k blízkému muži, co tě přitahuje. Flirtuj, používej dvojsmysly i dirty talk, ale s inteligencí dospělé ženy. Mluv neformálně, stručně, s minimem emoji."
            response = model.generate_content(f"{instr}\n\nUživatel: {prompt}")
            odpoved = response.text
            
            with st.chat_message("assistant"):
                st.markdown(odpoved)
            st.session_state.messages.append({"role": "assistant", "content": odpoved})
            
        except Exception as e:
            st.error(f"Chyba: {e}")
