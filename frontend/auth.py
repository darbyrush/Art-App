import streamlit as st
import hashlib
import json
import os
from datetime import datetime

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    if os.path.exists('users.json'):
        try:
            with open('users.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

def register_user(username, password):
    """Register a new user"""
    users = load_users()
    
    if username in users:
        return False, "Username already exists"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Create user
    users[username] = {
        'password': hashed_password,
        'created_at': datetime.now().isoformat(),
        'user_id': username  # Using username as user_id for simplicity
    }
    
    save_users(users)
    return True, "User registered successfully"

def login_user(username, password):
    """Login a user"""
    users = load_users()
    
    if username not in users:
        return False, "Invalid username or password"
    
    hashed_password = hash_password(password)
    if users[username]['password'] != hashed_password:
        return False, "Invalid username or password"
    
    return True, users[username]['user_id']

def get_current_user():
    """Get the current logged-in user from session state"""
    return st.session_state.get('current_user')

def is_logged_in():
    """Check if user is logged in"""
    return get_current_user() is not None

def logout_user():
    """Logout the current user"""
    if 'current_user' in st.session_state:
        del st.session_state['current_user']
    if 'username' in st.session_state:
        del st.session_state['username']

def render_login_page():
    """Render the login/register page"""
    st.markdown("""
    <style>
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            color: white;
            text-align: center;
        }
        .auth-form {
            background: rgba(255,255,255,0.1);
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        .auth-button {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            margin: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🎨 Art Explorer</h1>', unsafe_allow_html=True)
    
    # Create tabs for login and register
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.subheader("Welcome Back!")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    success, message = login_user(username, password)
                    if success:
                        st.session_state['current_user'] = message
                        st.session_state['username'] = username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all fields")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.subheader("Create Account")
        
        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit_register = st.form_submit_button("Register")
            
            if submit_register:
                if new_username and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        success, message = register_user(new_username, new_password)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                else:
                    st.error("Please fill in all fields")
        
        st.markdown('</div>', unsafe_allow_html=True) 