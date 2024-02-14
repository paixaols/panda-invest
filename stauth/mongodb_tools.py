import streamlit as st

from db import mongodb_engine as engine


@st.cache_resource
def get_database():
    return engine.get_database(st.secrets['DB']['NAME'])

db = get_database()


def get_user(userid: str, fields: dict={'user_col': 'users',
                                        'id_field': 'email',
                                        'name_field': 'name',
                                        'pw_hash_field': 'password'}) -> dict:
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
        The user information: userid, name, and password hash. Returns None if 
        the user is not found.
    '''
    doc = db[fields['user_col']].find_one({fields['id_field']: userid})
    if doc is not None:
        return {
            'userid': doc.get(fields['id_field']),
            'name': doc.get(fields['name_field']),
            'hash': doc.get(fields['pw_hash_field'])
        }
    return None
