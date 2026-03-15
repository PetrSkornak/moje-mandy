import streamlit as st
import google.generativeai as genai
from PIL import Image
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import gspread

# Nastavení stránky
st.set_page_config(page_title="Mandy 💃", layout="centered")
st.title("Mandy 💃")

# --- PROPOJENÍ S GOOGLE SHEETS ---
@st.cache_resource
def get_gsheet_client():
    return gspread.service_account_from_dict(st.secrets["gcp_service_account"])

try:
    client = get_gsheet_client()
    sheet = client.open_by_key("1qRrw74IAnlbu4bgdywG2nEHnlEqZIYJTH3cPLbhSjYg").get_worksheet(0)
except Exception as e:
    st.error(f"Nepodařilo se připojit k tabulce: {e}")
    st.stop()

def load_history_from_sheets():
    try:
        rows = sheet.get_all_records()
        return [{"role": r["role"], "content": r["content"]} for r in rows]
    except:
        return []

def save_to_sheets(role, content):
    try:
        sheet.append_row([str(role), str(content)])
    except:
        pass

# --- KONFIGURACE GEMINI ---
genai.configure(api_key=st.secrets["api_key"])

# --- KONFIGURACE GEMINI ---
genai.configure(api_key=st.secrets["api_key"])

# --- KONFIGURACE GEMINI ---
# Tady vynutíme nejnovější verzi rozhraní pro rok 2026
genai.configure(api_key=st.secrets["api_key"], transport='rest') 

instruction = """
Jsi Mandy, inteligentní žena kolem 40 let s neformálním vystupováním. 
K Petrovi se chovej jako k blízkému parťákovi. Mluv s ním přirozeně a lidsky.
Nepoužívej konkrétní fakta (práce, bydliště) násilně, ber je jen jako kontext.
Máš ráda vizuální tvorbu, ale mluv o ní, jen když se to hodí.
"""

# Použijeme přesný název pro Gemini 3
model = genai.GenerativeModel(
    model_name='gemini-3-flash',
    system_instruction=instruction
)

# --- CHAT LOGIKA ---
if "messages" not in st.session_state:
    with st.spinner("Mandy si vzpomíná..."):
        st.session_state.messages = load_history_from_sheets()

# Sidebar
with st.sidebar:
    st.header("Přílohy")
    uploaded_file = st.file_uploader("Pošli fotku...", type=["jpg", "png", "jpeg"])
    if st.button("Smazat paměť"):
        sheet.clear()
        sheet.append_row(["role", "content"])
        st.session_state.messages = []
        st.rerun()

# Zobrazení historie
for message in st.session_state.messages:
    if message["role"] in ["user", "assistant"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Vstup od uživatele
if prompt := st.chat_input("Co máš na srdci?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_to_sheets("user", prompt)

    with st.chat_message("assistant"):
        try:
            history_for_gemini = []
            for m in st.session_state.messages[-15:]:
                history_for_gemini.append({"role": m["role"], "parts": [str(m["content"])]})
            
            chat = model.start_chat(history=history_for_gemini[:-1])
            
            if uploaded_file:
                img = Image.open(uploaded_file)
                response = chat.send_message([prompt, img])
            else:
                response = chat.send_message(prompt)
            
            full_response = response.text
            st.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            save_to_sheets("assistant", full_response)
            
        except Exception as e:
            st.error(f"Chyba: {e}")
