# dashboard_cobradores_corregido.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from PIL import Image
import os
import base64
from jinja2 import Template
import openpyxl

def generar_medalla(valor, tipo="porcentaje"):
    """
    Genera una medalla (círculo de color) según reglas definidas por tipo de dato.
    
    Parámetros:
    - valor: número o porcentaje (0–1 o número grande)
    - tipo: 'porcentaje', 'monto', 'visitas', 'plantilla', etc.
    
    Devuelve: HTML con círculo verde, amarillo o rojo según rango.
    """
    tipo2 = ""
    if valor is None or pd.isna(valor):
        return ""
    # Si es porcentaje en formato decimal, lo pasamos a 0–100
    if valor <= 1 and valor >= 0:
        val = valor * 100
        tipo2 = "porcentaje"
    else:
        val = valor
    # Reglas por tipo
    reglas = {
        "contacto": {
            "verde": lambda v: v >= 65,
            "amarillo": lambda v: 40 <= v < 65,
            "rojo": lambda v: v < 40
        },
        "promesas_cumplidas": {
            "verde": lambda v: v >= 60,
            "amarillo": lambda v: 40 <= v < 60,
            "rojo": lambda v: v < 40
        },
        "logro_meta": {
            "verde": lambda v: v >= 70,
            "amarillo": lambda v: 50 <= v < 70,
            "rojo": lambda v: v < 50
        },
        "visitas": {
            "verde": lambda v: v >= 15,
            "amarillo": lambda v: 10 <= v < 15,
            "rojo": lambda v: v < 10
        },
        "plantilla": {
            "verde": lambda v: v >= 90,
            "amarillo": lambda v: 80 <= v < 90,
            "rojo": lambda v: v < 80
        }
    }
    # Determinar color según las reglas
    if tipo in reglas:
        if reglas[tipo]["verde"](val):
            color = "#32CD32"  # verde
        elif reglas[tipo]["amarillo"](val):
            color = "#FFD700"  # amarillo
        else:
            color = "#FF4C4C"  # rojo
    else:
        color = "#808080"  # gris por defecto
    # Formato del valor mostrado
    texto_valor = f"{val:.1f}%" if tipo2 == "porcentaje" else f"{int(val):,}"
    # HTML del círculo + valor
    return f"""<span style="display:inline-flex; align-items:center; gap:4px;">
        <span style="width:10px; height:10px; border-radius:50%; background-color:{color}; display:inline-block;"></span>
        <span>{texto_valor}</span>
    </span>"""

def semana_label(fecha=None):
    fecha = fecha or datetime.now()
    iso_year, iso_week, _ = fecha.isocalendar()
    semana = datetime.now().strftime("%Y%m%d")
    return f"{iso_year}Sem{iso_week-1:02d}"

def image_to_base64(path):
    try:
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    except FileNotFoundError:
        return "https://via.placeholder.com/72x72.png?text=Sin+Foto" 

@st.cache_data
def load_visualizations(nombre, semana):
    tipos = ["dictamen", "pagoscumpli"]
    visuales = []
    for tipo in tipos:
        ruta = f"D:/Cobranza/Streamlit/Resources/Visualizations/{semana}/{nombre}_{tipo}.png"
        if os.path.exists(ruta):
            img_b64 = image_to_base64(ruta)
            visuales.append(f'''<div class="grafico">
                                <img src="{img_b64}" style="width:100%; height:300px; object-fit:contain;">
                            </div>''')
    return "".join(visuales)

@st.cache_data
def load_data(path):
    df = pd.read_excel(path, sheet_name="one_page", engine="openpyxl")
    df.fillna(0, inplace=True)
    df["motos"] = df["motos"].apply(lambda x: int(x.split()[1]) if isinstance(x, str) and len(x.split()) > 1 else None)
    df.rename(columns={"meta": "logros_meta"}, inplace=True)
    df["nombre_junto"] = df["nombre"].str.replace(" ", "", regex=False)
    df["foto"] = "D:/Cobranza/Streamlit/Resources/Photos/" + df["nombre_junto"] + "Pic.png"
    df["foto_b64"] = df["foto"].apply(image_to_base64)
    return df

df = load_data("D:/Cobranza/Streamlit/Resources/Data/op_sl_sem43.xlsx")


# ---------------------------------------------------------------------

# ---------- Configuración de página ----------
st.set_page_config(page_title="One Page - Cobranza", layout="wide")

# ---------- CSS ----------
with open("D:/Cobranza/Streamlit/Resources/CSS/estilos.css") as f:
    css = f.read()

st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ---------- HEADER superior institucional ----------

logo_fincobranza = image_to_base64("D:/Cobranza/Streamlit/Resources/Logos/Logo_Fincomun.png")

header_html = f"""<div class="header-institucional" style="
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #ffffff;
    color: #000000;
    padding: 10px 20px;
    border: 2px solid #0033cc;
    border-radius: 4px;
    box-shadow: 0 0 6px rgba(0,0,0,0.1);
">
    <div style="display: flex; align-items: center; gap: 10px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" viewBox="0 0 24 24" fill="#2a6ee8">
          <path d="M2 4l8 8-8 8V4zm7 0l8 8-8 8V4zm7 0l8 8-8 8V4z"/>
        </svg>
        <div style="display: flex; flex-direction: column; line-height: 1.1;">
            <span style="font-weight: 700; font-size: 20px;">One Page</span>
            <span style="color:#2a6ee8; font-size: 14px;">COBRANZA</span>
        </div>
    </div>
    <div style="text-align: center;">
        <img src="{logo_fincobranza}" alt="Logo FinCobranza" style="height: 56px;">
    </div>
    <div style="text-align: right; font-size: 14px; line-height: 1.4;">
        <div><strong>Gerencia:</strong> Zona Metro</div>
        <div><strong>Canal:</strong> Presencial</div>
    </div>
</div>"""
st.markdown(header_html, unsafe_allow_html=True)

# ---------- FILTROS AUTOMÁTICOS (versión estática) ----------

# Mostramos solo una etiqueta informativa (sin filtro real)
#st.markdown('<div class="filtro-label">Zona: <span style="color:#9DB8FF;">Todas</span></div>', unsafe_allow_html=True)

# Por ahora siempre se usa todo el DF
df_filtrado = df.copy()

# ---------- FILTRO AUTOMÁTICO DE SEMANAS ----------

# Tomamos las semanas disponibles en los datos
semanas_disponibles = sorted(df_filtrado["semana"].unique().tolist())

# Seleccionamos automáticamente las últimas 4 (o todas si hay menos)
semanas_seleccionadas = semanas_disponibles[-4:] if len(semanas_disponibles) >= 4 else semanas_disponibles

# Filtramos el DF en memoria
df_filtrado = df_filtrado[df_filtrado["semana"].isin(semanas_seleccionadas)]


# ---------- Calcular promedio por cobrador y ordenar ----------
promedios = df_filtrado.groupby("nombre")["logros_meta"].mean()
# Aseguramos que todos los cobradores tienen un promedio (si no hay filas, evitar KeyError)
promedios = promedios.fillna(0)
orden = promedios.sort_values(ascending=False).index.tolist()

# ---------- Mostrar número de cobradores y tabla de debug (opcional) ----------
st.write(f"Coordinadores mostrados: {len(orden)}")

# ---------- Plantilla HTML de tarjeta ----------

with open("D:/Cobranza/Streamlit/Resources/Templates/tarjeta.html", "r", encoding="utf-8") as f:
    tarjeta_template = Template(f.read())

# ---------- Calcular promedio por cobrador y ordenar ----------
promedios = df_filtrado.groupby("nombre")["logros_meta"].mean().fillna(0)
orden = promedios.sort_values(ascending=False).index.tolist()

# --------- Guardando último valor registrado en plantilla --------
ultima_plantilla = (
    df_filtrado.sort_values(by=["nombre", "semana"])
    .groupby("nombre")["plantilla_general"]
    .last()
)

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
        "visitas": "15 X ERE",
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
        <div>{summary['visitas']}</div>
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
        visitas_html = generar_medalla(visitas, tipo="visitas")
        plantilla_html = generar_medalla(plantilla, tipo="plantilla")
        contacto_html = generar_medalla(contacto, tipo="contacto")
        promesas_contacto_html = generar_medalla(promesas_contacto, tipo="contacto")
        promesas_cumplidas_html = generar_medalla(promesas_cumplidas, tipo="promesas_cumplidas")
        logro_html = generar_medalla(logro, tipo="logro_meta")

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
    cobrador_nombre = nombre.replace(" ", "")
    tipos_grafico = ["dictamen", "pagoscumpli"]

    semana = semana_label()
    grafico_html = load_visualizations(cobrador_nombre, semana)

    tarjeta_html = tarjeta_template.render(
        nombre=nombre,
        zona=str(datos["zona"].iloc[0]),
        experiencia=str(datos["experiencia"].iloc[0]) if "experiencia" in datos.columns else "",
        motos=str(datos["motos"].iloc[0]) if "motos" in datos.columns else "",
        promedio=f"{promedio:.1f}",
        dictamen = str(dictamen_pct),
        filas=filas,
        foto=foto_html,
        visualizaciones=grafico_html
    )

    st.markdown(tarjeta_html, unsafe_allow_html=True)
