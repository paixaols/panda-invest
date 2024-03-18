import streamlit as st

from models.collections import Asset


def get_assets():
    user = st.session_state['user']
    if user.get('role') not in ['admin', 'super-admin']:
        return None

    return Asset().find(as_dataframe=True)

def create_asset(obj):
    user = st.session_state['user']
    if user.get('role') not in ['admin', 'super-admin']:
        return None

    inserted = Asset().insert_one(obj)
    return inserted


def delete_assets(ids):
    user = st.session_state['user']
    if user.get('role') not in ['admin', 'super-admin']:
        return None

    deleted_count = Asset().delete_many(ids)
    return deleted_count


def update_asset(_id, update):
    user = st.session_state['user']
    if user.get('role') not in ['admin', 'super-admin']:
        return None

    updated_count = Asset().update_one(_id, update)
    return updated_count
