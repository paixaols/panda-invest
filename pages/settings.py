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


tab1, tab2 = st.tabs(['Conta', 'Senha'])

# Configurações da conta
with tab1:
    # Atualizar dados
    with st.form('update-user-details'):
        st.subheader('Atualizar dados')
        user = st.session_state['user']
        st.text_input(
            'E-mail',
            placeholder=user.get('email'),
            disabled=True
        )
        user_details={
            'Nome': 'first_name',
            'Sobrenome': 'last_name'
        }
        user_detail_fields = [ f'{k}: {user.get(v)}' for k, v in user_details.items() ]
        selected_field = st.selectbox(
            'Campo',
            user_detail_fields
        )
        new_value = st.text_input('Novo valor*')
        submit = st.form_submit_button('Atualizar')

    if submit:
        field_readable_name = selected_field.split(':')[0]
        field_name = user_details.get(field_readable_name)
        response = ctr.auth.update_user_data(field_name, new_value)
        if response['success']:
            st.success(response['message'], icon='✔️')
        else:
            st.error(response['message'], icon='❌')

    st.divider()

    # Excluir conta
    with st.form('delete-account'):
        st.subheader('Excluir conta')
        st.write('**ATENÇÃO! Essa ação não pode ser revertida**.')

        confirmation_text = 'excluir minha conta'
        user_input = st.text_input(f'Digite "{confirmation_text}" e clique no botão abaixo')
        submit_delete = st.form_submit_button(
            'Quero excluir esta conta',
            type='primary'
        )

    if submit_delete:
        if user_input == confirmation_text:
            response = ctr.auth.delete_user_account()
            if response['success']:
                st.switch_page('app.py')
            else:
                st.error(response['message'], icon='❌')
        else:
            st.warning('Digite a mensagem de confirmação na caixa de texto acima', icon='⚠️')

# Alterar senha
with tab2:
    with st.form('change-password'):
        st.subheader('Alterar senha')
        current_pw = st.text_input(
            'Senha atual*',
            type='password'
        )
        new_pw = st.text_input(
            'Senha nova*',
            type='password'
        )
        repeat_new_pw = st.text_input(
            'Repetir senha nova*',
            type='password'
        )
        submit_password = st.form_submit_button('Alterar')

    if submit_password:
        response = ctr.auth.change_password({
            'password': current_pw,
            'new_password': new_pw,
            'repeat_password': repeat_new_pw
        })
        if response['success']:
            st.success(response['message'], icon='✔️')
        else:
            st.warning(response['message'], icon='⚠️')
