import streamlit as st

import controllers as ctr
from app import login_required, menu

login_required()
menu()

response = ctr.portfolio.get_wallet(invest_group='RV')

if response['data'] is None:
    st.warning('Nada encontrado. Insira seus dados na tela *Transações*.', icon='⚠️')
    st.stop()

invest = response['data']
currencies = invest['currency'].unique().tolist()

tabs = st.tabs(currencies)
for i in range(len(currencies)):
    data = invest[invest['currency'] == currencies[i]]
    asset_groups = sorted(data['asset_group'].unique().tolist())

    # Valor por grupo de ativos
    tabs[i].subheader('Valor por grupo de ativos')
    chart_data = data[['asset_group', 'value']].groupby('asset_group').sum()#.reset_index()
    tabs[i].bar_chart(chart_data)

    for group in asset_groups:
        tabs[i].subheader(group)
        group_data = data.loc[
            data['asset_group'] == group,
            ['asset', 'code', 'value', 'quantity', 'cost', 'price', 'base_date']
        ].reset_index(drop=True)
        tabs[i].write(group_data)
