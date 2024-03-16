from db.mongodb import Collection


class Dividend(Collection):
    def __init__(self):
        super().__init__()

class Account(Collection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = ['userid', 'bank', 'currency']
