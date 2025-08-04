import streamlit as st
from frontend.api_client import api_client

def is_logged_in() -> bool:
    """Check if user is logged in"""
    return st.session_state.get('access_token') is not None

def get_current_user() -> str:
    """Get the current logged-in user from session state"""
    return st.session_state.get('current_user')

def logout_user():
    """Logout the current user"""
    if 'access_token' in st.session_state:
        del st.session_state['access_token']
    if 'current_user' in st.session_state:
        del st.session_state['current_user']
    if 'username' in st.session_state:
        del st.session_state['username']

def register_user(username: str, password: str, email: str = None) -> tuple[bool, str]:
    """Register a new user via API"""
    try:
        result = api_client.register_user(username, password, email)
        if result:
            return True, "User registered successfully"
        else:
            return False, "Registration failed"
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def login_user(username: str, password: str) -> tuple[bool, str]:
    """Login a user via API"""
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

def render_login_page():
    """Render the login/register page with API integration"""
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
        .api-status {
            padding: 0.5rem;
            border-radius: 5px;
            margin: 1rem 0;
            font-size: 0.9rem;
        }
        .api-online {
            background: rgba(46, 204, 113, 0.2);
            border: 1px solid rgba(46, 204, 113, 0.5);
        }
        .api-offline {
            background: rgba(231, 76, 60, 0.2);
            border: 1px solid rgba(231, 76, 60, 0.5);
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
            email = st.text_input("Email (optional)")
            submit_register = st.form_submit_button("Register")
            
            if submit_register:
                if new_username and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        success, message = register_user(new_username, new_password, email)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                else:
                    st.error("Please fill in all required fields")
        
        st.markdown('</div>', unsafe_allow_html=True) 