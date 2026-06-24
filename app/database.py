import sqlite3
import sys
import os
from pathlib import Path
from config import DB_PATH

def obtener_conexion():
    return sqlite3.connect(DB_PATH)

def inicializar_base_datos():
    if not Path(DB_PATH).exists():
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = Path(base_dir) / "script_creacion.sql"
        if not script_path.exists():
            raise FileNotFoundError(f"No se encuentra script_creacion.sql en {script_path}")
        with open(script_path, "r", encoding="utf-8") as f:
            sql = f.read()
        conn = obtener_conexion()
        conn.executescript(sql)
        conn.commit()
        conn.close()
        print("Base de datos inicializada correctamente.")
    else:
        print("Base de datos local ya existe.")

def ejecutar_consulta(query, params=None, commit=False):
    """Ejecuta SQL y devuelve:
       - Para SELECT: lista de diccionarios
       - Para otros: dict con 'filas_afectadas'
    """
    conn = obtener_conexion()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        if query.strip().upper().startswith("SELECT"):
            filas = cur.fetchall()
            resultado = [dict(fila) for fila in filas]
            conn.close()
            return resultado
        else:
            if commit:
                conn.commit()
            filas_afectadas = cur.rowcount
            conn.close()
            return {"filas_afectadas": filas_afectadas}
    except Exception as e:
        conn.close()
        raise e

def obtener_ultimo_timestamp_sync(tabla, direccion="up"):
    tabla_log = "sync_log" if direccion == "up" else "sync_log_reverse"
    filas = ejecutar_consulta(f"SELECT last_timestamp FROM {tabla_log} WHERE tabla = ?", (tabla,))
    if filas and len(filas) > 0:
        return filas[0]["last_timestamp"]
    ejecutar_consulta(f"INSERT OR IGNORE INTO {tabla_log} (tabla, last_timestamp) VALUES (?, ?)", (tabla, "1970-01-01T00:00:00"), commit=True)
    return "1970-01-01T00:00:00"

def actualizar_ultimo_timestamp_sync(tabla, timestamp, direccion="up"):
    tabla_log = "sync_log" if direccion == "up" else "sync_log_reverse"
    ejecutar_consulta(f"UPDATE {tabla_log} SET last_timestamp = ? WHERE tabla = ?", (timestamp, tabla), commit=True)