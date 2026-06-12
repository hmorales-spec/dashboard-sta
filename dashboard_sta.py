import io
import html
import os
from datetime import datetime, date

import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials


st.set_page_config(
    page_title="Dashboard STA",
    layout="wide"
)


# --------------------------------------------------
# CONFIGURACIÓN DE ARCHIVOS
# --------------------------------------------------

CARPETA_DATA = "data"
ARCHIVO_HISTORICO = os.path.join(CARPETA_DATA, "historico_sta.csv")

os.makedirs(CARPETA_DATA, exist_ok=True)


# --------------------------------------------------
# COLORES ESTADOS
# --------------------------------------------------

COLOR_ESTADOS = {
    "Normal": "#2E7D32",
    "Seguimiento": "#1976D2",
    "Atrasado": "#F9A825",
    "Crítico": "#C62828",
}


# --------------------------------------------------
# ESTILO VISUAL
# Versión v16.7 final con iconografía sobria y fondo técnico sutil
# --------------------------------------------------

st.markdown(
    """
    <style>
        :root {
            --bg-app: #F4F6F8;
            --surface: #FFFFFF;
            --surface-soft: #F7F9FC;
            --text-main: #111827;
            --text-muted: #6B7280;
            --border: #DDE3EA;
            --navy: #123047;
            --navy-2: #1E425D;
            --blue: #1976D2;
            --green: #2E7D32;
            --amber: #F59E0B;
            --red: #C62828;
        }

        .stApp {
            background: var(--bg-app);
        }

        .main .block-container {
            padding-top: 0rem;
            padding-bottom: 2.5rem;
            max-width: 1520px;
        }

        [data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: var(--text-main);
        }

        .main-title {
            background: linear-gradient(90deg, var(--navy) 0%, var(--navy-2) 100%);
            padding: 13px 22px;
            border-radius: 11px;
            color: white;
            margin-top: -2.25rem;
            margin-bottom: 12px;
            border: 1px solid rgba(255,255,255,0.12);
            box-shadow: 0 2px 7px rgba(17,24,39,0.08);
        }

        .main-title h1 {
            margin: 0;
            font-size: 27px;
            line-height: 1.05;
            letter-spacing: -0.02em;
            font-weight: 850;
        }

        .main-title p {
            margin: 5px 0 0 0;
            font-size: 12.5px;
            opacity: 0.90;
        }

        .title-mark {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            margin-right: 8px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.18);
            color: #FFFFFF;
            font-size: 17px;
            vertical-align: -2px;
        }

        .process-flow {
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
            margin: -3px 0 13px 0;
        }

        .process-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 9px;
            border: 1px solid #D7E5F0;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.82);
            color: var(--navy);
            font-size: 11.5px;
            font-weight: 800;
            box-shadow: 0 1px 2px rgba(15,23,42,0.035);
        }

        .process-chip span {
            color: var(--blue);
            font-size: 12px;
            font-weight: 900;
        }

        .cutoff-strip {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            padding: 9px 12px;
            border: 1px solid var(--border);
            border-left: 5px solid var(--navy);
            border-radius: 11px;
            background: var(--surface);
            color: var(--text-main);
            margin: 7px 0 12px 0;
            box-shadow: 0 1px 3px rgba(15,23,42,0.05);
            font-size: 13px;
            font-weight: 600;
        }

        .cutoff-pill {
            display: inline-block;
            background: #EEF4FA;
            color: var(--navy);
            border: 1px solid #D7E5F0;
            border-radius: 999px;
            padding: 3px 9px;
            font-size: 12px;
            font-weight: 800;
        }

        .section-title-wrap {
            margin: 20px 0 10px 0;
            padding: 0 0 0 11px;
            border-left: 5px solid var(--navy);
        }

        .section-title-wrap h3 {
            margin: 0;
            color: var(--text-main);
            font-size: 21px;
            line-height: 1.1;
            font-weight: 850;
            letter-spacing: -0.01em;
        }

        .section-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 25px;
            height: 25px;
            margin-right: 8px;
            border-radius: 8px;
            background: #EEF4FA;
            border: 1px solid #D7E5F0;
            color: var(--navy);
            font-size: 14px;
            vertical-align: -3px;
        }

        .section-title-wrap p {
            margin: 4px 0 0 0;
            color: var(--text-muted);
            font-size: 13px;
            line-height: 1.35;
        }

        .module-note {
            color: var(--text-muted);
            font-size: 13px;
            margin-top: -2px;
            margin-bottom: 8px;
        }

        .kpi-card {
            padding: 13px 15px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background-color: var(--surface);
            box-shadow: 0 1px 4px rgba(15,23,42,0.05);
            min-height: 108px;
        }

        .kpi-title {
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 7px;
            font-weight: 800;
            line-height: 1.25;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }

        .kpi-head-row {
            display: flex;
            align-items: center;
            gap: 7px;
            margin-bottom: 7px;
        }

        .kpi-head-row .kpi-title {
            margin-bottom: 0;
        }

        .kpi-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 24px;
            width: 24px;
            height: 24px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 900;
            background: #F1F5F9;
            color: var(--navy);
            border: 1px solid #D7E5F0;
        }

        .green-card .kpi-icon { color: var(--green); background: #F1FAF3; border-color: #CFEBD6; }
        .blue-card .kpi-icon { color: var(--blue); background: #F1F7FF; border-color: #D6E8FF; }
        .orange-card .kpi-icon { color: #A16207; background: #FFF8E6; border-color: #FDE7B0; }
        .red-card .kpi-icon { color: var(--red); background: #FFF1F1; border-color: #F4C7C7; }

        .kpi-value {
            font-size: 28px;
            font-weight: 900;
            color: var(--text-main);
            line-height: 1.05;
            letter-spacing: -0.03em;
        }

        .kpi-note {
            font-size: 12px;
            margin-top: 7px;
            color: #4B5563;
            line-height: 1.35;
            font-weight: 600;
        }

        .green-card { border-left: 6px solid var(--green); }
        .orange-card { border-left: 6px solid var(--amber); }
        .red-card { border-left: 6px solid var(--red); }
        .blue-card { border-left: 6px solid var(--blue); }

        .postit-card {
            border-radius: 13px;
            padding: 13px 14px;
            margin-bottom: 12px;
            border: 1px solid var(--border);
            background: var(--surface);
            box-shadow: 0 1px 4px rgba(15,23,42,0.05);
        }

        .postit-card.info {
            border-left: 6px solid var(--blue);
            background: #F4F8FD;
        }

        .postit-card.warning {
            border-left: 6px solid var(--amber);
            background: #FFFAEC;
        }

        .postit-card.danger {
            border-left: 6px solid var(--red);
            background: #FFF3F3;
        }

        .postit-card.success {
            border-left: 6px solid var(--green);
            background: #F4FBF6;
        }

        .postit-title {
            font-size: 14px;
            font-weight: 850;
            color: var(--text-main);
            margin-bottom: 5px;
            letter-spacing: -0.01em;
        }

        .postit-text {
            font-size: 13.5px;
            color: #374151;
            line-height: 1.4;
            font-weight: 500;
        }

        .priority-box {
            border: 1px solid var(--border);
            border-left: 7px solid var(--red);
            border-radius: 14px;
            background: var(--surface);
            padding: 13px 15px;
            margin: 10px 0 16px 0;
            box-shadow: 0 1px 5px rgba(15,23,42,0.06);
        }

        .priority-title {
            font-size: 17px;
            font-weight: 900;
            color: var(--text-main);
            margin-bottom: 7px;
            letter-spacing: -0.01em;
        }

        .priority-item {
            font-size: 13px;
            line-height: 1.45;
            margin: 4px 0;
            color: #30343B;
        }

        .priority-label {
            font-weight: 850;
            color: var(--red);
        }

        .sidebar-note {
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.25;
        }

        .section-caption-tight {
            color: var(--text-muted);
            font-size: 13px;
            margin-top: -2px;
            margin-bottom: 8px;
        }

        div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 11px;
            padding: 10px 13px;
            box-shadow: 0 1px 3px rgba(15,23,42,0.04);
        }

        div[data-testid="stMetricLabel"] p {
            color: var(--text-muted);
            font-weight: 800;
            font-size: 12px;
        }

        div[data-testid="stMetricValue"] {
            color: var(--text-main);
            font-weight: 900;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
        }

        .stTabs [data-baseweb="tab"] {
            background: #F1F4F8;
            border-radius: 9px 9px 0 0;
            padding: 7px 11px;
            font-weight: 750;
        }

        .stTabs [aria-selected="true"] {
            background: #FFFFFF !important;
            color: var(--navy) !important;
            border-top: 3px solid var(--navy);
        }


        /* Encabezados de tablas más visibles */
        div[data-testid="stDataFrame"] [role="columnheader"] {
            background-color: var(--navy) !important;
            color: #FFFFFF !important;
            font-weight: 850 !important;
            border-color: #0B2538 !important;
        }

        div[data-testid="stDataFrame"] [role="columnheader"] * {
            color: #FFFFFF !important;
            fill: #FFFFFF !important;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 11px !important;
            overflow: hidden !important;
            border: 1px solid var(--border) !important;
        }

        /* Fallback para tablas HTML generadas por pandas Styler */
        table thead th {
            background-color: var(--navy) !important;
            color: #FFFFFF !important;
            font-weight: 850 !important;
            border-color: #0B2538 !important;
        }

        /* Tablas operativas HTML: encabezado navy real, sticky y filas con semáforo suave */
        .op-table-wrapper {
            width: 100%;
            background: #FFFFFF;
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow-x: auto;
            overflow-y: auto;
            margin: 6px 0 14px 0;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.035);
        }

        .op-table-wrapper table {
            width: 100% !important;
            border-collapse: collapse !important;
            font-size: 12.5px !important;
            color: var(--text-main) !important;
            background: #FFFFFF !important;
            margin: 0 !important;
        }

        .op-table-wrapper thead th,
        .op-table-wrapper table thead tr th,
        .op-table-wrapper table thead th.col_heading,
        .op-table-wrapper table thead th.blank {
            position: sticky !important;
            top: 0 !important;
            z-index: 3 !important;
            background: var(--navy) !important;
            background-color: var(--navy) !important;
            color: #FFFFFF !important;
            font-weight: 850 !important;
            padding: 9px 8px !important;
            border: 1px solid #0B2538 !important;
            text-align: left !important;
            white-space: nowrap !important;
        }

        .op-table-wrapper tbody td,
        .op-table-wrapper table tbody tr td {
            padding: 8px 8px !important;
            border: 1px solid #E5E7EB !important;
            vertical-align: middle !important;
            white-space: nowrap !important;
        }

        .op-table-wrapper tbody tr:hover td {
            filter: brightness(0.985);
        }


        .developer-credit {
            margin-top: 16px;
            padding: 10px 11px;
            border: 1px solid #D7E5F0;
            border-left: 5px solid var(--navy);
            border-radius: 11px;
            background: #F8FAFC;
            color: var(--text-main);
            font-size: 12px;
            line-height: 1.35;
            box-shadow: 0 1px 3px rgba(15,23,42,0.04);
        }

        .developer-credit strong {
            color: var(--navy);
            font-size: 12.5px;
            font-weight: 900;
        }

        .developer-credit span {
            color: var(--text-muted);
            font-weight: 650;
        }

        .app-footer {
            margin-top: 26px;
            padding: 12px 14px 2px 14px;
            border-top: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 12px;
            text-align: center;
            font-weight: 600;
        }

        .app-footer strong {
            color: var(--navy);
            font-weight: 900;
        }


        /* Pulido visual final */
        hr {
            margin: 1.15rem 0 1rem 0 !important;
            border-color: #DDE3EA !important;
        }

        div[data-testid="stPlotlyChart"] {
            background: #FFFFFF;
            border: 1px solid var(--border);
            border-radius: 13px;
            padding: 8px 10px 2px 10px;
            box-shadow: 0 1px 3px rgba(15,23,42,0.035);
        }

        div[data-testid="stExpander"] {
            border: 1px solid var(--border);
            border-radius: 11px;
            background: #FFFFFF;
        }

        div[data-testid="stExpander"] summary {
            font-size: 13px;
            font-weight: 750;
            color: var(--text-main);
        }

        .stButton > button {
            border-radius: 10px;
            border: 1px solid #CBD5E1;
            font-weight: 750;
        }

        .stDownloadButton > button {
            border-radius: 10px;
            font-weight: 800;
        }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="main-title">
        <h1><span class="title-mark">▣</span>Dashboard STA</h1>
        <p>Control Operativo Semanal · Productos en Servicio Técnico Autorizado</p>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# FUNCIONES GENERALES
# --------------------------------------------------

def limpiar_cp(valor):
    if pd.isna(valor):
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()

    if texto == "":
        return 0.0

    texto = (
        texto.replace("$", "")
        .replace("CLP", "")
        .replace("clp", "")
        .replace(" ", "")
        .strip()
    )

    caracteres_validos = "0123456789,.-"
    texto = "".join(c for c in texto if c in caracteres_validos)

    if texto in ["", "-", ".", ","]:
        return 0.0

    try:
        # Formato chileno: 59.618.016,79
        if "." in texto and "," in texto:
            texto = texto.replace(".", "")
            texto = texto.replace(",", ".")
            return float(texto)

        # Formato con coma decimal: 59618016,79
        if "," in texto and "." not in texto:
            partes = texto.split(",")

            if len(partes) == 2 and len(partes[1]) in [1, 2]:
                texto = texto.replace(",", ".")
                return float(texto)

            texto = texto.replace(",", "")
            return float(texto)

        # Formato con puntos: puede ser miles o decimal
        if "." in texto and "," not in texto:
            partes = texto.split(".")

            # Ejemplo: 70.116.656
            if len(partes) > 2:
                texto = texto.replace(".", "")
                return float(texto)

            # Ejemplo: 70.116 debe interpretarse como 70116 si son miles
            if len(partes) == 2 and len(partes[1]) == 3:
                texto = texto.replace(".", "")
                return float(texto)

            # Ejemplo: 70116656.0
            return float(texto)

        return float(texto)

    except Exception:
        return 0.0


def formato_pesos(valor):
    if pd.isna(valor):
        return "$0"

    try:
        numero = float(valor)
    except Exception:
        return "$0"

    signo = "-" if numero < 0 else ""
    numero = int(round(abs(numero), 0))

    return f"{signo}${numero:,.0f}".replace(",", ".")


def formato_numero(valor):
    return f"{valor:,.0f}".replace(",", ".")


def formato_porcentaje(valor):
    return f"{valor * 100:.1f}%".replace(".", ",")


def formato_porcentaje_puntos(valor):
    return f"{float(valor):.1f}%".replace(".", ",")


def normalizar_nombre_persona(valor, valor_vacio="Sin asignar"):
    """Normaliza nombres provenientes de Sphinx a formato legible.

    Ejemplo: 'HUGO ALVAREZ PERALTA' -> 'Hugo Alvarez Peralta'.
    Mantiene iniciales con punto: 'JAVIERA GUTIERREZ C.' -> 'Javiera Gutierrez C.'.
    """
    if pd.isna(valor):
        return valor_vacio

    texto = str(valor).strip()

    if texto == "" or texto.lower() in ["nan", "none"]:
        return valor_vacio

    texto = " ".join(texto.split())
    palabras_normalizadas = []

    for palabra in texto.split(" "):
        palabra_limpia = palabra.strip()

        if palabra_limpia == "":
            continue

        # Iniciales del tipo C. / U. / L.
        if len(palabra_limpia) == 2 and palabra_limpia.endswith("."):
            palabras_normalizadas.append(palabra_limpia[0].upper() + ".")
            continue

        # Palabras normales del nombre/apellido.
        palabras_normalizadas.append(palabra_limpia.lower().capitalize())

    return " ".join(palabras_normalizadas) if palabras_normalizadas else valor_vacio


def porcentaje_puntos(valor, total):
    if total is None or total == 0:
        return 0.0
    return (valor / total) * 100


def preparar_display_pesos(df_base, columnas_pesos=None, columnas_porcentaje=None):
    df_display = df_base.copy()

    if columnas_pesos:
        for columna in columnas_pesos:
            if columna in df_display.columns:
                df_display[columna] = df_display[columna].apply(formato_pesos)

    if columnas_porcentaje:
        for columna in columnas_porcentaje:
            if columna in df_display.columns:
                df_display[columna] = df_display[columna].apply(
                    lambda x: formato_porcentaje_puntos(x) if pd.notna(x) else "0,0%"
                )

    return df_display


COLOR_FONDO_FILAS = {
    "Normal": "#F1FAF3",
    "Seguimiento": "#F1F7FF",
    "Atrasado": "#FFF8E6",
    "Crítico": "#FFF1F1",
}

COLOR_TEXTO_FILAS = {
    "Normal": "#174D27",
    "Seguimiento": "#123A75",
    "Atrasado": "#6B4500",
    "Crítico": "#7F1D1D",
}

TRAMO_A_ESTADO = {
    "0 a 30 días": "Normal",
    "31 a 60 días": "Seguimiento",
    "61 a 120 días": "Atrasado",
    "Más de 120 días": "Crítico",
}


def obtener_estado_visual_fila(fila):
    columnas_estado = [
        "Estado Control",
        "Estado control",
        "Estado actual",
        "Estado Control_actual",
    ]

    for columna in columnas_estado:
        if columna in fila.index:
            valor = str(fila[columna]).strip()
            if valor in COLOR_FONDO_FILAS:
                return valor

    columnas_tramo = [
        "Tramo",
        "Tramo asociado",
        "Tramo_actual",
    ]

    for columna in columnas_tramo:
        if columna in fila.index:
            valor = str(fila[columna]).strip()
            if valor in TRAMO_A_ESTADO:
                return TRAMO_A_ESTADO[valor]

    columnas_dias = [
        "Días Proceso",
        "Días actual",
        "Días Proceso_actual",
    ]

    for columna in columnas_dias:
        if columna in fila.index:
            try:
                dias = float(str(fila[columna]).replace(".", "").replace(",", "."))
                return clasificar_estado_control(dias)
            except Exception:
                continue

    return None


def aplicar_color_operativo_fila(fila):
    estado = obtener_estado_visual_fila(fila)

    if estado is None:
        return ["" for _ in fila]

    fondo = COLOR_FONDO_FILAS.get(estado, "#FFFFFF")
    color_estado = COLOR_ESTADOS.get(estado, "#E5E7EB")
    texto = COLOR_TEXTO_FILAS.get(estado, "#111827")

    estilos = [
        f"background-color: {fondo}; color: #111827;"
        for _ in fila
    ]

    # Refuerzo visual suave en la primera columna de la fila.
    if estilos:
        estilos[0] += f" border-left: 5px solid {color_estado}; color: {texto}; font-weight: 700;"

    return estilos


def normalizar_nombre_columna(nombre_columna):
    texto = str(nombre_columna).strip().lower()
    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
    }

    for origen, destino in reemplazos.items():
        texto = texto.replace(origen, destino)

    texto = " ".join(texto.split())
    return texto


def obtener_estado_visual_columna(nombre_columna):
    """Asocia columnas operativas a colores de tramo/estado.

    Esto permite que tablas resumen, como administrativos/STA/marca, muestren
    el bloque de seguimiento, atraso y criticidad por columna, aunque no tengan
    una columna única de Estado Control o Tramo por fila.
    """
    col = normalizar_nombre_columna(nombre_columna)

    columnas_normal = {
        "normal",
        "0 a 30 dias",
        "0-30 dias",
    }

    columnas_seguimiento = {
        "seguimiento",
        "31 a 60 dias",
        "31-60 dias",
        "% seguimiento",
    }

    columnas_atrasado = {
        "atrasado",
        "61 a 120 dias",
        "61-120 dias",
        ">60 dias",
        "cp >60 dias",
        "cp sobre 60 dias",
        "% atrasado",
        "% atraso",
    }

    columnas_critico = {
        "critico",
        "criticos",
        "criticos >120",
        "criticos >120 dias",
        "mas de 120 dias",
        ">120 dias",
        "cp >120 dias",
        "% critico",
        "% criticos",
    }

    if col in columnas_normal:
        return "Normal"
    if col in columnas_seguimiento:
        return "Seguimiento"
    if col in columnas_atrasado:
        return "Atrasado"
    if col in columnas_critico:
        return "Crítico"

    return None


def aplicar_color_operativo_columnas(df_base):
    """Colorea columnas resumen asociadas a tramos/estados.

    Se usa solo cuando la fila no tiene un estado/tramo propio. Si la fila ya
    está coloreada por Estado Control, Tramo o Días Proceso, se respeta el color
    de fila para no mezclar lecturas.
    """
    estilos = pd.DataFrame("", index=df_base.index, columns=df_base.columns)

    for indice, fila in df_base.iterrows():
        if obtener_estado_visual_fila(fila) is not None:
            continue

        for columna in df_base.columns:
            estado_columna = obtener_estado_visual_columna(columna)

            if estado_columna is None:
                continue

            fondo = COLOR_FONDO_FILAS.get(estado_columna, "#FFFFFF")
            texto = COLOR_TEXTO_FILAS.get(estado_columna, "#111827")
            estilos.loc[indice, columna] = (
                f"background-color: {fondo}; color: {texto}; font-weight: 700;"
            )

    return estilos


def estilo_tabla_operativa(df_base):
    """Aplica encabezado azul marino y color suave por fila o columna según tramo/estado."""
    return (
        df_base
        .style
        .apply(aplicar_color_operativo_fila, axis=1)
        .apply(aplicar_color_operativo_columnas, axis=None)
        .set_table_styles(
            [
                {
                    "selector": "thead th",
                    "props": [
                        ("background-color", "#123047"),
                        ("color", "#FFFFFF"),
                        ("font-weight", "850"),
                        ("border-color", "#0B2538"),
                    ],
                },
                {
                    "selector": "tbody td",
                    "props": [
                        ("border-color", "#E5E7EB"),
                    ],
                },
            ]
        )
    )


_ST_DATAFRAME_ORIGINAL = st.dataframe


def _es_pandas_styler(objeto):
    return objeto.__class__.__name__ == "Styler" and hasattr(objeto, "to_html") and hasattr(objeto, "data")


def _render_tabla_html_operativa(datos, hide_index=True, height=None):
    """Renderiza tablas como HTML para controlar de forma real el color de encabezados."""
    if _es_pandas_styler(datos):
        styler = datos
        df_referencia = datos.data
    elif isinstance(datos, pd.DataFrame):
        styler = estilo_tabla_operativa(datos)
        df_referencia = datos
    else:
        return False

    if hide_index:
        try:
            styler = styler.hide(axis="index")
        except Exception:
            pass

    try:
        filas = len(df_referencia)
    except Exception:
        filas = 0

    if height is not None:
        alto = int(height)
    elif filas > 18:
        alto = 520
    elif filas > 10:
        alto = 430
    else:
        alto = None

    estilo_alto = f"max-height: {alto}px;" if alto else ""
    html_tabla = styler.to_html()

    st.markdown(
        f'<div class="op-table-wrapper" style="{estilo_alto}">{html_tabla}</div>',
        unsafe_allow_html=True
    )

    return True


def dataframe_operativa(datos=None, *args, use_container_width=True, hide_index=False, height=None, **kwargs):
    """Reemplazo visual controlado para st.dataframe.

    Streamlit dibuja varios encabezados de st.dataframe en canvas, por eso el CSS no siempre
    cambia el color del header. Esta función usa HTML cuando recibe DataFrame/Styler y mantiene
    el fallback original para cualquier otro caso.
    """
    if datos is not None and _render_tabla_html_operativa(datos, hide_index=hide_index, height=height):
        return None

    return _ST_DATAFRAME_ORIGINAL(
        datos,
        *args,
        use_container_width=use_container_width,
        hide_index=hide_index,
        height=height,
        **kwargs
    )


st.dataframe = dataframe_operativa


def clasificar_tramo(dias):
    if dias <= 30:
        return "0 a 30 días"
    elif dias <= 60:
        return "31 a 60 días"
    elif dias <= 120:
        return "61 a 120 días"
    else:
        return "Más de 120 días"


def clasificar_estado_control(dias):
    if dias <= 30:
        return "Normal"
    elif dias <= 60:
        return "Seguimiento"
    elif dias <= 120:
        return "Atrasado"
    else:
        return "Crítico"


def obtener_definicion_estados():
    return pd.DataFrame(
        {
            "Estado control": [
                "Normal",
                "Seguimiento",
                "Atrasado",
                "Crítico"
            ],
            "Tramo asociado": [
                "0 a 30 días",
                "31 a 60 días",
                "61 a 120 días",
                "Más de 120 días"
            ],
            "Lectura operativa": [
                "Producto dentro de rango normal de gestión.",
                "Producto aún no atrasado, pero requiere monitoreo preventivo.",
                "Producto fuera del rango esperado de gestión.",
                "Producto con atraso severo y prioridad de resolución."
            ],
            "Acción sugerida": [
                "Seguimiento normal.",
                "Revisar avance para evitar que pase a atraso.",
                "Gestionar con prioridad.",
                "Escalar, revisar causa y resolver prioritariamente."
            ]
        }
    )


def obtener_icono_kpi(titulo):
    titulo_limpio = str(titulo).lower()

    if "cp" in titulo_limpio:
        return "$"
    if "total" in titulo_limpio:
        return "▦"
    if "seguimiento" in titulo_limpio:
        return "◔"
    if "atras" in titulo_limpio or "60" in titulo_limpio:
        return "▲"
    if "crít" in titulo_limpio or "critic" in titulo_limpio or "120" in titulo_limpio:
        return "●"
    if "mediana" in titulo_limpio:
        return "◧"
    if "máximo" in titulo_limpio or "maximo" in titulo_limpio:
        return "⏱"

    return "▣"


def kpi_card(titulo, valor, nota, clase):
    icono = obtener_icono_kpi(titulo)
    st.markdown(
        f"""
        <div class="kpi-card {clase}">
            <div class="kpi-head-row">
                <span class="kpi-icon">{icono}</span>
                <div class="kpi-title">{texto_seguro(titulo)}</div>
            </div>
            <div class="kpi-value">{valor}</div>
            <div class="kpi-note">{nota}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def calcular_resumen(df_base):
    total = len(df_base)
    cp_total = df_base["CP"].sum()
    productos_60 = int((df_base["Días Proceso"] > 60).sum())
    productos_120 = int((df_base["Días Proceso"] > 120).sum())
    cp_60 = df_base.loc[df_base["Días Proceso"] > 60, "CP"].sum()
    cp_120 = df_base.loc[df_base["Días Proceso"] > 120, "CP"].sum()
    seguimiento = int((df_base["Estado Control"] == "Seguimiento").sum()) if "Estado Control" in df_base.columns else 0
    atrasados = int((df_base["Estado Control"] == "Atrasado").sum()) if "Estado Control" in df_base.columns else 0
    criticos = int((df_base["Estado Control"] == "Crítico").sum()) if "Estado Control" in df_base.columns else 0
    promedio = df_base["Días Proceso"].mean() if total > 0 else 0
    mediana = df_base["Días Proceso"].median() if total > 0 else 0
    maximo = df_base["Días Proceso"].max() if total > 0 else 0

    return {
        "Total productos": total,
        "CP total": cp_total,
        "Seguimiento": seguimiento,
        "Atrasados": atrasados,
        "Críticos": criticos,
        "Productos >60 días": productos_60,
        "Productos >120 días": productos_120,
        "CP >60 días": cp_60,
        "CP >120 días": cp_120,
        "Promedio días": promedio,
        "Mediana días": mediana,
        "Máximo días": maximo,
    }


def texto_variacion(valor_actual, valor_anterior, tipo="numero"):
    if valor_anterior is None:
        return "Sin corte anterior"

    diferencia = valor_actual - valor_anterior

    if tipo == "pesos":
        if diferencia > 0:
            return "▲ " + formato_pesos(diferencia)
        elif diferencia < 0:
            return "▼ " + formato_pesos(abs(diferencia))
        return "Sin variación"

    if diferencia > 0:
        return "▲ +" + formato_numero(diferencia)
    elif diferencia < 0:
        return "▼ -" + formato_numero(abs(diferencia))

    return "Sin variación"


def texto_variacion_porcentual(valor_actual, valor_anterior, tipo="numero"):
    if valor_anterior is None:
        return "Sin corte anterior"

    diferencia = valor_actual - valor_anterior

    if valor_anterior == 0:
        if diferencia == 0:
            return "Sin variación"
        if tipo == "pesos":
            return f"{texto_variacion(valor_actual, valor_anterior, tipo='pesos')} (sin base %)"
        return f"{texto_variacion(valor_actual, valor_anterior)} (sin base %)"

    variacion_pct = (diferencia / valor_anterior) * 100
    variacion_pct_txt = formato_porcentaje_puntos(abs(variacion_pct))

    if tipo == "pesos":
        if diferencia > 0:
            return f"▲ {formato_pesos(diferencia)} (+{variacion_pct_txt})"
        if diferencia < 0:
            return f"▼ {formato_pesos(abs(diferencia))} (-{variacion_pct_txt})"
        return "Sin variación (0,0%)"

    if diferencia > 0:
        return f"▲ +{formato_numero(diferencia)} (+{variacion_pct_txt})"
    if diferencia < 0:
        return f"▼ -{formato_numero(abs(diferencia))} (-{variacion_pct_txt})"

    return "Sin variación (0,0%)"


def frase_cambio(valor_actual, valor_anterior, tipo="numero"):
    if valor_anterior is None:
        return "no tiene comparación contra un corte anterior"

    diferencia = valor_actual - valor_anterior

    if tipo == "pesos":
        if diferencia > 0:
            return f"aumentó en {formato_pesos(diferencia)}"
        if diferencia < 0:
            return f"disminuyó en {formato_pesos(abs(diferencia))}"
        return "se mantuvo sin variación"

    if diferencia > 0:
        return f"aumentó en {formato_numero(diferencia)}"
    if diferencia < 0:
        return f"disminuyó en {formato_numero(abs(diferencia))}"

    return "se mantuvo sin variación"


def nota_kpi(participacion, variacion):
    if participacion:
        return f"{participacion} | {variacion}"
    return f"Vs corte anterior: {variacion}"



def texto_seguro(valor):
    return html.escape(str(valor))


def postit_card(titulo, texto, clase="info"):
    st.markdown(
        f"""
        <div class="postit-card {clase}">
            <div class="postit-title">{texto_seguro(titulo)}</div>
            <div class="postit-text">{texto_seguro(texto)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def obtener_icono_seccion(titulo):
    titulo_limpio = str(titulo).lower()

    if "resumen" in titulo_limpio:
        return "▦"
    if "control" in titulo_limpio:
        return "◈"
    if "análisis" in titulo_limpio or "analisis" in titulo_limpio:
        return "▤"
    if "movimiento" in titulo_limpio or "cambio" in titulo_limpio:
        return "↻"
    if "histórico" in titulo_limpio or "historico" in titulo_limpio:
        return "⌁"
    if "detalle" in titulo_limpio:
        return "▥"

    return "▣"


def section_header(titulo, subtitulo=""):
    subtitulo_html = f"<p>{texto_seguro(subtitulo)}</p>" if subtitulo else ""
    icono = obtener_icono_seccion(titulo)
    st.markdown(
        f"""
        <div class="section-title-wrap">
            <h3><span class="section-icon">{icono}</span>{texto_seguro(titulo)}</h3>
            {subtitulo_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def cutoff_strip(fecha_actual, fecha_anterior=None):
    fecha_actual_txt = fecha_actual.strftime("%d-%m-%Y") if fecha_actual else "Sin corte"
    if fecha_anterior is not None:
        fecha_anterior_txt = fecha_anterior.strftime("%d-%m-%Y")
        comparacion = f"<span class='cutoff-pill'>Comparativo: {fecha_anterior_txt}</span>"
    else:
        comparacion = "<span class='cutoff-pill'>Sin corte anterior</span>"

    st.markdown(
        f"""
        <div class="cutoff-strip">
            <span class="cutoff-pill">Corte visualizado: {fecha_actual_txt}</span>
            {comparacion}
            <span>Vista operativa para control semanal de gestión administrativa STA.</span>
        </div>
        <div class="process-flow">
            <div class="process-chip"><span>1</span>Cargar corte</div>
            <div class="process-chip"><span>2</span>Revisar estado</div>
            <div class="process-chip"><span>3</span>Detectar deterioros</div>
            <div class="process-chip"><span>4</span>Gestionar prioridad</div>
            <div class="process-chip"><span>5</span>Bajar al detalle</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def selector_chips_sidebar(titulo, opciones, key, expanded=True):
    opciones_limpias = []

    for opcion in opciones:
        if pd.isna(opcion):
            continue

        opcion_texto = str(opcion).strip()

        if opcion_texto == "":
            continue

        opciones_limpias.append(opcion_texto)

    opciones_limpias = list(dict.fromkeys(opciones_limpias))

    with st.expander(titulo, expanded=expanded):
        if not opciones_limpias:
            st.caption("Sin opciones disponibles.")
            return []

        if hasattr(st, "pills"):
            seleccion = st.pills(
                "Opciones",
                opciones_limpias,
                selection_mode="multi",
                key=key,
                label_visibility="collapsed"
            )
        else:
            seleccion = st.multiselect(
                "Opciones",
                opciones_limpias,
                key=key,
                label_visibility="collapsed"
            )

    if seleccion is None:
        return []

    if isinstance(seleccion, str):
        return [seleccion]

    return list(seleccion)


def crear_figura_tramos(resumen_tramos):
    fig_tramos = px.bar(
        resumen_tramos,
        x="Tramo",
        y="Productos",
        color="Estado Control",
        text="Productos",
        title="Distribución por antigüedad y estado",
        color_discrete_map=COLOR_ESTADOS
    )

    fig_tramos.update_traces(textposition="outside", marker_line_width=0)
    fig_tramos.update_layout(
        title=dict(text="Distribución por antigüedad y estado", x=0.02, xanchor="left"),
        height=385,
        xaxis_title="Tramo de antigüedad",
        yaxis_title="Productos",
        legend_title_text="Estado",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#111827", size=12),
        title_font=dict(size=17, color="#111827"),
        yaxis=dict(gridcolor="#E5E7EB"),
        margin=dict(l=20, r=20, t=52, b=20)
    )

    return fig_tramos



def crear_figura_atrasos_admin(resumen_admin):
    if resumen_admin.empty:
        return None

    columnas_necesarias = ["Administrativo", "Atrasado", "Critico"]
    if any(columna not in resumen_admin.columns for columna in columnas_necesarias):
        return None

    datos = resumen_admin.copy()
    datos["Crítico"] = datos["Critico"]
    datos["Total gestión prioritaria"] = datos["Atrasado"] + datos["Crítico"]
    datos = datos[datos["Total gestión prioritaria"] > 0].copy()

    if datos.empty:
        return None

    columnas_orden = ["Crítico", "Atrasado", "CP_60", "Total"]
    columnas_orden = [columna for columna in columnas_orden if columna in datos.columns]
    datos = datos.sort_values(columnas_orden, ascending=False).head(10)

    fig = px.bar(
        datos,
        x=["Atrasado", "Crítico"],
        y="Administrativo",
        orientation="h",
        title="Atrasados y críticos por administrativo",
        labels={
            "value": "Productos",
            "Administrativo": "Administrativo",
            "variable": "Estado",
        },
        color_discrete_map={
            "Atrasado": COLOR_ESTADOS["Atrasado"],
            "Crítico": COLOR_ESTADOS["Crítico"],
        },
    )

    fig.update_traces(
        texttemplate="%{x}",
        textposition="inside",
        insidetextanchor="middle",
        marker_line_width=0,
    )

    fig.update_layout(
        title=dict(text="Atrasados y críticos por administrativo", x=0.02, xanchor="left"),
        height=325,
        barmode="stack",
        xaxis_title="Productos",
        yaxis_title="Administrativo",
        yaxis=dict(categoryorder="total ascending"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#111827", size=12),
        title_font=dict(size=17, color="#111827"),
        xaxis=dict(gridcolor="#E5E7EB", rangemode="tozero"),
        legend_title_text="Estado",
        margin=dict(l=20, r=40, t=52, b=20)
    )

    return fig


def generar_prioridades_operativas(resumen_admin, tabla_sta, tabla_marca, resumen_actual, movimientos):
    prioridades = []

    if not resumen_admin.empty:
        foco_admin = resumen_admin.sort_values(
            ["Critico", "Atrasado", "CP_60", "Seguimiento", "Total"],
            ascending=False
        ).iloc[0]

        prioridades.append(
            f"<span class='priority-label'>Administrativo:</span> revisar primero a {texto_seguro(foco_admin['Administrativo'])}. "
            f"Concentra {formato_numero(foco_admin['Critico'])} críticos, "
            f"{formato_numero(foco_admin['Atrasado'])} atrasados y "
            f"{formato_pesos(foco_admin['CP_60'])} de CP sobre 60 días."
        )

    if not tabla_sta.empty:
        foco_sta = tabla_sta.sort_values(["Productos", "CP"], ascending=False).iloc[0]
        prioridades.append(
            f"<span class='priority-label'>STA:</span> hacer seguimiento a {texto_seguro(foco_sta['STA'])}. "
            f"Mantiene {formato_numero(foco_sta['Productos'])} productos sobre 60 días "
            f"y {formato_pesos(foco_sta['CP'])} asociados."
        )

    if not tabla_marca.empty:
        foco_marca = tabla_marca.sort_values(["Productos", "CP"], ascending=False).iloc[0]
        prioridades.append(
            f"<span class='priority-label'>Marca:</span> revisar casos de {texto_seguro(foco_marca['Marca'])}. "
            f"Registra {formato_numero(foco_marca['Productos'])} productos sobre 60 días "
            f"y {formato_pesos(foco_marca['CP'])} asociados."
        )

    empeoraron = len(movimientos.get("Empeoraron de tramo", pd.DataFrame()))
    criticos = resumen_actual.get("Productos >120 días", 0)

    if empeoraron > 0:
        prioridades.append(
            f"<span class='priority-label'>Deterioro:</span> controlar {formato_numero(empeoraron)} productos que empeoraron de tramo. "
            "Revisar causa y definir gestión antes de que aumente el bloque crítico."
        )
    elif criticos > 0:
        prioridades.append(
            f"<span class='priority-label'>Críticos:</span> mantener gestión activa sobre {formato_numero(criticos)} productos sobre 120 días. "
            "Solicitar respuesta, cierre o escalamiento según corresponda."
        )

    if not prioridades:
        prioridades.append("Sin focos operativos relevantes bajo el filtro actual.")

    return prioridades[:4]


def mostrar_prioridades_operativas(prioridades):
    items = "".join([f"<div class='priority-item'>{item}</div>" for item in prioridades])
    st.markdown(
        f"""
        <div class="priority-box">
            <div class="priority-title">Prioridad de gestión semanal</div>
            {items}
        </div>
        """,
        unsafe_allow_html=True
    )


def clasificar_prioridad_operativa(fila):
    estado = fila.get("Estado Control", "")
    dias = fila.get("Días Proceso", 0)
    cp = fila.get("CP", 0)

    if estado == "Crítico" and dias >= 180:
        return "Alta crítica"
    if estado == "Crítico":
        return "Crítica"
    if estado == "Atrasado" and cp > 0:
        return "Atrasada con CP"
    if estado == "Atrasado":
        return "Atrasada"
    return "Revisión"


def accion_sugerida_prioridad(fila):
    estado = fila.get("Estado Control", "")
    dias = fila.get("Días Proceso", 0)
    cp = fila.get("CP", 0)

    if estado == "Crítico" and dias >= 180:
        return "Escalar y cerrar definición"
    if estado == "Crítico":
        return "Gestionar respuesta o salida STA"
    if estado == "Atrasado" and cp > 0:
        return "Solicitar avance y priorizar por CP"
    if estado == "Atrasado":
        return "Solicitar avance y fecha de resolución"

    return "Revisar"


def preparar_prioridad_semanal(df_base):
    columnas_prioridad = [
        "Prioridad",
        "Acción sugerida",
        "Administrativo",
        "Estado Control",
        "Tramo",
        "Días Proceso",
        "CP",
        "STA",
        "Marca",
        "Id Ficha",
        "Id Producto",
        "Serie",
        "Descripción",
    ]

    prioridad = df_base[df_base["Estado Control"].isin(["Atrasado", "Crítico"])].copy()

    if prioridad.empty:
        return pd.DataFrame(columns=columnas_prioridad)

    prioridad["Prioridad"] = prioridad.apply(clasificar_prioridad_operativa, axis=1)
    prioridad["Acción sugerida"] = prioridad.apply(accion_sugerida_prioridad, axis=1)
    prioridad["Orden prioridad"] = prioridad["Estado Control"].map({"Crítico": 2, "Atrasado": 1}).fillna(0)

    prioridad = prioridad.sort_values(
        ["Orden prioridad", "Días Proceso", "CP"],
        ascending=[False, False, False]
    )

    columnas_prioridad = [col for col in columnas_prioridad if col in prioridad.columns]
    return prioridad[columnas_prioridad].head(40)


def generar_resumen_movimiento_operativo(mov_admin, movimientos):
    if mov_admin.empty:
        return "No hay movimientos relevantes por administrativo bajo el filtro actual."

    empeoraron_total = len(movimientos.get("Empeoraron de tramo", pd.DataFrame()))
    pasaron_60_total = len(movimientos.get("Pasaron >60", pd.DataFrame()))
    pasaron_120_total = len(movimientos.get("Pasaron >120", pd.DataFrame()))
    siguen_criticos_total = len(movimientos.get("Siguen críticos", pd.DataFrame()))

    partes = []

    if empeoraron_total > 0 and "Empeoraron de tramo" in mov_admin.columns:
        foco_empeora = mov_admin.sort_values("Empeoraron de tramo", ascending=False).iloc[0]
        partes.append(
            f"Se detectan {formato_numero(empeoraron_total)} productos que empeoraron de tramo; "
            f"el mayor foco está en {foco_empeora['Administrativo']} "
            f"({formato_numero(foco_empeora['Empeoraron de tramo'])})."
        )

    if pasaron_60_total > 0 and "Pasaron >60" in mov_admin.columns:
        foco_60 = mov_admin.sort_values("Pasaron >60", ascending=False).iloc[0]
        partes.append(
            f"Pasaron a más de 60 días {formato_numero(pasaron_60_total)} productos; "
            f"revisar primero {foco_60['Administrativo']} "
            f"({formato_numero(foco_60['Pasaron >60'])})."
        )

    if pasaron_120_total > 0 and "Pasaron >120" in mov_admin.columns:
        foco_120 = mov_admin.sort_values("Pasaron >120", ascending=False).iloc[0]
        partes.append(
            f"Pasaron a condición crítica {formato_numero(pasaron_120_total)} productos; "
            f"validar gestión con {foco_120['Administrativo']} "
            f"({formato_numero(foco_120['Pasaron >120'])})."
        )

    if siguen_criticos_total > 0 and "Siguen críticos" in mov_admin.columns:
        foco_critico = mov_admin.sort_values("Siguen críticos", ascending=False).iloc[0]
        partes.append(
            f"Siguen críticos {formato_numero(siguen_criticos_total)} productos; "
            f"principal responsable de gestión: {foco_critico['Administrativo']} "
            f"({formato_numero(foco_critico['Siguen críticos'])})."
        )

    if not partes:
        mayor_reduccion = mov_admin.sort_values("Neto", ascending=True).iloc[0]
        mayor_aumento = mov_admin.sort_values("Neto", ascending=False).iloc[0]

        if mayor_reduccion["Neto"] < 0 or mayor_aumento["Neto"] > 0:
            return (
                f"No hay deterioros relevantes bajo el filtro actual. "
                f"Mayor reducción neta: {mayor_reduccion['Administrativo']} ({formato_numero(mayor_reduccion['Neto'])}); "
                f"mayor aumento neto: {mayor_aumento['Administrativo']} (+{formato_numero(mayor_aumento['Neto'])})."
            )

        return "Los movimientos no muestran deterioros ni variaciones netas relevantes bajo el filtro actual."

    return " ".join(partes)


def generar_postits_operativos(
    resumen_actual,
    resumen_anterior,
    movimientos,
    resumen_admin,
    tabla_sta,
    tabla_marca,
    fecha_anterior,
    fecha_corte
):
    total_actual = resumen_actual["Total productos"]
    cp_total_actual = resumen_actual["CP total"]
    productos_60 = resumen_actual["Productos >60 días"]
    productos_120 = resumen_actual["Productos >120 días"]
    cp_60 = resumen_actual["CP >60 días"]

    pct_60 = formato_porcentaje(productos_60 / total_actual) if total_actual > 0 else "0,0%"
    pct_120 = formato_porcentaje(productos_120 / total_actual) if total_actual > 0 else "0,0%"
    pct_cp_60 = formato_porcentaje(cp_60 / cp_total_actual) if cp_total_actual > 0 else "0,0%"

    nuevos = len(movimientos.get("Nuevos", pd.DataFrame()))
    salidos = len(movimientos.get("Salidos", pd.DataFrame()))
    empeoraron = len(movimientos.get("Empeoraron de tramo", pd.DataFrame()))
    pasaron_60 = len(movimientos.get("Pasaron >60", pd.DataFrame()))
    pasaron_120 = len(movimientos.get("Pasaron >120", pd.DataFrame()))
    siguen_criticos = len(movimientos.get("Siguen críticos", pd.DataFrame()))

    postits = []

    if resumen_anterior is not None:
        total_anterior = resumen_anterior["Total productos"]
        neto = total_actual - total_anterior
        clase_movimiento = "success" if salidos >= nuevos else "warning"
        texto_movimiento = (
            f"Ingresaron {formato_numero(nuevos)} y salieron {formato_numero(salidos)} productos; "
            f"variación neta {formato_numero(neto)}. Para gestión semanal, revisar "
            f"{formato_numero(empeoraron)} que empeoraron de tramo, "
            f"{formato_numero(pasaron_60)} que pasaron a >60 días y "
            f"{formato_numero(pasaron_120)} que pasaron a >120 días."
        )
    else:
        clase_movimiento = "info"
        texto_movimiento = (
            "Primer corte registrado. La lectura de movimiento semanal se activará cuando exista un corte anterior comparable."
        )

    postits.append({
        "titulo": "Movimiento semanal",
        "clase": clase_movimiento,
        "texto": texto_movimiento
    })

    if productos_60 > 0:
        texto_riesgo = (
            f"El bloque de gestión prioritaria reúne {formato_numero(productos_60)} productos sobre 60 días "
            f"({pct_60}), con {formato_pesos(cp_60)} comprometidos ({pct_cp_60} del CP). "
            f"Dentro de ese universo, {formato_numero(productos_120)} están sobre 120 días ({pct_120}) "
            f"y {formato_numero(siguen_criticos)} se mantienen críticos."
        )
        clase_riesgo = "danger" if productos_120 > 0 else "warning"
    else:
        texto_riesgo = "No hay productos sobre 60 días bajo el filtro actual. Mantener control preventivo en seguimiento."
        clase_riesgo = "success"

    postits.append({
        "titulo": "Riesgo operativo",
        "clase": clase_riesgo,
        "texto": texto_riesgo
    })

    acciones = []

    atrasados_61_120 = max(productos_60 - productos_120, 0)

    if productos_120 > 0:
        acciones.append(
            f"revisar primero {formato_numero(productos_120)} productos críticos sobre 120 días"
        )

    if atrasados_61_120 > 0:
        acciones.append(
            f"luego gestionar {formato_numero(atrasados_61_120)} atrasados entre 61 y 120 días"
        )

    if empeoraron > 0:
        acciones.append(
            f"validar {formato_numero(empeoraron)} productos que empeoraron de tramo"
        )

    if pasaron_60 > 0:
        acciones.append(
            f"tomar {formato_numero(pasaron_60)} productos que pasaron a más de 60 días antes de que lleguen a crítico"
        )

    if siguen_criticos > 0:
        acciones.append(
            f"escalar o cerrar definición para {formato_numero(siguen_criticos)} productos que siguen críticos"
        )

    if acciones:
        texto_accion = "Para esta semana: " + "; ".join(acciones[:4]) + ". Usar filtros de administrativo, STA y marca para bajar al detalle."
        clase_accion = "danger" if productos_120 > 0 else "warning"
    else:
        texto_accion = "Sin acciones urgentes bajo el filtro actual. Mantener control preventivo sobre productos en seguimiento."
        clase_accion = "success"

    postits.append({
        "titulo": "Gestión sugerida",
        "clase": clase_accion,
        "texto": texto_accion
    })

    return postits


# --------------------------------------------------
# FUNCIONES DE HISTÓRICO CENTRAL GOOGLE SHEETS
# --------------------------------------------------

COLUMNAS_HISTORICO = [
    "Fecha Corte",
    "Llave",
    "Id Ficha",
    "Id Producto",
    "Serie",
    "Descripción",
    "Marca",
    "Familia",
    "Administrativo",
    "STA",
    "Proveedor",
    "Días Proceso",
    "CP",
    "Tramo",
    "Estado Control"
]


@st.cache_resource(show_spinner=False)
def obtener_worksheet_google():
    service_account_info = dict(st.secrets["gcp_service_account"])

    if "private_key" in service_account_info:
        service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=scopes,
    )

    client = gspread.authorize(creds)

    sheet_name = st.secrets["app"].get("sheet_name", "Historico_STA_Dashboard")
    worksheet_name = st.secrets["app"].get("worksheet_name", "Historico_STA")

    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet(worksheet_name)

    return worksheet


def normalizar_historico(historico):
    if historico.empty:
        return historico

    for columna in COLUMNAS_HISTORICO:
        if columna not in historico.columns:
            historico[columna] = ""

    historico = historico[COLUMNAS_HISTORICO].copy()

    historico["Fecha Corte"] = pd.to_datetime(
        historico["Fecha Corte"],
        errors="coerce"
    ).dt.date

    historico["Días Proceso"] = pd.to_numeric(
        historico["Días Proceso"],
        errors="coerce"
    ).fillna(0).astype(int)

    historico["CP"] = historico["CP"].apply(limpiar_cp).round(0)

    for columna in ["Llave", "Id Ficha", "Id Producto", "Serie", "Descripción", "Marca", "Familia", "Administrativo", "STA", "Proveedor"]:
        historico[columna] = historico[columna].fillna("").astype(str).str.strip()

    historico["Administrativo"] = historico["Administrativo"].apply(normalizar_nombre_persona)

    historico.loc[historico["STA"].isin(["", "651", "nan", "None"]), "STA"] = "Sin STA"

    historico["Tramo"] = historico["Días Proceso"].apply(clasificar_tramo)
    historico["Estado Control"] = historico["Días Proceso"].apply(clasificar_estado_control)

    return historico


def cargar_historico():
    try:
        worksheet = obtener_worksheet_google()
        registros = worksheet.get_all_records()
    except Exception as error:
        st.error("No se pudo conectar con el histórico central en Google Sheets.")
        st.exception(error)
        st.stop()

    if not registros:
        return pd.DataFrame(columns=COLUMNAS_HISTORICO)

    historico = pd.DataFrame(registros)
    return normalizar_historico(historico)


def escribir_historico(historico_final):
    worksheet = obtener_worksheet_google()

    historico_salida = historico_final.copy()

    for columna in COLUMNAS_HISTORICO:
        if columna not in historico_salida.columns:
            historico_salida[columna] = ""

    historico_salida = historico_salida[COLUMNAS_HISTORICO].copy()
    historico_salida["Fecha Corte"] = historico_salida["Fecha Corte"].astype(str)

    historico_salida["CP"] = pd.to_numeric(
        historico_salida["CP"],
        errors="coerce"
    ).fillna(0).round(0).astype(int)

    historico_salida["Días Proceso"] = pd.to_numeric(
        historico_salida["Días Proceso"],
        errors="coerce"
    ).fillna(0).round(0).astype(int)

    historico_salida = historico_salida.fillna("")

    valores = [COLUMNAS_HISTORICO] + historico_salida.values.tolist()

    worksheet.clear()
    worksheet.update(valores, value_input_option="RAW")


def limpiar_historico_central():
    worksheet = obtener_worksheet_google()
    worksheet.clear()


def preparar_para_historico(df_base, fecha_corte):
    df_hist = df_base.copy()
    df_hist["Fecha Corte"] = fecha_corte.isoformat()

    if "CP" in df_hist.columns:
        df_hist["CP"] = pd.to_numeric(
            df_hist["CP"],
            errors="coerce"
        ).fillna(0).round(0).astype(int)

    for columna in COLUMNAS_HISTORICO:
        if columna not in df_hist.columns:
            df_hist[columna] = ""

    return df_hist[COLUMNAS_HISTORICO]


def registrar_corte(df_base, fecha_corte):
    nuevo_corte = preparar_para_historico(df_base, fecha_corte)
    historico_actual = cargar_historico()

    if not historico_actual.empty:
        historico_actual = historico_actual[historico_actual["Fecha Corte"] != fecha_corte].copy()
        historico_actual["Fecha Corte"] = historico_actual["Fecha Corte"].astype(str)

        historico_final = pd.concat(
            [historico_actual, nuevo_corte],
            ignore_index=True
        )
    else:
        historico_final = nuevo_corte

    escribir_historico(historico_final)


def obtener_ultimo_corte():
    historico = cargar_historico()

    if historico.empty:
        return None, None

    fechas = sorted(historico["Fecha Corte"].dropna().unique())

    if not fechas:
        return None, None

    fecha_actual = fechas[-1]
    df_actual = historico[historico["Fecha Corte"] == fecha_actual].copy()

    return fecha_actual, df_actual


def obtener_corte_anterior(fecha_corte):
    historico = cargar_historico()

    if historico.empty:
        return None, None

    fechas_anteriores = sorted([
        fecha for fecha in historico["Fecha Corte"].dropna().unique()
        if fecha < fecha_corte
    ])

    if not fechas_anteriores:
        return None, None

    fecha_anterior = fechas_anteriores[-1]
    df_anterior = historico[historico["Fecha Corte"] == fecha_anterior].copy()

    return fecha_anterior, df_anterior


# --------------------------------------------------
# FUNCIONES DE CARGA Y PREPARACIÓN DE REPORTE
# --------------------------------------------------

def leer_reporte_sta(archivo):
    excel = pd.ExcelFile(archivo)

    if "Reporte - Bandeja" not in excel.sheet_names:
        raise ValueError("No se encontró la hoja 'Reporte - Bandeja'.")

    df_base = pd.read_excel(archivo, sheet_name="Reporte - Bandeja")
    df_base = df_base.dropna(how="all")
    df_base.columns = df_base.columns.astype(str).str.strip()

    return preparar_dataframe_sta(df_base)


def preparar_dataframe_sta(df_base):
    df_preparado = df_base.copy()

    columnas_requeridas = [
        "Id Ficha",
        "Id Producto",
        "Serie",
        "Descripción",
        "Marca",
        "Usuario Emisor",
        "Sta",
        "Días Proceso",
        "CP"
    ]

    columnas_faltantes = [columna for columna in columnas_requeridas if columna not in df_preparado.columns]

    if columnas_faltantes:
        raise ValueError(f"Faltan columnas necesarias en la hoja 'Reporte - Bandeja': {columnas_faltantes}")

    df_preparado["Días Proceso"] = pd.to_numeric(
        df_preparado["Días Proceso"],
        errors="coerce"
    ).fillna(0).astype(int)

    df_preparado["CP"] = df_preparado["CP"].apply(limpiar_cp)

    df_preparado["Administrativo"] = df_preparado["Usuario Emisor"].apply(normalizar_nombre_persona)
    df_preparado["Marca"] = df_preparado["Marca"].fillna("Sin marca").astype(str).str.strip()
    df_preparado["STA"] = df_preparado["Sta"].fillna("Sin STA").astype(str).str.strip()

    if "Familia" not in df_preparado.columns:
        df_preparado["Familia"] = ""

    if "Proveedor" not in df_preparado.columns:
        df_preparado["Proveedor"] = ""

    df_preparado["Familia"] = df_preparado["Familia"].fillna("Sin familia").astype(str).str.strip()
    df_preparado["Proveedor"] = df_preparado["Proveedor"].fillna("Sin proveedor").astype(str).str.strip()

    df_preparado.loc[df_preparado["STA"].isin(["", "651", "nan", "None"]), "STA"] = "Sin STA"

    df_preparado["Tramo"] = df_preparado["Días Proceso"].apply(clasificar_tramo)
    df_preparado["Estado Control"] = df_preparado["Días Proceso"].apply(clasificar_estado_control)

    df_preparado["Llave"] = (
        df_preparado["Id Ficha"].astype(str).str.strip()
        + "|"
        + df_preparado["Id Producto"].astype(str).str.strip()
        + "|"
        + df_preparado["Serie"].astype(str).str.strip()
    )

    return df_preparado


# FUNCIONES DE FILTROS Y MOVIMIENTOS
# --------------------------------------------------

def aplicar_filtros(
    df_base,
    admin_seleccionado,
    sta_seleccionado,
    marca_seleccionada,
    tramo_seleccionado,
    estado_seleccionado,
    busqueda
):
    df_resultado = df_base.copy()

    if admin_seleccionado and "Administrativo" in df_resultado.columns:
        df_resultado = df_resultado[df_resultado["Administrativo"].isin(admin_seleccionado)]

    if sta_seleccionado and "STA" in df_resultado.columns:
        df_resultado = df_resultado[df_resultado["STA"].isin(sta_seleccionado)]

    if marca_seleccionada and "Marca" in df_resultado.columns:
        df_resultado = df_resultado[df_resultado["Marca"].isin(marca_seleccionada)]

    if tramo_seleccionado and "Tramo" in df_resultado.columns:
        df_resultado = df_resultado[df_resultado["Tramo"].isin(tramo_seleccionado)]

    if estado_seleccionado and "Estado Control" in df_resultado.columns:
        df_resultado = df_resultado[df_resultado["Estado Control"].isin(estado_seleccionado)]

    if busqueda.strip() != "":
        texto_busqueda = busqueda.strip().lower()

        columnas_busqueda = [
            "Id Ficha",
            "Id Producto",
            "Serie",
            "Descripción"
        ]

        columnas_busqueda = [
            columna for columna in columnas_busqueda
            if columna in df_resultado.columns
        ]

        mascara = pd.Series(False, index=df_resultado.index)

        for columna in columnas_busqueda:
            mascara = mascara | df_resultado[columna].astype(str).str.lower().str.contains(
                texto_busqueda,
                na=False
            )

        df_resultado = df_resultado[mascara]

    return df_resultado


def columnas_disponibles(df_base, columnas):
    return [columna for columna in columnas if columna in df_base.columns]


def tabla_simple(df_base):
    columnas = [
        "Administrativo",
        "Estado Control",
        "Tramo",
        "Días Proceso",
        "STA",
        "Marca",
        "Id Ficha",
        "Id Producto",
        "Serie",
        "Descripción",
        "CP"
    ]

    columnas = columnas_disponibles(df_base, columnas)

    if df_base.empty:
        return pd.DataFrame(columns=columnas)

    return df_base[columnas].sort_values("Días Proceso", ascending=False)


def tabla_movimiento_desde_merge(df_merge):
    columnas_origen = [
        "Administrativo_actual",
        "STA_actual",
        "Marca_actual",
        "Id Ficha_actual",
        "Id Producto_actual",
        "Serie_actual",
        "Descripción_actual",
        "Días Proceso_anterior",
        "Días Proceso_actual",
        "Estado Control_anterior",
        "Estado Control_actual",
        "CP_actual"
    ]

    columnas_origen = columnas_disponibles(df_merge, columnas_origen)

    if df_merge.empty:
        columnas_salida = [
            "Administrativo",
            "STA",
            "Marca",
            "Id Ficha",
            "Id Producto",
            "Serie",
            "Descripción",
            "Días anterior",
            "Días actual",
            "Estado anterior",
            "Estado actual",
            "CP"
        ]
        return pd.DataFrame(columns=columnas_salida)

    tabla = df_merge[columnas_origen].copy()

    renombrar = {
        "Administrativo_actual": "Administrativo",
        "STA_actual": "STA",
        "Marca_actual": "Marca",
        "Id Ficha_actual": "Id Ficha",
        "Id Producto_actual": "Id Producto",
        "Serie_actual": "Serie",
        "Descripción_actual": "Descripción",
        "Días Proceso_anterior": "Días anterior",
        "Días Proceso_actual": "Días actual",
        "Estado Control_anterior": "Estado anterior",
        "Estado Control_actual": "Estado actual",
        "CP_actual": "CP"
    }

    tabla = tabla.rename(columns=renombrar)
    tabla = tabla.sort_values("Días actual", ascending=False)

    return tabla


def calcular_movimientos(df_actual, df_anterior):
    movimientos = {}

    nombres_base = [
        "Nuevos",
        "Salidos",
        "Pasaron >60",
        "Pasaron >120",
        "Siguen críticos",
        "Empeoraron de tramo"
    ]

    if df_anterior is None or df_anterior.empty:
        for nombre in nombres_base:
            movimientos[nombre] = pd.DataFrame()
        return movimientos

    actual = df_actual.copy()
    anterior = df_anterior.copy()

    actual["Llave"] = actual["Llave"].astype(str)
    anterior["Llave"] = anterior["Llave"].astype(str)

    llaves_actual = set(actual["Llave"])
    llaves_anterior = set(anterior["Llave"])

    nuevos = actual[~actual["Llave"].isin(llaves_anterior)].copy()
    salidos = anterior[~anterior["Llave"].isin(llaves_actual)].copy()

    comunes = actual.merge(
        anterior,
        on="Llave",
        suffixes=("_actual", "_anterior"),
        how="inner"
    )

    if comunes.empty:
        pasaron_60 = pd.DataFrame()
        pasaron_120 = pd.DataFrame()
        siguen_criticos = pd.DataFrame()
        empeoraron = pd.DataFrame()
    else:
        pasaron_60 = comunes[
            (comunes["Días Proceso_anterior"] <= 60)
            & (comunes["Días Proceso_actual"] > 60)
        ].copy()

        pasaron_120 = comunes[
            (comunes["Días Proceso_anterior"] <= 120)
            & (comunes["Días Proceso_actual"] > 120)
        ].copy()

        siguen_criticos = comunes[
            (comunes["Días Proceso_anterior"] > 120)
            & (comunes["Días Proceso_actual"] > 120)
        ].copy()

        severidad = {
            "Normal": 0,
            "Seguimiento": 1,
            "Atrasado": 2,
            "Crítico": 3
        }

        comunes["Severidad anterior"] = comunes["Estado Control_anterior"].map(severidad).fillna(0)
        comunes["Severidad actual"] = comunes["Estado Control_actual"].map(severidad).fillna(0)

        empeoraron = comunes[
            comunes["Severidad actual"] > comunes["Severidad anterior"]
        ].copy()

    movimientos["Nuevos"] = tabla_simple(nuevos)
    movimientos["Salidos"] = tabla_simple(salidos)
    movimientos["Pasaron >60"] = tabla_movimiento_desde_merge(pasaron_60)
    movimientos["Pasaron >120"] = tabla_movimiento_desde_merge(pasaron_120)
    movimientos["Siguen críticos"] = tabla_movimiento_desde_merge(siguen_criticos)
    movimientos["Empeoraron de tramo"] = tabla_movimiento_desde_merge(empeoraron)

    return movimientos


def resumen_movimientos_por_dimension(movimientos, dimension):
    nombres_mov = [
        "Nuevos",
        "Salidos",
        "Pasaron >60",
        "Pasaron >120",
        "Siguen críticos",
        "Empeoraron de tramo"
    ]

    valores_dimension = set()

    for nombre in nombres_mov:
        tabla = movimientos.get(nombre, pd.DataFrame())
        if not tabla.empty and dimension in tabla.columns:
            valores_dimension.update(tabla[dimension].dropna().astype(str).unique())

    if not valores_dimension:
        return pd.DataFrame(
            columns=[
                dimension,
                "Nuevos",
                "Salidos",
                "Neto",
                "Pasaron >60",
                "Pasaron >120",
                "Siguen críticos",
                "Empeoraron de tramo"
            ]
        )

    resumen = pd.DataFrame({dimension: sorted(valores_dimension)})

    for nombre in nombres_mov:
        tabla = movimientos.get(nombre, pd.DataFrame())

        if tabla.empty or dimension not in tabla.columns:
            conteo = pd.DataFrame(columns=[dimension, nombre])
        else:
            conteo = (
                tabla
                .groupby(dimension)
                .size()
                .reset_index(name=nombre)
            )

        resumen = resumen.merge(conteo, on=dimension, how="left")

    for nombre in nombres_mov:
        resumen[nombre] = resumen[nombre].fillna(0).astype(int)

    resumen["Neto"] = resumen["Nuevos"] - resumen["Salidos"]

    resumen = resumen[
        [
            dimension,
            "Nuevos",
            "Salidos",
            "Neto",
            "Pasaron >60",
            "Pasaron >120",
            "Siguen críticos",
            "Empeoraron de tramo"
        ]
    ]

    resumen = resumen.sort_values(
        ["Siguen críticos", "Empeoraron de tramo", "Pasaron >120", "Pasaron >60", "Nuevos"],
        ascending=False
    )

    return resumen


def generar_lecturas(
    resumen_actual,
    resumen_anterior,
    movimientos,
    resumen_admin,
    tabla_sta,
    tabla_marca,
    fecha_anterior,
    fecha_corte
):
    total_actual = resumen_actual["Total productos"]
    cp_total_actual = resumen_actual["CP total"]
    seguimiento = resumen_actual["Seguimiento"]
    productos_60 = resumen_actual["Productos >60 días"]
    productos_120 = resumen_actual["Productos >120 días"]
    cp_60 = resumen_actual["CP >60 días"]

    porcentaje_seguimiento = seguimiento / total_actual if total_actual > 0 else 0
    porcentaje_60 = productos_60 / total_actual if total_actual > 0 else 0
    porcentaje_120 = productos_120 / total_actual if total_actual > 0 else 0
    porcentaje_cp_60 = cp_60 / cp_total_actual if cp_total_actual > 0 else 0

    nuevos = len(movimientos.get("Nuevos", pd.DataFrame()))
    salidos = len(movimientos.get("Salidos", pd.DataFrame()))
    pasaron_120 = len(movimientos.get("Pasaron >120", pd.DataFrame()))
    siguen_criticos = len(movimientos.get("Siguen críticos", pd.DataFrame()))

    if resumen_anterior is not None:
        total_anterior = resumen_anterior["Total productos"]

        lectura_general = (
            f"Respecto al corte anterior ({fecha_anterior.strftime('%d-%m-%Y')}), "
            f"el stock STA {frase_cambio(total_actual, total_anterior)}. "
            f"El corte actual registra {formato_numero(total_actual)} productos, "
            f"con un CP total de {formato_pesos(cp_total_actual)}."
        )

        lectura_movimientos = (
            f"Entre ambos cortes se detectan {formato_numero(nuevos)} productos nuevos "
            f"y {formato_numero(salidos)} productos que salieron del stock reportado en STA. "
            f"La variación neta es de {formato_numero(total_actual - total_anterior)} productos, "
            f"equivalente a {formato_porcentaje((total_actual - total_anterior) / total_anterior) if total_anterior > 0 else 'sin base porcentual'}."
        )

        lectura_atraso = (
            f"El estado Seguimiento registra {formato_numero(seguimiento)} productos "
            f"entre 31 y 60 días, equivalente al {formato_porcentaje(porcentaje_seguimiento)} del stock filtrado. "
            f"Los productos Atrasados + Críticos, es decir sobre 60 días, "
            f"{frase_cambio(productos_60, resumen_anterior['Productos >60 días'])}, "
            f"quedando en {formato_numero(productos_60)} unidades, equivalente al "
            f"{formato_porcentaje(porcentaje_60)} del stock filtrado. "
            f"El CP asociado a productos Atrasados + Críticos es {formato_pesos(cp_60)}, "
            f"equivalente al {formato_porcentaje(porcentaje_cp_60)} del CP total."
        )

        lectura_criticos = (
            f"Los productos Críticos sobre 120 días {frase_cambio(productos_120, resumen_anterior['Productos >120 días'])}, "
            f"quedando en {formato_numero(productos_120)} casos, equivalente al "
            f"{formato_porcentaje(porcentaje_120)} del stock filtrado. "
            f"Durante la semana, {formato_numero(pasaron_120)} productos pasaron a condición crítica "
            f"y {formato_numero(siguen_criticos)} se mantienen críticos desde el corte anterior."
        )
    else:
        lectura_general = (
            f"El corte actual registra {formato_numero(total_actual)} productos en STA, "
            f"con un CP total de {formato_pesos(cp_total_actual)}. "
            f"No existe un corte anterior registrado para comparar variación semanal."
        )

        lectura_movimientos = (
            "No hay corte anterior registrado, por lo que todavía no es posible calcular productos nuevos, "
            "salidos o cambios de tramo respecto a la semana anterior."
        )

        lectura_atraso = (
            f"Actualmente hay {formato_numero(seguimiento)} productos en Seguimiento, "
            f"equivalentes al {formato_porcentaje(porcentaje_seguimiento)} del stock filtrado. "
            f"Los productos sobre 60 días equivalen al {formato_porcentaje(porcentaje_60)} del stock filtrado."
        )

        lectura_criticos = (
            f"Actualmente hay {formato_numero(productos_120)} productos Críticos sobre 120 días, "
            f"equivalentes al {formato_porcentaje(porcentaje_120)} del stock filtrado."
        )

    if not resumen_admin.empty:
        top_admin = resumen_admin.sort_values(
            ["Critico", "Atrasado", "Seguimiento", "Total"],
            ascending=False
        ).iloc[0]

        texto_admin = (
            f"En gestión administrativa, el principal foco se concentra en "
            f"{top_admin['Administrativo']}, con {formato_numero(top_admin['Seguimiento'])} productos en Seguimiento "
            f"({formato_porcentaje_puntos(top_admin['% seguimiento'])}), "
            f"{formato_numero(top_admin['Atrasado'])} Atrasados "
            f"({formato_porcentaje_puntos(top_admin['% atrasado'])}) y "
            f"{formato_numero(top_admin['Critico'])} Críticos "
            f"({formato_porcentaje_puntos(top_admin['% crítico'])})."
        )
    else:
        texto_admin = "No hay información administrativa disponible para el filtro aplicado."

    if not tabla_sta.empty:
        top_sta = tabla_sta.iloc[0]
        texto_sta = (
            f"Por STA, el mayor foco de atraso corresponde a {top_sta['STA']}, "
            f"con {formato_numero(top_sta['Productos'])} productos sobre 60 días "
            f"y un CP asociado de {formato_pesos(top_sta['CP'])}."
        )
    else:
        texto_sta = "No se detectan productos sobre 60 días para STA bajo el filtro actual."

    if not tabla_marca.empty:
        top_marca = tabla_marca.iloc[0]
        texto_marca = (
            f"Por marca, el principal foco de atraso corresponde a {top_marca['Marca']}, "
            f"con {formato_numero(top_marca['Productos'])} productos sobre 60 días "
            f"y un CP asociado de {formato_pesos(top_marca['CP'])}."
        )
    else:
        texto_marca = "No se detectan productos sobre 60 días por marca bajo el filtro actual."

    lectura_focos = f"{texto_admin} {texto_sta} {texto_marca}"

    lecturas = {
        "Lectura general": lectura_general,
        "Lectura de movimientos": lectura_movimientos,
        "Lectura de atraso": lectura_atraso,
        "Lectura de críticos": lectura_criticos,
        "Lectura de focos": lectura_focos,
    }

    return lecturas


def crear_excel_descarga(
    detalle_df,
    resumen_df,
    admin_df,
    tramos_df,
    estado_definiciones_df,
    movimientos,
    mov_admin,
    mov_sta,
    mov_marca,
    lectura_df
):
    salida = io.BytesIO()

    with pd.ExcelWriter(salida, engine="openpyxl") as writer:
        lectura_df.to_excel(writer, index=False, sheet_name="Lectura operativa")
        resumen_df.to_excel(writer, index=False, sheet_name="Resumen")
        estado_definiciones_df.to_excel(writer, index=False, sheet_name="Estados control")
        admin_df.to_excel(writer, index=False, sheet_name="Administrativos")
        tramos_df.to_excel(writer, index=False, sheet_name="Tramos")
        mov_admin.to_excel(writer, index=False, sheet_name="Mov Admin")
        mov_sta.to_excel(writer, index=False, sheet_name="Mov STA")
        mov_marca.to_excel(writer, index=False, sheet_name="Mov Marca")
        detalle_df.to_excel(writer, index=False, sheet_name="Detalle filtrado")

        for nombre, tabla in movimientos.items():
            nombre_hoja = nombre.replace(">", "mayor ").replace("í", "i")[:31]
            tabla.to_excel(writer, index=False, sheet_name=nombre_hoja)

        libro = writer.book

        for hoja_nombre in libro.sheetnames:
            hoja = libro[hoja_nombre]

            for columna in hoja.columns:
                largo_maximo = 0
                letra_columna = columna[0].column_letter

                for celda in columna:
                    valor = celda.value
                    if valor is not None:
                        largo_maximo = max(largo_maximo, len(str(valor)))

                ancho = min(max(largo_maximo + 2, 12), 60)
                hoja.column_dimensions[letra_columna].width = ancho

            for celda in hoja[1]:
                celda.font = celda.font.copy(bold=True)

    salida.seek(0)
    return salida


# --------------------------------------------------
# SIDEBAR Y FUENTE DE DATOS
# --------------------------------------------------

orden_tramos = [
    "0 a 30 días",
    "31 a 60 días",
    "61 a 120 días",
    "Más de 120 días"
]

orden_estado = [
    "Normal",
    "Seguimiento",
    "Atrasado",
    "Crítico"
]

estado_definiciones = obtener_definicion_estados()

# Contenedores creados en este orden para que los filtros queden arriba
# y la configuración/histórico central queden al final del panel lateral.
st.sidebar.header("Filtros")
st.sidebar.caption("Selecciona opciones con los botones. Puedes combinar varios filtros.")
filtros_sidebar = st.sidebar.container()

st.sidebar.divider()
st.sidebar.header("Búsqueda directa")
busqueda_sidebar = st.sidebar.container()

st.sidebar.divider()
config_sidebar = st.sidebar.expander("Configuración y carga de cortes", expanded=False)

st.sidebar.divider()
historico_sidebar = st.sidebar.expander("Histórico central", expanded=False)

st.sidebar.markdown(
    """
    <div class="developer-credit">
        <strong>Desarrollado por Hugo Morales</strong><br>
        <span>Procesos y Calidad · RMA · PCFactory</span>
    </div>
    """,
    unsafe_allow_html=True
)

historico = cargar_historico()

df_cargado = None
fecha_corte_cargado = None

with config_sidebar:
    modo_acceso = st.radio(
        "Modo de acceso",
        ["Supervisor", "Administrador"],
        index=0
    )

    if modo_acceso == "Administrador":
        st.subheader("Carga de cortes")

        clave_ingresada = st.text_input(
            "Clave administrador",
            type="password"
        )

        clave_admin = st.secrets["app"].get("admin_password", "")

        if clave_ingresada == "":
            st.info("Ingresa la clave para habilitar la carga de cortes.")
        elif clave_ingresada != clave_admin:
            st.error("Clave incorrecta. Se mantiene vista de solo lectura.")
        else:
            st.success("Modo administrador habilitado.")

            fecha_admin = st.date_input(
                "Fecha de corte del reporte",
                value=date.today()
            )

            archivo = st.file_uploader(
                "Carga aquí el archivo Excel del reporte STA",
                type=["xlsx"]
            )

            if archivo is not None:
                try:
                    df_cargado = leer_reporte_sta(archivo)
                    fecha_corte_cargado = fecha_admin

                    st.success(
                        f"Archivo cargado: {formato_numero(len(df_cargado))} productos."
                    )

                    if st.button("Guardar corte en histórico central"):
                        registrar_corte(df_cargado, fecha_admin)
                        st.success(
                            f"Corte {fecha_admin.strftime('%d-%m-%Y')} guardado correctamente."
                        )
                        st.rerun()

                except Exception as error:
                    st.error("No se pudo procesar el archivo cargado.")
                    st.exception(error)
                    st.stop()
            else:
                st.info("Carga un Excel solo cuando necesites registrar un nuevo corte.")

            st.divider()
            st.subheader("Mantenimiento")
            confirmacion_limpieza = st.text_input(
                "Para limpiar el histórico central, escribe LIMPIAR",
                value=""
            )

            if st.button("Limpiar histórico central"):
                if confirmacion_limpieza == "LIMPIAR":
                    limpiar_historico_central()
                    st.success("Histórico central limpiado correctamente.")
                    st.rerun()
                else:
                    st.error("Debes escribir LIMPIAR para confirmar.")
    else:
        st.caption("Vista de solo lectura para supervisores.")

with historico_sidebar:
    if historico.empty:
        st.info("Aún no hay cortes registrados en Google Sheets.")
    else:
        cortes_registrados = sorted(historico["Fecha Corte"].dropna().unique())
        st.success(f"Cortes registrados: {len(cortes_registrados)}")
        st.write([fecha.strftime("%d-%m-%Y") for fecha in cortes_registrados])

if df_cargado is not None:
    df = df_cargado.copy()
    fecha_corte = fecha_corte_cargado
    st.info(
        "Vista previa del archivo cargado en modo administrador. "
        "Si aún no guardaste el corte, los supervisores todavía verán el último corte registrado."
    )
else:
    fecha_corte, df = obtener_ultimo_corte()

    if df is None or df.empty:
        st.info(
            "Todavía no hay cortes registrados en el histórico central. "
            "Ingresa como Administrador, carga el primer Excel y guarda el corte."
        )
        st.stop()

# --------------------------------------------------
# FILTROS
# --------------------------------------------------

filtro_keys = [
    "filtro_admin",
    "filtro_tramo",
    "filtro_estado",
    "filtro_sta",
    "filtro_marca",
    "busqueda_texto",
]

with filtros_sidebar:
    if st.button("Limpiar filtros", use_container_width=True):
        for key in filtro_keys:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    admin_seleccionado = selector_chips_sidebar(
        "Administrativo",
        sorted(df["Administrativo"].unique()),
        key="filtro_admin",
        expanded=True
    )

    tramo_seleccionado = selector_chips_sidebar(
        "Tramo de antigüedad",
        orden_tramos,
        key="filtro_tramo",
        expanded=True
    )

    estado_seleccionado = selector_chips_sidebar(
        "Estado control",
        orden_estado,
        key="filtro_estado",
        expanded=True
    )

    sta_seleccionado = selector_chips_sidebar(
        "STA",
        sorted(df["STA"].unique()),
        key="filtro_sta",
        expanded=False
    )

    marca_seleccionada = selector_chips_sidebar(
        "Marca",
        sorted(df["Marca"].unique()),
        key="filtro_marca",
        expanded=False
    )

with busqueda_sidebar:
    busqueda = st.text_input(
        "Buscar por ficha, producto, serie o descripción",
        key="busqueda_texto"
    )


df_filtrado = aplicar_filtros(
    df,
    admin_seleccionado,
    sta_seleccionado,
    marca_seleccionada,
    tramo_seleccionado,
    estado_seleccionado,
    busqueda
)


# --------------------------------------------------
# CORTE ANTERIOR Y MOVIMIENTOS
# --------------------------------------------------

fecha_anterior, df_anterior = obtener_corte_anterior(fecha_corte)

if df_anterior is not None:
    df_anterior_filtrado = aplicar_filtros(
        df_anterior,
        admin_seleccionado,
        sta_seleccionado,
        marca_seleccionada,
        tramo_seleccionado,
        estado_seleccionado,
        busqueda
    )
else:
    df_anterior_filtrado = None

movimientos = calcular_movimientos(df_filtrado, df_anterior_filtrado)

mov_admin = resumen_movimientos_por_dimension(movimientos, "Administrativo")
mov_sta = resumen_movimientos_por_dimension(movimientos, "STA")
mov_marca = resumen_movimientos_por_dimension(movimientos, "Marca")


# --------------------------------------------------
# RESUMEN ACTUAL Y ANTERIOR
# --------------------------------------------------

resumen_actual = calcular_resumen(df_filtrado)

if df_anterior_filtrado is not None:
    resumen_anterior = calcular_resumen(df_anterior_filtrado)
else:
    resumen_anterior = None


cutoff_strip(fecha_corte, fecha_anterior if resumen_anterior is not None else None)
section_header(
    "Resumen operativo del corte",
    "Indicadores base del stock STA filtrado y variación contra el corte anterior."
)


participacion_seguimiento = f"{formato_porcentaje(resumen_actual['Seguimiento'] / resumen_actual['Total productos'])} del stock" if resumen_actual["Total productos"] > 0 else "0,0% del stock"
participacion_atraso = f"{formato_porcentaje(resumen_actual['Productos >60 días'] / resumen_actual['Total productos'])} del stock" if resumen_actual["Total productos"] > 0 else "0,0% del stock"
participacion_critico = f"{formato_porcentaje(resumen_actual['Productos >120 días'] / resumen_actual['Total productos'])} del stock" if resumen_actual["Total productos"] > 0 else "0,0% del stock"
participacion_cp_60 = f"{formato_porcentaje(resumen_actual['CP >60 días'] / resumen_actual['CP total'])} del CP total" if resumen_actual["CP total"] > 0 else "0,0% del CP total"


c1, c2, c3, c4 = st.columns(4)

with c1:
    anterior = resumen_anterior["Total productos"] if resumen_anterior else None
    kpi_card(
        "Total productos STA",
        formato_numero(resumen_actual["Total productos"]),
        nota_kpi(
            "",
            texto_variacion_porcentual(resumen_actual["Total productos"], anterior)
        ),
        "green-card"
    )

with c2:
    anterior = resumen_anterior["CP total"] if resumen_anterior else None
    kpi_card(
        "CP total",
        formato_pesos(resumen_actual["CP total"]),
        nota_kpi(
            "",
            texto_variacion_porcentual(resumen_actual["CP total"], anterior, tipo="pesos")
        ),
        "green-card"
    )

with c3:
    anterior = resumen_anterior["Seguimiento"] if resumen_anterior else None
    kpi_card(
        "Seguimiento",
        formato_numero(resumen_actual["Seguimiento"]),
        nota_kpi(
            participacion_seguimiento,
            texto_variacion_porcentual(resumen_actual["Seguimiento"], anterior)
        ),
        "blue-card"
    )

with c4:
    anterior = resumen_anterior["Productos >60 días"] if resumen_anterior else None
    kpi_card(
        "Atrasados + críticos",
        formato_numero(resumen_actual["Productos >60 días"]),
        nota_kpi(
            participacion_atraso,
            texto_variacion_porcentual(resumen_actual["Productos >60 días"], anterior)
        ),
        "orange-card"
    )

c5, c6, c7, c8 = st.columns(4)

with c5:
    anterior = resumen_anterior["Productos >120 días"] if resumen_anterior else None
    kpi_card(
        "Críticos >120 días",
        formato_numero(resumen_actual["Productos >120 días"]),
        nota_kpi(
            participacion_critico,
            texto_variacion_porcentual(resumen_actual["Productos >120 días"], anterior)
        ),
        "red-card"
    )

with c6:
    anterior = resumen_anterior["CP >60 días"] if resumen_anterior else None
    kpi_card(
        "CP sobre 60 días",
        formato_pesos(resumen_actual["CP >60 días"]),
        nota_kpi(
            participacion_cp_60,
            texto_variacion_porcentual(resumen_actual["CP >60 días"], anterior, tipo="pesos")
        ),
        "orange-card"
    )

with c7:
    kpi_card(
        "Mediana días proceso",
        f"{resumen_actual['Mediana días']:.1f}".replace(".", ","),
        "Valor central del stock filtrado",
        "blue-card"
    )

with c8:
    kpi_card(
        "Máximo días proceso",
        formato_numero(resumen_actual["Máximo días"]),
        "Caso más antiguo del filtro",
        "red-card"
    )


# --------------------------------------------------
# TABLAS BASE
# --------------------------------------------------

resumen_tramos = (
    df_filtrado
    .groupby(["Tramo", "Estado Control"])
    .agg(
        Productos=("Id Ficha", "count"),
        CP=("CP", "sum")
    )
    .reset_index()
)

resumen_tramos["% productos"] = resumen_tramos["Productos"].apply(
    lambda x: porcentaje_puntos(x, resumen_actual["Total productos"])
)

resumen_tramos["% CP"] = resumen_tramos["CP"].apply(
    lambda x: porcentaje_puntos(x, resumen_actual["CP total"])
)

resumen_tramos["Tramo"] = pd.Categorical(
    resumen_tramos["Tramo"],
    categories=orden_tramos,
    ordered=True
)

resumen_tramos["Estado Control"] = pd.Categorical(
    resumen_tramos["Estado Control"],
    categories=orden_estado,
    ordered=True
)

resumen_tramos = resumen_tramos.sort_values(["Tramo", "Estado Control"])

resumen_admin = (
    df_filtrado
    .groupby("Administrativo")
    .agg(
        Total=("Id Ficha", "count"),
        Normal=("Estado Control", lambda x: int((x == "Normal").sum())),
        Seguimiento=("Estado Control", lambda x: int((x == "Seguimiento").sum())),
        Atrasado=("Estado Control", lambda x: int((x == "Atrasado").sum())),
        Critico=("Estado Control", lambda x: int((x == "Crítico").sum())),
        Sobre_60=("Días Proceso", lambda x: int((x > 60).sum())),
        Sobre_120=("Días Proceso", lambda x: int((x > 120).sum())),
        CP_Total=("CP", "sum"),
        Max_Dias=("Días Proceso", "max")
    )
    .reset_index()
)

cp_60_admin = (
    df_filtrado[df_filtrado["Días Proceso"] > 60]
    .groupby("Administrativo")
    .agg(CP_60=("CP", "sum"))
    .reset_index()
)

resumen_admin = resumen_admin.merge(cp_60_admin, on="Administrativo", how="left")
resumen_admin["CP_60"] = resumen_admin["CP_60"].fillna(0)
resumen_admin["% seguimiento"] = (resumen_admin["Seguimiento"] / resumen_admin["Total"]) * 100
resumen_admin["% atrasado"] = (resumen_admin["Atrasado"] / resumen_admin["Total"]) * 100
resumen_admin["% crítico"] = (resumen_admin["Critico"] / resumen_admin["Total"]) * 100
resumen_admin["% atraso"] = (resumen_admin["Sobre_60"] / resumen_admin["Total"]) * 100
resumen_admin = resumen_admin.sort_values(["Critico", "Atrasado", "Seguimiento"], ascending=False)

tabla_sta = (
    df_filtrado[df_filtrado["Días Proceso"] > 60]
    .groupby("STA")
    .agg(
        Productos=("Id Ficha", "count"),
        CP=("CP", "sum")
    )
    .reset_index()
    .sort_values(["Productos", "CP"], ascending=False)
    .head(10)
)

tabla_marca = (
    df_filtrado[df_filtrado["Días Proceso"] > 60]
    .groupby("Marca")
    .agg(
        Productos=("Id Ficha", "count"),
        CP=("CP", "sum")
    )
    .reset_index()
    .sort_values(["Productos", "CP"], ascending=False)
    .head(10)
)

lecturas = generar_lecturas(
    resumen_actual=resumen_actual,
    resumen_anterior=resumen_anterior,
    movimientos=movimientos,
    resumen_admin=resumen_admin,
    tabla_sta=tabla_sta,
    tabla_marca=tabla_marca,
    fecha_anterior=fecha_anterior,
    fecha_corte=fecha_corte
)

lectura_exportar = pd.DataFrame({
    "Sección": list(lecturas.keys()),
    "Lectura": list(lecturas.values())
})

postits_operativos = generar_postits_operativos(
    resumen_actual=resumen_actual,
    resumen_anterior=resumen_anterior,
    movimientos=movimientos,
    resumen_admin=resumen_admin,
    tabla_sta=tabla_sta,
    tabla_marca=tabla_marca,
    fecha_anterior=fecha_anterior,
    fecha_corte=fecha_corte
)

prioridades_operativas = generar_prioridades_operativas(
    resumen_admin=resumen_admin,
    tabla_sta=tabla_sta,
    tabla_marca=tabla_marca,
    resumen_actual=resumen_actual,
    movimientos=movimientos
)

fig_atrasos_admin = crear_figura_atrasos_admin(resumen_admin)
prioridad_semanal = preparar_prioridad_semanal(df_filtrado)


# --------------------------------------------------
# CONTROL OPERATIVO SIEMPRE VISIBLE
# --------------------------------------------------

st.divider()
section_header(
    "Control operativo semanal",
    "Vista de trabajo: prioridad, cambios del corte, antigüedad y acciones para la gestión administrativa STA."
)

mostrar_prioridades_operativas(prioridades_operativas)

col_visual, col_lectura = st.columns([1.2, 0.8])

with col_visual:
    st.markdown("#### Distribución por antigüedad")
    st.plotly_chart(crear_figura_tramos(resumen_tramos), use_container_width=True)

    if fig_atrasos_admin is not None:
        st.plotly_chart(fig_atrasos_admin, use_container_width=True)

    st.markdown("##### Semáforo operativo")
    st.dataframe(
        estilo_tabla_operativa(
            preparar_display_pesos(
                resumen_tramos,
                columnas_pesos=["CP"],
                columnas_porcentaje=["% productos", "% CP"]
            )
        ),
        use_container_width=True,
        hide_index=True
    )

    with st.expander("Ver criterio de clasificación de estados", expanded=False):
        st.dataframe(
            estilo_tabla_operativa(estado_definiciones),
            use_container_width=True,
            hide_index=True
        )

with col_lectura:
    st.markdown("#### Lectura operativa")

    for postit in postits_operativos:
        postit_card(
            titulo=postit["titulo"],
            texto=postit["texto"],
            clase=postit.get("clase", "info")
        )


# --------------------------------------------------
# MÓDULOS DE ANÁLISIS DETALLADO
# --------------------------------------------------

st.divider()
section_header(
    "Módulos de trabajo",
    "Revisión operativa por administrativo, cambios del corte, detalle descargable e histórico semanal."
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Administrativos",
        "Cambios semanales",
        "Detalle operativo",
        "Histórico"
    ]
)


with tab1:
    st.markdown("#### Carga y riesgo por administrativo")
    st.caption("Vista compacta para identificar quién concentra seguimiento, atraso, criticidad y CP asociado.")

    tabla_admin = resumen_admin.rename(
        columns={
            "Critico": "Crítico",
            "Sobre_60": ">60 días",
            "Sobre_120": ">120 días",
            "CP_Total": "CP total",
            "CP_60": "CP >60 días",
            "Max_Dias": "Máx días"
        }
    )

    columnas_admin_visibles = [
        "Administrativo",
        "Total",
        "Seguimiento",
        "Atrasado",
        "Crítico",
        ">60 días",
        ">120 días",
        "CP >60 días",
        "% atraso"
    ]
    columnas_admin_visibles = [col for col in columnas_admin_visibles if col in tabla_admin.columns]
    tabla_admin_visible = tabla_admin[columnas_admin_visibles].copy()

    col1, col2 = st.columns([1.15, 0.85])

    with col1:
        st.dataframe(
            estilo_tabla_operativa(
                preparar_display_pesos(
                    tabla_admin_visible,
                    columnas_pesos=["CP >60 días"],
                    columnas_porcentaje=["% atraso"]
                )
            ),
            use_container_width=True,
            hide_index=True
        )

        with st.expander("Ver resumen administrativo completo", expanded=False):
            st.dataframe(
                estilo_tabla_operativa(
                    preparar_display_pesos(
                        tabla_admin,
                        columnas_pesos=["CP total", "CP >60 días"],
                        columnas_porcentaje=["% seguimiento", "% atrasado", "% crítico", "% atraso"]
                    )
                ),
                use_container_width=True,
                hide_index=True
            )

    with col2:
        resumen_admin_grafico = resumen_admin.rename(columns={"Critico": "Crítico"}).copy()
        resumen_admin_grafico["Total foco operativo"] = (
            resumen_admin_grafico["Crítico"]
            + resumen_admin_grafico["Atrasado"]
            + resumen_admin_grafico["Seguimiento"]
        )
        resumen_admin_grafico = resumen_admin_grafico.sort_values(
            ["Crítico", "Atrasado", "Seguimiento", "Total"],
            ascending=False
        )

        fig_admin = px.bar(
            resumen_admin_grafico,
            x=["Seguimiento", "Atrasado", "Crítico"],
            y="Administrativo",
            orientation="h",
            title="Carga operativa por administrativo",
            labels={
                "value": "Productos",
                "Administrativo": "Administrativo",
                "variable": "Estado",
            },
            color_discrete_map=COLOR_ESTADOS
        )

        fig_admin.update_traces(
            texttemplate="%{x}",
            textposition="inside",
            insidetextanchor="middle",
            marker_line_width=0,
        )

        fig_admin.update_layout(
            title=dict(text="Carga operativa por administrativo", x=0.02, xanchor="left"),
            height=max(360, 48 * len(resumen_admin_grafico) + 125),
            barmode="stack",
            xaxis_title="Productos",
            yaxis_title="Administrativo",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#111827", size=12),
            title_font=dict(size=17, color="#111827"),
            xaxis=dict(gridcolor="#E5E7EB", rangemode="tozero"),
            yaxis=dict(
                categoryorder="array",
                categoryarray=resumen_admin_grafico["Administrativo"].tolist()[::-1]
            ),
            margin=dict(l=20, r=20, t=56, b=30),
            legend_title_text="Estado"
        )

        st.plotly_chart(fig_admin, use_container_width=True)

    st.markdown("#### Prioridad de gestión semanal")
    st.caption("Lista operativa ordenada por severidad, antigüedad y CP. Incluye Atrasado 61 a 120 días y Crítico sobre 120 días.")

    if prioridad_semanal.empty:
        st.info("No hay productos atrasados o críticos bajo el filtro actual.")
    else:
        st.dataframe(
            estilo_tabla_operativa(
                preparar_display_pesos(prioridad_semanal, columnas_pesos=["CP"])
            ),
            use_container_width=True,
            hide_index=True
        )


with tab2:
    if df_anterior_filtrado is None:
        st.info("No hay corte anterior registrado para calcular movimientos semanales.")
    else:
        st.markdown(
            f"#### Cambios respecto al corte anterior: {fecha_anterior.strftime('%d-%m-%Y')} "
            f"→ {fecha_corte.strftime('%d-%m-%Y')}"
        )

        stock_anterior = len(df_anterior_filtrado)
        stock_actual = len(df_filtrado)
        nuevos_total = len(movimientos["Nuevos"])
        salidos_total = len(movimientos["Salidos"])
        neto = stock_actual - stock_anterior

        pct_nuevos = porcentaje_puntos(nuevos_total, stock_anterior)
        pct_salidos = porcentaje_puntos(salidos_total, stock_anterior)
        pct_neto = porcentaje_puntos(neto, stock_anterior)

        m1, m2, m3, m4, m5 = st.columns(5)

        with m1:
            st.metric("Stock anterior", stock_anterior)

        with m2:
            st.metric("Nuevos", nuevos_total, f"{formato_porcentaje_puntos(pct_nuevos)} del stock anterior")

        with m3:
            st.metric("Salidos", salidos_total, f"{formato_porcentaje_puntos(pct_salidos)} del stock anterior")

        with m4:
            st.metric("Stock actual", stock_actual, f"{formato_porcentaje_puntos(pct_neto)} vs anterior")

        with m5:
            st.metric("Variación neta", neto, f"{formato_porcentaje_puntos(pct_neto)} vs anterior")

        st.info(generar_resumen_movimiento_operativo(mov_admin, movimientos))

        st.markdown("#### Resumen por responsable, STA y marca")

        r1, r2, r3 = st.tabs(
            [
                "Por administrativo",
                "Por STA",
                "Por marca"
            ]
        )

        with r1:
            st.dataframe(estilo_tabla_operativa(mov_admin), use_container_width=True, hide_index=True)

        with r2:
            st.dataframe(estilo_tabla_operativa(mov_sta), use_container_width=True, hide_index=True)

        with r3:
            st.dataframe(estilo_tabla_operativa(mov_marca), use_container_width=True, hide_index=True)

        st.markdown("#### Movimientos que requieren revisión")
        st.caption("Primero revisar deterioros, cambios a >60, cambios a >120 y casos que siguen críticos. Nuevos y salidos quedan como complemento.")

        sub1, sub2, sub3, sub4 = st.tabs(
            [
                "Empeoraron de tramo",
                "Pasaron >60",
                "Pasaron >120",
                "Siguen críticos"
            ]
        )

        with sub1:
            st.dataframe(
                estilo_tabla_operativa(
                    preparar_display_pesos(movimientos["Empeoraron de tramo"], columnas_pesos=["CP"])
                ),
                use_container_width=True,
                hide_index=True
            )

        with sub2:
            st.dataframe(
                estilo_tabla_operativa(
                    preparar_display_pesos(movimientos["Pasaron >60"], columnas_pesos=["CP"])
                ),
                use_container_width=True,
                hide_index=True
            )

        with sub3:
            st.dataframe(
                estilo_tabla_operativa(
                    preparar_display_pesos(movimientos["Pasaron >120"], columnas_pesos=["CP"])
                ),
                use_container_width=True,
                hide_index=True
            )

        with sub4:
            st.dataframe(
                estilo_tabla_operativa(
                    preparar_display_pesos(movimientos["Siguen críticos"], columnas_pesos=["CP"])
                ),
                use_container_width=True,
                hide_index=True
            )

        with st.expander("Ver detalle complementario: nuevos y salidos", expanded=False):
            comp1, comp2 = st.tabs(["Nuevos", "Salidos"])

            with comp1:
                st.dataframe(
                    estilo_tabla_operativa(
                        preparar_display_pesos(movimientos["Nuevos"], columnas_pesos=["CP"])
                    ),
                    use_container_width=True,
                    hide_index=True
                )

            with comp2:
                st.dataframe(
                    estilo_tabla_operativa(
                        preparar_display_pesos(movimientos["Salidos"], columnas_pesos=["CP"])
                    ),
                    use_container_width=True,
                    hide_index=True
                )


with tab3:
    st.markdown("#### Detalle operativo filtrable")
    st.caption("La tabla responde a los filtros del panel lateral. Usar búsqueda directa para ficha, producto, serie o descripción.")

    columnas_detalle = [
        "Id Ficha",
        "Id Producto",
        "Serie",
        "Estado",
        "Descripción",
        "Marca",
        "Familia",
        "Tipo Factura",
        "Tipo Gestión",
        "Comentario",
        "Administrativo",
        "STA",
        "Proveedor",
        "Días Rma",
        "Días Estado",
        "Días Proceso",
        "Estado ficha",
        "CP",
        "Tramo",
        "Estado Control"
    ]

    columnas_detalle = [col for col in columnas_detalle if col in df_filtrado.columns]

    detalle = df_filtrado[columnas_detalle].sort_values("Días Proceso", ascending=False)

    st.dataframe(
        estilo_tabla_operativa(
            preparar_display_pesos(detalle, columnas_pesos=["CP"])
        ),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("#### Descarga operativa")

    resumen_exportar = pd.DataFrame({
        "Indicador": list(resumen_actual.keys()),
        "Valor": list(resumen_actual.values())
    })

    archivo_excel = crear_excel_descarga(
        detalle,
        resumen_exportar,
        resumen_admin,
        resumen_tramos,
        estado_definiciones,
        movimientos,
        mov_admin,
        mov_sta,
        mov_marca,
        lectura_exportar
    )

    fecha_actual = datetime.now().strftime("%Y%m%d_%H%M")

    st.download_button(
        label="Descargar detalle operativo en Excel",
        data=archivo_excel,
        file_name=f"detalle_filtrado_sta_{fecha_actual}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


with tab4:
    st.markdown("#### Histórico semanal registrado")
    st.caption("Respaldo de tendencia. La gestión principal se realiza sobre el corte actual y los cambios del corte anterior.")

    historico_actualizado = cargar_historico()

    if historico_actualizado.empty:
        st.info("Todavía no hay cortes registrados.")
    else:
        resumen_historico = (
            historico_actualizado
            .groupby("Fecha Corte")
            .agg(
                Total_productos=("Id Ficha", "count"),
                CP_total=("CP", "sum"),
                Seguimiento=("Estado Control", lambda x: int((x == "Seguimiento").sum())),
                Atrasados=("Estado Control", lambda x: int((x == "Atrasado").sum())),
                Criticos=("Estado Control", lambda x: int((x == "Crítico").sum())),
                Productos_60=("Días Proceso", lambda x: int((x > 60).sum())),
                Productos_120=("Días Proceso", lambda x: int((x > 120).sum()))
            )
            .reset_index()
            .sort_values("Fecha Corte")
        )

        cp_60_hist = (
            historico_actualizado[historico_actualizado["Días Proceso"] > 60]
            .groupby("Fecha Corte")
            .agg(CP_60=("CP", "sum"))
            .reset_index()
        )

        cp_120_hist = (
            historico_actualizado[historico_actualizado["Días Proceso"] > 120]
            .groupby("Fecha Corte")
            .agg(CP_120=("CP", "sum"))
            .reset_index()
        )

        resumen_historico = resumen_historico.merge(cp_60_hist, on="Fecha Corte", how="left")
        resumen_historico = resumen_historico.merge(cp_120_hist, on="Fecha Corte", how="left")

        resumen_historico["CP_60"] = resumen_historico["CP_60"].fillna(0)
        resumen_historico["CP_120"] = resumen_historico["CP_120"].fillna(0)

        resumen_historico["% seguimiento"] = (
            resumen_historico["Seguimiento"] / resumen_historico["Total_productos"]
        ) * 100

        resumen_historico["% atrasados"] = (
            resumen_historico["Atrasados"] / resumen_historico["Total_productos"]
        ) * 100

        resumen_historico["% críticos"] = (
            resumen_historico["Criticos"] / resumen_historico["Total_productos"]
        ) * 100

        resumen_historico["% >60 días"] = (
            resumen_historico["Productos_60"] / resumen_historico["Total_productos"]
        ) * 100

        resumen_historico["% >120 días"] = (
            resumen_historico["Productos_120"] / resumen_historico["Total_productos"]
        ) * 100

        resumen_historico["Atrasados + críticos"] = resumen_historico["Productos_60"]

        historico_visible = resumen_historico[
            [
                "Fecha Corte",
                "Total_productos",
                "CP_total",
                "Atrasados + críticos",
                "Productos_120",
                "CP_60",
                "% >60 días",
                "% >120 días"
            ]
        ].rename(
            columns={
                "Total_productos": "Total productos",
                "CP_total": "CP total",
                "Productos_120": "Críticos >120",
                "CP_60": "CP >60"
            }
        )

        st.dataframe(
            estilo_tabla_operativa(
                preparar_display_pesos(
                    historico_visible,
                    columnas_pesos=["CP total", "CP >60"],
                    columnas_porcentaje=["% >60 días", "% >120 días"]
                )
            ),
            use_container_width=True,
            hide_index=True
        )

        with st.expander("Ver histórico completo", expanded=False):
            st.dataframe(
                estilo_tabla_operativa(
                    preparar_display_pesos(
                        resumen_historico,
                        columnas_pesos=["CP_total", "CP_60", "CP_120"],
                        columnas_porcentaje=[
                            "% seguimiento",
                            "% atrasados",
                            "% críticos",
                            "% >60 días",
                            "% >120 días"
                        ]
                    )
                ),
                use_container_width=True,
                hide_index=True
            )

        resumen_historico_grafico = resumen_historico.rename(columns={"Criticos": "Crítico"})

        col_hist1, col_hist2 = st.columns(2)

        with col_hist1:
            fig_stock = px.line(
                resumen_historico_grafico,
                x="Fecha Corte",
                y="Total_productos",
                markers=True,
                title="Evolución del stock total"
            )

            fig_stock.update_layout(
                height=345,
                xaxis_title="Fecha corte",
                yaxis_title="Productos",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#111827", size=12),
                title_font=dict(size=17, color="#111827"),
                yaxis=dict(gridcolor="#E5E7EB"),
                margin=dict(l=20, r=20, t=48, b=20)
            )

            st.plotly_chart(fig_stock, use_container_width=True)

        with col_hist2:
            fig_riesgo = px.line(
                resumen_historico_grafico,
                x="Fecha Corte",
                y=["Seguimiento", "Atrasados", "Crítico"],
                markers=True,
                title="Evolución del riesgo operativo",
                color_discrete_map={
                    "Seguimiento": COLOR_ESTADOS["Seguimiento"],
                    "Atrasados": COLOR_ESTADOS["Atrasado"],
                    "Crítico": COLOR_ESTADOS["Crítico"],
                }
            )

            fig_riesgo.update_layout(
                height=345,
                xaxis_title="Fecha corte",
                yaxis_title="Productos",
                legend_title_text="Estado",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#111827", size=12),
                title_font=dict(size=17, color="#111827"),
                yaxis=dict(gridcolor="#E5E7EB"),
                margin=dict(l=20, r=20, t=48, b=20)
            )

            st.plotly_chart(fig_riesgo, use_container_width=True)

st.markdown(
    """
    <div class="app-footer">
        Dashboard STA · Control operativo semanal · ▣ Desarrollado por <strong>Hugo Morales</strong>
    </div>
    """,
    unsafe_allow_html=True
)
