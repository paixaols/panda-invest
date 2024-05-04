import streamlit as st

from stauth import mongodb_tools as db_tools
from stauth.hash import check_pw
from stauth.validator import Validator


def authenticate(userid, password):
    message = [
        'Ok',
        'E-mail e/ou senha incorretos',
        'Conta bloqueada',
    ]

    user = db_tools.get_user(userid)

    if user is None:
        return {'success': False, 'message': message[1], 'error': 1}

    if not user.get('active'):
        return {'success': False, 'message': message[2], 'error': 2}

    if check_pw(password, user['hashed_pw']):
        st.session_state['authenticated'] = True
        st.session_state['user'] = {
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'active': user['active'],
            'role': user['role']
        }
        return {'success': True, 'message': message[0], 'error': 0}
    return {'success': False, 'message': message[1], 'error': 1}


def user_registration(user_data):
    message = [
        'Usuário cadastrado com sucesso',
        'Campos com asterisco são obrigatórios',
        'E-mail inválido',
        'Nome inválido',
        'Sobrenome inválido',
        'As senhas não coincidem',
        'A senha deve ter pelo menos 8 caracteres',
        'Usuário já cadastrado',
        'Falha no cadastro, tente novamente mais tarde'
    ]

    # Verifica presença dos campos requeridos
    required_fields = ['email', 'first_name', 'last_name', 'password', 'repeat_password']
    if not all([ f in user_data for f in required_fields ]):
        return {'success': False, 'message': message[1], 'error': 1}
    if any([ user_data[f] == '' for f in required_fields ]):
        return {'success': False, 'message': message[1], 'error': 1}

    # Validação dos dados
    validator = Validator()
    if not validator.validate_email(user_data['email']):
        return {'success': False, 'message': message[2], 'error': 2}
    if not validator.validate_name(user_data['first_name']):
        return {'success': False, 'message': message[3], 'error': 3}
    if not validator.validate_name(user_data['last_name']):
        return {'success': False, 'message': message[4], 'error': 4}
    if user_data['password'] != user_data['repeat_password']:
        return {'success': False, 'message': message[5], 'error': 5}
    if not validator.validate_password(user_data['password']):
        return {'success': False, 'message': message[6], 'error': 6}

    # Criação do usuário
    user = db_tools.get_user(user_data.get('email'))
    if user is not None:
        return {'success': False, 'message': message[7], 'error': 7}

    user_created = db_tools.create_new_user({
        'email': user_data['email'],
        'first_name': user_data['first_name'],
        'last_name': user_data['last_name'],
        'password': user_data['password']
    })
    if user_created:
        return {'success': True, 'message': message[0], 'error': 0}
    else:
        return {'success': False, 'message': message[8], 'error': 8}
