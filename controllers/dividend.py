import streamlit as st

from models.collections import Account, Asset, Dividend


def get_dividends():
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    userid = st.session_state['user']['email']

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

    return {
        'success': True,
        'data': {'df': df, 'accounts': accounts, 'assets': assets},
        'message': '',
        'status': 200
    }


def insert_dividend(obj):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    userid = st.session_state['user']['email']

    obj['userid'] = userid
    obj['account_id'] = obj['account'].split('id: ')[1].split(')')[0]
    obj['asset_id'] = obj['asset'].split('id: ')[1].split(')')[0]
    obj['value'] = obj['value']-obj['tax']
    inserted = Dividend().insert_one(obj, datetime_fields={'date': '%Y-%m-%d'})

    # Update account balance
    if inserted:
        Account().update_one(
            obj['account_id'],
            {'$inc': {'balance': obj['value']}}
        )
        return {'success': True, 'message': '', 'status': 200}
    return {'success': False, 'message': '', 'status': 500}


def update_dividend(_id, update):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

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
    return {
        'success': True,
        'data': {'updated_count': updated_count},
        'message': '',
        'status': 200
    }


def delete_dividends(ids):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    deleted_count = Dividend().delete_many(ids)
    return {
        'success': True,
        'data': {'deleted_count': deleted_count},
        'message': '',
        'status': 200
    }
