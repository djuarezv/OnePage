import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime

df = pd.read_excel("D:/Cobranza/Streamlit/Resources/Data/op_sl_sem43.xlsx", sheet_name = "graficas")
df.fillna(0, inplace=True)
df = df.drop(["semana", "n_reestructuras"], axis=1)
df["dictamen"] = df[["Promesas", "Vía de solución", "Negativa Fraude", "No localizado"]].values.tolist()
df = df.drop(columns = ["Promesas", "Vía de solución", "Negativa Fraude", "No localizado"])

df["pagos_cumplidos"] = df[["pago_parcial", "al_coriente", "liquidados", "monto_reestructuras"]].values.tolist()
df = df.drop(columns = ["pago_parcial", "al_coriente", "liquidados", "monto_reestructuras"])

tipo_dictamen = ["Promesas", "Vía de Solución", "Negativa Fraude", "No Localizada"]

tipo_pagocum = ["Pago Parcial", "Al corriente", "Liquidación", "Reestructura"]

def semana_label(fecha=None):
    fecha = fecha or datetime.now()
    iso_year, iso_week, _ = fecha.isocalendar()
    semana = datetime.now().strftime("%Y%m%d")
    return f"{iso_year}Sem{iso_week:02d}"

semana = semana_label()

# Colores y estilo
texto_color = "white"
barra_color_dictamen = "skyblue"

for _, row in df.iterrows():
    nombre = row["nombre"]
    nombre_cobrador = nombre.replace(" ", "")

    # Gráfico de dictamen
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(tipo_dictamen, row["dictamen"], color=barra_color_dictamen)
    ax.set_title("Dictamen", color=texto_color)
    ax.tick_params(colors=texto_color)
    ax.spines['bottom'].set_color(texto_color)
    ax.spines['left'].set_color(texto_color)
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    plt.xticks(rotation=20, ha="right", fontsize=12, color=texto_color)
    plt.yticks(color=texto_color)
    plt.tight_layout()
    plt.savefig(f"D:/Cobranza/Streamlit/Resources/Visualizations/{semana}_{nombre_cobrador}_dictamen.png", transparent = True, dpi = 400)
    plt.close()

    # Tabla de pagos cumplidos 
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axis('off')

    tabla_data = [[tipo_pagocum[i], row["pagos_cumplidos"][i]] for i in range(4)]
    tabla = ax.table(cellText=tabla_data,
                     colWidths=[0.5, 0.5],
                     cellLoc='center',
                     loc='center')

    tabla.scale(1.5, 2)
    for key, cell in tabla.get_celld().items():
        cell.set_edgecolor(texto_color)
        cell.set_text_props(color=texto_color)
        cell.set_facecolor('none')
        cell.set_fontsize(14)

    plt.savefig(f"D:/Cobranza/Streamlit/Resources/Visualizations/{semana}_{nombre_cobrador}_pagoscumpli.png", transparent = True, dpi = 400)
    plt.close()
