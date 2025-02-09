import streamlit as st

# st.set_page_config(
#     page_title='Panda Invest',
#     page_icon=':panda_face:',
#     layout='wide'
# )

import controllers as ctr


def authenticated_menu():
    '''
    Show a navigation menu for authenticated users
    '''
    with st.sidebar:
        col1, col2 = st.columns([2, 1])
        col1.write(f'Bem-vindo(a) *{st.session_state["user"]["first_name"]}*')
        with col2:
            if st.button('Sair'):
                ctr.auth.logout()
                st.switch_page('app.py')
        # User pages
        st.page_link('pages/dashboard.py', label='Painel')
        st.page_link('pages/accounts.py', label='Caixa')
        st.page_link('pages/dividend.py', label='Dividendos')
        st.page_link('pages/transaction.py', label='Transações')
        st.page_link('pages/portfolio.py', label='Portfólio')
        # Config
        st.divider()
        st.page_link('pages/settings.py', label='Configurações')
        # Admin
        if st.session_state['user']['role'] in ['admin', 'super-admin']:
            st.divider()
            st.page_link('pages/manage_assets.py', label='Ativos')
        if st.session_state['user']['role'] == 'super-admin':
            st.page_link('pages/manage_users.py', label='Usuários')


def unauthenticated_menu():
    '''
    Show a navigation menu for unauthenticated users
    '''
    with st.sidebar:
        st.page_link('app.py', label='Home')
        st.page_link('pages/signin.py', label='Entrar')


def menu():
    '''
    Determine if a user is logged in or not, then show the correct navigation menu
    '''
    if st.session_state.get('authenticated'):
        authenticated_menu()
    else:
        st.session_state['authenticated'] = False
        unauthenticated_menu()


def login_required():
    '''
    Redirect users to the main page if not logged in
    '''
    if not st.session_state.get('authenticated'):
        st.switch_page('pages/signin.py')


menu()

st.write('panda invest')
