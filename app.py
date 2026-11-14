"""Interfaz Streamlit del liquidador nacional."""

import pandas as pd
import streamlit as st

from liquidacion import (
    DIAS_MAXIMOS_CORTE,
    DIAS_MINIMOS_CORTE,
    FACTORES_PAGO,
    LETRAS_CONCEPTO,
    MATRIZ_TURNOS,
    SALARIO_2026,
    calcular_liquidacion,
    moneda_cop,
)


st.set_page_config(
    page_title="Liquidador de turnos | La Principal",
    page_icon="💛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Paleta y componentes visuales conservados: negro carbón, amarillo y blanco.
st.markdown("""
<style>
:root{--fondo:#080909;--panel:#111313;--panel-2:#171918;--amarillo:#ffd400;--amarillo-suave:#ffe24a;--texto:#f7f7f4;--muted:#b9b9b2;--borde:#34332a}
.stApp{background:radial-gradient(ellipse at 78% 0%,#282008 0,#0b0d0d 34%,var(--fondo) 75%);color:var(--texto)}
[data-testid="stHeader"]{background:transparent}.block-container{max-width:1180px;padding-top:2.2rem;padding-bottom:3rem}
h1,h2,h3,p,label,[data-testid="stMarkdownContainer"]{color:var(--texto)}
h1{font-size:clamp(2.2rem,5vw,3.7rem)!important;font-weight:800!important;letter-spacing:-.04em}
.eyebrow{display:inline-block;color:var(--amarillo);border:1px solid #6a5900;background:#211c04;border-radius:999px;padding:.42rem .8rem;font-size:.78rem;font-weight:700;letter-spacing:.14em}
.lead{color:var(--muted);font-size:1.06rem;max-width:820px;line-height:1.7}
.section-title{color:var(--amarillo);font-size:1.05rem;font-weight:750;margin:.7rem 0 .25rem}
.hint{color:var(--muted);font-size:.88rem}
div[data-testid="stNumberInput"] input,div[data-testid="stTextInput"] input{background:#101212;color:var(--texto);border-color:#414139;border-radius:10px}
div[data-testid="stNumberInput"] button{color:var(--amarillo);background:#20211e;border-color:#414139}
div[data-testid="stSelectbox"] div[data-baseweb="select"]>div{background:#141615;color:var(--texto);border-color:#414139}
div.stButton>button[kind="primary"]{background:var(--amarillo);color:#111;border:0;border-radius:11px;font-weight:750;min-height:3rem}
div.stButton>button[kind="primary"]:hover{background:var(--amarillo-suave);color:#111}
[data-testid="stMetric"]{background:#141615;border:1px solid var(--borde);padding:1rem 1.15rem;border-radius:15px}
[data-testid="stMetricLabel"]{color:var(--muted)}[data-testid="stMetricValue"]{color:var(--amarillo)}
[data-testid="stDataFrame"]{border:1px solid var(--borde);border-radius:12px;overflow:hidden}
hr{border-color:#34332a}footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

st.markdown('<span class="eyebrow">NÓMINA · COLOMBIA · SMLV 2026</span>', unsafe_allow_html=True)
st.title("Liquidador de turnos y recargos")
st.markdown(
    '<p class="lead">Selecciona la sede, registra cuántos días se trabajó en cada turno y consulta el resumen de horas y recargos del corte.</p>',
    unsafe_allow_html=True,
)

# La sede se elige al inicio. La matriz elegida controla los inputs visibles.
sede = st.selectbox("Sede", list(MATRIZ_TURNOS.keys()), key="sede")
nombre = st.text_input("Nombre del colaborador", placeholder="Escribe el nombre")

st.markdown('<div class="section-title">Días laborados por turno</div>', unsafe_allow_html=True)
st.markdown(
    f'<span class="hint">Ingresa cantidades enteras no negativas. La suma de turnos y descansos debe estar entre {DIAS_MINIMOS_CORTE} y {DIAS_MAXIMOS_CORTE} días.</span>',
    unsafe_allow_html=True,
)

dias_por_turno = {}
columnas = st.columns(2)
for indice, turno in enumerate(MATRIZ_TURNOS[sede]):
    with columnas[indice % 2]:
        dias_por_turno[turno] = st.number_input(
            turno,
            min_value=0,
            max_value=15,
            value=0,
            step=1,
            key=f"dias_{sede}_{indice}",
        )

with columnas[1]:
    dias_descanso = st.number_input(
        "Días de descanso en el corte",
        min_value=0,
        max_value=15,
        value=0,
        step=1,
        key=f"descanso_{sede}",
    )

total_dias = sum(dias_por_turno.values()) + dias_descanso
st.markdown(
    f'<div class="hint">Días registrados: <b>{total_dias}</b> · Rango aceptado: {DIAS_MINIMOS_CORTE}–{DIAS_MAXIMOS_CORTE}</div>',
    unsafe_allow_html=True,
)

if st.button("Calcular liquidación", type="primary", use_container_width=True):
    if not nombre.strip():
        st.error("Escribe el nombre del colaborador para generar el resumen.")
    elif not DIAS_MINIMOS_CORTE <= total_dias <= DIAS_MAXIMOS_CORTE:
        st.error(
            f"El corte debe sumar entre {DIAS_MINIMOS_CORTE} y {DIAS_MAXIMOS_CORTE} días. "
            f"Actualmente registra {total_dias}."
        )
    else:
        resultado = calcular_liquidacion(sede, dias_por_turno, dias_descanso)
        st.success(
            f"Liquidación calculada para {nombre.strip().upper()} · {sede} · "
            f"{resultado['total_dias']} días validados."
        )
        st.subheader("Resumen de liquidación")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total adicional a pagar", moneda_cop(resultado["total_pago"]))
        m2.metric("Horas extras y recargos", f'{resultado["total_horas_novedades"]:.2f} h')
        m3.metric("Horas ordinarias normales", f'{resultado["horas"]["E"]:.2f} h')

        filas = []
        for letra, concepto in LETRAS_CONCEPTO.items():
            factor = FACTORES_PAGO.get(letra)
            filas.append({
                "Concepto": concepto,
                "Horas": round(resultado["horas"][letra], 2),
                "Factor": f"{factor:.2f}" if factor is not None else "—",
                "Valor": moneda_cop(resultado["pagos"].get(letra, 0)),
            })
        st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
        st.caption(
            f"Salario base: {moneda_cop(SALARIO_2026)} COP · "
            f"Valor hora ordinaria ({resultado['divisor']} h): {moneda_cop(resultado['valor_hora'])} COP · "
            f"Días de descanso: {resultado['dias_descanso']}"
        )

st.divider()
st.caption("El cálculo utiliza la matriz de turnos y los factores incluidos en el código suministrado.")
