import jwt
import streamlit as st
import extra_streamlit_components as stx

from datetime import datetime, timedelta

from . import mongodb_tools as db_tools
from .hash import check_pw
from .validator import Validator


class Authenticator:
    '''
    This class manages user authentication and creates register user, login, 
    logout, and reset password widgets.
    '''
    def __init__(self, cookie_name: str, key: str, cookie_expiry_days: float=1.0, user_id_type: str='username'):
        '''
        Instanciate the Authenticate object.

        Parameters
        ----------
        cookie_name: str
            The name of the JWT cookie stored on the client's browser for 
            passwordless reauthentication.
        key: str
            The key to be used to hash the signature of the JWT cookie.
        cookie_expiry_days: float
            The number of days before the reauthentication cookie automatically 
            expires on the client's browser.
        '''
        if user_id_type not in ['username', 'email']:
            raise ValueError("user_id_type must be one of 'username' or 'email'")

        self.user_id_type = user_id_type
        self.cookie_name = cookie_name
        self.key = key
        self.cookie_expiry_days = cookie_expiry_days
        self.cookie_manager = stx.CookieManager()
        self.validator = Validator()

        self._check_cookie()

        if 'authenticated' not in st.session_state:
            st.session_state['authenticated'] = None
        if 'failed_login_attempts' not in st.session_state:
            st.session_state['failed_login_attempts'] = {}
        if 'logout' not in st.session_state:
            st.session_state['logout'] = None
        if 'user' not in st.session_state:
            st.session_state['user'] = {}

    def _token_encode(self) -> str:
        '''
        Encodes the contents of the reauthentication cookie.

        Returns
        -------
        str
            The JWT cookie for passwordless reauthentication.
        '''
        return jwt.encode(
            {
                'userid': st.session_state['user']['userid'],
                'first_name': st.session_state['user']['first_name'],
                'last_name': st.session_state['user']['last_name'],
                'active': st.session_state['user']['active'],
                'role': st.session_state['user']['role'],
                'exp_date': self.exp_date
            },
            self.key,
            algorithm='HS256'
        )

    def _token_decode(self) -> str:
        '''
        Decodes the contents of the reauthentication cookie.

        Returns
        -------
        str
            The decoded JWT cookie for passwordless reauthentication.
        '''
        try:
            return jwt.decode(self.token, self.key, algorithms=['HS256'])
        except:
            return False

    def _set_exp_date(self) -> str:
        '''
        Creates the reauthentication cookie's expiry date.

        Returns
        -------
        str
            The JWT cookie's expiry timestamp in Unix epoch.
        '''
        return (datetime.utcnow() + timedelta(days=self.cookie_expiry_days)).timestamp()

    def _check_cookie(self):
        '''
        Checks the validity of the reauthentication cookie.
        '''
        self.token = self.cookie_manager.get(self.cookie_name)
        if self.token is not None:
            self.token = self._token_decode()
            if self.token is not False:
                if not st.session_state['logout']:
                    if self.token['exp_date'] > datetime.utcnow().timestamp():
                        if 'userid' in self.token:
                            st.session_state['user'] = {
                                'userid': self.token['userid'],
                                'first_name': self.token['first_name'],
                                'last_name': self.token['last_name'],
                                'active': self.token['active'],
                                'role': self.token['role']
                            }
                            st.session_state['authenticated'] = True

    def _set_cookie(self):
        '''
        Saves authentication cookie.
        '''
        self.exp_date = self._set_exp_date()
        self.token = self._token_encode()
        self.cookie_manager.set(
            self.cookie_name,
            self.token,
            expires_at=datetime.now() + timedelta(days=self.cookie_expiry_days)
        )

    def _check_credentials(self, userid, password, save_state=True) -> bool:
        '''
        Checks the validity of the entered credentials. If the credentials are 
        valid, authentication status is stored in session state, under the key 
        "authenticated", and the authentication cookie is stored on the 
        client's browser.

        Parameters
        ----------
        userid: str
            ID of the user to be verified.
        password: str
            Password of the user to be verified.
        save_state: bool
            True: authentication status and credentials (if valid) are stored 
            in session state and cookie; False: nothing is stored.

        Returns
        -------
        bool
            Validity of the credentials.
        '''
        # Retrieve data from database
        user = db_tools.get_user(userid)
        if user is not None and check_pw(password, user['hashed_pw']):
            if not user.get('active'):
                if save_state:
                    st.session_state['user'] = {'active': False}
                return False
            if save_state:
                # Session state
                st.session_state['authenticated'] = True
                st.session_state['user'] = {
                    'userid': user[self.user_id_type],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'active': user['active'],
                    'role': user['role']
                }
                # Cookie
                self._set_cookie()
            return True
        else:
            if save_state:
                st.session_state['authenticated'] = False
            return False

    def login(self, location: str='main', fields: dict={'form name':'Login',
                                                        'userid':'Username',
                                                        'password':'Password',
                                                        'submit':'Login'}) -> bool:
        '''
        Creates a login widget.

        Parameters
        ----------
        location: str
            The location of the login widget i.e. main or sidebar.
        fields: dict
            The rendered names of the fields/buttons.

        Returns
        -------
        bool
            The status of authentication, None: no credentials entered, 
            False: incorrect credentials, True: correct credentials.
        '''
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")

        if location == 'main':
            login_form = st.form('login')
        elif location == 'sidebar':
            login_form = st.sidebar.form('login')

        login_form.subheader(
            'Login' if 'form name' not in fields else fields['form name']
        )
        userid = login_form.text_input(
            'Username' if 'userid' not in fields else fields['userid']
        )
        password = login_form.text_input(
            'Password' if 'password' not in fields else fields['password'],
            type='password'
        )
        submitted = login_form.form_submit_button(
            'Login' if 'submit' not in fields else fields['submit']
        )

        if submitted:
            if self._check_credentials(userid, password):
                st.query_params.clear()

        return st.session_state['authenticated']

    def _implement_logout(self):
        '''
        Clears cookie and session state variables associated with the logged in user.
        '''
        self.cookie_manager.delete(self.cookie_name)
        st.session_state['authenticated'] = None
        st.session_state['logout'] = True
        st.session_state['user'] = {}
        st.query_params.clear()

    def logout(self, button_name: str='Logout', location: str='main', key: str=None):
        '''
        Creates a logout button.

        Parameters
        ----------
        button_name: str
            The rendered name of the logout button.
        location: str
            The location of the logout button: main, sidebar or unrendered.
        key: str
            A unique key to be used in multipage applications.
        '''
        if location not in ['main', 'sidebar','unrendered']:
            raise ValueError("Location must be one of 'main' or 'sidebar' or 'unrendered'")
        if location == 'main':
            if st.button(button_name, key):
                self._implement_logout()
        elif location == 'sidebar':
            if st.sidebar.button(button_name, key):
                self._implement_logout()
        elif location == 'unrendered':
            if st.session_state['authenticated']:
                self._implement_logout()

    def _validate_form_data(self, form_data: dict) -> tuple:
        '''
        Perform validation checks on form data.

        Parameters
        ----------
        form_data: dict
            Data to validate.

        Returns
        -------
        bool
            Boolean indicating the validity of the data.
        str
            Message explaining validation status.
        '''
        if 'required' in form_data:
            if '' in form_data['required']:
                return False, 'Fields with an asterisk are required'

        if 'email' in form_data:
            if not self.validator.validate_email(form_data['email']):
                return False, 'Invalid e-mail'

        if 'username' in form_data:
            if not self.validator.validate_username(form_data['username']):
                return False, 'Invalid username'

        if 'name' in form_data:
            if isinstance(form_data['name'], list):
                if not all([ self.validator.validate_name(name) for name in form_data['name'] ]):
                    return False, 'Invalid name'
            else:
                if not self.validator.validate_name(form_data['name']):
                    return False, 'Invalid name'

        if 'password' in form_data and 'repeat_password' in form_data:
            if form_data['password'] != form_data['repeat_password']:
                return False, 'Passwords do not match'

        if 'password' in form_data:
            if not self.validator.validate_password(form_data['password']):
                return False, 'Password must be at least 8 characters long'

        return True, ''

    def _create_new_user(self, new_user_data: dict) -> tuple:
        '''
        Inserts new user in the database.

        Parameters
        ----------
        new_user_data: dict
            Data from the registration form.

        Returns
        -------
        bool
            Whether user creation was successful or not.
        str
            Success or error message.
        '''
        user = db_tools.get_user(new_user_data.get('userid'))
        if user is not None:
            return False, 'User already registered'

        success = db_tools.create_new_user(new_user_data)
        if success:
            return True, 'User registered successfully'
        else:
            return False, 'Registration failed, please try again later'

    def register_user(self, location: str='main', fields: dict={'form name':'Register',
                                                           'userid':'Username*',
                                                           'first name': 'First ame*',
                                                           'last name': 'Last name*',
                                                           'password':'Password*',
                                                           'repeat password':'Repeat password*',
                                                           'submit':'Register'}) -> tuple:
        '''
        Creates a user registration widget and inserts a new profile in the 
        database.

        Parameters
        ----------
        location: str
            The location of the registration widget i.e. main or sidebar.
        fields: dict
            The rendered names of the fields/buttons.

        Returns
        -------
        bool
            The status of registration, None: form not submitted, False: error 
            during registration, True: registration successful.
        str
            Success or error message.
        '''
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")

        if location == 'main':
            register_user_form = st.form('register-user')
        elif location == 'sidebar':
            register_user_form = st.sidebar.form('register-user')

        register_user_form.subheader(
            'Register' if 'form name' not in fields else fields['form name']
        )
        userid = register_user_form.text_input(
            'Username*' if 'userid' not in fields else fields['userid']+'*'
        )
        first_name = register_user_form.text_input(
            'First name*' if 'first name' not in fields else fields['first name']+'*'
        )
        last_name = register_user_form.text_input(
            'Last name*' if 'last name' not in fields else fields['last name']+'*'
        )
        password = register_user_form.text_input(
            'Password*' if 'password' not in fields else fields['password']+'*',
            type='password'
        )
        repeat_pw = register_user_form.text_input(
            'Repeat password*' if 'repeat password' not in fields else fields['repeat password']+'*',
            type='password'
        )
        submitted = register_user_form.form_submit_button(
            'Register' if 'submit' not in fields else fields['submit']
        )

        if submitted:
            valid_form, msg = self._validate_form_data({
                'required': [userid, first_name, last_name, password, repeat_pw],
                self.user_id_type: userid,
                'name': [first_name, last_name],
                'password': password,
                'repeat_password': repeat_pw
            })
            if not valid_form:
                return False, msg

            registration_complete, msg = self._create_new_user({
                'id_type': self.user_id_type,
                'userid': userid,
                'first_name': first_name,
                'last_name': last_name,
                'password': password
            })
            return registration_complete, msg

        return None, ''

    def reset_password(self, location: str='main', fields: dict={'form name': 'Reset Password',
                                                                 'current password': 'Current password*',
                                                                 'new password': 'New password*',
                                                                 'repeat new password': 'Repeat new password*',
                                                                 'submit': 'Reset'}) -> tuple:
        '''
        Creates a password reset widget.

        Parameters
        ----------
        location: str
            The location of the password reset widget i.e. main or sidebar.
        fields: dict
            The rendered names of the fields/buttons.

        Returns
        -------
        bool
            The status of resetting the password, None: form not submitted, 
            False: error during reset, True: reset successful.
        str
            Success or error message.
        '''
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")

        if location == 'main':
            reset_password_form = st.form('reset-password')
        elif location == 'sidebar':
            reset_password_form = st.sidebar.form('reset-password')

        reset_password_form.subheader(
            'Reset password' if 'form name' not in fields else fields['form name']
        )
        current_pw = reset_password_form.text_input(
            'Current password*' if 'current password' not in fields else fields['current password']+'*',
            type='password'
        )
        new_pw = reset_password_form.text_input(
            'New password*' if 'new password' not in fields else fields['new password']+'*',
            type='password'
        )
        repeat_new_pw = reset_password_form.text_input(
            'Repeat new password*' if 'repeat new password' not in fields else fields['repeat new password']+'*',
            type='password'
        )
        submitted = reset_password_form.form_submit_button(
            'Reset' if 'submit' not in fields else fields['submit']
        )

        if submitted:
            # Check required fields
            valid_form, msg = self._validate_form_data({
                'required': [current_pw, new_pw, repeat_new_pw],
                'password': new_pw,
                'repeat_password': repeat_new_pw
            })
            if not valid_form:
                return False, msg
            
            # Check current credentials
            userid = st.session_state['user']['userid']
            success = self._check_credentials(
                userid=userid,
                password=current_pw,
                save_state=False
            )
            if not success:
                return False, 'Current password is incorrect'

            # Check new password
            if current_pw == new_pw:
                return False, 'Current and new passwords are the same'

            # Update password
            if db_tools.update_password(userid, new_pw):
                return True, 'Password updated successfully'
            else:
                return False, 'Update failed, please try again later'

        return None, ''

    def _account_deletion(self):
        if db_tools.delete_user(st.session_state['user']['userid']):
            self._implement_logout()

    def delete_account(self, fields: dict={'delete': 'Delete account',
                                           'confirm': 'I want to delete this account'}):
        '''
        Creates a delete account button.

        Parameters
        ----------
        fields: dict
            The rendered names of the buttons.
        '''
        col1, col2 = st.columns([1, 3])
        with col1:
            exclude_acc = st.button(
                'Delete account' if 'delete' not in fields else fields['delete']
            )
        if exclude_acc:
            with col2:
                st.button(
                    'I want to delete this account' if 'confirm' not in fields else fields['confirm'],
                    type='primary', on_click=self._account_deletion
                )

    def update_user_details(self, user_details: dict={'Name': 'name'}, fields: dict={'form name': 'Update user details',
                                                                                     'userid': 'Username',
                                                                                     'field': 'Field',
                                                                                     'new_value': 'New value*',
                                                                                     'submit': 'Update'}) -> tuple:
        '''
        Creates an update user details widget.

        Parameters
        ----------
        user_details: dict
            Updatable user details. Keys: human readable names; values: database
            names.
        fields: dict
            The rendered names of the fields/buttons.

        Returns
        -------
        bool
            The status of details updating, None: form not submitted, 
            False: error during update, True: update successful.
        str
            Success or error message.
        '''
        update_user_details_form = st.form('update-user-details')
        update_user_details_form.subheader(
            'Update user details' if 'form name' not in fields else fields['form name']
        )
        update_user_details_form.text_input(
            'Username' if 'userid' not in fields else fields['userid'],
            placeholder=st.session_state['user'].get('userid'),
            disabled=True
        )
        user = st.session_state['user']
        user_detail_fields = [ f'{k}: {user.get(v)}' for k, v in user_details.items() ]
        selected_option = update_user_details_form.selectbox(
            'Field' if 'field' not in fields else fields['field'],
            user_detail_fields
        )
        new_value = update_user_details_form.text_input(
            'New value*' if 'new_value' not in fields else fields['new_value']+'*'
        )
        submitted = update_user_details_form.form_submit_button(
            'Update' if 'submit' not in fields else fields['submit']
        )

        if submitted:
            field_readable_name = selected_option.split(':')[0]
            field_name = user_details.get(field_readable_name)
            if field_name not in user:
                return False, f'Could not recognize field: {field_name}'

            valid_form, msg = self._validate_form_data({'name': new_value})
            if not valid_form:
                return False, msg

            if user[field_name] == new_value:
                return False, 'Current and new value are the same'

            if db_tools.update_user_info(user['userid'], field_name, new_value):
                st.session_state['user'][field_name] = new_value
                self._set_cookie()
                return True, 'Data updated successfully'
            else:
                return False, 'Update failed, please try again later'

        return None, ''
