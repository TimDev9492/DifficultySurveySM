import streamlit as st
from st_supabase_connection import SupabaseConnection, execute_query

st_supabase_client = st.connection(name='supabase', type=SupabaseConnection)
st_supabase_client.client.postgrest.schema(st.secrets.DB_SCHEMA or 'dev')

session_state_key = 'item'
finished_flag_key = 'finished'

def get_database_entry(persist_state=True):
    if persist_state and session_state_key in st.session_state:
        return st.session_state[session_state_key]

    response = st_supabase_client.table(
        'obtain_item_materials'
    ).select(
        '*'
    ).is_(
        'difficulty', 'NULL'
    ).limit(1).execute()

    if not response.data or len(response.data) == 0:
        st.session_state[finished_flag_key] = True
        return None

    st.session_state[finished_flag_key] = False
    resp_data = response.data[0]
    st.session_state[session_state_key] = resp_data
    return resp_data

def update_difficulty(difficulty, entry):
    response = st_supabase_client.table(
        'obtain_item_materials'
    ).update({
        'difficulty': difficulty
    }).eq(
        'id', entry['id']
    ).execute()
    return len(response.data) > 0

get_database_entry()

if st.session_state[finished_flag_key]:
    st.title("All items have been rated!")
    st.stop()

st.title(st.session_state[session_state_key]['name'])
st.divider()
difficulty = st.slider(
    "How difficult is it to get this item? (1=Very Easy, 10=Impossible)",
    1, 10, 5
)

_, center, _ = st.columns([2, 1, 2])

def save_difficulty_load_new_item():
    msg = st.toast("Saving changes...")
    success = update_difficulty(difficulty, st.session_state[session_state_key])
    if success:
        msg.toast(f'Saved difficulty {difficulty} for "{st.session_state[session_state_key]["name"]}"')
    else:
        msg.toast(f'There was an error while trying to save the difficulty! Please try again.')
    get_database_entry(persist_state=not success)

center.button("Save & Next", use_container_width=True, on_click=save_difficulty_load_new_item)
