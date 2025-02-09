import datetime as dt
import pandas as pd
import streamlit as st

from models.collections import Portfolio, Wallet


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


def get_wallet():
    if not st.session_state['authenticated']:
        return {'success': False, 'message': 'Login required', 'status': 400}

    userid = st.session_state['user'].get('email')
    w = Wallet().find({'userid': userid})

    return {
        'success': True,
        'data': w,
        'message': '',
        'status': 200
    }
