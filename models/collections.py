from db.mongodb import Collection


class Account(Collection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = ['userid', 'bank', 'currency']


class Asset(Collection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = ['name', 'description', 'code', 'type', 'currency']


class Dividend(Collection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = ['userid', 'date', 'asset_id', 'value', 'account_id']
