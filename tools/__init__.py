import locale


currency_symbol = {
    'BRL': 'R$',
    'EUR': '€',
    'USD': 'US$',
}


def format_currency(value, currency):
    symbol = currency_symbol.get(currency)
    amount = locale.currency(value, grouping=True, symbol=False)
    return f'{symbol} {amount}'
