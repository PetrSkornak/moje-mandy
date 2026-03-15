import streamlit as st
import google.generativeai as genai
from PIL import Image
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import gspread
from google.oauth2.service_account import Credentials

# Nastavení stránky
st.set_page_config(page_title="Mandy 💃", layout="centered")
st.title("Mandy 💃")

# --- PROPOJENÍ S GOOGLE SHEETS ---
@st.cache_resource
def get_gsheet_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Tady se děje to kouzlo, které opraví tu chybu PEM:
    creds_info = st.secrets["gcp_service_account"]
    if isinstance(creds_info, st.runtime.secrets.AttrDict):
        creds_info = dict(creds_info)
    
    # Oprava zalomení řádků v klíči
    creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
    
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gsheet_client()
    # ID tvojí tabulky
    sheet = client.open_by_key("1qRrw74IAnlbu4bgdywG2nEHnlEqZIYJTH3cPLbhSjYg").get_worksheet(0)
except Exception as e:
    st.error(f"Nepodařilo se připojit k tabulce: {e}")
    st.stop()

def load_history_from_sheets():
    # Načte řádky a převede je na formát pro chat
    rows = sheet.get_all_records()
    return [{"role": r["role"], "content": r["content"]} for r in rows]

def save_to_sheets(role, content):
    # Zapíše novou zprávu do tabulky
    sheet.append_row([role, content])

# --- KONFIGURACE GEMINI ---
genai.configure(api_key=st.secrets["api_key"])

# Tady je ta lidštější Mandy bez konkrétních názvů firem a měst
instruction = """
Jsi Mandy, inteligentní žena kolem 40 let s neformálním vystupováním. 
K Petrovi se chovej jako k blízkému parťákovi. Mluv s ním přirozeně a lidsky.
Nepoužívej konkrétní fakta (práce, bydliště) násilně, ber je jen jako kontext.
Máš ráda vizuální tvorbu, ale mluv o ní, jen když se to hodí.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash-latest',
    system_instruction=instruction,
    safety_settings={cat: HarmBlockThreshold.BLOCK_NONE for cat in HarmCategory}
)

# --- CHAT LOGIKA ---
if "messages" not in st.session_state:
    with st.spinner("Mandy si vzpomíná, o čem jste mluvili..."):
        st.session_state.messages = load_history_from_sheets()

# Sidebar pro doplňky
with st.sidebar:
    st.header("Přílohy")
    uploaded_file = st.file_uploader("Pošli fotku...", type=["jpg", "png", "jpeg"])
    if st.button("Smazat paměť"):
        sheet.clear()
        sheet.append_row(["role", "content"]) # Obnova hlavičky
        st.session_state.messages = []
        st.rerun()

# Zobrazení historie chatu
for message in st.session_state.messages:
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
            # Posíláme Gemini posledních 15 zpráv jako kontext
            history_for_gemini = []
            for m in st.session_state.messages[-15:]:
                history_for_gemini.append({"role": m["role"], "parts": [m["content"]]})
            
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
