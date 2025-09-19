import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import requests
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from io import BytesIO
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

API_URL = "http://127.0.0.1:8000"

def visualizar_registros():
    st.title("📊 Visualización de Registros Semanales - Ovitrampas")
    user_province = st.session_state.get("province")

    access_token = st.session_state.get("access_token")
    if not access_token:
        st.error("🔒 Debes iniciar sesión para acceder a esta sección.")
        return

    headers = {"Authorization": f"Bearer {access_token}"}

    # --- Cargar registros ---
    st.info("Cargando registros...")
    try:
        response = requests.get(f"{API_URL}/trap_reports/all/", headers=headers)
        response.raise_for_status()
        registros = response.json()
    except Exception as e:
        st.error(f"Error al obtener los datos: {e}")
        return

    df = pd.DataFrame(registros)

    if df.empty:
        st.warning("No hay registros disponibles.")
        return

    # --- Filtro por Provincia del Usuario ---
    df = df[df['province_id'] == user_province]

    # --- Filtros de Año y Semana ---
    st.subheader("🗓️ Filtros por Año y Semana")

    años = sorted(df["year"].unique())
    año = st.selectbox("Año", años, index=len(años)-1)

    semanas = sorted(df[df["year"] == año]["week_number"].unique())
    semana_inicio = st.selectbox("Semana Inicial", semanas)
    semana_fin = st.selectbox("Semana Final", semanas, index=len(semanas)-1)

    df_filtrado = df[
        (df["year"] == año) &
        (df["week_number"] >= semana_inicio) &
        (df["week_number"] <= semana_fin)
    ]

    if df_filtrado.empty:
        st.warning("No hay registros en el rango seleccionado.")
        return

    # --- Mostrar Registros en AgGrid ---
    st.subheader("📋 Registros Filtrados")

    gd = GridOptionsBuilder.from_dataframe(df_filtrado)
    gd.configure_pagination(paginationAutoPageSize=True)
    gd.configure_side_bar()
    gd.configure_default_column(resizable=True, filterable=True)
    grid_options = gd.build()

    AgGrid(
        df_filtrado,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.NO_UPDATE,
        height=350,
        theme="streamlit",
    )

    # --- Descargar como Excel ---
    st.subheader("⬇️ Descargar Datos")

    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Registros")
        return output.getvalue()

    st.download_button(
        label="📥 Descargar como Excel",
        data=to_excel(df_filtrado),
        file_name=f"ovitrampas_{año}_S{semana_inicio}-{semana_fin}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # --- Gráfico: Positivas vs Negativas ---
    st.subheader("📈 Trampas Positivas vs Negativas")
    resumen = df_filtrado.groupby(["week_number", "is_positive"]).size().unstack(fill_value=0)

    # Normaliza columnas por si faltan Positivas o Negativas
    for val in [True, False]:
        if val not in resumen.columns:
            resumen[val] = 0

    # Reordenar columnas y renombrar
    resumen = resumen.reindex(columns=[False, True])
    resumen.columns = ["Negativas", "Positivas"]
    

    fig1, ax1 = plt.subplots(figsize=(10, 4))
    resumen.plot(kind="bar", stacked=True, ax=ax1, color=["green", "red"])
    ax1.set_title("Cantidad de Trampas por Semana")
    ax1.set_xlabel("Semana Epidemiológica")
    ax1.set_ylabel("Cantidad")
    st.pyplot(fig1)

    # --- Gráfico: Porcentaje de Positividad ---
    st.subheader("📉 Porcentaje de Positividad")

    resumen["Total"] = resumen.sum(axis=1)
    resumen["% Positivas"] = (resumen["Positivas"] / resumen["Total"]) * 100

    fig2, ax2 = plt.subplots(figsize=(10, 3.5))
    resumen["% Positivas"].plot(marker='o', color="blue", ax=ax2)
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("% Positividad")
    ax2.set_xlabel("Semana Epidemiológica")
    ax2.set_title("Porcentaje de Trampas Positivas")
    st.pyplot(fig2)

    # --- Mapa de Calor ---
    st.subheader("🗺️ Mapa de Calor de Trampas Positivas")

    positivos = df_filtrado[df_filtrado["is_positive"] == True]

    if not positivos.empty and {"latitude", "longitude"}.issubset(positivos.columns):
        heatmap_data = positivos[["latitude", "longitude"]].dropna().values.tolist()
        center = [positivos["latitude"].mean(), positivos["longitude"].mean()]
        mapa = folium.Map(location=center, zoom_start=10)
        HeatMap(heatmap_data, radius=15).add_to(mapa)
        st_folium(mapa, width=800, height=500)
    else:
        st.info("No hay datos positivos georreferenciados para mostrar en mapa.")
