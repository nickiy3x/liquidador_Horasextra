"""Motor de cálculo por minuto para turnos, recargos y horas extra.

Reglas parametrizadas conforme a la legislación colombiana vigente desde julio
de 2026. El divisor mensual de 220 se conserva porque fue solicitado para este
proyecto; no se infiere automáticamente del límite semanal de jornada.
"""

from collections import defaultdict
from datetime import date, datetime, time, timedelta

SALARIO_MENSUAL = 1_750_905
DIVISOR_HORAS = 220  # Valor solicitado por el proyecto.
JORNADA_SEMANAL_MAX = 42
JORNADA_DIARIA_MAX = 8
RECARGO_NOCTURNO = 0.35
RECARGO_EXTRA_DIURNA = 0.25
RECARGO_EXTRA_NOCTURNA = 0.75
RECARGO_DESCANSO_2026 = 0.90

# Tiempos de entrada y salida indicados por el usuario (24 horas).
SEDES = {
    "Tocancipá": {
        "Turno mañana ordinaria (06:00–13:30)": (time(6), time(13, 30)),
        "Turno tarde ordinaria (12:00–19:30)": (time(12), time(19, 30)),
        "Turno noche ordinaria (19:30–06:00)": (time(19, 30), time(6)),
        "Sábado noche (19:30–06:00)": (time(19, 30), time(6)),
        "Domingo noche 1 (19:30–06:00)": (time(19, 30), time(6)),
        "Domingo noche 2 / festivo (19:30–06:00)": (time(19, 30), time(6)),
        "Lunes festivo–martes normal (19:30–06:00)": (time(19, 30), time(6)),
    },
    "Villavicencio": {
        "Nocturno normal (21:00–07:00)": (time(21), time(7)),
        "Sábado (21:00–07:00)": (time(21), time(7)),
        "Domingo 1 (21:00–07:00)": (time(21), time(7)),
        "Domingo 2 / festivo (21:00–07:00)": (time(21), time(7)),
        "Lunes festivo–martes normal (21:00–07:00)": (time(21), time(7)),
    },
    "Girón": {
        "Jueves (07:00–20:20)": (time(7), time(20, 20)),
        "Viernes (07:30–20:40)": (time(7, 30), time(20, 40)),
        "Sábado (07:30–18:40)": (time(7, 30), time(18, 40)),
        "Domingo (07:00–17:00)": (time(7), time(17)),
        "Lunes (07:00–18:50)": (time(7), time(18, 50)),
        "Martes (07:00–17:00)": (time(7), time(17)),
    },
    "Cartagena": {
        "Nocturno 1 (18:00–22:00)": (time(18), time(22)),
        "Nocturno 2 (18:00–23:00)": (time(18), time(23)),
    },
    "Barranquilla": {
        "Nocturno 1 / sábado / festivo (18:00–01:00)": (time(18), time(1)),
        "Nocturno 2 / dominical 2 (18:00–02:00)": (time(18), time(2)),
    },
    "Administrativos": {
        "Sábado (08:00–09:00)": (time(8), time(9)),
    },
}

DESCANSO = "Descanso"


def _minutos(hora):
    return hora.hour * 60 + hora.minute


def _instante_turno(fecha, hora_inicio, hora_fin):
    """Construye los extremos de un turno; si termina antes, acaba al día siguiente."""
    inicio = datetime.combine(fecha, hora_inicio)
    fin = datetime.combine(fecha, hora_fin)
    if fin <= inicio:
        fin += timedelta(days=1)
    return inicio, fin


def _instante_pausa(fecha, hora_pausa, hora_inicio):
    """Sitúa una hora de pausa en el mismo turno, incluso si cruza medianoche."""
    inicio_min = _minutos(hora_inicio)
    pausa_min = _minutos(hora_pausa)
    offset = (pausa_min - inicio_min) % (24 * 60)
    return datetime.combine(fecha, hora_inicio) + timedelta(minutes=offset)


def _segmentos_laborados(registro):
    """Devuelve los intervalos trabajados, excluyendo la pausa no remunerada."""
    fecha = registro["fecha"]
    hora_inicio, hora_fin = registro["horario"]
    inicio, fin = _instante_turno(fecha, hora_inicio, hora_fin)
    if not registro.get("pausa_inicio") or not registro.get("pausa_fin"):
        if bool(registro.get("pausa_inicio")) != bool(registro.get("pausa_fin")):
            raise ValueError(f"{fecha}: completa inicio y fin de la pausa.")
        return [(inicio, fin)]

    pausa_inicio = _instante_pausa(fecha, registro["pausa_inicio"], hora_inicio)
    pausa_fin = _instante_pausa(fecha, registro["pausa_fin"], hora_inicio)
    if pausa_fin <= pausa_inicio:
        pausa_fin += timedelta(days=1)
    if pausa_inicio < inicio or pausa_fin > fin or pausa_fin <= pausa_inicio:
        raise ValueError(f"{fecha}: la pausa debe quedar dentro del turno y durar más de cero minutos.")
    return [(inicio, pausa_inicio), (pausa_fin, fin)]


def calcular_periodo(registros, sede, horas_antes_semana_inicial=0,
                     limite_diario=JORNADA_DIARIA_MAX,
                     recargo_descanso=RECARGO_DESCANSO_2026):
    """Calcula pagos adicionales por minuto y fecha.

    Cada registro incluye fecha, turno, horario, incluido, descanso_obligatorio,
    festivo, pausa_inicio y pausa_fin. Un turno no laborado se omite. Las horas
    incluidas se pagan; una fecha de contexto excluida puede consumir cupo de la
    jornada semanal para clasificar correctamente las fechas siguientes.
    """
    if sede not in SEDES:
        raise ValueError(f"Sede no reconocida: {sede}")
    if limite_diario not in (8, 9):
        raise ValueError("El límite diario debe ser 8 horas o 9 con jornada flexible acordada.")
    if recargo_descanso not in (0.90, 1.00):
        raise ValueError("El recargo por descanso debe ser 90% o 100%.")

    valor_hora = SALARIO_MENSUAL / DIVISOR_HORAS
    conceptos = defaultdict(float)
    horas_tipo = defaultdict(float)
    horas_dia = defaultdict(int)
    horas_semana = defaultdict(int)
    extras_dia_corte = defaultdict(int)
    extras_semana_corte = defaultdict(int)
    semana_inicial = min((r["fecha"] for r in registros), default=date.today())
    lunes_inicial = semana_inicial - timedelta(days=semana_inicial.weekday())
    horas_semana[lunes_inicial] = int(round(float(horas_antes_semana_inicial) * 60))
    festivos = {r["fecha"] for r in registros if r.get("festivo")}
    descansos = {r["fecha"] for r in registros if r.get("descanso_obligatorio")}

    # Procesar cronológicamente permite aplicar el límite semanal de 42 horas.
    for registro in sorted(registros, key=lambda x: (x["fecha"], x.get("incluido", True) is False)):
        if registro.get("turno") == DESCANSO or registro.get("horario") is None:
            continue
        for tramo_inicio, tramo_fin in _segmentos_laborados(registro):
            instante = tramo_inicio
            while instante < tramo_fin:
                fecha_hora = instante.date()
                semana_minuto = fecha_hora - timedelta(days=fecha_hora.weekday())
                minuto_dia = instante.hour * 60 + instante.minute
                es_nocturna = minuto_dia >= 19 * 60 or minuto_dia < 6 * 60
                es_descanso = fecha_hora.weekday() == 6 or fecha_hora in descansos
                es_festivo = fecha_hora in festivos
                es_dia_especial = es_descanso or es_festivo

                es_extra = (
                    horas_dia[registro["fecha"]] >= limite_diario * 60
                    or horas_semana[semana_minuto] >= JORNADA_SEMANAL_MAX * 60
                )
                if es_extra and es_nocturna and es_dia_especial:
                    clave = "extra_nocturna_descanso"
                elif es_extra and es_nocturna:
                    clave = "extra_nocturna"
                elif es_extra and es_dia_especial:
                    clave = "extra_diurna_descanso"
                elif es_extra:
                    clave = "extra_diurna"
                elif es_nocturna and es_dia_especial:
                    clave = "nocturna_descanso"
                elif es_nocturna:
                    clave = "nocturna_ordinaria"
                elif es_dia_especial:
                    clave = "diurna_descanso"
                else:
                    clave = "diurna_ordinaria"

                # Todas las fechas afectan el cupo semanal; solo las marcadas
                # como incluidas producen pago en el período que se liquida.
                if es_extra and registro.get("incluido", True):
                    extras_dia_corte[registro["fecha"]] += 1
                    extras_semana_corte[semana_minuto] += 1
                horas_dia[registro["fecha"]] += 1
                horas_semana[semana_minuto] += 1
                if registro.get("incluido", True):
                    horas_tipo[clave] += 1 / 60
                instante += timedelta(minutes=1)

    # La hora extra se paga a tarifa total (1.25 o 1.75); las horas ordinarias
    # generan solo los recargos aplicables. Se suma el recargo dominical/festivo.
    factores = {
        "nocturna_ordinaria": RECARGO_NOCTURNO,
        "diurna_descanso": recargo_descanso,
        "nocturna_descanso": RECARGO_NOCTURNO + recargo_descanso,
        "extra_diurna": 1 + RECARGO_EXTRA_DIURNA,
        "extra_nocturna": 1 + RECARGO_EXTRA_NOCTURNA,
        "extra_diurna_descanso": 1 + RECARGO_EXTRA_DIURNA + recargo_descanso,
        "extra_nocturna_descanso": 1 + RECARGO_EXTRA_NOCTURNA + recargo_descanso,
    }
    etiquetas = {
        "diurna_ordinaria": "Hora ordinaria diurna (sin recargo)",
        "nocturna_ordinaria": "Recargo nocturno ordinario (35%)",
        "diurna_descanso": f"Recargo diurno en descanso/festivo ({recargo_descanso:.0%})",
        "nocturna_descanso": f"Nocturno + descanso/festivo ({RECARGO_NOCTURNO + recargo_descanso:.0%})",
        "extra_diurna": "Hora extra diurna (125% total)",
        "extra_nocturna": "Hora extra nocturna (175% total)",
        "extra_diurna_descanso": f"Extra diurna + descanso/festivo ({1 + RECARGO_EXTRA_DIURNA + recargo_descanso:.0%} total)",
        "extra_nocturna_descanso": f"Extra nocturna + descanso/festivo ({1 + RECARGO_EXTRA_NOCTURNA + recargo_descanso:.0%} total)",
    }
    detalle = []
    for clave, etiqueta in etiquetas.items():
        horas = horas_tipo[clave]
        factor = factores.get(clave, 0)
        # Las horas diurnas ordinarias no generan pago adicional.
        pago = horas * valor_hora * factor if clave != "diurna_ordinaria" else 0
        detalle.append({"concepto": etiqueta, "horas": horas, "factor": factor, "pago": pago})

    total_horas = sum(horas_tipo.values())
    total_pago = sum(item["pago"] for item in detalle)
    return {
        "salario": SALARIO_MENSUAL,
        "divisor": DIVISOR_HORAS,
        "valor_hora": valor_hora,
        "detalle": detalle,
        "horas": dict(horas_tipo),
        "extras_por_dia": {k: v / 60 for k, v in extras_dia_corte.items()},
        "extras_por_semana": {k: v / 60 for k, v in extras_semana_corte.items()},
        "total_horas": total_horas,
        "total_pago": total_pago,
    }


def moneda_cop(valor):
    """Representa un valor en COP con separadores de miles colombianos."""
    return f"${valor:,.0f}".replace(",", ".")
