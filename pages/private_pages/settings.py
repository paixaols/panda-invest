import streamlit as st


def create_page(authenticator):
    tab1, tab2 = st.tabs(['Conta', 'Senha'])

    with tab1:
        success, msg = authenticator.update_user_details(
            user_details={
                'Nome': 'first_name',
                'Sobrenome': 'last_name'
            },
            fields = {
                'form name': 'Atualizar dados',
                'userid': 'E-mail',
                'field': 'Campo',
                'new_value': 'Novo valor',
                'submit': 'Atualizar'
            }
        )
        if success:
            st.success(msg, icon='✔️')
        else:
            if success is not None:
                st.error(msg, icon='❌')

        st.divider()

        st.subheader('Excluir conta')
        st.write('Ao excluir a conta seus dados serão apagados. **Essa ação não pode ser revertida**.')
        authenticator.delete_account(
            fields={
                'delete': 'Excluir conta',
                'confirm': 'Quero excluir esta conta'
            }
        )

    with tab2:
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
