import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuración básica de la página ---
# Esto le da un aspecto más profesional, ocupando todo el ancho de la pantalla
st.set_page_config(page_title="Amazon Dashboard", page_icon="📦", layout="wide")

# --- 2. Título y subtítulo llamativos con emojis ---
st.title("📦📈 Explorador de Acciones de AMAZON (2020-2025) 🚀💸")
st.markdown("### *Descubre las tendencias financieras, el volumen de operaciones y cómo impactan los eventos clave en el mercado* 📊🔥")
st.markdown("---")

# --- 1. Cargar los datos ---
# Usamos @st.cache_data para que la aplicación no recargue el CSV cada vez que movemos un filtro
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data/datos.csv")
    df['Fecha'] = pd.to_datetime(df['Fecha']) # Convertimos la columna a formato fecha
    return df

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("🚨 No se pudo encontrar el archivo 'data/datos.csv'. ¡Verifica que la carpeta y el archivo existan!")
    st.stop()

# --- 4. Filtros interactivos ---
st.sidebar.header("Filtros de Búsqueda 🔍")

# Filtro 1: Dropdown (Multiselect) para el Trimestre
trimestres_unicos = df['Trimestre'].unique().tolist()
trimestre_seleccionado = st.sidebar.multiselect(
    "Selecciona el Trimestre (Q):",
    options=trimestres_unicos,
    default=trimestres_unicos # Por defecto seleccionamos todos
)

# Filtro 2: Checkbox para Tendencia Alcista
solo_alcistas = st.sidebar.checkbox("Mostrar SOLO días con Tendencia Alcista 📈", value=False)

# Aplicar los filtros al DataFrame
df_filtrado = df[df['Trimestre'].isin(trimestre_seleccionado)]

if solo_alcistas:
    df_filtrado = df_filtrado[df_filtrado['Tendencia_Alcista'] == True]

# Mensaje de seguridad por si filtramos demasiado y nos quedamos sin datos
if df_filtrado.empty:
    st.warning("No hay datos que coincidan con los filtros seleccionados. 😅 Intenta cambiar tus opciones.")
    st.stop()

# --- 3. Checkbox para mostrar vista previa de los datos ---
if st.checkbox("👀 Mostrar vista previa de los datos filtrados (Primeras 10 filas)"):
    st.dataframe(df_filtrado.head(10), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True) # Espaciado

# --- 5 y 6. Tres gráficos interactivos con Plotly Express usando el ancho completo ---
# Dividimos la pantalla en 2 columnas para los primeros dos gráficos
col1, col2 = st.columns(2)

with col1:
    # Gráfico 1: Gráfico de Barras Verticales
    st.subheader("📊 Volumen de Transacciones por Evento")
    # Agrupamos los datos para ver la suma total de volumen por evento en los filtros actuales
    df_bar = df_filtrado.groupby('Evento_Clave', as_index=False)['Volumen_Transacciones'].sum()
    
    fig_bar = px.bar(
        df_bar,
        x='Evento_Clave',
        y='Volumen_Transacciones',
        color='Evento_Clave',
        text_auto='.2s',
        template='plotly_white'
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    # Gráfico 2: Gráfico circular (Donut chart)
    st.subheader("🍩 Distribución del Sentimiento del Mercado")
    
    fig_pie = px.pie(
        df_filtrado,
        names='Sentimiento_Mercado',
        values='Volumen_Transacciones',
        hole=0.4, # Esto lo convierte en una "dona"
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

# Gráfico 3: Histograma (Ocupa todo el ancho en la parte inferior)
st.markdown("---")
st.subheader("📉 Frecuencia de los Precios de Cierre")

fig_hist = px.histogram(
    df_filtrado,
    x='Precio_Cierre',
    nbins=20,
    color='Trimestre', # Diferenciamos por trimestre
    marginal='box',    # Agrega un boxplot arribita para más detalle
    template='plotly_white',
    labels={'Precio_Cierre': 'Precio de Cierre ($)'}
)
fig_hist.update_layout(yaxis_title="Frecuencia (Cantidad de Días)")
st.plotly_chart(fig_hist, use_container_width=True)