import datetime as dt
import pandas as pd
import streamlit as st

from bson import ObjectId

from db import mongodb_engine as engine


@st.cache_resource
def get_database():
    return engine.get_database(st.secrets['DB']['NAME'])

db = get_database()


def get_dividends():
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    collection = db['dividend']
    query = {'userid': userid}
    cursor = collection.find(query)

    df = pd.DataFrame(cursor)
    if df.shape[0] == 0:
        return pd.DataFrame(
            columns=['data', 'mês', 'ativo', 'valor', 'local', 'conta']
        )
    df['_id'] = df['_id'].astype(str)
    df['data'] = df['data'].dt.date
    df['valor'] = df['valor'].astype(float)
    df['mês'] = df['data'].apply(lambda x: x.strftime('%Y-%m'))
    df['local'] = 'br'
    return df


def insert_dividend(obj):
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    required_fields = ['data', 'ativo', 'valor', 'conta']
    if not all(key in obj for key in required_fields):
        return False
    dividend = {
        'userid': userid,
        'data': dt.datetime.strptime(obj['data'], '%Y-%m-%d'),
        'ativo': obj['ativo'],
        'valor': obj['valor'],
        'conta': obj['conta']
    }
    result = db['dividend'].insert_one(dividend)
    return result.acknowledged


def update_one(_id, update):
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    if 'data' in update:
        try:
            update['data'] = dt.datetime.strptime(update['data'], '%Y-%m-%d')
        except:
            pass

    collection = db['dividend']
    query = {
        'userid': userid,
        '_id': ObjectId(_id)
    }
    result = collection.update_one(query, {'$set': update})
    return result.modified_count


def delete_dividends(ids):
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    collection = db['dividend']
    objids = [ ObjectId(_id) for _id in ids ]
    query = {
        'userid': userid,
        '_id': {'$in': objids}
    }
    result = collection.delete_many(query)
    return result.deleted_count
