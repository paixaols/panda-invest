import streamlit as st

# st.set_page_config(
#     page_title='Panda Invest | Entrar',
#     page_icon=':panda_face:',
#     layout='wide'
# )

import controllers as ctr
from app import menu

menu()


col1, col2 = st.columns(2, gap='large')

# Login form
with col1:
    with st.form('login-form'):
        st.subheader('Entrar')
        userid = st.text_input('E-mail')
        password = st.text_input('Senha', type='password')
        submit = st.form_submit_button('Entrar')

    if submit:
        response = ctr.auth.authenticate(userid, password)
        if response['success']:
            st.switch_page('pages/account.py')
        if response['error']:
            st.error(response['message'], icon='❌')

# Register user form
with col2:
    with st.form('register-user-form'):
        st.subheader('Cadastro')
        userid = st.text_input('E-mail*')
        first_name = st.text_input('Nome*')
        last_name = st.text_input('Sobrenome*')
        password = st.text_input('Senha*', type='password')
        repeat_pw = st.text_input('Repetir senha*', type='password')
        submit = st.form_submit_button('Cadastrar-se')
    if submit:
        st.warning('Em desenvolvimento', icon='⚠️')
#     if success:
#         st.success(msg, icon='✔️')
#     else:
#         if success is not None:
#             st.error(msg, icon='❌')
