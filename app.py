import streamlit as st

# st.set_page_config(
#     page_title='Panda Invest',
#     page_icon=':panda_face:',
#     layout='wide'
# )


def logout():
    st.session_state['authenticated'] = False
    st.session_state['user'] = {}


def authenticated_menu():
    # Show a navigation menu for authenticated users
    with st.sidebar:
        col1, col2 = st.columns([2, 1])
        col1.write(f'Bem-vindo(a) *{st.session_state["user"]["first_name"]}*')
        with col2:
            if st.button('Sair'):
                logout()
                st.switch_page('app.py')
        st.page_link('pages/account.py', label='Caixa')


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    with st.sidebar:
        st.page_link('app.py', label='Home')
        st.page_link('pages/signin.py', label='Entrar')


def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    if st.session_state.get('authenticated'):
        authenticated_menu()
    else:
        st.session_state['authenticated'] = False
        unauthenticated_menu()


def login_required():
    # Redirect users to the main page if not logged in
    if 'authenticated' not in st.session_state or st.session_state['authenticated'] is None:
        st.switch_page('app.py')


menu()

st.write('panda invest')
