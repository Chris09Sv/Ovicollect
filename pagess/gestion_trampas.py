import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit_extras.stylable_container import stylable_container
import io
from streamlit_folium import st_folium
import folium# ovitraps_app.py
import streamlit as st
import requests
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, MousePosition, MeasureControl

API_URL = "http://127.0.0.1:8000"


def fetch_json(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        if response.ok:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {e}")
    return []





# --------- FORM DEPENDENCY FUNCTIONS ---------
def get_provincias(): return fetch_json("dm/provincias/")
def get_municipalities(prov_id): return fetch_json(f"dm/municipalities/{prov_id}")
def get_districts(mun_id): return fetch_json(f"dm/districts/{mun_id}")
def get_sections(dist_id): return fetch_json(f"dm/sections/{dist_id}")
def get_neighborhoods(sec_id): return fetch_json(f"dm/neighborhoods/{sec_id}")


# --------- ADD TRAP UI ---------


import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, MousePosition, MeasureControl

API_URL = "http://127.0.0.1:8000"

def fetch_json(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        if response.ok:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {e}")
    return []

def reverse_geocode(lat, lon):
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lon,
                "format": "jsonv2",
                "addressdetails": 1,
                "accept-language": "es",
                "countrycodes": "do"
            },
            headers={"User-Agent": "Ovitrampas-App/1.0"}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("display_name"), data.get("address", {})
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
    return None, {}

def geocode_address(address):
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "json", "countrycodes": "do", "limit": 1},
            headers={"User-Agent": "OviCollect-App"}
        )
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        st.warning(f"Error en geocodificación: {e}")
    return None, None

def match_nombre(nombre_sugerido, diccionario_local):
    if not nombre_sugerido:
        return None
    for nombre_opcion in diccionario_local:
        if nombre_opcion.lower().strip() == nombre_sugerido.lower().strip():
            return nombre_opcion
    return None

def gestion_trampas():
    st.header("🆕 Agregar Nueva Trampa")

    if "manual_lat" not in st.session_state:
        st.session_state.manual_lat = 0.0
    if "manual_lon" not in st.session_state:
        st.session_state.manual_lon = 0.0

    provincias = fetch_json("dm/provincias/")
    prov_dict = {p["provincia"]: p["id"] for p in provincias}
    prov_name = st.selectbox("Provincia", prov_dict.keys())
    prov_id = prov_dict.get(prov_name)

    municipios = fetch_json(f"dm/municipalities/{prov_id}")
    muni_dict = {m["municipality"]: m["id"] for m in municipios}
    muni_name = st.selectbox("Municipio", muni_dict.keys())
    muni_id = muni_dict.get(muni_name)

    distritos = fetch_json(f"dm/districts/{muni_id}")
    dist_dict = {d["district"]: d["id"] for d in distritos}
    dist_name = st.selectbox("Distrito", dist_dict.keys())
    dist_id = dist_dict.get(dist_name)

    secciones = fetch_json(f"dm/sections/{dist_id}")
    sec_dict = {s["section"]: s["id"] for s in secciones}
    sec_name = st.selectbox("Sección", sec_dict.keys())
    sec_id = sec_dict.get(sec_name)

    barrios = fetch_json(f"dm/neighborhoods/{sec_id}")
    barrio_dict = {b["neighborhood"]: b["id"] for b in barrios}
    barrio_name = st.selectbox("Barrio", barrio_dict.keys())
    barrio_id = barrio_dict.get(barrio_name)

    area_salud = st.text_input("Área de Salud")
    clave_ovitrampa = st.text_input("Clave de la Ovitrampa")
    clave_manzana = st.text_input("Clave de la Manzana")
    direccion = st.text_input("Dirección")

    st.subheader("🔎 Buscar Localidad por Nombre")
    busqueda_localidad = st.text_input("Nombre de la localidad")
    map_center = [18.4861, -69.9312]

    if busqueda_localidad:
        lat_busq, lon_busq = geocode_address(busqueda_localidad)
        if lat_busq and lon_busq:
            map_center = [lat_busq, lon_busq]
            st.session_state.manual_lat = lat_busq
            st.session_state.manual_lon = lon_busq
            st.success(f"Localidad encontrada: Lat {lat_busq:.5f}, Lon {lon_busq:.5f}")
        else:
            st.warning("No se encontró la localidad.")

    st.markdown("### 🧭 Coordenadas Manuales")
    col_lat, col_lon = st.columns(2)
    st.session_state.manual_lat = col_lat.number_input("Latitud manual", value=st.session_state.manual_lat, format="%.6f", key="input_lat")
    st.session_state.manual_lon = col_lon.number_input("Longitud manual", value=st.session_state.manual_lon, format="%.6f", key="input_lon")

    if st.session_state.manual_lat != 0.0 and st.session_state.manual_lon != 0.0:
        map_center = [st.session_state.manual_lat, st.session_state.manual_lon]

    st.subheader("📍 Mapa de Ubicación")
    marker_text = st.text_input("Texto del Marcador", "📍 Ovitrampa Nueva")
    m = folium.Map(location=map_center, zoom_start=17, control_scale=True)
    LocateControl(auto_start=False, fly_to=True).add_to(m)
    folium.TileLayer('OpenStreetMap').add_to(m)
    folium.TileLayer('Esri.WorldImagery', name='Satélite').add_to(m)
    folium.LayerControl().add_to(m)
    m.add_child(MeasureControl())
    MousePosition().add_to(m)

    custom_icon = folium.CustomIcon("https://cdn-icons-png.flaticon.com/512/684/684908.png", icon_size=(40, 40))
    folium.Marker(location=map_center, draggable=True, popup=marker_text, icon=custom_icon).add_to(m)

    output = st_folium(m, width=800, height=550)
    lat, lon = None, None

    if output and output.get("last_clicked"):
        lat = output["last_clicked"]["lat"]
        lon = output["last_clicked"]["lng"]
        st.session_state.manual_lat = lat
        st.session_state.manual_lon = lon
        st.success(f"Ubicación seleccionada: Lat {lat:.5f}, Lon {lon:.5f}")
    elif st.session_state.manual_lat != 0.0 and st.session_state.manual_lon != 0.0:
        lat = st.session_state.manual_lat
        lon = st.session_state.manual_lon
        st.info(f"Usando coordenadas manuales: Lat {lat:.5f}, Lon {lon:.5f}")

    if lat and lon:
        display_name, address_info = reverse_geocode(lat, lon)
        if display_name:
            st.info(f"Dirección detectada: {display_name}")
            posible_provincia = address_info.get("state")
            posible_municipio = address_info.get("city") or address_info.get("town") or address_info.get("village")
            posible_barrio = address_info.get("neighbourhood") or address_info.get("suburb")

            st.write("📍 Sugerencias desde mapa:")
            st.write(f"Provincia: {posible_provincia}")
            st.write(f"Municipio: {posible_municipio}")
            st.write(f"Barrio: {posible_barrio}")

            nombre_prov_match = match_nombre(posible_provincia, prov_dict)
            if nombre_prov_match:
                prov_name = nombre_prov_match
                prov_id = prov_dict[prov_name]
                st.success(f"Provincia asignada: {prov_name}")

                muni_dict = {m["municipality"]: m["id"] for m in fetch_json(f"dm/municipalities/{prov_id}")}
                nombre_muni_match = match_nombre(posible_municipio, muni_dict)
                if nombre_muni_match:
                    muni_name = nombre_muni_match
                    muni_id = muni_dict[muni_name]
                    st.success(f"Municipio asignado: {muni_name}")

                    barrio_dict = {b["neighborhood"]: b["id"] for b in fetch_json(f"dm/neighborhoods/{sec_id}")}
                    nombre_barrio_match = match_nombre(posible_barrio, barrio_dict)
                    if nombre_barrio_match:
                        barrio_name = nombre_barrio_match
                        barrio_id = barrio_dict[barrio_name]
                        st.success(f"Barrio asignado: {barrio_name}")

    if st.button("➕ Añadir Trampa"):
        if not lat or not lon:
            st.error("Faltan coordenadas válidas.")
            return

        payload = {
            "province_id": prov_id,
            "municipality_id": muni_id,
            "neighborhood_id": barrio_id,
            "health_area": area_salud,
            "ovitrap_code": clave_ovitrampa,
            "block_code": clave_manzana,
            "address": direccion,
            "location_description": marker_text,
            "latitude": lat,
            "longitude": lon,
            "created_by": 1
        }

        token = st.session_state.get("access_token")
        if not token:
            st.error("Token no disponible.")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        res = requests.post(f"{API_URL}/traps/", json=payload, headers=headers)
        if res.ok:
            st.success(f"✅ Trampa creada: {res.json().get('trap_key')}")
        else:
            st.error(f"❌ Error: {res.status_code} - {res.text}")


def admin_dashboard():
    st.header("🛠️ Administración de Trampas")

    token = st.session_state.get("access_token")
    if not token:
        st.error("⚠️ Token no disponible. Inicia sesión.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{API_URL}/traps/list", headers=headers)
        response.raise_for_status()
        traps = response.json()
    except Exception as e:
        st.error(f"❌ Error cargando trampas: {e}")
        return

    if not traps:
        st.warning("🚫 No se encontraron trampas.")
        return

    df = pd.DataFrame(traps)

    # Filter UI
    col1, col2 = st.columns(2)
    with col1:
        selected_province = st.selectbox("📍 Provincia", ["Todas"] + sorted(df["province"].unique()))
    with col2:
        selected_municipality = st.selectbox("🏘️ Municipio", ["Todos"] + sorted(df["municipality"].unique()))

    filtered_df = df.copy()
    if selected_province != "Todas":
        filtered_df = filtered_df[filtered_df["province"] == selected_province]
    if selected_municipality != "Todos":
        filtered_df = filtered_df[filtered_df["municipality"] == selected_municipality]



    # Convert filtered DataFrame to Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name="Trampas")

    # Button to download
    st.download_button(
        label="📥 Descargar Trampas en Excel",
        data=excel_buffer.getvalue(),
        file_name="trampas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    trap_labels ={
        f"{row['trap_key']} ({row['province']}, {row['municipality']})": row
        for _, row in filtered_df.iterrows()
    }
    st.markdown("### 🌐 Mapa de Todas las Trampas Filtradas")

    if not filtered_df.empty:
        all_map = folium.Map(location=[filtered_df["latitude"].mean(), filtered_df["longitude"].mean()],
                            zoom_start=8, control_scale=True)

        for _, row in filtered_df.iterrows():
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=f"{row['trap_key']}<br>{row['province']}, {row['municipality']}",
                icon=folium.Icon(color="green" if row["status"] == "A" else "red", icon="info-sign")
            ).add_to(all_map)

        st_folium(all_map, height=400)
    else:
        st.info("No hay trampas que mostrar en el mapa.")


    if not trap_labels:
        st.info("No hay trampas que coincidan con los filtros.")
        return

    selected_label = st.selectbox("🔎 Selecciona una trampa", list(trap_labels.keys()))
    selected_trap = trap_labels[selected_label]

    # Display trap details
    with st.container(border=True):
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown(f"### 🪤 Clave: `{selected_trap['trap_key']}`")
            st.markdown(f"**Provincia:** {selected_trap['province']}")
            st.markdown(f"**Municipio:** {selected_trap['municipality']}")
            st.markdown(f"**Barrio:** {selected_trap['neighborhood']}")
            st.markdown(f"**Dirección:** {selected_trap['address']}")
            st.markdown(f"**Área Salud:** {selected_trap['health_area']}")

        with col2:
            st.markdown(f"**📍 Coordenadas:** `{selected_trap['latitude']}, {selected_trap['longitude']}`")
            st.markdown(f"**🕒 Creado:** {format_datetime(selected_trap['created_at'])}")
            st.markdown(f"**🕓 Modificado:** {format_datetime(selected_trap['updated_at'])}")
            status_display = "🟢 Activa" if selected_trap["status"] == "A" else "🔴 Inactiva"
            st.markdown(f"**Estado:** {status_display}")

            # 🗺️ Mini Map
            try:
                lat, lon = float(selected_trap['latitude']), float(selected_trap['longitude'])
                m = folium.Map(location=[lat, lon], zoom_start=17, control_scale=True)
                folium.Marker(
                    location=[lat, lon],
                    popup=f"Trap: {selected_trap['trap_key']}",
                    icon=folium.Icon(color="green" if selected_trap["status"] == "A" else "red", icon="info-sign")
                ).add_to(m)
                st_folium(m, width=350, height=250)
            except Exception as e:
                st.warning(f"Error mostrando mapa: {e}")

        with st.expander("✏️ Editar Trampa"):
            show_edit_form(selected_trap, token)


def format_datetime(dt_str):
    from datetime import datetime
    try:
        return datetime.fromisoformat(dt_str).strftime("%d/%m/%Y %H:%M")
    except:
        return dt_str

def show_edit_form(trap, token):
    with st.form(f"edit_form_{trap['id']}"):
        trap_key = st.text_input("Clave de Trampa", trap["trap_key"])
        health_area = st.text_input("Área de Salud", trap["health_area"])
        address = st.text_input("Dirección", trap["address"])
        status = st.selectbox("Estado", ["A", "I"], index=0 if trap["status"] == "A" else 1)

        if st.form_submit_button("💾 Guardar Cambios"):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            payload = {
                "trap_key": trap_key,
                "health_area": health_area,
                "address": address,
                "status": status
            }
            try:
                res = requests.put(f"{API_URL}/traps/{trap['id']}", json=payload, headers=headers)
                if res.ok:
                    st.success("✅ Trampa actualizada correctamente.")
                    st.experimental_rerun()
                else:
                    st.error("❌ Error al actualizar la trampa.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# --------- MAIN ---------
st.set_page_config(page_title="Ovitrampas", layout="wide")
def main():
    tabs = st.tabs(["🆕 Agregar Trampa", "🛠️ Admin Trampas"])

    with tabs[0]:
        gestion_trampas()

    with tabs[1]:
        admin_dashboard()
