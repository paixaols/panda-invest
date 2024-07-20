import datetime as dt
import streamlit as st

from models.collections import Account, Asset, Transaction


def validate_transaction(data):
    for k, v in data.items():
        if v is None:
            return False

    if data['event'] == 'Compra' or data['event'] == 'Venda':
        return validate_buy_sell_transaction(data)
    elif data['event'] == 'Desdobramento':
        return validate_split_transaction(data)
    elif data['event'] == 'Grupamento':
        return validate_reverse_split_transaction(data)
    return False


def validate_buy_sell_transaction(data):
    if data['quantity'] <= 0:
        return False
    if data['value'] <= 0:
        return False
    if data['fee'] < 0:
        return False
    return True


def validate_split_transaction(data):
    if data['pre_split'] <= 0 or data['post_split'] <= 0:
        return False
    if data['pre_split'] >= data['post_split']:
        return False
    return True


def validate_reverse_split_transaction(data):
    if data['pre_split'] <= 0 or data['post_split'] <= 0:
        return False
    if data['pre_split'] <= data['post_split']:
        return False
    return True


def submit_new_transaction(data):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    if validate_transaction(data):
        data['userid'] = st.session_state['user']['email']

        # Convert date to datetime for proper processing by the database
        data['date'] = dt.datetime.combine(
            data['date'], dt.datetime.min.time()
        )

        data['account_id'] = data['account'].split('id: ')[1].split(')')[0]
        data['asset_id'] = data['asset'].split('id: ')[1].split(')')[0]

        inserted = Transaction().insert_one(data, missing_fields='ignore')
        if inserted:
            return {'success': True, 'message': 'Ok', 'status': 200}
        else:
            return {'success': False, 'message': 'Database error', 'status': 500}

    else:
        return {'success': False, 'message': 'Dados inválidos', 'status': 200}


def update_transaction(_id, update):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    # Convert date to datetime for proper processing by the database
    update['date'] = dt.datetime.combine(
        update['date'], dt.datetime.min.time()
    )

    update['account_id'] = update['account'].split('id: ')[1].split(')')[0]
    update['asset_id'] = update['asset'].split('id: ')[1].split(')')[0]

    updated_count = Transaction().update_one(
        _id,
        {'$set': update}
    )

    return {
        'success': True,
        'data': {'updated_count': updated_count},
        'message': 'Ok',
        'status': 200
    }


def get_transactions():
    userid = st.session_state['user'].get('email')
    if userid is None:
        return None

    # Transactions
    df = Transaction().find({'userid': userid}, as_dataframe=True)

    # User's accounts
    df_acc = Account().find({'userid': userid}, as_dataframe=True)
    df_acc['acc_label'] = df_acc.apply(lambda x: f"{x['bank']} (id: {x['_id']})", axis=1)
    accounts = df_acc['acc_label'].to_list()

    # Merge dividend and account dataframes
    df = df.merge(df_acc[['_id', 'bank']], left_on='account_id', right_on='_id', suffixes=('', '_acc'))
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

    return df, accounts, assets


def get_transaction(id):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    userid = st.session_state['user'].get('email')
    transaction = Transaction().find({'userid': userid, '_id': id})[0]

    return {
        'success': True,
        'data': transaction,
        'message': '',
        'status': 200
    }


def delete_transactions(ids):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    deleted_count = Transaction().delete_many(ids)
    return {
        'success': True,
        'data': {'deleted_count': deleted_count},
        'message': '',
        'status': 200
    }
