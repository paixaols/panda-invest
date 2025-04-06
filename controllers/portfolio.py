import datetime as dt
import pandas as pd
import streamlit as st

from models.collections import Account, Asset, Portfolio, Wallet


def get_portfolio():
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    userid = st.session_state['user'].get('email')
    p = Portfolio().find({'userid': userid})

    return {
        'success': True,
        'data': p,
        'message': '',
        'status': 200
    }


def get_wallet(invest_group='all'):
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    userid = st.session_state['user'].get('email')

    # Wallet
    w = Wallet().find({'userid': userid})
    if len(w) == 0:
        return {'success': True, 'data': None, 'message': '', 'status': 200}

    df = pd.DataFrame(w[0]['investment'])

    # User's accounts
    df_acc = Account().find({'userid': userid}, as_dataframe=True)
    df_acc.rename(columns={'_id': 'account_id'}, inplace=True)

    # Assets
    df_ass = Asset().find(as_dataframe=True)
    df_ass.rename(columns={
        '_id': 'asset_id', 'name': 'asset'
    }, inplace=True)

    # Merge
    df = df.merge(df_acc[['account_id', 'bank']], on='account_id')
    df = df.merge(df_ass[[
        'asset_id', 'asset', 'code', 'type', 'currency', 'maturity'
    ]], on='asset_id')

    df['invest_group'] = df['type'].apply(lambda x: x.split(' | ')[0])
    df['asset_group'] = df['type'].apply(lambda x: x.split(' | ')[1])
    df['value'] = df['quantity']*df['price']

    if invest_group != 'all':
        df = df[df['invest_group'] == invest_group]
        if df.empty:
            df = None

    return {
        'success': True,
        'data': df,
        'message': '',
        'status': 200
    }
