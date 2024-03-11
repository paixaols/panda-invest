import streamlit as st

from datetime import datetime

from .hash import hash_pw
from db import mongodb_engine as engine


@st.cache_resource
def get_database():
    return engine.get_database(st.secrets['DB']['NAME'])

db = get_database()


def get_user(userid: str, fields: dict={'user_coll': 'users',
                                        'id_field': 'email',
                                        'name_field': 'name',
                                        'pw_hash_field': 'hashed_pw'}) -> dict:
    '''
    Retrieves user info from the database.

    Parameters
    ----------
    userid: str
        The ID of the user.
    fields: dict
        The names of the fields of interest in the database.

    Returns
    -------
    dict
        The user information or None if the user is not found.
    '''
    doc = db[fields['user_coll']].find_one({fields['id_field']: userid})
    return doc


def create_new_user(new_user_data: dict) -> bool:
    '''
    Inserts new user in the database.

    Parameters
    ----------
    new_user_data: dict
        Data from the registration form.

    Returns
    -------
    bool
        Acknowledgement of the insertion operation.
    '''
    id_field_name = new_user_data['id_type']
    new_user = {
        id_field_name: new_user_data['userid'],
        'first_name': new_user_data['first_name'],
        'last_name': new_user_data['last_name'],
        'hashed_pw': hash_pw(new_user_data['password']),
        'date_joined': datetime.now(),
        'active': False,
        'role': 'user'
    }
    result = db['users'].insert_one(new_user)
    return result.acknowledged


def update_password(userid, new_password):
    result = db['users'].find_one_and_update(
        {'email': userid},
        {'$set': {'hashed_pw': hash_pw(new_password)}}
    )
    return result is not None


def update_user_info(userid, field, value):
    result = db['users'].find_one_and_update(
        {'email': userid},
        {'$set': {field: value}}
    )
    return result is not None


def delete_user(userid):
    result = db['users'].delete_one({'email': userid})
    return result.deleted_count > 0
