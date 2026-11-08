"""Liquidador quincenal de turnos y recargos (SMLV 2026)."""
import streamlit as st

SALARIO_2026 = 1_750_905
DIAS_CORTE = 13


def calcular_liquidacion_quincenal(dias_manana_ord, dias_tarde_ord, dias_noche_ord,
                                   dias_sabado_n1, dias_domingo_n1, dias_dom_manana,
                                   dias_dom_tarde):
    """Calcula las horas y pagos adicionales con las reglas del ejercicio."""
    h_normales = dias_manana_ord * 7 + dias_tarde_ord * 6.3
    h_rec_nocturno = dias_tarde_ord * .3 + dias_noche_ord * 7 + dias_sabado_n1 * 4 + dias_domingo_n1 * 3
    h_extra_nocturna = dias_noche_ord * 2.3 + dias_domingo_n1 * 3
    h_rec_dom_diurno = dias_dom_manana * 7 + dias_dom_tarde * 6.3
    h_extra_noct_dom = dias_sabado_n1 * 2.3
    h_rec_noct_dom = dias_sabado_n1 * 3 + dias_dom_tarde * .3 + dias_domingo_n1 * 4
    valor_hora = SALARIO_2026 / 220
    horas = {
        "h_normales": h_normales,
        "h_rec_nocturno": h_rec_nocturno,
        "h_extra_nocturna": h_extra_nocturna,
        "h_rec_dom_diurno": h_rec_dom_diurno,
        "h_extra_noct_dom": h_extra_noct_dom,
        "h_rec_noct_dom": h_rec_noct_dom,
    }
    pagos = {
        "pago_rec_nocturno": h_rec_nocturno * valor_hora * .35,
        "pago_extra_nocturna": h_extra_nocturna * valor_hora * 1.75,
        "pago_rec_dom_diurno": h_rec_dom_diurno * valor_hora * .80,
        "pago_extra_noct_dom": h_extra_noct_dom * valor_hora * 2.55,
        "pago_rec_noct_dom": h_rec_noct_dom * valor_hora * 1.15,
    }
    return {
        "salario": SALARIO_2026, "valor_hora": valor_hora, **horas,
        "total_horas_novedades": sum(v for k, v in horas.items() if k != "h_normales"),
        **pagos, "total_pago_novedades": sum(pagos.values()),
    }


def formato_cop(valor):
    return f"${valor:,.0f}".replace(",", ".")


st.set_page_config(page_title="Liquidador de turnos | La Principal", page_icon="💛", layout="wide")
st.markdown("""
<style>
:root {--fondo:#080909;--panel:#111313;--amarillo:#ffd400;--texto:#f7f7f4;--muted:#b9b9b2;--borde:#34332a}
.stApp{background:radial-gradient(ellipse at 78% 0%,#282008 0,#0b0d0d 34%,var(--fondo) 75%);color:var(--texto)}
[data-testid="stHeader"]{background:transparent}.block-container{max-width:1180px;padding-top:2.2rem;padding-bottom:3rem}
h1,h2,h3,p,label,[data-testid="stMarkdownContainer"]{color:var(--texto)}
h1{font-size:clamp(2.2rem,5vw,3.7rem)!important;font-weight:800!important;letter-spacing:-.04em}
.eyebrow{display:inline-block;color:var(--amarillo);border:1px solid #6a5900;background:#211c04;border-radius:999px;padding:.42rem .8rem;font-size:.78rem;font-weight:700;letter-spacing:.14em}
.lead,.hint{color:var(--muted)}.lead{font-size:1.06rem;max-width:780px;line-height:1.7}.hint{font-size:.88rem}
.card-title{color:var(--amarillo);font-size:1.05rem;font-weight:750;margin:.6rem 0 .3rem}
div[data-testid="stNumberInput"] input,div[data-testid="stTextInput"] input{background:#101212;color:var(--texto);border-color:#414139;border-radius:10px}
div[data-testid="stNumberInput"] button{color:var(--amarillo);background:#20211e;border-color:#414139}
div.stButton>button[kind="primary"]{background:var(--amarillo);color:#111;border:0;border-radius:11px;font-weight:750;min-height:3rem}
div.stButton>button[kind="primary"]:hover{background:#ffe24a;color:#111}
[data-testid="stMetric"]{background:#141615;border:1px solid var(--borde);padding:1rem 1.15rem;border-radius:15px}
[data-testid="stMetricLabel"]{color:var(--muted)}[data-testid="stMetricValue"]{color:var(--amarillo)}
[data-testid="stDataFrame"]{border:1px solid var(--borde);border-radius:12px;overflow:hidden}hr{border-color:#34332a}footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

st.markdown('<span class="eyebrow">NÓMINA · COLOMBIA · CORTE DE 13 DÍAS</span>', unsafe_allow_html=True)
st.title("Liquidador de turnos y recargos")
st.markdown('<p class="lead">Registra la programación del colaborador y consulta el resumen de horas y recargos de la quincena. La interfaz adapta la identidad visual de La Principal con fondo negro carbón, amarillo dorado y texto blanco.</p>', unsafe_allow_html=True)

st.markdown('<div class="card-title">Datos del colaborador</div>', unsafe_allow_html=True)
nombre = st.text_input("Nombre del colaborador", placeholder="Escribe el nombre", label_visibility="collapsed")
st.caption("Salario base del ejercicio: $1.750.905 COP · divisor de 220 horas.")
st.markdown('<div class="card-title">Días trabajados por turno</div>', unsafe_allow_html=True)
st.markdown('<span class="hint">Ingresa días enteros. Los turnos más los días de descanso deben sumar exactamente 13.</span>', unsafe_allow_html=True)

turnos = [
    ("Mañana ordinaria", "06:00–13:30 · lunes a sábado"),
    ("Tarde ordinaria", "12:00–19:30 · lunes a sábado"),
    ("Noche ordinaria", "19:30–06:00 · lunes a viernes"),
    ("Sábado noche", "19:30–06:00"),
    ("Domingo noche", "19:30–06:00"),
    ("Domingo día", "06:00–13:30 · domingo/festivo"),
    ("Domingo tarde", "12:00–19:30 · domingo/festivo"),
]
valores = []
cols = st.columns(2)
for idx, (titulo, detalle) in enumerate(turnos):
    with cols[idx % 2]:
        valores.append(st.number_input(f"{titulo} — {detalle}", min_value=0, max_value=13, value=0, step=1, key=f"turno_{idx}"))
with cols[1]:
    dias_descanso = st.number_input("Días de descanso", min_value=0, max_value=13, value=0, step=1)

total_dias = sum(valores) + dias_descanso
st.markdown(f'<div class="hint">Días registrados: <b>{total_dias} / {DIAS_CORTE}</b></div>', unsafe_allow_html=True)
if st.button("Calcular liquidación", type="primary", use_container_width=True):
    if not nombre.strip():
        st.error("Escribe el nombre del colaborador para generar el resumen.")
    elif total_dias != DIAS_CORTE:
        st.error(f"El corte debe sumar exactamente {DIAS_CORTE} días. Actualmente registra {total_dias}.")
    else:
        res = calcular_liquidacion_quincenal(*valores)
        st.success(f"Liquidación calculada para {nombre.strip().upper()} · {DIAS_CORTE} días validados.")
        st.subheader("Resumen de la liquidación")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total adicional a pagar", formato_cop(res["total_pago_novedades"]))
        c2.metric("Horas de novedades", f'{res["total_horas_novedades"]:.1f} h')
        c3.metric("Horas ordinarias", f'{res["h_normales"]:.1f} h')
        filas = [
            ("Recargo nocturno normal (0,35)", "h_rec_nocturno", "pago_rec_nocturno"),
            ("Hora extra nocturna (1,75)", "h_extra_nocturna", "pago_extra_nocturna"),
            ("Recargo dominical diurno (0,80)", "h_rec_dom_diurno", "pago_rec_dom_diurno"),
            ("Hora extra nocturna dominical (2,55)", "h_extra_noct_dom", "pago_extra_noct_dom"),
            ("Recargo nocturno dominical (1,15)", "h_rec_noct_dom", "pago_rec_noct_dom"),
        ]
        st.dataframe([{"Concepto": nombre_fila, "Horas": f'{res[h]:.1f} h', "Valor": formato_cop(res[p])} for nombre_fila, h, p in filas], hide_index=True, use_container_width=True)
        st.caption(f"Salario base: {formato_cop(res['salario'])} COP · Valor hora ordinaria: {formato_cop(res['valor_hora'])} COP · Días de descanso: {dias_descanso}")

st.divider()
st.caption("Herramienta académica basada en las reglas y porcentajes incluidos en el código fuente del ejercicio.")
