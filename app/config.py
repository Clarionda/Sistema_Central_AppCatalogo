"""
Código Crítico - Tercer Semestre - Año 2026
Archivo de configuración central para la aplicación.
Define rutas, tablas de sincronización, intervalos y parámetros globales.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (opcional)
load_dotenv()

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

# Ruta de la base de datos local (SQLite)
DB_PATH = os.environ.get("DB_PATH", "catalogo.db")

# ============================================================
# CONFIGURACIÓN DE TURSO
# ============================================================

TURSO_URL = "https://distribuidora-clarionda.aws-ap-northeast-1.turso.io/v2/pipeline"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODIyNDE3MTEsImlkIjoiMDE5ZWY1ZTItMWQwMS03YmEyLTg4ODAtYmFmMWExYzcwNTYwIiwicmlkIjoiMThiYTc1YWYtN2JhZi00OTUwLWFiZDctNzAyYjZhMzc1ODZjIn0.fUcHC6wItczuWAPB9jhxbY57CMUy3_oRt_lRnZGuY7lwgZBfimqL4HIa7CpX3WqpFhJY7HUjsWDaqmn25hKEAQ"

# ============================================================
# INTERVALOS DE SINCRONIZACIÓN (3 segundos)
# ============================================================

SUBIDA_CADA_SEGUNDOS = 3   # Sube cambios cada 3 segundos
BAJADA_CADA_SEGUNDOS = 3   # Baja maestras cada 3 segundos

# ============================================================
# TABLAS PARTICIPANTES EN SINCRONIZACIÓN
# ============================================================

# Tablas que SUBEN a Turso (local -> Turso)
TABLAS_SUBIDA = [
    "clientes",
    "preventistas",
    "categorias",
    "notas_venta",
    "nota_venta_detalle",
    "cobros",
    "cuenta_corriente_movimientos",
    "posiciones_preventistas",
    "visitas_clientes"
]

# Tablas que BAJAN desde Turso (Turso -> local)
# NOTA: 'lotes' está excluido porque no tiene datos en Turso
TABLAS_BAJADA = [
    "clientes",
    "preventistas",
    "categorias"
]

# ============================================================
# OPCIONES ADICIONALES
# ============================================================

CACHE_IMAGENES_DIR = os.path.join(os.path.dirname(__file__), "cache_imagenes")

# ============================================================
# VALIDACIÓN DE CONFIGURACIÓN
# ============================================================

if not TURSO_TOKEN:
    print("ADVERTENCIA: TURSO_TOKEN no está configurado.")
else:
    print(f"✅ Configuración de Turso cargada correctamente.")
    print(f"   URL: {TURSO_URL}")
    print(f"   Token: {TURSO_TOKEN[:20]}...")
    print(f"   Subida cada: {SUBIDA_CADA_SEGUNDOS}s")
    print(f"   Bajada cada: {BAJADA_CADA_SEGUNDOS}s")