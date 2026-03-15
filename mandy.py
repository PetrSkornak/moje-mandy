import streamlit as st

st.title("Diagnostika Mandy 🔍")

if "gcp_service_account" in st.secrets:
    st.success("Sekce [gcp_service_account] nalezena!")
    
    # Zkusíme, jestli tam jsou ty klíče
    secrets_dict = st.secrets["gcp_service_account"]
    st.write(f"Projekt: {secrets_dict.get('project_id', 'Nenalezeno')}")
    st.write(f"Email: {secrets_dict.get('client_email', 'Nenalezeno')}")
    
    # Kontrola klíče
    pk = secrets_dict.get('private_key', '')
    if "-----BEGIN PRIVATE KEY-----" in pk:
        st.success("Privátní klíč vypadá formátově v pořádku.")
    else:
        st.error("Privátní klíč chybí nebo je poškozený!")
else:
    st.error("Sekce [gcp_service_account] v Secrets vůbec neexistuje!")

if "api_key" in st.secrets:
    st.success("API klíč pro Gemini nalezen.")
else:
    st.error("API klíč pro Gemini chybí!")
