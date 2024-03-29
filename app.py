import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title='Panda Invest', page_icon=':panda_face:', layout='wide')

from stauth import Authenticator
from pages import private_pages, public_pages


def set_param(key):
    st.query_params[key] = st.session_state.get(key)


def get_param(key):
    return st.query_params.get(key)


# Settings
# ==============================================================================
authenticator = Authenticator(
    cookie_name=st.secrets['COOKIE']['NAME'],
    key=st.secrets['COOKIE']['SIGNATURE_KEY'],
    cookie_expiry_days=1,
    user_id_type='email'
)

# Main app
# ==============================================================================
if st.session_state['authenticated']:
    private_pages_list = [
        # ('Painel', 'columns'), 
        ('Caixa', 'cash-stack'), ('Dividendos', 'coin'), 
        ('---', ''), ('Configurações', 'gear')
    ]
    if st.session_state['user']['role'] in ['admin', 'super-admin']:
        private_pages_list.extend([('---', ''), ('Ativos', 'collection')])
    if st.session_state['user']['role'] == 'super-admin':
        private_pages_list.extend([('---', ''), ('Usuários', 'people')])
    page_names = [ p[0] for p in private_pages_list ]
    page_icons = [ p[1] for p in private_pages_list ]
    try:
        page_index = page_names.index(get_param('p'))
    except ValueError:
        st.session_state['p'] = None
        st.query_params.clear()
        page_index = 0

    with st.sidebar:
        col1, col2 = st.columns([2, 1])
        col1.write(f'Bem-vindo(a) *{st.session_state["user"]["first_name"]}*')
        with col2:
            authenticator.logout(button_name='Sair')
        st.divider()
        active_page = option_menu(
            menu_title=None,
            options=page_names,
            icons=page_icons,
            default_index=page_index,
            on_change=set_param,
            key='p'
        )
        st.divider()
else:
    public_pages_list = ['Home']
    active_page = 'Home'

# Views
# ==============================================================================
# User
# if active_page == 'Painel':
#     private_pages.dashboard.create_page()
if active_page == 'Caixa':
    private_pages.account.create_page()
if active_page == 'Dividendos':
    private_pages.dividend.create_page()
if active_page == 'Configurações':
    private_pages.settings.create_page(authenticator)

# Admin
if active_page == 'Ativos':
    private_pages.manage_assets.create_page()

# Super-admin
if active_page == 'Usuários':
    private_pages.manage_users.create_page()

# Public
if active_page == 'Home':
    public_pages.home.create_page(authenticator)
