import streamlit as st

def create_page(authenticator):
    col1, col2 = st.columns(2, gap='large')

    # Login form
    with col1:
        authenticator.login(
            fields={
                'form name':'Entrar',
                'userid':'E-mail',
                'password':'Senha',
                'submit':'Entrar'
            }
        )
        if  st.session_state["authenticated"] is False:
            st.error('E-mail e/ou senha incorretos', icon='❌')

    # Register user form
    with col2:
        success, msg = authenticator.register_user(
            fields={
                'form name':'Cadastro',
                'userid':'E-mail',
                'first name': 'Nome',
                'last name': 'Sobrenome',
                'password':'Senha',
                'repeat password': 'Repetir senha',
                'submit':'Cadastrar-se'
            }
        )
        if success:
            st.success(msg, icon='✔️')
        else:
            if success is not None:
                st.error(msg, icon='❌')
