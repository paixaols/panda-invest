import streamlit as st


def create_page(authenticator):
    tab1, tab2 = st.tabs(['Conta', 'Senha'])

    with tab1:
        st.header('Alterar dados')
        st.header('Excluir conta')

    with tab2:
        st.header('Alterar senha')
