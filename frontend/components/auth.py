#!/usr/bin/env python3
"""
Frontend Authentication Component
Handles user authentication UI and logic
"""

import streamlit as st
from frontend.api_client import api_client

def is_logged_in() -> bool:
    """Check if user is logged in"""
    return st.session_state.get('access_token') is not None

def get_current_user() -> str:
    """Get current user username"""
    return st.session_state.get('current_user')

def logout_user():
    """Logout current user"""
    if 'access_token' in st.session_state:
        del st.session_state['access_token']
    if 'current_user' in st.session_state:
        del st.session_state['current_user']
    if 'username' in st.session_state:
        del st.session_state['username']

def register_user(username: str, password: str, email: str = None) -> tuple[bool, str]:
    """Register a new user"""
    try:
        result = api_client.register_user(username, password, email)
        if result:
            return True, "User registered successfully"
        else:
            return False, "Registration failed"
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def login_user(username: str, password: str) -> tuple[bool, str]:
    """Login user"""
    try:
        token = api_client.login_user(username, password)
        if token:
            st.session_state['access_token'] = token
            st.session_state['current_user'] = username
            st.session_state['username'] = username
            return True, "Login successful"
        else:
            return False, "Invalid username or password"
    except Exception as e:
        return False, f"Login error: {str(e)}"

def require_auth():
    """Global authentication wrapper - call this at the top of each page"""
    if not is_logged_in():
        render_login_page()
        st.stop()

def render_login_page():
    """Render the login/register page"""
    # Custom CSS for login page
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            color: #2c3e50;
            font-size: 2.5rem;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .api-status {
            padding: 0.5rem 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            text-align: center;
            font-weight: bold;
        }
        
        .api-online {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .api-offline {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .form-container {
            margin-top: 1rem;
        }
        
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 10px;
            font-weight: bold;
            margin-top: 1rem;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }
        
        .tab-container {
            margin-top: 2rem;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            border-radius: 8px;
            color: #495057;
            padding: 10px 16px;
            border: 1px solid #dee2e6;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-header">🎨 Art Explorer</h1>', unsafe_allow_html=True)

    # Check API status
    api_online = api_client.health_check()
    if api_online:
        st.markdown('<div class="api-status api-online">✅ API Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="api-status api-offline">❌ API Offline - Please start the backend server</div>', unsafe_allow_html=True)
        st.info("To start the API server, run: `uvicorn api.main:app --reload --port 8000`")
        return

    # Login/Register tabs
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("### Welcome Back!")
        
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit_button = st.form_submit_button("🔐 Login")
            
            if submit_button:
                if username and password:
                    success, message = login_user(username, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all fields")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("### Join Art Explorer!")
        
        with st.form("register_form"):
            new_username = st.text_input("Username", key="register_username")
            new_password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            email = st.text_input("Email (optional)", key="register_email")
            submit_button = st.form_submit_button("📝 Register")
            
            if submit_button:
                if new_username and new_password and confirm_password:
                    if new_password == confirm_password:
                        success, message = register_user(new_username, new_password, email)
                        if success:
                            st.success(message)
                            st.info("You can now login with your new account!")
                        else:
                            st.error(message)
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in all required fields")
        
        st.markdown('</div>', unsafe_allow_html=True) 