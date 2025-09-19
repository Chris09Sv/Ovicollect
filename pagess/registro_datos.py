import streamlit as st
import requests
import datetime
import folium
from streamlit_folium import st_folium

API_URL = "http://127.0.0.1:8000"

def registro_datos():
    st.header("📋 Registro de Datos Semanales - Ovitrampas")

    # --- Verificar sesión activa ---
    access_token = st.session_state.get("access_token")
    user_id = st.session_state.get("username")
    user_province = st.session_state.get("province")  # assumed stored at login

    if not access_token or not user_id:
        st.error("Debes iniciar sesión para registrar datos.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # --- Semana Epidemiológica ---
    st.subheader("📅 Seleccione la Semana Epidemiológica")

    today = datetime.date.today()
    current_week = today.isocalendar()[1]
    current_year = today.year

    año_seleccionado = st.number_input("Año", min_value=2020, max_value=2050, value=current_year, step=1)
    semana_seleccionada = st.number_input("Semana", min_value=1, max_value=current_week, value=current_week, step=1)

    # --- Cargar trampas pendientes ---
    st.subheader("🪤 Seleccione la Trampa")

    try:
        response = requests.get(f"{API_URL}/trap_reports/pending/", headers=headers)
        # response.raise_for_status()
        todas_trampas = response.json()
    except Exception as e:
        st.error(f"Error al cargar trampas pendientes: {e}")
        return
    # --- Filtrar por provincia del usuario ---
    trampas_filtradas = [
        t for t in todas_trampas
        if t.get("province_id") == user_province
    ]

    if not trampas_filtradas:
        st.success("✅ Todas las trampas en tu provincia ya han sido reportadas esta semana.")
        return

    # --- Selección de trampa ---
    seleccion_trampa = st.selectbox(
        "Seleccione una trampa para reportar",
        options=trampas_filtradas,
        format_func=lambda t: f"{t.get('ovitrap_code', 'Sin nombre')} (ID: {t['id']})"

    )

    # --- Mostrar mapa ---
    st.markdown(f"📍 Coordenadas: `{seleccion_trampa['latitude']}, {seleccion_trampa['longitude']}`")

    m = folium.Map(location=[seleccion_trampa["latitude"], seleccion_trampa["longitude"]], zoom_start=17)
    folium.Marker(
        [seleccion_trampa["latitude"], seleccion_trampa["longitude"]],
        popup=seleccion_trampa.get("ovitrap_code", "Sin nombre"),
        icon=folium.Icon(color="blue")
    ).add_to(m)


    st_folium(m, height=250)

    # --- Resultado ---
    resultado = st.radio("Resultado de la Trampa", options=["Positiva", "Negativa"])
    es_positiva = resultado == "Positiva"

    # --- Enviar ---
    if st.button("✅ Registrar Reporte Semanal"):
        datos = {
            "trap_id": seleccion_trampa["id"],
            "week_number": semana_seleccionada,
            "year": año_seleccionado,
            "is_positive": es_positiva,
            "created_by": user_id
        }

        try:
            envio = requests.post(f"{API_URL}/trap_reports/", json=datos, headers=headers)
            if envio.status_code == 200:
                st.success("🎉 Reporte registrado exitosamente.")
                st.experimental_rerun()
            else:
                st.error(f"❌ Error al registrar reporte: {envio.status_code} - {envio.text}")
        except Exception as e:
            st.error(f"❌ Error al enviar reporte: {e}")
