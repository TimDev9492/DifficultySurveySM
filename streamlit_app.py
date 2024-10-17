import streamlit as st
from st_supabase_connection import SupabaseConnection

st_supabase_client = st.connection(name='supabase', type=SupabaseConnection)
st_supabase_client.client.postgrest.schema(st.secrets.DB_SCHEMA or 'dev')

st.title("Rate the difficulty of Minecraft Missions!")
st.write(
    f'Using database schema "{st.secrets.DB_SCHEMA}"'
)
