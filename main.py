# main.py
# from col import report_pending_traps
import login
import streamlit as st
from db import init_db, authenticate_user, register_user
from pagess.gestion_trampas import main
from pagess.registro_datos import registro_datos
from pagess.visualizar_registros import visualizar_registros
from login import login 

PAGES = {
    "Registro de Datos": registro_datos,
    "Visualización de Registros": visualizar_registros
}

# Add admin-only pages if the user is authorized
if st.session_state.get("profile") in ["Administrador", "Administrador General"]:
    PAGES["Gestión de Trampas"] = main




def register():
    st.header("Registro de Usuario")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Registrar"):
        register_user(username, password)
        st.success("Usuario registrado correctamente.")

def logout():
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["logged_in"] = False
        st.sidebar.success("Sesión cerrada correctamente.")



def main():
    init_db()

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.sidebar.title("Autenticación")
        choice = st.sidebar.radio("Opciones", ["Iniciar Sesión", "Registrarse"])
        if choice == "Iniciar Sesión":
            login()
        elif choice == "Registrarse":
            register()
    else:
        st.sidebar.title("Navegación")
        logout()
        selection = st.sidebar.radio("Ir a", list(PAGES.keys()))
        page = PAGES[selection]
        page()

if __name__ == "__main__":
    main()
