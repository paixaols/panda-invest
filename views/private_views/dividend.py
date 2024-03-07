import streamlit as st

import controllers as c


def create_page():
    data = c.mock.dividends()

    tab1, tab2, tab3 = st.tabs(['Histórico', 'Mês', 'Novo'])

    # Tab history
    with tab1:
        st.subheader('Histórico de pagamentos')

        if data.shape[0] == 0:
            st.warning('Nada encontrado. Insira seus dividendos na aba *Novo*.', icon='⚠️')
        else:
            grouped_data = data[['local', 'mês', 'valor']].groupby(['local', 'mês']).sum().reset_index()
            grouped_data = grouped_data.pivot(columns='local', index='mês', values='valor')
            st.bar_chart(grouped_data)

    # Tab month
    with tab2:
        st.subheader('Pagamentos do mês')

        options = data['mês'].unique()
        option = st.selectbox('Mês', options)
        filtered_data = data[data['mês'] == option]
        st.write(filtered_data)

    # Tab new
    with tab3:
        assets = ['BBAS3', 'SLG', 'XPLG11']
        with st.form(key='new_dividend'):
            st.subheader('Adicionar dividendo')
            st.selectbox(
                'Ativo',
                assets,
                index=None,
                placeholder='Selecione uma opção'
            )
            st.date_input('Data do pagamento', format='DD/MM/YYYY')
            st.text_input('Banco')
            st.number_input('Valor')
            st.form_submit_button('Enviar')
