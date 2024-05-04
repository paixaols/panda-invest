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


def update_user_data(field, value):
    message = [
        'Dados atualizados com sucesso',
        'Campo "{}" não reconhecido',
        'Nome inválido',
        'O valor atual e o novo são iguais',
        'Falha na atualização, tente novamente mais tarde',
    ]
    user = st.session_state['user']
    if field not in user:
        return {'success': False, 'message': message[1].format(field), 'error': 1}

    # Validação dos dados
    validator = Validator()
    if not validator.validate_name(value):
        return {'success': False, 'message': message[2], 'error': 2}

    if user[field] == value:
        return {'success': False, 'message': message[3], 'error': 3}

    if db_tools.update_user_info(user['email'], field, value):
        st.session_state['user'][field] = value
        return {'success': True, 'message': message[0], 'error': 0}
    else:
        return {'success': False, 'message': message[4], 'error': 4}


def logout():
    st.session_state['authenticated'] = False
    st.session_state['user'] = None


def delete_user_account():
    if db_tools.delete_user(st.session_state['user']['email']):
        logout()
        return {'success': True, 'message': '', 'status': 200}
    return {
        'success': False,
        'message': 'Banco de dados não acessível, tente novamente mais tarde',
        'status': 500
    }


def change_password(data):
    message = [
        'Senha atualizada com sucesso',
        'Campos com asterisco são obrigatórios',
        'As senhas não coincidem',
        'A senha deve ter pelo menos 8 caracteres',
        'A senha atual está incorreta',
        'Nova senha deve ser diferente da atual',
        'Banco de dados não acessível, tente novamente mais tarde',
    ]

    # Verifica presença dos campos requeridos
    required_fields = ['password', 'new_password', 'repeat_password']
    if not all([ f in data for f in required_fields ]):
        return {'success': False, 'message': message[1], 'status': 200}
    if any([ data[f] == '' for f in required_fields ]):
        return {'success': False, 'message': message[1], 'status': 200}

    # Validação dos dados
    validator = Validator()
    if data['new_password'] != data['repeat_password']:
        return {'success': False, 'message': message[2], 'status': 200}
    if not validator.validate_password(data['new_password']):
        return {'success': False, 'message': message[3], 'status': 200}

    # Check current credentials
    email = st.session_state['user']['email']
    user = db_tools.get_user(email)
    if not check_pw(data['password'], user['hashed_pw']):
        return {'success': False, 'message': message[4], 'status': 200}

    # Check new password
    if data['password'] == data['new_password']:
        return {'success': False, 'message': message[5], 'status': 200}

    # Update password
    if db_tools.update_password(email, data['new_password']):
        return {'success': True, 'message': message[0], 'status': 200}
    else:
        return {'success': False, 'message': message[6], 'status': 500}
