# Liquidador de turnos y recargos · SMLV 2026

Aplicación Streamlit con interfaz negro carbón, amarillo dorado y blanco, conservada del diseño anterior. Los inputs y cálculos cambian dinámicamente según la sede.

## Sedes incluidas

- Tocancipá
- Barranquilla
- Fórmula 1

La aplicación valida que los días por turno más los días de descanso sumen entre **13 y 15 días**. Usa el SMLV fijo de **$1.750.905 COP** y divisor de **220 horas**.

## Archivos

- `app.py`: interfaz gráfica Streamlit.
- `liquidacion.py`: matriz de horarios, factores y cálculo compartido.
- `Liquidador_Horas_Extra.ipynb`: versión autocontenida para Jupyter Notebook o Google Colab.
- `requirements.txt`: dependencias.

El motor conserva las matrices, los conceptos y los factores exactamente como aparecen en el código fuente entregado. Los valores y su interpretación deben verificarse antes de usar el resultado como liquidación laboral definitiva.

## Probar en Jupyter o Google Colab

Abre `Liquidador_Horas_Extra.ipynb` y ejecuta las celdas en orden. En la segunda sección, selecciona una sede y ajusta los días de cada turno y descanso. El notebook incluye el motor completo, sin depender de Streamlit.

## Ejecutar localmente

Requiere Python 3.10 o superior.

```bash
python -m venv .venv
```

En Windows PowerShell, activa el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instala las dependencias e inicia la aplicación:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Publicar en GitHub

1. Crea un repositorio en GitHub.
2. En esta carpeta, inicializa Git si aún no está inicializado.
3. Agrega y confirma `app.py`, `liquidacion.py`, `Liquidador_Horas_Extra.ipynb`, `requirements.txt`, `README.md` y `.gitignore`.
4. Configura el repositorio de GitHub como remoto y publica la rama principal.

El archivo Excel de programación está excluido en `.gitignore` porque contiene datos de colaboradores y no es necesario para ejecutar la app.

## Desplegar en Streamlit Community Cloud

1. Publica los archivos del proyecto en GitHub.
2. En Streamlit Community Cloud, crea una aplicación y conecta el repositorio.
3. Selecciona la rama principal y establece `app.py` como archivo principal.
4. Despliega. Streamlit instalará las dependencias declaradas en `requirements.txt`.
