from datetime import date


class FormField(object):
    def __init__(self, label, required, disabled):
        if not isinstance(label, str):
            raise TypeError('Form field label must be of type str')
        self.label = label
        self.required = required
        self.disabled = disabled

    def __repr__(self):
        return f'Form field <{self.label}>'


class CharField(FormField):
    input_type = 'text_input'

    def __init__(self, label, max_chars=None, required=True, disabled=False):
        super().__init__(label, required, disabled)
        self.max_chars = max_chars


class TextField(FormField):
    input_type = 'text_area'

    def __init__(self, label, required=True, disabled=False):
        super().__init__(label, required, disabled)


class DateField(FormField):
    input_type = 'date_input'

    def __init__(self, label, min_value=None, max_value=None, required=True, disabled=False):
        super().__init__(label, required, disabled)
        if min_value == 'today':
            self.min_value = date.today()
        else:
            self.min_value = min_value
        if max_value == 'today':
            self.max_value = date.today()
        else:
            self.max_value = max_value


class IntegerField(FormField):
    input_type = 'integer_input'

    def __init__(self, label, min_value=None, max_value=None, required=True, disabled=False):
        super().__init__(label, required, disabled)
        if min_value is not None and not isinstance(min_value, int):
            raise TypeError('Minimum value of IntegerField must be integer or None')
        self.min_value = min_value
        if max_value is not None and not isinstance(max_value, int):
            raise TypeError('Maximum value of IntegerField must be integer or None')
        self.max_value = max_value


class FloatField(FormField):
    input_type = 'float_input'

    def __init__(self, label, min_value=None, max_value=None, required=True, disabled=False):
        super().__init__(label, required, disabled)
        self.min_value = None if min_value is None else float(min_value)
        self.max_value = None if max_value is None else float(max_value)


class SelectField(FormField):
    input_type = 'select_box'

    def __init__(self, label, options=[], index=None, required=True, disabled=False):
        super().__init__(label, required, disabled)
        self.options = options
        self.index = index
