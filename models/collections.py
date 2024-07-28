from db.mongodb import Collection


class Account(Collection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = ['userid', 'bank', 'currency', 'balance']


class Asset(Collection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = ['name', 'description', 'maturity', 'code', 'type', 'currency']


class Dividend(Collection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = ['userid', 'date', 'asset_id', 'value', 'account_id']


class Transaction(Collection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = [
            'userid',
            'account_id',
            'asset_id',
            'date',
            'event',
            'pre_split',
            'post_split',
            'quantity',
            'fee',
            'value',
        ]
