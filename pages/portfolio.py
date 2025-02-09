import streamlit as st

import controllers as ctr
from app import login_required, menu

login_required()
menu()
