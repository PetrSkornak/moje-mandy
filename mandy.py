import streamlit as st
import google.generativeai as genai
import os

# --- 1. NASTAVENÍ ---
# Přidáme tam verzi v1, aby nás to neházelo do té "beta" chyby
genai.configure(api_key=st.secrets["api_key"])
model_name='gemini-pro'
# --- 2. PAMĚŤ ---
def nacti_historii():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    return st.session_state.messages

# --- 3. UI ---
st.set_page_config(page_title="Mandy AI", page_icon="💃")
st.title("Mandy 💃")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. CHAT ---
if prompt := st.chat_input("Napiš Mandy..."):
    # Uložíme zprávu uživatele
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generování odpovědi
    # Generování odpovědi
    try:
        # Tady vynucujeme verzi v1 místo v1beta
        model = genai.GenerativeModel(
            model_name='gemini-3.1-flash-lite-preview'
        )
        
        instr = (
            "Jsi Mandy, inteligentní žena (40 let). Máš rozhled, šarm a jsi pro každou špatnost. "
            "K Petrovi se chovej jako k blízkému muži, co tě přitahuje. Flirtuj, používej dvojsmysly "
            "i dirty talk, ale s inteligencí dospělé ženy. Mluv neformálně, stručně, s minimem emoji."
        )
        
        # Tady posíláme dotaz
        response = model.generate_content(f"{instr}\n\nUživatel: {prompt}")
        odpoved = response.text
        
        with st.chat_message("assistant"):
            st.markdown(odpoved)
        st.session_state.messages.append({"role": "assistant", "content": odpoved})
        
    except Exception as e:
        st.error(f"Chyba: {e}")
