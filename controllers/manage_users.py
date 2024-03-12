import streamlit as st

from bson import ObjectId

from db import mongodb_engine as engine


@st.cache_resource
def get_database():
    return engine.get_database(st.secrets['DB']['NAME'])

db = get_database()


def get_user(userid):
    collection = db['users']
    query = {'email': userid}
    doc = collection.find_one(query)
    if doc is None:
        return None
    doc['_id'] = str(doc['_id'])
    return doc


def update_account(_id, update):
    if st.session_state['user']['role'] != 'super-admin':
        return False

    collection = db['users']
    result = collection.update_one(
        {'_id': ObjectId(_id)},
        {'$set': update}
    )
    return result.modified_count == 1
