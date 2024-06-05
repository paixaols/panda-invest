import streamlit as st

from .fields import FormField


class Meta(type):
    def __new__(mcs, name, bases, attrs):
        field_list = []
        for k, v in attrs.items():
            if isinstance(v, FormField):
                v.name = k
                field_list.append(v)

        cls = type.__new__(mcs, name, bases, attrs)
        cls.fields = field_list

        return cls


class Form(object, metaclass=Meta):
    def __init__(self, data=None):
        if isinstance(data, dict):
            self.data = data
        else:
            self.data = {}
        self.input_data = {}

    def render(self, header=None, submit='Submit'):
        if header is not None:
            st.subheader(header)

        for f in self.fields:
            if f.input_type == 'text_input':
                self.input_data[f.name] = st.text_input(
                    f.label,
                    value=self.data.get(f.name),
                    max_chars=f.max_chars,
                    disabled=f.disabled,
                )
            elif f.input_type == 'text_area':
                self.input_data[f.name] = st.text_area(
                    f.label,
                    value=self.data.get(f.name),
                    disabled=f.disabled,
                )
            elif f.input_type == 'date_input':
                self.input_data[f.name] = st.date_input(
                    f.label,
                    value=self.data.get(f.name),
                    min_value=f.min_value,
                    max_value=f.max_value,
                    disabled=f.disabled,
                )
            elif f.input_type == 'integer_input':
                self.input_data[f.name] = st.number_input(
                    f.label,
                    value=self.data.get(f.name),
                    step=1,
                    min_value=f.min_value,
                    max_value=f.max_value,
                    disabled=f.disabled,
                )
            elif f.input_type == 'float_input':
                self.input_data[f.name] = st.number_input(
                    f.label,
                    value=self.data.get(f.name),
                    step=0.01,
                    min_value=f.min_value,
                    max_value=f.max_value,
                    disabled=f.disabled,
                )
            elif f.input_type == 'select_box':
                self.input_data[f.name] = st.selectbox(
                    f.label,
                    f.options,
                    index=f.index,
                    disabled=f.disabled,
                )
        return st.form_submit_button(submit)

    def is_valid(self):
        for k, v in self.input_data.items():
            if v is None:
                return False
        return True
