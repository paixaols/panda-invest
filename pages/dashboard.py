import datetime as dt
import locale
import pandas as pd
import streamlit as st

# st.set_page_config(
#     page_title='Panda Invest',
#     page_icon=':panda_face:',
#     layout='wide'
# )

import controllers as ctr
from app import login_required, menu
from tools import format_currency

login_required()
menu()

locale.setlocale(locale.LC_ALL, 'pt_BR')

# Data
response = ctr.portfolio.get_portfolio()
portfolio = response['data']

if len(portfolio) == 0:
    st.warning('Nada encontrado. Insira seus dados na tela *Transações*.', icon='⚠️')
    st.stop()

# Parse portfolio
agg = []
for p in portfolio:
    aux = pd.DataFrame(p['agg']).T
    aux['date'] = p['dt_updated']
    agg.append(aux)
agg_hist = pd.concat(agg)
agg_hist = agg_hist.reset_index().rename(columns={'index': 'currency'}).set_index('date')

currencies = agg_hist['currency'].unique()

# Extend columns to include Caixa, RF, RV
should_have = {'Caixa', 'RF', 'RV'}
has = set(agg_hist.columns)
for c in should_have-has:
    agg_hist[c] = 0
agg_hist = agg_hist[['currency', 'Caixa', 'RF', 'RV']]
agg_hist.fillna(0, inplace=True)
agg_hist['Total'] = agg_hist[['Caixa', 'RF', 'RV']].apply(sum, axis=1)

# Choose timeframe
cols = st.columns(len(currencies)+1)
TF_ALL = 'Tudo'
timeframe = cols[-1].selectbox(
    'Timeframe',
    ['12M', '6M', '3M', TF_ALL],
    label_visibility='hidden'
)

# Filter selected timeframe
if timeframe != TF_ALL:
    months = int(timeframe[:-1])
    days = round(30.4*(months-1))
    today = dt.datetime.combine(dt.date.today(), dt.time.min)
    start_day = today-dt.timedelta(days=days)
    start_day = start_day.replace(day=1)
    agg_hist = agg_hist[agg_hist.index > start_day]

# Net worth change
for i in range(len(currencies)):
    currency = currencies[i]

    agg = agg_hist[agg_hist['currency'] == currency]
    if agg.shape[0] == 0:
        initial = 0
        final = 0
    else:
        initial = agg['Total'].iloc[0]
        final = agg['Total'].iloc[-1]

    change = final-initial

    # Metric
    label = f'Patrimônio ({currency})'
    metric_value = format_currency(final, currency)
    metric_delta = locale.currency(change, grouping = True, symbol=False)
    if initial > 0:
        metric_delta += locale.format_string(' (%.1f%%)', 100*change/initial)
    cols[i].metric(label, metric_value, metric_delta)

# Net worth history
tabs = st.tabs(currencies.tolist())
for i in range(len(currencies)):
    # Stack area plot
    currency = currencies[i]
    agg_currency_hist = agg_hist[agg_hist['currency'] == currency].copy()
    agg_currency_hist.drop(columns='currency', inplace=True)
    tabs[i].area_chart(agg_currency_hist.drop(columns='Total'))

    # Current values
    if len(agg_currency_hist) > 0:
        agg_currency = agg_currency_hist.iloc[[-1]].T.copy()
        agg_currency.columns = ['Valor']
        total = agg_currency.iloc[-1, 0]
        agg_currency['Valor %'] = agg_currency['Valor'].apply(lambda x: locale.format_string('%.2f%%', 100*x/total))
        agg_currency['Valor'] = agg_currency['Valor'].apply(lambda x: format_currency(x, currency))
        tabs[i].dataframe(agg_currency, use_container_width=True)
