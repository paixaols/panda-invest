import datetime as dt
import pandas as pd
import streamlit as st


def get_portfolio():
    p = [{
        'userid': 'lucas',
        'dt_updated': dt.datetime(2024, 1, 20, 0, 0),
        'agg': {
            'BRL': {'Caixa': 0, 'RF': 20000, 'RV': 15000, 'Total': 35000},
            'USD': {'Caixa': 0, 'RF': 0, 'RV': 1500, 'Total': 1500}
        }
    },{
        'userid': 'lucas',
        'dt_updated': dt.datetime(2024, 3, 25, 0, 0),
        'agg': {
            'BRL': {'Caixa': 0, 'RF': 21000, 'RV': 15500, 'Total': 36500},
            'USD': {'Caixa': 0, 'RF': 0, 'RV': 1450, 'Total': 1450}
        }
    },{
        'userid': 'lucas',
        'dt_updated': dt.datetime(2024, 5, 25, 0, 0),
        'agg': {
            'BRL': {'Caixa': 0, 'RF': 21000, 'RV': 15500, 'Total': 36500},
            'USD': {'Caixa': 0, 'RF': 0, 'RV': 1350, 'Total': 1350}
        }
    },{
        'userid': 'lucas',
        'dt_updated': dt.datetime(2024, 7, 30, 0, 0),
        'agg': {
            'BRL': {'Caixa': 5000, 'RF': 21000, 'RV': 15500, 'Total': 41500},
            'USD': {'Caixa': 50, 'RF': 0, 'RV': 1450, 'Total': 1500}
        }
    },{
        'userid': 'lucas',
        'dt_updated': dt.datetime(2024, 8, 30, 0, 0),
        'agg': {
            'BRL': {'Caixa': 4500, 'RF': 23000, 'RV': 15500, 'Total': 43000},
            'USD': {'Caixa': 50, 'RF': 0, 'RV': 1550, 'Total': 1600}
        }
    }]
    return {
        'success': True,
        'data': p,
        'message': '',
        'status': 200
    }
