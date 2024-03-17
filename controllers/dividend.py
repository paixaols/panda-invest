import streamlit as st

from models.collections import Account, Dividend


def get_dividends():
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    # User's dividends
    df = Dividend().find({'userid': userid}, as_dataframe=True)
    df['value'] = df['value'].astype(float)
    df['month'] = df['date'].apply(lambda x: x.strftime('%Y-%m'))

    # User's accounts
    df_acc = Account().find({'userid': userid}, as_dataframe=True)
    df_acc['acc_label'] = df_acc.apply(lambda x: f"{x['bank']} (id: {x['_id']})", axis=1)
    accounts = df_acc['acc_label'].to_list()

    # Merge dividend and account dataframes
    df = df.merge(df_acc[['_id', 'bank', 'currency']], left_on='account_id', right_on='_id', suffixes=('', '_acc'))
    df.drop(columns=['_id_acc'], inplace=True)

    return df, accounts


def insert_dividend(obj):
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    obj['userid'] = userid
    obj['account_id'] = obj['bank'].split('id: ')[1].split(')')[0]
    inserted = Dividend().insert_one(obj, datetime_fields={'date': '%Y-%m-%d'})
    return inserted


def update_dividend(_id, update):
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    if 'bank' in update:
        update['account_id'] = update['bank'].split('id: ')[1].split(')')[0]

    updated_count = Dividend().update_one(
        userid,
        _id,
        update,
        datetime_fields={'date': '%Y-%m-%d'}
    )
    return updated_count


def delete_dividends(ids):
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    deleted_count = Dividend().delete_many(userid, ids)
    return deleted_count
