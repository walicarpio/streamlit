import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Dashboard SAVAL", layout="wide")

USUARIOS = {"admin": "1234", "usuario": "saval2025"}

def login():
    with st.sidebar:
        st.title("Login")
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if usuario in USUARIOS and USUARIOS[usuario] == password:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = usuario
            else:
                st.error("Credenciales incorrectas")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    login()
    st.stop()

@st.cache_data
def cargar_datos():
    df = pd.read_excel("junio_base.xlsx", engine="openpyxl", parse_dates=["Fecha Ingreso", "Fecha Servicio"])
    return df

df = cargar_datos()

st.sidebar.header("Filtros")

rango_fecha = st.sidebar.date_input("Fecha Servicio", 
    [df["Fecha Servicio"].min(), df["Fecha Servicio"].max()])

centros = st.sidebar.multiselect("Centro Saval", df["Centro Saval"].unique())
clientes = st.sidebar.multiselect("Cliente", df["Cliente"].unique())
servicios = st.sidebar.multiselect("Servicio", df["Servicio"].unique())
especialidades = st.sidebar.multiselect("Especialidad", df["Especialidad"].unique())
representante = st.sidebar.multiselect("Representante", df["Representante"].unique())

df_filtrado = df[
    (df["Fecha Servicio"] >= pd.to_datetime(rango_fecha[0])) &
    (df["Fecha Servicio"] <= pd.to_datetime(rango_fecha[1]))
]

if centros:
    df_filtrado = df_filtrado[df_filtrado["Centro Saval"].isin(centros)]
if clientes:
    df_filtrado = df_filtrado[df_filtrado["Cliente"].isin(clientes)]
if servicios:
    df_filtrado = df_filtrado[df_filtrado["Servicio"].isin(servicios)]
if especialidades:
    df_filtrado = df_filtrado[df_filtrado["Especialidad"].isin(especialidades)]
if representante:
    df_filtrado = df_filtrado[df_filtrado["Representante"].isin(representante)]

st.title("Dashboard Interactivo SAVAL")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Cantidad por Servicio")
    fig1 = px.bar(df_filtrado.groupby("Servicio")["Cantidad"].sum().reset_index(),
                  x="Servicio", y="Cantidad", title="Servicios Totales")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Distribución por Centro Saval")
    fig2 = px.pie(df_filtrado, names="Centro Saval", values="Cantidad", title="Distribución por Centro")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Tendencia de cantidad por día")
df_time = df_filtrado.groupby("Fecha Servicio")["Cantidad"].sum().reset_index()
fig3 = px.line(df_time, x="Fecha Servicio", y="Cantidad", markers=True)
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Tabla de datos filtrados")

st.dataframe(df_filtrado, use_container_width=True)

def convertir_csv(df):
    return df.to_csv(index=False).encode('utf-8')

st.download_button("📥 Descargar tabla filtrada", 
                   data=convertir_csv(df_filtrado),
                   file_name="resultados_filtrados.csv",
                   mime="text/csv")

with st.expander("Exportar gráfico"):
    st.markdown("Haz clic derecho sobre el gráfico y selecciona **'Guardar como imagen'**.")
