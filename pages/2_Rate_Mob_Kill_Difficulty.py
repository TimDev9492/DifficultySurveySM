import streamlit as st
import random
from st_supabase_connection import SupabaseConnection, execute_query

st_supabase_client = st.connection(name='supabase', type=SupabaseConnection)
st_supabase_client.client.postgrest.schema(st.secrets.DB_SCHEMA or 'dev')

session_state_key = 'mob'
finished_flag_key = f'{session_state_key}_finished'
history_key = f'{session_state_key}_history'

# setup history
if not history_key in st.session_state:
    st.session_state[history_key] = []

def get_database_entry(persist_state=True):
    if persist_state and session_state_key in st.session_state:
        return st.session_state[session_state_key]

    response = st_supabase_client.table(
        'mob_types_to_kill'
    ).select(
        '*'
    ).is_(
        'difficulty', 'NULL'
    ).execute()

    if not response.data or len(response.data) == 0:
        st.session_state[finished_flag_key] = True
        return None

    st.session_state[finished_flag_key] = False
    resp_data = random.choice(response.data)
    st.session_state[session_state_key] = resp_data
    return resp_data

def get_progress():
    # Query to get the count of rows where difficulty is NULL
    response = st_supabase_client.client.rpc(
        'completion_progress', {
            'table_name': 'mob_types_to_kill',
            'condition': 'difficulty IS NOT NULL'
        }).execute()
        
    return response.data

def update_difficulty(difficulty, entry):
    response = st_supabase_client.table(
        'mob_types_to_kill'
    ).update({
        'difficulty': difficulty
    }).eq(
        'id', entry['id']
    ).execute()
    return response

get_database_entry()

if st.session_state[finished_flag_key]:
    st.title("All mobs have been rated!")
    st.stop()

progress = get_progress()
st.progress(progress, text="Progress: {:.2f}%".format(progress * 100))

st.title(st.session_state[session_state_key]['name'])
st.divider()
difficulty = st.slider(
    "How difficult is it to kill this mob? (1=Very Easy, 10=Impossible)",
    1, 10, 5 if session_state_key not in st.session_state or st.session_state[session_state_key]['difficulty'] == None else st.session_state[session_state_key]['difficulty']
)

left, middle, right = st.columns(3)

def save_difficulty_load_new_item():
    msg = st.toast("Saving changes...")
    updated = update_difficulty(difficulty, st.session_state[session_state_key])
    success = len(updated.data) > 0
    # push updated item to history
    st.session_state[history_key].append(updated.data[0])
    if success:
        msg.toast(f'Saved difficulty {difficulty} for "{st.session_state[session_state_key]["name"]}"')
    else:
        msg.toast(f'There was an error while trying to save the difficulty! Please try again.')
    get_database_entry(persist_state=not success)

def skip_entry():
    st.toast(f'Skipping "{st.session_state[session_state_key]["name"]}"...')
    get_database_entry(persist_state=False)

def go_back():
    if not history_key in st.session_state or len(st.session_state[history_key]) == 0:
        st.toast('No more items to go back to!')
        return
    st.session_state[session_state_key] = st.session_state[history_key].pop()

left.button("Go Back", use_container_width=True, on_click=go_back)
middle.button("Skip", use_container_width=True, on_click=skip_entry)
right.button("Save & Next", use_container_width=True, on_click=save_difficulty_load_new_item)
