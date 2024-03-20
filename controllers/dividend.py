import streamlit as st

from models.collections import Account, Asset, Dividend


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

    # Assets
    df_ass = Asset().find(as_dataframe=True)
    df_ass['ass_label'] = df_ass.apply(lambda x: f"{x['code']} (id: {x['_id']})", axis=1)
    assets = df_ass['ass_label'].to_list()

    # Merge dividend and account dataframes
    df = df.merge(df_ass[['_id', 'code']], left_on='asset_id', right_on='_id', suffixes=('', '_ass'))
    df.drop(columns=['_id_ass'], inplace=True)

    # Rename merged columns
    df.rename(columns={'bank': 'account', 'code': 'asset'}, inplace=True)

    # Create temporary *tax* field
    df['tax'] = 0

    return df, accounts, assets


def insert_dividend(obj):
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    obj['userid'] = userid
    obj['account_id'] = obj['account'].split('id: ')[1].split(')')[0]
    obj['asset_id'] = obj['asset'].split('id: ')[1].split(')')[0]
    obj['value'] = obj['value']-obj['tax']
    inserted = Dividend().insert_one(obj, datetime_fields={'date': '%Y-%m-%d'})

    # Update account balance
    Account().update_one(
        obj['account_id'],
        {'$inc': {'balance': obj['value']}}
    )

    return inserted


def update_dividend(_id, update):
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    implement = {'$set': {}, '$inc': {}}
    for k, v in update.items():
        if k == 'account':
            implement['$set']['account_id'] = v.split('id: ')[1].split(')')[0]
        elif k == 'asset':
            implement['$set']['asset_id'] = v.split('id: ')[1].split(')')[0]
        elif k == 'tax':
            implement['$inc']['value'] = -v
        else:
            implement['$set'][k] = v
    
    updated_count = Dividend().update_one(
        _id,
        implement,
        datetime_fields={'date': '%Y-%m-%d'}
    )
    return updated_count


def delete_dividends(ids):
    userid = st.session_state['user'].get('userid')
    if userid is None:
        return None

    deleted_count = Dividend().delete_many(ids)
    return deleted_count
