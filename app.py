"""Interfaz Streamlit para liquidar turnos por fecha y sede."""

from datetime import date, time, timedelta

import pandas as pd
import streamlit as st

from liquidacion import (
    DESCANSO,
    DIVISOR_HORAS,
    JORNADA_DIARIA_MAX,
    JORNADA_SEMANAL_MAX,
    RECARGO_DESCANSO_2026,
    SALARIO_MENSUAL,
    SEDES,
    calcular_periodo,
    moneda_cop,
)


st.set_page_config(
    page_title="Liquidador nacional | La Principal",
    page_icon="💛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
:root{--fondo:#080909;--panel:#121414;--amarillo:#ffd400;--texto:#f7f7f4;--muted:#b9b9b2;--borde:#34332a}
.stApp{background:radial-gradient(ellipse at 78% 0%,#282008 0,#0b0d0d 34%,var(--fondo) 75%);color:var(--texto)}
[data-testid="stHeader"]{background:transparent}.block-container{max-width:1240px;padding-top:1.8rem;padding-bottom:3rem}
h1,h2,h3,p,label,[data-testid="stMarkdownContainer"]{color:var(--texto)}
h1{font-size:clamp(2.1rem,5vw,3.4rem)!important;font-weight:800!important;letter-spacing:-.04em}
.eyebrow{display:inline-block;color:var(--amarillo);border:1px solid #6a5900;background:#211c04;border-radius:999px;padding:.42rem .8rem;font-size:.78rem;font-weight:700;letter-spacing:.14em}
.lead,.hint{color:var(--muted)}.lead{font-size:1.02rem;max-width:920px;line-height:1.65}.hint{font-size:.87rem}
.section-title{color:var(--amarillo);font-size:1.13rem;font-weight:750;margin:.9rem 0 .35rem}
div[data-testid="stTextInput"] input,div[data-testid="stDateInput"] input,div[data-testid="stNumberInput"] input{background:#101212;color:var(--texto);border-color:#414139;border-radius:9px}
div[data-testid="stSelectbox"] div[data-baseweb="select"]>div{background:#141615;color:var(--texto);border-color:#414139}
div.stButton>button[kind="primary"]{background:var(--amarillo);color:#111;border:0;border-radius:10px;font-weight:750;min-height:2.9rem}
div.stButton>button[kind="primary"]:hover{background:#ffe24a;color:#111}
[data-testid="stMetric"]{background:#141615;border:1px solid var(--borde);padding:1rem;border-radius:14px}
[data-testid="stMetricLabel"]{color:var(--muted)}[data-testid="stMetricValue"]{color:var(--amarillo)}
[data-testid="stExpander"]{background:#111313;border:1px solid var(--borde);border-radius:12px;margin:.35rem 0}
[data-testid="stDataFrame"]{border:1px solid var(--borde);border-radius:12px;overflow:hidden}hr{border-color:#34332a}footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

st.markdown('<span class="eyebrow">NÓMINA · COLOMBIA · TURNOS POR FECHA</span>', unsafe_allow_html=True)
st.title("Liquidador de horas extras y recargos")
st.markdown(
    '<p class="lead">Selecciona una sede, registra cada turno del calendario y consulta horas ordinarias, recargos nocturnos, extras y trabajo en día de descanso o festivo.</p>',
    unsafe_allow_html=True,
)

# El menú de sede aparece al inicio y determina los turnos que se pueden elegir.
sede = st.selectbox("Sede", list(SEDES.keys()), index=1, key="sede")
nombre = st.text_input("Nombre del colaborador", placeholder="Nombre del colaborador")

with st.expander("Parámetros del período y de jornada", expanded=True):
    p1, p2, p3 = st.columns(3)
    fecha_inicio = p1.date_input("Primera fecha del calendario", value=date(2026, 9, 24), format="DD/MM/YYYY")
    dias_contexto = p2.number_input("Fechas de calendario a registrar", min_value=13, max_value=31, value=14, step=1)
    limite_diario = p3.selectbox(
        "Límite diario ordinario",
        [JORNADA_DIARIA_MAX, 9],
        format_func=lambda n: "8 h (jornada general)" if n == 8 else "9 h (solo con acuerdo flexible)",
    )
    if limite_diario == 9:
        st.caption("Selecciona 9 horas únicamente si existe acuerdo de distribución flexible de jornada.")
    w1, w2 = st.columns(2)
    horas_previas = w1.number_input(
        "Horas trabajadas antes de la primera fecha en esa semana",
        min_value=0.0,
        max_value=42.0,
        value=0.0,
        step=0.5,
        help="Incluye las horas del lunes hasta el día anterior al inicio del calendario, si corresponde.",
    )
    recargo_descanso = w2.selectbox(
        "Recargo por descanso obligatorio o festivo",
        [RECARGO_DESCANSO_2026, 1.00],
        format_func=lambda n: "90 % · gradual legal 2026" if n == 0.90 else "100 % · si la empresa ya aplica el máximo",
    )

st.info(
    "El Excel cubre 14 fechas (24/09–07/10/2026). Marca exactamente 13 como parte del corte; "
    "la fecha de contexto no se paga, pero sus horas sí ayudan a clasificar el límite semanal."
)
st.markdown('<div class="section-title">Programación diaria</div>', unsafe_allow_html=True)
st.markdown(
    '<span class="hint">En cada fecha indica turno o descanso, día de descanso obligatorio/festivo y pausa no remunerada. Las pausas se excluyen del tiempo trabajado.</span>',
    unsafe_allow_html=True,
)

registros = []
opciones_turno = [DESCANSO, *SEDES[sede].keys()]
for indice in range(int(dias_contexto)):
    fecha = fecha_inicio + timedelta(days=indice)
    incluir_default = indice < 13
    dia_nombre = fecha.strftime("%A %d/%m/%Y")
    with st.expander(f"{dia_nombre.title()} · {sede}", expanded=indice == 0):
        c1, c2 = st.columns([1, 2])
        incluido = c1.checkbox(
            "Incluir en los 13 días del corte",
            value=incluir_default,
            key=f"incluido_{indice}",
        )
        turno = c2.selectbox("Turno de esta sede", opciones_turno, key=f"turno_{indice}")
        c3, c4, c5 = st.columns(3)
        descanso_obligatorio = c3.checkbox(
            "Día de descanso obligatorio",
            value=fecha.weekday() == 6,
            key=f"descanso_{indice}",
            help="Por defecto se marca domingo. Cambia la selección si el descanso fue pactado para otro día.",
        )
        festivo = c4.checkbox("Festivo trabajado", value=False, key=f"festivo_{indice}")
        tiene_pausa = c5.selectbox(
            "¿Tuvo pausa no remunerada?",
            ["Sin confirmar", "No", "Sí"],
            index=0,
            key=f"tiene_pausa_{indice}",
            disabled=turno == DESCANSO,
        )
        pausa_inicio = pausa_fin = None
        if turno != DESCANSO and tiene_pausa == "Sí":
            b1, b2 = st.columns(2)
            pausa_inicio = b1.time_input("Inicio de la pausa", value=None, key=f"pausa_ini_{indice}")
            pausa_fin = b2.time_input("Fin de la pausa", value=None, key=f"pausa_fin_{indice}")

        horario = SEDES[sede].get(turno)
        registros.append({
            "fecha": fecha,
            "turno": turno,
            "horario": horario,
            "incluido": incluido,
            "descanso_obligatorio": descanso_obligatorio,
            "festivo": festivo,
            "pausa_inicio": pausa_inicio,
            "pausa_fin": pausa_fin,
            "pausa_confirmada": turno == DESCANSO or tiene_pausa != "Sin confirmar",
        })

seleccionados = sum(1 for r in registros if r["incluido"])
st.markdown(f"**Días seleccionados para liquidar: {seleccionados} / 13**")

if st.button("Calcular liquidación", type="primary", use_container_width=True):
    errores = []
    if not nombre.strip():
        errores.append("Escribe el nombre del colaborador.")
    if seleccionados != 13:
        errores.append(f"Selecciona exactamente 13 días para liquidar; actualmente hay {seleccionados}.")
    sin_confirmar = [r["fecha"].strftime("%d/%m") for r in registros if not r["pausa_confirmada"]]
    if sin_confirmar:
        errores.append("Confirma si hubo pausa no remunerada en los turnos de: " + ", ".join(sin_confirmar))
    incompletas = [
        r["fecha"].strftime("%d/%m") for r in registros
        if r["turno"] != DESCANSO and bool(r["pausa_inicio"]) != bool(r["pausa_fin"])
    ]
    if incompletas:
        errores.append("Completa hora inicial y final de pausa para: " + ", ".join(incompletas))

    if errores:
        for error in errores:
            st.error(error)
    else:
        try:
            resultado = calcular_periodo(
                registros,
                sede,
                horas_antes_semana_inicial=horas_previas,
                limite_diario=limite_diario,
                recargo_descanso=recargo_descanso,
            )
        except ValueError as error:
            st.error(str(error))
        else:
            st.success(f"Liquidación calculada para {nombre.strip().upper()} · {sede} · 13 días.")
            m1, m2, m3 = st.columns(3)
            m1.metric("Pago de extras y recargos", moneda_cop(resultado["total_pago"]))
            m2.metric("Horas laboradas del corte", f'{resultado["total_horas"]:.2f} h')
            m3.metric("Valor de hora configurado", moneda_cop(resultado["valor_hora"]))

            tabla = [
                {
                    "Concepto": item["concepto"],
                    "Horas": round(item["horas"], 2),
                    "Factor aplicado": f'{item["factor"]:.0%}' if item["factor"] else "—",
                    "Pago": moneda_cop(item["pago"]),
                }
                for item in resultado["detalle"]
            ]
            st.dataframe(pd.DataFrame(tabla), hide_index=True, use_container_width=True)
            st.caption(
                f"SMLV: {moneda_cop(SALARIO_MENSUAL)} COP · Divisor configurado: {DIVISOR_HORAS} · "
                f"Jornada semanal: {JORNADA_SEMANAL_MAX} h · Recargo nocturno: 35 % · "
                f"Horas extra: 25 % diurna / 75 % nocturna."
            )
            excesos_dia = [f"{d:%d/%m}: {h:.2f} h" for d, h in resultado["extras_por_dia"].items() if h > 2]
            excesos_semana = [f"Semana {d:%d/%m}: {h:.2f} h" for d, h in resultado["extras_por_semana"].items() if h > 12]
            if excesos_dia or excesos_semana:
                st.warning(
                    "La programación supera el tope general de horas extra (2 diarias o 12 semanales): "
                    + "; ".join(excesos_dia + excesos_semana)
                )

st.divider()
st.caption(
    "El divisor de 220 horas se conserva por requisito del proyecto. La liquidación depende del acuerdo de jornada, "
    "del día de descanso pactado y de pausas realmente no remuneradas. Verifica las reglas aplicables a cada relación laboral."
)
st.markdown(
    "Fuentes normativas: [Ley 2466 de 2025](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=260676) · "
    "[Ley 2101 de 2021](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=166506)."
)
