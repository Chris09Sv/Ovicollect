from pagess import visualizar_registros
import streamlit as st
import requests

# http://localhost:8000/docs
LOGIN_API_URL = "http://localhost:8000/token"
API_URL = "http://localhost:8000/"

# Function to handle login
def login():
    st.header("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar Sesión"):
        if username and password:
            # Make request to FastAPI /token endpoint
            try:
                response = requests.post(
                    f"{API_URL}/token",
                    data={"username": username, "password": password},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )

                if response.status_code == 200:
                    tokens = response.json()
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["access_token"] = tokens["access_token"]  # ✅ Save token here
                    st.session_state["province"] = tokens["dps_das"]  # Or however it's labeled
                    st.session_state["profile"] = tokens["profile"]
                else:
                    st.error("Usuario o contraseña incorrectos.")
            except Exception as e:
                st.error(f"Error al conectar al servidor: {str(e)}")
        else:
            st.error("Por favor ingresa usuario y contraseña.")

# Function to fetch user details
def get_user_details(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(API_URL + "users/me", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error('Error al intentar obtener datos de usuario.')
        return None

# Sidebar menu function
def home_page():
    # Define menu options
    menu_options = {
        "Home": visualizar_registros,
        # "Sat": Sat_home
    }

    # Sidebar menu (selection logic inside sidebar)
    with st.sidebar:
        st.header("MULTPAGE WITH CUSTOM MENU")
        selected = st.selectbox("Choose a page", options=list(menu_options.keys()))

    # Main content area (rendering outside sidebar)
    page_container = st.container()  # Container to ensure content separation
    with page_container:
        if selected in menu_options:
            try:
                menu_options[selected]()  # Render the selected page content in the main area
            except Exception as e:
                st.error(f"An error occurred while loading the page: {e}")

# Main function controlling login and app pages
def main():
    # Initialize session state for user login
    if 'token' not in st.session_state:
        st.session_state['token'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'  # Set default page as login

    # Logout and menu handling
    if st.session_state['page'] != 'login' and st.session_state['token']:
        home_page()
        with st.sidebar:  # Place logout button in the sidebar
            if st.button("Logout"):
                st.session_state['token'] = None
                st.session_state['username'] = None
                st.session_state['page'] = 'login'
                st.rerun()

    # Function to switch to logged-in state
    def set_login():
        st.session_state['page'] = 'main'

    # # Login page logic
    # if st.session_state['page'] == 'login':
    #     st.title("Log in Page")
    #     st.subheader("Please log in to access the app")
    #     username = st.text_input("Username")
    #     password = st.text_input("Password", type="password")
    #     if st.button("Login"):
    #         token = login(username, password)
    #         if token:
    #             st.session_state['token'] = token
    #             st.session_state['username'] = username
    #             set_login()  # Switch to the main page after successful login
    # else:
    #     # Main app content page
    #     st.title("Main App Content")
    #     st.write("This is the main app page that requires authentication.")

# Run the app
if __name__ == "__main__":
    main()
