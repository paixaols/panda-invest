import streamlit as st

from models.collections import Account


def get_bank_accounts():
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    userid = st.session_state['user']['email']
    bank_accounts = Account().find({'userid': userid}, as_dataframe=True)
    return {
        'success': True,
        'data': bank_accounts,
        'message': '',
        'status': 200
    }


def create_bank_account(obj):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    userid = st.session_state['user']['email']
    obj['userid'] = userid
    inserted = Account().insert_one(obj)
    if inserted:
        return {'success': True, 'message': '', 'status': 200}
    else:
        return {'success': False, 'message': '', 'status': 500}


def delete_bank_accounts(ids):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    deleted_count = Account().delete_many(ids)
    return {
        'success': True,
        'data': {'deleted_count': deleted_count},
        'message': '',
        'status': 200
    }


def update_bank_account(_id, update):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    updated_count = Account().update_one(
        _id,
        {'$set': update}
    )
    return {
        'success': True,
        'data': {'updated_count': updated_count},
        'message': '',
        'status': 200
    }
