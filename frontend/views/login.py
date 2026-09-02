"""Step 1 of the workflow: Login."""

from __future__ import annotations

import streamlit as st

from frontend import components as ui
from frontend import state


def render() -> None:
    left, middle, right = st.columns([1, 1.05, 1])
    with middle:
        st.markdown(
            f'<div class="fo-auth-brand fo-animate">{ui.brand_block(stacked=True)}</div>',
            unsafe_allow_html=True,
        )
        with st.container(key="auth_card"):
            sign_in_tab, sign_up_tab = st.tabs(["Sign in", "Create account"])
            with sign_in_tab:
                _render_sign_in()
            with sign_up_tab:
                _render_sign_up()


def _render_sign_in() -> None:
    with st.form("sign_in", clear_on_submit=False, border=False):
        username = st.text_input("Username", autocomplete="username", placeholder="Enter your username")
        password = st.text_input(
            "Password", type="password", autocomplete="current-password", placeholder="Enter your password"
        )
        submitted = st.form_submit_button("Sign in", type="primary", width="stretch")

    if submitted:
        if state.authenticate(username, password):
            st.rerun()
        st.error("Incorrect username or password.")


def _render_sign_up() -> None:
    with st.form("sign_up", clear_on_submit=False, border=False):
        name = st.text_input("Full name", placeholder="Jane Doe")
        username = st.text_input("Username", placeholder="Choose a username")
        password = st.text_input("Password", type="password", placeholder="Choose a password")
        role = st.selectbox("Role", state.ROLES)
        created = st.form_submit_button("Create account", type="primary", width="stretch")

    if created:
        ok, message = state.create_account(name, username, password, role)
        if ok:
            st.rerun()
        st.error(message)
