import pandas as pd
import streamlit as st

import controllers as ctr
from app import login_required, menu

login_required()
menu()

response = ctr.portfolio.get_wallet(invest_group='RF')

if response['data'] is None:
    st.warning('Nada encontrado. Insira seus dados na tela *Transações*.', icon='⚠️')
    st.stop()

invest = response['data']
currencies = invest['currency'].unique().tolist()

tabs = st.tabs(currencies)
for i in range(len(currencies)):
    data = invest[invest['currency'] == currencies[i]]
    asset_groups = sorted(data['asset_group'].unique().tolist())

    # Valor dos investimentos por ano de vencimento
    tabs[i].subheader('Valor dos investimentos por ano de vencimento')
    data['year'] = data['maturity'].apply(lambda x: x.year)
    chart_data = pd.pivot_table(
        data,
        values='value',
        index='year',
        columns='asset_group',
        aggfunc='sum'
    )
    tabs[i].bar_chart(chart_data)

    for group in asset_groups:
        tabs[i].subheader(group)
        group_data = data.loc[
            data['asset_group'] == group,
            ['asset', 'code', 'value', 'quantity', 'cost', 'price', 'base_date', 'maturity']
        ].reset_index(drop=True)
        tabs[i].write(group_data)
