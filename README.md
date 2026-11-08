# Liquidador de turnos y recargos

Aplicación Streamlit para calcular las horas de novedades y el pago adicional de una quincena, siguiendo las reglas del ejercicio académico para el SMLV 2026.

La interfaz toma como referencia visual la imagen de La Principal: fondo negro carbón, paneles oscuros, amarillo dorado para acciones y cifras, y texto blanco. La paleta está definida directamente en `app.py`; la imagen no es necesaria para ejecutar o desplegar la aplicación.

## Requisitos

- Python 3.10 o superior.
- Dependencias indicadas en `requirements.txt`.

## Ejecución local

```bash
python -m venv .venv
```

Activa el entorno virtual y ejecuta:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

En Windows PowerShell, activa el entorno con `\.venv\Scripts\Activate.ps1`.

## Publicación en GitHub

1. Crea un repositorio vacío en GitHub.
2. Desde esta carpeta, inicializa Git si hace falta, agrega los archivos del proyecto y crea un commit.
3. Configura la URL del repositorio como remoto `origin` y publica la rama principal.

Los archivos necesarios son `app.py`, `requirements.txt`, `README.md` y `.gitignore`. `LNF_LAPRINCIPAL.png` puede permanecer como referencia local; la app no la carga ni depende de ella.

## Despliegue en Streamlit Community Cloud

1. Publica los archivos en la rama principal del repositorio de GitHub.
2. En Streamlit Community Cloud, crea una aplicación y conéctala al repositorio.
3. Selecciona la rama principal y usa `app.py` como archivo principal.
4. Despliega. Streamlit instalará lo declarado en `requirements.txt`.

## Reglas incluidas

El formulario solicita siete categorías de turnos y los días de descanso; deben sumar exactamente 13 días. Conserva las horas por turno, el salario base de $1.750.905 COP, el divisor de 220 horas y los factores de recargo del código suministrado.

> Este proyecto implementa las reglas del ejercicio proporcionado. Verifica las tarifas y reglas laborales vigentes antes de usarlo en liquidaciones reales.
