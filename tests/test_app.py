from streamlit.testing.v1 import AppTest


def test_run_app():
    at = AppTest.from_file('app.py').run()
    assert not at.exception
