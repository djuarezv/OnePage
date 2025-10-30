import streamlit as st
import pandas as pd
import numpy as np
import random

# --------------------------
# SIMULACIÓN DE DATOS
# --------------------------
cobradores = ["Ana", "Luis", "Carlos", "María", "Jorge", "Beatriz"]
zonas = ["Norte", "Sur", "Centro"]
semanas = ["Semana 1", "Semana 2", "Semana 3", "Semana 4"]

# Crear dataframe simulado
data = []
for cobrador in cobradores:
    zona = random.choice(zonas)
    for semana in semanas:
        data.append({
            "Cobrador": cobrador,
            "Zona": zona,
            "Semana": semana,
            "Logro_META": round(random.uniform(70, 120), 2),
            "Cartera_Asignada": random.randint(100000, 250000),
            "Monto_Recuperado": random.randint(70000, 240000),
            "Clientes_Atendidos": random.randint(30, 80)
        })
df = pd.DataFrame(data)

# --------------------------
# CONFIGURACIÓN DE PÁGINA
# --------------------------
st.set_page_config(page_title="Dashboard de Cobranza", layout="wide")

st.markdown("""
    <style>
    body { background-color: #0e1117; color: white; }
    .titulo { text-align: center; font-size: 30px; font-weight: bold; margin-bottom: 30px; }
    .filtro-label { font-size: 18px; margin-bottom: 5px; }
    .cobrador-card {
        background-color: white;
        color: black;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 8px rgba(255, 255, 255, 0.1);
        justify-content: space-between;
    }
    .cobrador-info {
        flex: 3;
        padding-left: 15px;
    }
    .cobrador-nombre {
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .semana-label {
        text-align: center;
        font-size: 20px;
        margin-top: 20px;
        font-weight: 600;
    }
    .indicadores {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        text-align: center;
        font-size: 14px;
        gap: 10px;
    }
    .foto {
        border-radius: 50%;
        width: 90px;
        height: 90px;
        background-color: #1f77b4;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        font-size: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------
# TÍTULO
# --------------------------
st.markdown('<div class="titulo">📊 Dashboard de Cobranza</div>', unsafe_allow_html=True)

# --------------------------
# FILTROS
# --------------------------
st.markdown('<div class="filtro-label">Zona:</div>', unsafe_allow_html=True)
zonas_unicas = ["Todas"] + sorted(df["Zona"].unique().tolist())
zona_seleccionada = st.selectbox("", zonas_unicas)

# Filtrar dataframe según zona
if zona_seleccionada != "Todas":
    df_filtrado = df[df["Zona"] == zona_seleccionada]
else:
    df_filtrado = df.copy()

# --------------------------
# ORDEN SEGÚN PROMEDIO LOGRO META
# --------------------------
ranking = df_filtrado.groupby("Cobrador")["Logro_META"].mean().sort_values(ascending=False)
df_filtrado["Promedio_Logro"] = df_filtrado["Cobrador"].map(ranking)
df_filtrado = df_filtrado.sort_values("Promedio_Logro", ascending=False)

# --------------------------
# CREAR TARJETAS
# --------------------------
for cobrador in df_filtrado["Cobrador"].unique():
    datos_cobrador = df_filtrado[df_filtrado["Cobrador"] == cobrador]
    promedio = datos_cobrador["Logro_META"].mean()

    # Tarjeta HTML
    tarjeta_html = f"""
    <div class="cobrador-card">
        <div class="foto">{cobrador[0]}</div>
        <div class="cobrador-info">
            <div class="cobrador-nombre">{cobrador}</div>
            <div>Zona: {datos_cobrador['Zona'].iloc[0]}</div>
            <div>Promedio Logro META: <b>{promedio:.2f}%</b></div>
            <hr>
            <div class="indicadores">
    """

    # Agregar cada semana como fila
    for _, fila in datos_cobrador.iterrows():
        tarjeta_html += f"""
            <div><b>{fila['Semana']}</b><br>Meta: {fila['Logro_META']}%</div>
            <div>Cartera: ${fila['Cartera_Asignada']:,}</div>
            <div>Recuperado: ${fila['Monto_Recuperado']:,}</div>
            <div>Clientes: {fila['Clientes_Atendidos']}</div>
        """

    tarjeta_html += """
            </div>
        </div>
    </div>
    """

    st.markdown(tarjeta_html, unsafe_allow_html=True)
