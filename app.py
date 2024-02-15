import streamlit as st
from streamlit_option_menu import option_menu

# st.set_page_config(page_title='Home', layout='wide')

from stauth import Authenticator
from views.public import home

# Settings
# ==============================================================================
authenticator = Authenticator(
    cookie_name = 'some_cookie_name',
    key = 'some_signature_key',
    cookie_expiry_days = 1
)

# Main app
# ==============================================================================
if st.session_state['authenticated']:
    with st.sidebar:
        st.write(f'Bem-vindo(a) *{st.session_state["user"]["name"]}*')
        authenticator.logout(button_name='Sair')
        st.divider()
        selected_page = option_menu(
            menu_title=None,
            options=['Painel', '---', 'Alterar senha'],
            icons=['columns', '', 'gear'],# https://icons.getbootstrap.com/
            default_index=0,
        )
        st.divider()
else:
    selected_page = 'home'

# Views
# ==============================================================================
if selected_page == 'home':
    home.create_page(authenticator)
