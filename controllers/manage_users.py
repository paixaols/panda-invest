import streamlit as st

from bson import ObjectId

from db import mongodb_engine as engine


@st.cache_resource
def get_database():
    return engine.get_database(st.secrets['DB']['NAME'])

db = get_database()


def get_user(email):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    user = st.session_state['user']
    if user['role'] != 'super-admin':
        return {'success': False, 'message': 'Forbidden', 'status': 400}

    collection = db['users']
    query = {'email': email}
    doc = collection.find_one(query)
    if doc is not None:
        doc['_id'] = str(doc['_id'])
    return {
        'success': True,
        'data': doc,
        'message': '',
        'status': 200
    }


def update_account(_id, update):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    user = st.session_state['user']
    if user['role'] != 'super-admin':
        return {'success': False, 'message': 'Forbidden', 'status': 400}

    collection = db['users']
    result = collection.update_one(
        {'_id': ObjectId(_id)},
        {'$set': update}
    )
    return {
        'success': result.modified_count == 1,
        'data': {'updated_count': result.modified_count},
        'message': '',
        'status': 200 if result.modified_count == 1 else 500
    }
