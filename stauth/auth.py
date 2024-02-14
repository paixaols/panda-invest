import bcrypt
import jwt
import streamlit as st
import extra_streamlit_components as stx

from datetime import datetime, timedelta

from . import mongodb_tools as db_tools

def hash_pw(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()


def check_pw(password, hashedpw):
    return bcrypt.checkpw(password.encode('utf-8'), hashedpw.encode('utf-8'))


class Authenticator:
    '''
    This class manages user authentication and creates register user, login, 
    logout, and reset password widgets.
    '''
    def __init__(self, cookie_name: str, key: str, cookie_expiry_days: float=1.0):
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
        self.cookie_name = cookie_name
        self.key = key
        self.cookie_expiry_days = cookie_expiry_days
        self.cookie_manager = stx.CookieManager()

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
                'user_id': st.session_state['user']['userid'],
                'user_name': st.session_state['user']['name'],
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
                        if 'user_id' in self.token:
                            st.session_state['user'] = {
                                'userid': self.token['user_id'],
                                'name': self.token['user_name']
                            }
                            st.session_state['authenticated'] = True

    def _check_credentials(self):
        '''
        Checks the validity of the entered credentials. If the credentials are 
        valid, authentication status is stored in session state, under the key 
        "authenticated", and the authentication cookie is stored on the 
        client's browser.
        '''
        # Retrieve data from database
        user = db_tools.get_user(self.userid)
        if user is not None and check_pw(self.password, user['hash']):
            # Session state
            st.session_state['authenticated'] = True
            st.session_state['user'] = {
                'userid': user['userid'],
                'name': user['name']
            }
            # Cookie
            self.exp_date = self._set_exp_date()
            self.token = self._token_encode()
            self.cookie_manager.set(
                self.cookie_name,
                self.token,
                expires_at=datetime.now() + timedelta(days=self.cookie_expiry_days)
            )
        else:
            st.session_state['authenticated'] = False

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

        if not st.session_state['authenticated']:
            self._check_cookie()
            if not st.session_state['authenticated']:
                if location == 'main':
                    login_form = st.form('Login')
                elif location == 'sidebar':
                    login_form = st.sidebar.form('Login')

                login_form.subheader(
                    'Login' if 'form name' not in fields else fields['form name']
                )
                self.userid = login_form.text_input(
                    'Username' if 'userid' not in fields else fields['userid']
                )
                self.password = login_form.text_input(
                    'Password' if 'password' not in fields else fields['password'],
                    type='password'
                )

                submitted = login_form.form_submit_button(
                    'Login' if 'submit' not in fields else fields['submit']
                )
                if submitted:
                    self._check_credentials()

        return st.session_state['authenticated']

    def _implement_logout(self):
        '''
        Clears cookie and session state variables associated with the logged in user.
        '''
        self.cookie_manager.delete(self.cookie_name)
        st.session_state['authenticated'] = None
        st.session_state['logout'] = True
        st.session_state['user'] = {}

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
