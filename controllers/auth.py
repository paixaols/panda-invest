import streamlit as st

from stauth import mongodb_tools as db_tools
from stauth.hash import check_pw


def authenticate(userid, password):
    error_message = [
        'Ok',
        'E-mail e/ou senha incorretos',
        'Conta bloqueada',
    ]

    user = db_tools.get_user(userid)

    if user is None:
        return {
            'success': False,
            'message': error_message[1],
            'error': 1
        }

    if not user.get('active'):
        return {
            'success': False,
            'message': error_message[2],
            'error': 2
        }

    if check_pw(password, user['hashed_pw']):
        st.session_state['authenticated'] = True
        st.session_state['user'] = {
            'userid': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'active': user['active'],
            'role': user['role']
        }
        return {
            'success': True,
            'message': error_message[0],
            'error': 0
        }
    return {
        'success': False,
        'message': error_message[1],
        'error': 1
    }
