import streamlit as st


def create_page(authenticator):
    tab1, tab2 = st.tabs(['Conta', 'Senha'])

    # with tab1:
    #     st.header('Alterar dados')
    #     st.header('Excluir conta')

    with tab1:
        success, msg = authenticator.reset_password(
            fields={
                'form name': 'Alterar senha',
                'current password': 'Senha atual',
                'new password': 'Senha nova',
                'repeat new password': 'Repetir senha nova',
                'submit': 'Alterar'
            }
        )
        if success:
            st.success(msg, icon='✔️')
        else:
            if success is not None:
                st.error(msg, icon='❌')
