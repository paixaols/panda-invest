import streamlit as st
from streamlit_option_menu import option_menu

# st.set_page_config(page_title='Home', layout='wide')

from stauth import Authenticator
from views import private_views, public_views


def set_param(key):
    st.query_params[key] = st.session_state.get(key)


def get_param(key):
    return st.query_params.get(key)


# Settings
# ==============================================================================
authenticator = Authenticator(
    cookie_name = 'some_cookie_name',
    key = 'some_signature_key',
    cookie_expiry_days = 1
)

# Main app
# ==============================================================================
private_pages = ['Painel', '---', 'Configurações']
public_pages = ['Home']

if st.session_state['authenticated']:
    try:
        page_index = private_pages.index(get_param('p'))
    except ValueError:
        st.session_state['p'] = None
        st.query_params.clear()
        page_index = 0

    with st.sidebar:
        st.write(f'Bem-vindo(a) *{st.session_state["user"]["name"]}*')
        authenticator.logout(button_name='Sair')
        st.divider()
        active_page = option_menu(
            menu_title=None,
            options=private_pages,
            icons=['columns', '', 'gear'],
            default_index=page_index,
            on_change=set_param,
            key='p'
        )
        st.divider()
else:
    active_page = 'Home'

# Views
# ==============================================================================
if active_page == 'Painel':
    private_views.dashboard.create_page()
if active_page == 'Configurações':
    private_views.settings.create_page(authenticator)

if active_page == 'Home':
    public_views.home.create_page(authenticator)
