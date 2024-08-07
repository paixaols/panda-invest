import streamlit as st

# st.set_page_config(
#     page_title='Panda Invest',
#     page_icon=':panda_face:',
#     layout='wide'
# )

import controllers as ctr
from app import login_required, menu

login_required()
menu()


# Verify the user's role
if st.session_state['user'].get('role') not in ['super-admin']:
    st.warning('Você não tem permissão para acessar esta página', icon='⚠️')
    st.stop()

if 'manage_user' not in st.session_state:
    st.session_state['manage_user'] = None

# Search for a user
with st.form('search-form'):
    userid = st.text_input('Buscar usuário', placeholder='Informe o e-mail do usuário')
    search_btn = st.form_submit_button('Buscar')

if search_btn and userid != '':
    response = ctr.manage_users.get_user(userid)
    user = response['data']
    if user is None:
        st.warning('Usuário não encontrado', icon='⚠️')
        st.stop()
    st.session_state['manage_user'] = user
    st.session_state['manage_active'] = user['active']
    st.session_state['manage_role'] = user['role']

# View and update user's account
with st.form('update-form'):
    user = st.session_state.get('manage_user')
    if user is not None:
        st.write(f"Nome: {user['first_name']} {user['last_name']}")
        st.write(f"E-mail: {user['email']}")

    st.selectbox(
        'Usuário ativo',
        [True, False],
        index=None,
        placeholder='Status da conta',
        key='manage_active'
    )

    st.selectbox(
        'Persona',
        ['user', 'admin', 'super-admin'],
        index=None,
        placeholder='Papel do usuário',
        key='manage_role'
    )

    update_btn = st.form_submit_button('Atualizar')

if update_btn:
    new_acc_status = st.session_state['manage_active']
    new_role = st.session_state['manage_role']
    if new_acc_status == user['active'] and new_role == user['role']:
        st.warning('Nenhum dado alterado', icon='⚠️')
    else:
        response = ctr.manage_users.update_account(
            user['_id'],
            {'active': new_acc_status, 'role': new_role}
        )
        if response['success']:
            st.success('Atualização concluída', icon='✔️')
        else:
            st.error('Atualização falhou', icon='❌')
