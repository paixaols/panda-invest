import streamlit as st

from models.collections import Asset


def get_assets():
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    # user = st.session_state['user']
    # if user['role'] not in ['admin', 'super-admin']:
    #     return {'success': False, 'message': 'Forbidden', 'status': 400}

    assets = Asset().find(as_dataframe=True)
    return {
        'success': True,
        'data': assets,
        'message': '',
        'status': 200
    }


def create_asset(obj):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    user = st.session_state['user']
    if user['role'] not in ['admin', 'super-admin']:
        return {'success': False, 'message': 'Forbidden', 'status': 400}

    inserted = Asset().insert_one(obj)
    if inserted:
        return {'success': True, 'message': '', 'status': 200}
    else:
        return {'success': False, 'message': '', 'status': 500}


def delete_assets(ids):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    user = st.session_state['user']
    if user['role'] not in ['admin', 'super-admin']:
        return {'success': False, 'message': 'Forbidden', 'status': 400}

    deleted_count = Asset().delete_many(ids)
    return {
        'success': True,
        'data': {'deleted_count': deleted_count},
        'message': '',
        'status': 200
    }


def update_asset(_id, update):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    user = st.session_state['user']
    if user['role'] not in ['admin', 'super-admin']:
        return {'success': False, 'message': 'Forbidden', 'status': 400}

    updated_count = Asset().update_one(
        _id,
        {'$set': update}
    )
    return {
        'success': True,
        'data': {'updated_count': updated_count},
        'message': '',
        'status': 200
    }
