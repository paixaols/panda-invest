import streamlit as st

from models.collections import Account


def get_accounts():
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    return Account().find({'userid': userid}, as_dataframe=True)


def create_account(obj):
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    obj['userid'] = userid
    inserted = Account().insert_one(obj)
    return inserted


def delete_accounts(ids):
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    deleted_count = Account().delete_many(ids)
    return deleted_count


def update_account(_id, update):
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    updated_count = Account().update_one(_id, update)
    return updated_count
