from db.mongodb import Collection


class Dividend(Collection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = ['userid', 'date', 'asset', 'value', 'account_id']


class Account(Collection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = ['userid', 'bank', 'currency']
