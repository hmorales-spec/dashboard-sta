import io
import os
from datetime import datetime, date

import streamlit as st
import pandas as pd
import plotly.express as px


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
# --------------------------------------------------

st.markdown(
    """
    <style>
        .main-title {
            background: linear-gradient(90deg, #12372A 0%, #1F6F50 100%);
            padding: 22px 28px;
            border-radius: 14px;
            color: white;
            margin-bottom: 18px;
        }

        .main-title h1 {
            margin: 0;
            font-size: 34px;
        }

        .main-title p {
            margin: 6px 0 0 0;
            font-size: 15px;
            opacity: 0.92;
        }

        .kpi-card {
            padding: 20px 20px;
            border-radius: 14px;
            border: 1px solid #E6E6E6;
            background-color: #FFFFFF;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
            min-height: 132px;
        }

        .kpi-title {
            font-size: 16px;
            color: #4A4A4A;
            margin-bottom: 9px;
            font-weight: 700;
            line-height: 1.25;
        }

        .kpi-value {
            font-size: 32px;
            font-weight: 850;
            color: #111111;
            line-height: 1.1;
        }

        .kpi-note {
            font-size: 14px;
            margin-top: 9px;
            color: #555555;
            line-height: 1.35;
            font-weight: 500;
        }

        .green-card {
            border-left: 7px solid #2E7D32;
        }

        .orange-card {
            border-left: 7px solid #F9A825;
        }

        .red-card {
            border-left: 7px solid #C62828;
        }

        .blue-card {
            border-left: 7px solid #1976D2;
        }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="main-title">
        <h1>Dashboard STA</h1>
        <p>Control semanal de productos en Servicio Técnico Autorizado</p>
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

    texto = str(valor)
    texto = texto.replace("$", "")
    texto = texto.replace(" ", "")
    texto = texto.strip()

    if "," in texto and "." in texto:
        texto = texto.replace(".", "")
        texto = texto.replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    elif texto.count(".") > 1:
        texto = texto.replace(".", "")

    numero = pd.to_numeric(texto, errors="coerce")

    if pd.isna(numero):
        return 0.0

    return float(numero)


def formato_pesos(valor):
    if pd.isna(valor):
        return "$0"

    numero = float(valor)
    signo = "-" if numero < 0 else ""
    numero_abs = abs(numero)

    if abs(numero_abs - round(numero_abs)) < 0.005:
        texto = f"{int(round(numero_abs)):,.0f}"
    else:
        texto = f"{numero_abs:,.2f}"

    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")

    return f"{signo}${texto}"


def formato_numero(valor):
    return f"{valor:,.0f}".replace(",", ".")


def formato_porcentaje(valor):
    return f"{valor * 100:.1f}%".replace(".", ",")


def formato_porcentaje_puntos(valor):
    return f"{float(valor):.1f}%".replace(".", ",")


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


def kpi_card(titulo, valor, nota, clase):
    st.markdown(
        f"""
        <div class="kpi-card {clase}">
            <div class="kpi-title">{titulo}</div>
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


# --------------------------------------------------
# FUNCIONES DE HISTÓRICO
# --------------------------------------------------

def cargar_historico():
    if not os.path.exists(ARCHIVO_HISTORICO):
        return pd.DataFrame()

    historico = pd.read_csv(ARCHIVO_HISTORICO, dtype=str)

    historico["Fecha Corte"] = pd.to_datetime(
        historico["Fecha Corte"],
        errors="coerce"
    ).dt.date

    historico["Días Proceso"] = pd.to_numeric(
        historico["Días Proceso"],
        errors="coerce"
    ).fillna(0).astype(int)

    historico["CP"] = pd.to_numeric(
        historico["CP"],
        errors="coerce"
    ).fillna(0.0)

    historico["Estado Control"] = historico["Días Proceso"].apply(clasificar_estado_control)
    historico["Tramo"] = historico["Días Proceso"].apply(clasificar_tramo)

    return historico


def preparar_para_historico(df_base, fecha_corte):
    columnas_historico = [
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

    df_hist = df_base.copy()
    df_hist["Fecha Corte"] = fecha_corte.isoformat()

    for columna in columnas_historico:
        if columna not in df_hist.columns:
            df_hist[columna] = ""

    return df_hist[columnas_historico]


def registrar_corte(df_base, fecha_corte):
    nuevo_corte = preparar_para_historico(df_base, fecha_corte)

    historico_actual = cargar_historico()

    if not historico_actual.empty:
        historico_actual = historico_actual[historico_actual["Fecha Corte"] != fecha_corte]
        historico_actual["Fecha Corte"] = historico_actual["Fecha Corte"].astype(str)

        historico_final = pd.concat(
            [historico_actual, nuevo_corte],
            ignore_index=True
        )
    else:
        historico_final = nuevo_corte

    historico_final.to_csv(ARCHIVO_HISTORICO, index=False, encoding="utf-8-sig")


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

    if df_anterior is None or df_anterior.empty:
        movimientos["Nuevos"] = pd.DataFrame()
        movimientos["Salidos"] = pd.DataFrame()
        movimientos["Pasaron >60"] = pd.DataFrame()
        movimientos["Pasaron >120"] = pd.DataFrame()
        movimientos["Siguen críticos"] = pd.DataFrame()
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

    movimientos["Nuevos"] = tabla_simple(nuevos)
    movimientos["Salidos"] = tabla_simple(salidos)
    movimientos["Pasaron >60"] = tabla_movimiento_desde_merge(pasaron_60)
    movimientos["Pasaron >120"] = tabla_movimiento_desde_merge(pasaron_120)
    movimientos["Siguen críticos"] = tabla_movimiento_desde_merge(siguen_criticos)

    return movimientos


def resumen_movimientos_por_dimension(movimientos, dimension):
    nombres_mov = [
        "Nuevos",
        "Salidos",
        "Pasaron >60",
        "Pasaron >120",
        "Siguen críticos"
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
                "Siguen críticos"
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
            "Siguen críticos"
        ]
    ]

    resumen = resumen.sort_values(
        ["Siguen críticos", "Pasaron >120", "Pasaron >60", "Nuevos"],
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
        lectura_df.to_excel(writer, index=False, sheet_name="Lectura ejecutiva")
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
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Configuración")

fecha_corte = st.sidebar.date_input(
    "Fecha de corte del reporte",
    value=date.today()
)

archivo = st.file_uploader(
    "Carga aquí el archivo Excel del reporte STA",
    type=["xlsx"]
)

if archivo is None:
    st.info("Carga el archivo Excel para comenzar.")
    st.stop()


# --------------------------------------------------
# CARGA DE DATA
# --------------------------------------------------

try:
    excel = pd.ExcelFile(archivo)

    if "Reporte - Bandeja" not in excel.sheet_names:
        st.error("No se encontró la hoja 'Reporte - Bandeja'.")
        st.stop()

    df = pd.read_excel(archivo, sheet_name="Reporte - Bandeja")
    df = df.dropna(how="all")
    df.columns = df.columns.astype(str).str.strip()

except Exception as error:
    st.error("No se pudo leer el archivo Excel.")
    st.exception(error)
    st.stop()


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

columnas_faltantes = [columna for columna in columnas_requeridas if columna not in df.columns]

if columnas_faltantes:
    st.error("Faltan columnas necesarias en la hoja 'Reporte - Bandeja':")
    st.write(columnas_faltantes)
    st.stop()


# --------------------------------------------------
# PREPARACIÓN DE DATA
# --------------------------------------------------

df["Días Proceso"] = pd.to_numeric(df["Días Proceso"], errors="coerce").fillna(0).astype(int)
df["CP"] = df["CP"].apply(limpiar_cp)

df["Administrativo"] = df["Usuario Emisor"].fillna("Sin asignar").astype(str).str.strip()
df["Marca"] = df["Marca"].fillna("Sin marca").astype(str).str.strip()
df["STA"] = df["Sta"].fillna("Sin STA").astype(str).str.strip()

if "Familia" not in df.columns:
    df["Familia"] = ""

if "Proveedor" not in df.columns:
    df["Proveedor"] = ""

df["Familia"] = df["Familia"].fillna("Sin familia").astype(str).str.strip()
df["Proveedor"] = df["Proveedor"].fillna("Sin proveedor").astype(str).str.strip()

df.loc[df["STA"].isin(["", "651", "nan", "None"]), "STA"] = "Sin STA"

df["Tramo"] = df["Días Proceso"].apply(clasificar_tramo)
df["Estado Control"] = df["Días Proceso"].apply(clasificar_estado_control)

df["Llave"] = (
    df["Id Ficha"].astype(str).str.strip()
    + "|"
    + df["Id Producto"].astype(str).str.strip()
    + "|"
    + df["Serie"].astype(str).str.strip()
)

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


# --------------------------------------------------
# REGISTRO DE HISTÓRICO
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.header("Histórico semanal")

if st.sidebar.button("Registrar corte semanal"):
    registrar_corte(df, fecha_corte)
    st.sidebar.success(f"Corte {fecha_corte.strftime('%d-%m-%Y')} registrado correctamente.")

historico = cargar_historico()

if historico.empty:
    st.sidebar.info("Aún no hay histórico registrado.")
else:
    cortes_registrados = sorted(historico["Fecha Corte"].dropna().unique())
    st.sidebar.success(f"Cortes registrados: {len(cortes_registrados)}")
    st.sidebar.write([fecha.strftime("%d-%m-%Y") for fecha in cortes_registrados])


# --------------------------------------------------
# FILTROS
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.header("Filtros")

admin_seleccionado = st.sidebar.multiselect(
    "Administrativo",
    sorted(df["Administrativo"].unique())
)

sta_seleccionado = st.sidebar.multiselect(
    "STA",
    sorted(df["STA"].unique())
)

marca_seleccionada = st.sidebar.multiselect(
    "Marca",
    sorted(df["Marca"].unique())
)

tramo_seleccionado = st.sidebar.multiselect(
    "Tramo antigüedad",
    orden_tramos
)

estado_seleccionado = st.sidebar.multiselect(
    "Estado control",
    orden_estado
)

busqueda = st.sidebar.text_input(
    "Buscar por ficha, producto, serie o descripción"
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


st.markdown("### Resumen general")

if resumen_anterior is not None:
    st.caption(f"Comparación contra corte anterior: {fecha_anterior.strftime('%d-%m-%Y')}")
else:
    st.caption("Sin corte anterior registrado para comparar.")


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
        "CP atrasado + crítico",
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
    .sort_values("Productos", ascending=False)
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
    .sort_values("Productos", ascending=False)
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


# --------------------------------------------------
# VISUALIZACIONES
# --------------------------------------------------

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Lectura ejecutiva",
        "Resumen visual",
        "Foco administrativo",
        "Movimientos semana",
        "Detalle y descarga",
        "Histórico"
    ]
)


with tab1:
    st.markdown("#### Lectura automática del corte")

    st.info(lecturas["Lectura general"])
    st.info(lecturas["Lectura de movimientos"])
    st.warning(lecturas["Lectura de atraso"])
    st.error(lecturas["Lectura de críticos"])
    st.success(lecturas["Lectura de focos"])

    st.markdown("#### Definición de estados de control")

    st.dataframe(
        estado_definiciones,
        use_container_width=True,
        hide_index=True
    )


with tab2:
    col1, col2 = st.columns(2)

    with col1:
        fig_tramos = px.bar(
            resumen_tramos,
            x="Tramo",
            y="Productos",
            color="Estado Control",
            text="Productos",
            title="Productos STA por tramo y estado de control",
            color_discrete_map=COLOR_ESTADOS
        )

        fig_tramos.update_traces(textposition="outside")
        fig_tramos.update_layout(
            height=430,
            xaxis_title="Tramo",
            yaxis_title="Productos"
        )

        st.plotly_chart(fig_tramos, use_container_width=True)

    with col2:
        st.markdown("#### Semáforo de antigüedad")

        st.dataframe(
            preparar_display_pesos(
                resumen_tramos,
                columnas_pesos=["CP"],
                columnas_porcentaje=["% productos", "% CP"]
            ),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("#### Definición de estados de control")

    st.dataframe(
        estado_definiciones,
        use_container_width=True,
        hide_index=True
    )

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### STA con mayor atraso")

        st.dataframe(
            preparar_display_pesos(tabla_sta, columnas_pesos=["CP"]),
            use_container_width=True,
            hide_index=True
        )

    with col4:
        st.markdown("#### Marcas con mayor atraso")

        st.dataframe(
            preparar_display_pesos(tabla_marca, columnas_pesos=["CP"]),
            use_container_width=True,
            hide_index=True
        )


with tab3:
    col1, col2 = st.columns([1.2, 1])

    with col1:
        resumen_admin_grafico = resumen_admin.rename(columns={"Critico": "Crítico"})

        fig_admin = px.bar(
            resumen_admin_grafico,
            x="Administrativo",
            y=["Seguimiento", "Atrasado", "Crítico"],
            title="Productos por estado de control y administrativo",
            color_discrete_map=COLOR_ESTADOS
        )

        fig_admin.update_layout(
            height=430,
            xaxis_title="Administrativo",
            yaxis_title="Productos"
        )

        st.plotly_chart(fig_admin, use_container_width=True)

    with col2:
        st.markdown("#### Resumen por administrativo")

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

        st.dataframe(
            preparar_display_pesos(
                tabla_admin,
                columnas_pesos=["CP total", "CP >60 días"],
                columnas_porcentaje=["% seguimiento", "% atrasado", "% crítico", "% atraso"]
            ),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("#### Prioridad semanal: casos críticos STA >120 días")

    columnas_criticas = [
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

    criticos = (
        df_filtrado[df_filtrado["Días Proceso"] > 120]
        .sort_values("Días Proceso", ascending=False)
        .head(15)
    )

    st.dataframe(
        preparar_display_pesos(criticos[columnas_criticas], columnas_pesos=["CP"]),
        use_container_width=True,
        hide_index=True
    )


with tab4:
    if df_anterior_filtrado is None:
        st.info("No hay corte anterior registrado para calcular movimientos semanales.")
    else:
        st.markdown(
            f"#### Movimientos entre {fecha_anterior.strftime('%d-%m-%Y')} "
            f"y {fecha_corte.strftime('%d-%m-%Y')}"
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

        st.markdown("#### Resumen de movimientos por dimensión")

        r1, r2, r3 = st.tabs(
            [
                "Por administrativo",
                "Por STA",
                "Por marca"
            ]
        )

        with r1:
            st.dataframe(mov_admin, use_container_width=True, hide_index=True)

        with r2:
            st.dataframe(mov_sta, use_container_width=True, hide_index=True)

        with r3:
            st.dataframe(mov_marca, use_container_width=True, hide_index=True)

        st.markdown("#### Detalle de movimientos")

        sub1, sub2, sub3, sub4, sub5 = st.tabs(
            [
                "Nuevos",
                "Salidos",
                "Pasaron >60",
                "Pasaron >120",
                "Siguen críticos"
            ]
        )

        with sub1:
            st.dataframe(
                preparar_display_pesos(movimientos["Nuevos"], columnas_pesos=["CP"]),
                use_container_width=True,
                hide_index=True
            )

        with sub2:
            st.dataframe(
                preparar_display_pesos(movimientos["Salidos"], columnas_pesos=["CP"]),
                use_container_width=True,
                hide_index=True
            )

        with sub3:
            st.dataframe(
                preparar_display_pesos(movimientos["Pasaron >60"], columnas_pesos=["CP"]),
                use_container_width=True,
                hide_index=True
            )

        with sub4:
            st.dataframe(
                preparar_display_pesos(movimientos["Pasaron >120"], columnas_pesos=["CP"]),
                use_container_width=True,
                hide_index=True
            )

        with sub5:
            st.dataframe(
                preparar_display_pesos(movimientos["Siguen críticos"], columnas_pesos=["CP"]),
                use_container_width=True,
                hide_index=True
            )


with tab5:
    st.markdown("#### Detalle filtrable")

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
        preparar_display_pesos(detalle, columnas_pesos=["CP"]),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("#### Descarga")

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
        label="Descargar detalle filtrado en Excel",
        data=archivo_excel,
        file_name=f"detalle_filtrado_sta_{fecha_actual}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


with tab6:
    st.markdown("#### Histórico semanal registrado")

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

        st.dataframe(
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
            ),
            use_container_width=True,
            hide_index=True
        )

        resumen_historico_grafico = resumen_historico.rename(columns={"Criticos": "Crítico"})

        fig_hist = px.line(
            resumen_historico_grafico,
            x="Fecha Corte",
            y=["Total_productos", "Seguimiento", "Atrasados", "Crítico"],
            markers=True,
            title="Evolución semanal por estado de control",
            color_discrete_map={
                "Seguimiento": COLOR_ESTADOS["Seguimiento"],
                "Atrasados": COLOR_ESTADOS["Atrasado"],
                "Crítico": COLOR_ESTADOS["Crítico"],
            }
        )

        fig_hist.update_layout(
            height=430,
            xaxis_title="Fecha corte",
            yaxis_title="Productos"
        )

        st.plotly_chart(fig_hist, use_container_width=True)