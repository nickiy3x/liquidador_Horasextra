"""Lógica del liquidador tomada de la matriz del código recibido."""

SALARIO_2026 = 1_750_905.0
DIVISOR_MENSUAL = 220
DIAS_MINIMOS_CORTE = 13
DIAS_MAXIMOS_CORTE = 15

# E=normal, F=extra diurna, H=recargo nocturno, J=extra nocturna,
# L=recargo dominical diurno, N=extra nocturna dominical,
# P=extra diurna dominical, R=recargo nocturno dominical.
LETRAS_CONCEPTO = {
    "E": "Horas ordinarias normales",
    "F": "Hora extra diurna",
    "H": "Recargo nocturno normal",
    "J": "Hora extra nocturna",
    "L": "Recargo dominical diurno compensado",
    "N": "Hora extra nocturna dominical",
    "P": "Hora extra diurna dominical",
    "R": "Recargo nocturno dominical",
}

FACTORES_PAGO = {
    "F": 1.25,
    "H": 0.35,
    "J": 1.75,
    "L": 0.80,
    "N": 2.55,
    "P": 2.05,
    "R": 1.15,
}

MATRIZ_TURNOS = {
    "TOCANCIPÁ": {
        "Turno Mañana [06:00-13:30]": {"E": 7, "F": 0, "H": 0, "J": 0, "L": 0, "N": 0, "P": 0, "R": 0},
        "Turno Tarde [12:00-19:30]": {"E": 6.3, "F": 0, "H": 0.3, "J": 0, "L": 0, "N": 0, "P": 0, "R": 0},
        "Turno Noche [19:30-06:00]": {"E": 0, "F": 0, "H": 7, "J": 2.3, "L": 0, "N": 0, "P": 0, "R": 0},
        "Sábado Noche [19:30-06:00]": {"E": 0, "F": 0, "H": 4, "J": 0, "L": 0, "N": 2.3, "P": 0, "R": 3},
        "Domingo Noche [19:30-06:00]": {"E": 0, "F": 0, "H": 3, "J": 3, "L": 0, "N": 0, "P": 0, "R": 4},
        "Domingo Día [06:00-13:30]": {"E": 0, "F": 0, "H": 0, "J": 0, "L": 7, "N": 0, "P": 0, "R": 0},
        "Domingo Tarde [12:00-19:30]": {"E": 0, "F": 0, "H": 0, "J": 0, "L": 6.3, "N": 0, "P": 0, "R": 0.3},
    },
    "BARRANQUILLA": {
        "NOCT1-REF LABORAL [6:00 PM - 1:00 AM]": {"E": 1, "F": 0, "H": 6, "J": 0, "L": 0, "N": 0, "P": 0, "R": 0},
        "NOCT2-REF LABORAL [6:00 PM - 2:00 AM]": {"E": 1, "F": 0, "H": 7, "J": 0, "L": 0, "N": 0, "P": 0, "R": 0},
        "SAB NOC 1 [6:00 PM - 1:00 AM]": {"E": 1, "F": 0, "H": 5, "J": 0, "L": 0, "N": 0, "P": 0, "R": 1},
        "DOMINICAL TURNO 1 [6:00 PM - 1:00 AM]": {"E": 0, "F": 0, "H": 1, "J": 0, "L": 1, "N": 0, "P": 0, "R": 5},
        "DOMINICAL TURNO 2 [6:00 PM - 2:00 AM]": {"E": 0, "F": 0, "H": 2, "J": 0, "L": 1, "N": 0, "P": 0, "R": 5},
        "FESTIVO TURNO 1 [6:00 PM - 1:00 AM]": {"E": 0, "F": 0, "H": 0, "J": 0, "L": 1, "N": 0, "P": 0, "R": 6},
        "NOCT1-normal [11:00 PM - 06:00 AM]": {"E": 0, "F": 0, "H": 7, "J": 0, "L": 0, "N": 0, "P": 0, "R": 0},
        "NOCT2-normal [10:00 PM - 06:00 AM]": {"E": 0, "F": 0, "H": 8, "J": 0, "L": 0, "N": 0, "P": 0, "R": 0},
        "NOCT2-SABADO [11:00 PM - 06:00 AM]": {"E": 0, "F": 0, "H": 1, "J": 0, "L": 0, "N": 0, "P": 0, "R": 6},
        "DOMINGO TURNO 6 A 2 [06:00 PM - 02:00 AM]": {"E": 0, "F": 0, "H": 2, "J": 0, "L": 1, "N": 0, "P": 0, "R": 5},
        "NOCT 4-DOM REFORMA [11:00 PM - 06:00 AM]": {"E": 0, "F": 0, "H": 6, "J": 0, "L": 0, "N": 0, "P": 0, "R": 1},
        "FESTIVO [11:00 PM - 06:00 AM]": {"E": 0, "F": 0, "H": 0, "J": 0, "L": 0, "N": 0, "P": 0, "R": 7},
    },
    "FÓRMULA 1": {
        "REC NORM [07:00 PM - 03:00 AM]": {"E": 0, "F": 0, "H": 8, "J": 0, "L": 0, "N": 0, "P": 0, "R": 0},
        "REC NORM [07:00 PM - 02:00 AM]": {"E": 0, "F": 0, "H": 7, "J": 0, "L": 0, "N": 0, "P": 0, "R": 0},
        "REC SABADO [07:00 PM - 01:00 AM]": {"E": 0, "F": 0, "H": 5, "J": 0, "L": 0, "N": 0, "P": 0, "R": 1},
        "FESTIVO LUNES [07:00 PM - 02:00 AM]": {"E": 0, "F": 0, "H": 0, "J": 0, "L": 0, "N": 0, "P": 0, "R": 7},
        "TURNO 9 HORAS (N2) [06:00 PM - 03:00 AM]": {"E": 0, "F": 0, "H": 6, "J": 0, "L": 0, "N": 0, "P": 0, "R": 0},
    },
}


def calcular_liquidacion(sede, dias_por_turno, dias_descanso):
    """Calcula horas por concepto y pagos con la matriz del código suministrado."""
    if sede not in MATRIZ_TURNOS:
        raise ValueError(f"Sede no reconocida: {sede}")
    if not isinstance(dias_descanso, int) or dias_descanso < 0:
        raise ValueError("Los días de descanso deben ser un entero no negativo.")

    turnos_validos = MATRIZ_TURNOS[sede]
    if set(dias_por_turno) != set(turnos_validos):
        raise ValueError("Los días ingresados deben corresponder exactamente a los turnos de la sede.")
    for turno, dias in dias_por_turno.items():
        if not isinstance(dias, int) or dias < 0:
            raise ValueError(f"Los días de '{turno}' deben ser un entero no negativo.")

    total_dias = sum(dias_por_turno.values()) + dias_descanso
    if not DIAS_MINIMOS_CORTE <= total_dias <= DIAS_MAXIMOS_CORTE:
        raise ValueError(
            f"El corte debe sumar entre {DIAS_MINIMOS_CORTE} y {DIAS_MAXIMOS_CORTE} días; ingresaste {total_dias}."
        )

    horas = {letra: 0.0 for letra in LETRAS_CONCEPTO}
    for turno, cantidad_dias in dias_por_turno.items():
        for letra, horas_turno in turnos_validos[turno].items():
            horas[letra] += cantidad_dias * horas_turno

    valor_hora = SALARIO_2026 / DIVISOR_MENSUAL
    pagos = {letra: horas[letra] * valor_hora * factor for letra, factor in FACTORES_PAGO.items()}
    total_horas_novedades = sum(horas.values()) - horas["E"]
    total_pago = sum(pagos.values())

    return {
        "sede": sede,
        "total_dias": total_dias,
        "dias_descanso": dias_descanso,
        "salario": SALARIO_2026,
        "divisor": DIVISOR_MENSUAL,
        "valor_hora": valor_hora,
        "horas": horas,
        "pagos": pagos,
        "total_horas_novedades": total_horas_novedades,
        "total_pago": total_pago,
    }


def moneda_cop(valor):
    """Formatea valores en pesos colombianos sin decimales."""
    return f"${valor:,.0f}".replace(",", ".")
