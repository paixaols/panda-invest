import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import controllers as ctr
from app import login_required, menu

login_required()
menu()

# Current investment data
response = ctr.portfolio.get_wallet()

if response['data'] is None:
    st.warning('Nada encontrado. Insira seus dados na tela *Transações*.', icon='⚠️')
    st.stop()

invest = response['data']
currencies = invest['currency'].unique().tolist()

tabs = st.tabs(currencies)
for i in range(len(currencies)):
    currency = currencies[i]

    # Renda variável
    tabs[i].header('Renda Variável')
    aux = invest[
        (invest['invest_group'] == 'RV') &
        (invest['currency'] == currency)
    ][['asset_group', 'value']].groupby('asset_group').sum()
    aux.sort_values('value', ascending=False, inplace=True)

    col1, col2 = tabs[i].columns(2)
    fig, ax = plt.subplots(figsize=(5, 5))
    aux.plot(
        y='value',
        kind='pie',
        ylabel='',
        colormap='GnBu_r',
        legend=False,
        fontsize=14,
        autopct='%.1f%%',
        ax=ax
    )
    col1.pyplot(fig)
    col2.bar_chart(aux)

    # Renda fixa
    tabs[i].divider()
    tabs[i].header('Renda Fixa')

    # Valor de investimentos por ano de vencimento
    aux = invest[
        (invest['invest_group'] == 'RF') &
        (invest['currency'] == currency)
    ].copy()
    aux['year'] = aux['maturity'].apply(lambda x: x.year)
    chart_data = pd.pivot_table(
        aux,
        values='value',
        index='year',
        columns='asset_group',
        aggfunc='sum'
    )
    tabs[i].subheader('Valor de investimentos por ano de vencimento')
    tabs[i].bar_chart(chart_data)
