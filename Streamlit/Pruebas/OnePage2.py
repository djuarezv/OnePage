# dashboard_cobradores_corregido.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from PIL import Image
import os
import base64

def generar_medalla(valor, meta, margen=0.05, es_porcentaje=True):
    """
    Devuelve un pequeño círculo de color dependiendo de la comparación entre valor y meta.
    - Verde: >= meta
    - Amarillo: dentro del margen de tolerancia
    - Rojo: por debajo del margen
    
    Si es_porcentaje=False, no se multiplica por 100 ni se agrega '%'.
    """
    if valor is None or pd.isna(valor):
        return ""

    # Definir colores según desempeño
    if valor >= meta:
        color = "#32CD32"  # verde
    elif valor >= meta * (1 - margen):
        color = "#FFD700"  # amarillo
    else:
        color = "#FF4C4C"  # rojo

    # Formato del texto
    if es_porcentaje:
        texto = f"{valor*100:.1f}%"
    else:
        texto = f"{valor:.0f}"

    # HTML del círculo + texto
    return f"""<span style="display:inline-flex; align-items:center; gap:4px;">
        <span style="width:10px; height:10px; border-radius:50%; background-color:{color}; display:inline-block;"></span>
        <span>{texto}</span>
    </span>"""


def semana_label(fecha=None):
    fecha = fecha or datetime.now()
    iso_year, iso_week, _ = fecha.isocalendar()
    semana = datetime.now().strftime("%Y%m%d")
    return f"{iso_year}Sem{iso_week:02d}"

def image_to_base64(path):
    try:
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    except FileNotFoundError:
        return "https://via.placeholder.com/72x72.png?text=Sin+Foto"    



df = pd.read_csv("D:/Cobranza/Streamlit/Resources/Data/one_page_sem42.csv")

df.fillna(0, inplace=True)

# Limpiar columna "motos"
df["motos"] = df["motos"].apply(
    lambda x: int(x.split()[1]) if isinstance(x, str) and len(x.split()) > 1 else None
)

# Renombrar
df.rename(columns={"meta": "logros_meta"}, inplace=True)

# Crear columna sin espacios (para construir nombres de archivo)
df["nombre_junto"] = df["nombre"].str.replace(" ", "", regex=False)

# Generar rutas de fotos
df["foto"] = "D:/Cobranza/Streamlit/Resources/Photos/" + df["nombre_junto"] + "Pic.png"

df["foto_b64"] = df["foto"].apply(image_to_base64)

st.dataframe(df)

# ---------------------------------------------------------------------

# ---------- Configuración de página ----------
st.set_page_config(page_title="One Page - Cobranza", layout="wide")

# ---------- CSS ----------
with open("D:/Cobranza/Streamlit/Resources/CSS/estilos.css") as f:
    css = f.read()

st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ---------- HEADER con título y logo ----------

col1, col2 = st.columns([6,1])
with col1:
    st.markdown(f"""
        <h2 style='color:white; margin-bottom:2px;'>One Page - Cobranza &nbsp; 
            <small style='color:#d0d7ff'>{datetime.now().strftime('%d/%m/%Y')}</small>
        </h2>
        <div style="font-size:12px; color:#bfcfe8; margin-top:2px;">
            Gerencia: Metro &nbsp;&nbsp;|&nbsp;&nbsp; Canal: Presencial
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.image("D:/Cobranza/Streamlit/Resources/Logos/Logo_Fincomun.png", width=240)

st.warning("⚠️ Las medallas están basadas en el rendimiento individual del coordinador. ")

# ---------- FILTROS ----------
st.markdown('<div class="filtro-label">Zona:</div>', unsafe_allow_html=True)
zonas_unicas = ["Todas"] + sorted(df["zona"].unique().tolist())
zona_seleccionada = st.selectbox("", zonas_unicas, accept_new_options=False, disabled=True)

if zona_seleccionada == "Todas":
    df_filtrado = df.copy()
else:
    df_filtrado = df[df["zona"] == zona_seleccionada]

# ---------- FILTRO DE SEMANAS ----------
semanas_disponibles = sorted(df_filtrado["semana"].unique().tolist())

# Selección con valor por defecto (últimas 4 semanas si hay suficientes)
default_weeks = semanas_disponibles[-4:] if len(semanas_disponibles) >= 4 else semanas_disponibles
semanas_seleccionadas = st.multiselect(
    "Selecciona semanas",
    semanas_disponibles,
    default=default_weeks,
    disabled=True
)

# Validación: máximo 4 semanas
if len(semanas_seleccionadas) > 4:
    st.markdown(
        """
        <div style="
            background-color:#1F2A44;
            color:#FFD700;
            padding:8px 12px;
            border-radius:6px;
            border:1px solid #FFD700;
            margin-top:6px;
            font-weight:600;
        ">
            ⚠️ Solo puedes seleccionar <strong>hasta 4 semanas</strong>.
        </div>
        """,
        unsafe_allow_html=True
    )
    semanas_seleccionadas = semanas_seleccionadas[:4]

# Si no seleccionan ninguna, mostramos todas o prevenimos error
if not semanas_seleccionadas:
    semanas_seleccionadas = default_weeks

# Aplicar filtro correctamente
df_filtrado = df_filtrado[df_filtrado["semana"].isin(semanas_seleccionadas)]

# ---------- Calcular promedio por cobrador y ordenar ----------
promedios = df_filtrado.groupby("nombre")["logros_meta"].mean()
# Aseguramos que todos los cobradores tienen un promedio (si no hay filas, evitar KeyError)
promedios = promedios.fillna(0)
orden = promedios.sort_values(ascending=False).index.tolist()

# ---------- Mostrar número de cobradores y tabla de debug (opcional) ----------
st.write(f"Coordinadores mostrados: {len(orden)}")
# st.dataframe(df_filtrado)   # descomenta si quieres ver la tabla filtrada

# ---------- Plantilla HTML de tarjeta (placeholders) ----------
tarjeta_template = """<div class="cobrador-card">
  <div class="card-left">
    __FOTO__
    <div class="card-text">
      <div style="font-weight:700; font-size:18px;">__NOMBRE__</div>
      <div class="small-muted">Zona: __ZONA__</div>
      <div class="small-muted">__EXPERIENCIA__</div>
      <div class="small-muted">Motos: __MOTOS__</div>
    </div>
  </div>
  <div class="card-center">
    <div class="semana-container">
      <div class="semana-header">
        <div>Semana</div>
        <div>Plantilla</div>
        <div>Horas de Visita</div>
        <div>Visitas Totales</div>
        <div>Visitas</div>
        <div>Contacto</div>
        <div>Promesas / Contacto</div>
        <div>Promesas Cumplidas</div>
        <div>Monto Cobrado</div>
        <div>Logro META</div>
      </div>
      __FILAS_SEMANAS__
    </div>
    <div class="visualizaciones-container">
      __VISUALIZACIONES__
    </div>
  </div>
</div>"""

# ---------- Calcular promedio por cobrador y ordenar ----------
promedios = df_filtrado.groupby("nombre")["logros_meta"].mean().fillna(0)
orden = promedios.sort_values(ascending=False).index.tolist()

# --------- Guardando último valor registrado en plantilla --------
ultima_plantilla = (
    df_filtrado.sort_values(by=["nombre", "semana"])
    .groupby("nombre")["plantilla_general"]
    .last()
)

# ---------- Calcular metas automáticas por cobrador ----------
# Usamos percentil 75 (ajustable) para fijar metas alcanzables
metas_por_cobrador = {}

metricas = ["plantilla", "contacto", "promesas_contacto", "promesas_cumplidas", "logros_meta"]

for nombre, grupo in df_filtrado.groupby("nombre"):
    metas_por_cobrador[nombre] = {}
    for metrica in metricas:
        if metrica in grupo.columns:
            valores = grupo[metrica].dropna()
            if not valores.empty:
                metas_por_cobrador[nombre][metrica] = np.percentile(valores, 75)  # meta = percentil 75
            else:
                metas_por_cobrador[nombre][metrica] = 0.8  # fallback
        else:
            metas_por_cobrador[nombre][metrica] = 0.8

# ---------- Generar tarjetas en el orden calculado ----------
for nombre in orden:
    datos = df_filtrado[df_filtrado["nombre"] == nombre].sort_values(by="semana", ascending=True)
    if datos.empty:
        continue    
    promedio = promedios.get(nombre, 0)

    # Foto: usar imagen si existe, si no, inicial del nombre en círculo
    foto_html = ""
    foto_url = datos["foto_b64"].iloc[0]
    if isinstance(foto_url, str) and foto_url.strip():
        foto_html = f'<img src="{foto_url}" alt="foto">'
    else:
        inicial = nombre.strip()[0].upper() if nombre.strip() else "?"
        foto_html = f'<div style="width:72px; height:72px; border-radius:50%; background:#1f77b4; display:flex; align-items:center; justify-content:center; font-weight:700; color:white;">{inicial}</div>'

    # Dictamen
    avg_monto = datos["monto"].mean() if "monto" in datos.columns else 0
    dictamen_pct = min(int((avg_monto / max(avg_monto, 1)) * 80) + 20, 100)  # ejemplo entre 20 y 100

    # ---- Cálculos de resumen por cobrador ----
    summary = {
        "plantilla": ultima_plantilla.get(nombre, None),
        "horas_visita": datos["horas_visita"].mean() if "horas_visita" in datos.columns else 0,
        "visitas_totales": datos["visitas_totales"].mean() if "visitas_totales" in datos.columns else 0,
        "visitas": datos["visitas"].mean() if "visitas" in datos.columns else 0,
        "contacto": datos["contacto"].mean() if "contacto" in datos.columns else 0,
        "promesas_contacto": datos["promesas_contacto"].mean() if "promesas_contacto" in datos.columns else 0,
        "promesas_cumplidas": datos["promesas_cumplidas"].mean() if "promesas_cumplidas" in datos.columns else 0,
        "monto": datos["monto"].mean() if "monto" in datos.columns else 0,
        "logros_meta": datos["logros_meta"].mean() if "logros_meta" in datos.columns else 0,
    }

    # ---- Fila de resumen ----
    plantilla_valor = summary["plantilla"] if summary["plantilla"] is not None else "-"
    summary_html = f"""<div class="semana-summary">
        <div>Promedios</div>
        <div>{plantilla_valor}</div>
        <div>{summary['horas_visita']:.1f}</div>
        <div>{summary['visitas_totales']:.1f}</div>
        <div>{summary['visitas']:.1f}</div>
        <div>{summary['contacto']*100:.1f}%</div>
        <div>{summary['promesas_contacto']*100:.1f}%</div>
        <div>{summary['promesas_cumplidas']*100:.1f}%</div>
        <div>${int(summary['monto']):,}</div>
        <div>{summary['logros_meta']*100:.1f}%</div>
    </div>"""

    # ---- Construcción de las filas de semanas ----
    filas = summary_html
    for _, fila in datos.iterrows():
        semana = fila.get("semana", "")
        plantilla = fila.get("plantilla", "")
        horas_visita = fila.get("horas_visita", "")
        visitas_totales = fila.get("visitas_totales", "")
        visitas = fila.get("visitas", "")
        contacto = fila.get("contacto", "")
        promesas_contacto = fila.get("promesas_contacto", "")
        promesas_cumplidas = fila.get("promesas_cumplidas", "")
        logro = fila.get("logros_meta", "")
        monto = fila.get("monto", 0)

        # Obtener metas automáticas
        metas = metas_por_cobrador.get(nombre, {})
        visitas_html = generar_medalla(visitas, metas.get("visitas", 80), es_porcentaje=False)
        plantilla_html = generar_medalla(plantilla, metas.get("plantilla", 0.8))
        contacto_html = generar_medalla(contacto, metas.get("contacto", 0.8))
        promesas_contacto_html = generar_medalla(promesas_contacto, metas.get("promesas_contacto", 0.8))
        promesas_cumplidas_html = generar_medalla(promesas_cumplidas, metas.get("promesas_cumplidas", 0.8))
        logro_html = generar_medalla(logro, metas.get("logros_meta", 0.8))

        monto_str = f"${int(monto):,}" if not pd.isna(monto) else "-"

        filas += f"""<div class="semana-row">
            <div>{semana}</div>
            <div>{plantilla_html}</div>
            <div>{horas_visita:.1f}</div>
            <div>{visitas_totales:.0f}</div>
            <div>{visitas_html}</div>
            <div>{contacto_html}</div>
            <div>{promesas_contacto_html}</div>
            <div>{promesas_cumplidas_html}</div>
            <div>{monto_str}</div>
            <div>{logro_html}</div>
        </div>"""

    # ---- Render final ----
    tarjeta_html = tarjeta_template.replace("__FOTO__", foto_html)\
                                   .replace("__NOMBRE__", nombre)\
                                   .replace("__ZONA__", str(datos["zona"].iloc[0]))\
                                   .replace("__EXPERIENCIA__", str(datos["experiencia"].iloc[0]) if "experiencia" in datos.columns else "")\
                                   .replace("__MOTOS__", str(datos["motos"].iloc[0]) if "motos" in datos.columns else "")\
                                   .replace("__PROMEDIO__", f"{promedio:.1f}")\
                                   .replace("__DICTAMEN__", str(dictamen_pct))\
                                   .replace("__FILAS_SEMANAS__", filas)

    cobrador_nombre = nombre.replace(" ", "")
    tipos_grafico = ["dictamen", "pagoscumpli"]

    semana = semana_label()

    grafico_html = ''
    for tipo in tipos_grafico:
        ruta = f"D:/Cobranza/Streamlit/Resources/Visualizations/{semana}_{cobrador_nombre}_{tipo}.png"
        if os.path.exists(ruta):
            with open(ruta, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            grafico_html += f'''<div class="grafico" style="margin-top:8px">
                                    <img src="data:image/png;base64,{img_base64}" style="width:100%; height:300px; object-fit:contain;">
                                </div>'''
        else:
            print(f"No se encontró: {ruta}")

    tarjeta_html = tarjeta_html.replace("__VISUALIZACIONES__", grafico_html)
    st.markdown(tarjeta_html, unsafe_allow_html=True)