import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# Como você usaria:
# supabase = init_connection()
# response = supabase.table('meu_dataset').select("*").execute()