import streamlit as st

import controllers as ctr

def search_user(userid):
    user = ctr.manage_users.get_user(userid)
    st.session_state['_user'] = user

def create_page():
    # Verify the user's role
    if st.session_state['user'].get('role') not in ['super-admin']:
        st.warning('Você não tem permissão para acessar esta página', icon='⚠️')
        st.stop()

    if '_user' not in st.session_state:
        st.session_state['_user'] = None

    # Search for a user
    with st.form('search-form'):
        userid = st.text_input('Buscar usuário', placeholder='Informe o e-mail do usuário')
        search_btn = st.form_submit_button('Buscar')

    if search_btn and userid != '':
        user = ctr.manage_users.get_user(userid)
        if user is None:
            st.warning('Usuário não encontrado', icon='⚠️')
            st.stop()
        st.session_state['_user'] = user
        st.session_state['_active'] = user['active']
        st.session_state['_role'] = user['role']

    # View and update user's account
    with st.form('update-form'):
        user = st.session_state.get('_user')
        if user is not None:
            st.write(f"Nome: {user['first_name']} {user['last_name']}")
            st.write(f"E-mail: {user['email']}")

        st.selectbox(
            'Usuário ativo',
            [True, False],
            index=None,
            placeholder='Status da conta',
            key='_active'
        )

        st.selectbox(
            'Persona',
            ['user', 'admin', 'super-admin'],
            index=None,
            placeholder='Papel do usuário',
            key='_role'
        )

        update_btn = st.form_submit_button('Atualizar')

    if update_btn:
        new_acc_status = st.session_state['_active']
        new_role = st.session_state['_role']
        if new_acc_status == user['active'] and new_role == user['role']:
            st.warning('Nenhum dado alterado', icon='⚠️')
        else:
            success = ctr.manage_users.update_account(
                user['_id'],
                {'active': new_acc_status, 'role': new_role}
            )
            if success:
                st.success('Atualização concluída', icon='✔️')
            else:
                st.error('Atualização falhou', icon='❌')
