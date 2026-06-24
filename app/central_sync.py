#!/usr/bin/env python3
import os
import sys
import time
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import libsql_experimental as libsql

load_dotenv()

DB_PATH = os.environ.get("DB_PATH", "distribuidora.db")
TURSO_URL = os.environ.get("TURSO_URL", "https://distribuidora-db-clarionda.aws-us-east-1.turso.io")
TURSO_TOKEN = os.environ.get("TURSO_TOKEN")

if not TURSO_TOKEN:
    print("Error: Falta TURSO_TOKEN en .env")
    sys.exit(1)

# Limpiar URL (eliminar /v2/pipeline si está)
if TURSO_URL.endswith("/v2/pipeline"):
    TURSO_URL = TURSO_URL.replace("/v2/pipeline", "")

SUBIDA_INTERVALO = int(os.environ.get("SUBIDA_CADA_SEGUNDOS", 30))
BAJADA_INTERVALO = int(os.environ.get("BAJADA_CADA_SEGUNDOS", 60))

# Tablas que el CENTRAL sube (maestras)
TABLAS_SUBIDA = ["clientes", "productos", "preventistas", "categorias", "usuarios"]
# Tablas que el CENTRAL baja (transacciones generadas por tablets)
TABLAS_BAJADA = ["notas_venta", "nota_venta_detalle", "cobros", "cuenta_corriente_movimientos", "cheques"]

# ------------------------------------------------------------
# Funciones para base local
# ------------------------------------------------------------
def obtener_conexion():
    return sqlite3.connect(DB_PATH)

def ejecutar_consulta(query, params=None, commit=False):
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
    # Asegurar que la tabla_log existe
    ejecutar_consulta(f"CREATE TABLE IF NOT EXISTS {tabla_log} (tabla TEXT PRIMARY KEY, last_timestamp TEXT DEFAULT '1970-01-01T00:00:00')", commit=True)
    filas = ejecutar_consulta(f"SELECT last_timestamp FROM {tabla_log} WHERE tabla = ?", (tabla,))
    if filas:
        return filas[0]["last_timestamp"]
    ejecutar_consulta(f"INSERT OR IGNORE INTO {tabla_log} (tabla, last_timestamp) VALUES (?, ?)", (tabla, "1970-01-01T00:00:00"), commit=True)
    return "1970-01-01T00:00:00"

def actualizar_ultimo_timestamp_sync(tabla, timestamp, direccion="up"):
    tabla_log = "sync_log" if direccion == "up" else "sync_log_reverse"
    ejecutar_consulta(f"UPDATE {tabla_log} SET last_timestamp = ? WHERE tabla = ?", (timestamp, tabla), commit=True)

def obtener_columnas_tabla(tabla):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({tabla})")
    rows = cursor.fetchall()
    conn.close()
    return [row[1] for row in rows if row[1] != 'rowid']

def conectar_turso():
    """Devuelve una conexión a Turso usando libsql."""
    return libsql.connect("turso_db", sync_url=TURSO_URL, auth_token=TURSO_TOKEN)

def subir_tabla(tabla):
    try:
        last_ts = obtener_ultimo_timestamp_sync(tabla, "up")
        filas = ejecutar_consulta(f"SELECT * FROM {tabla} WHERE created_at > ? ORDER BY created_at ASC", (last_ts,))
        if not filas:
            return
        columnas = obtener_columnas_tabla(tabla)
        if not columnas:
            return
        columnas_str = ", ".join(columnas)
        placeholders = ", ".join(["?" for _ in columnas])
        conn_turso = conectar_turso()
        cursor = conn_turso.cursor()
        for fila in filas:
            valores = [fila.get(col) for col in columnas]
            valores_tupla = tuple(valores)
            sql = f"INSERT OR REPLACE INTO {tabla} ({columnas_str}) VALUES ({placeholders})"
            cursor.execute(sql, valores_tupla)
        conn_turso.commit()
        conn_turso.close()
        max_ts = max(f["created_at"] for f in filas)
        actualizar_ultimo_timestamp_sync(tabla, max_ts, "up")
        print(f"[SUBIDA] {tabla}: {len(filas)} filas enviadas. Último TS: {max_ts}")
    except Exception as e:
        print(f"[ERROR] Subiendo {tabla}: {e}")

def bajar_tabla(tabla):
    try:
        last_ts = obtener_ultimo_timestamp_sync(tabla, "down")
        conn_turso = conectar_turso()
        cursor = conn_turso.cursor()
        cursor.execute(f"SELECT * FROM {tabla} WHERE created_at > ? ORDER BY created_at ASC", (last_ts,))
        rows = cursor.fetchall()
        conn_turso.close()
        if not rows:
            return
        # Obtener nombres de columnas desde cursor.description
        col_names = [desc[0] for desc in cursor.description]
        rows_dict = [dict(zip(col_names, row)) for row in rows]
        columnas = obtener_columnas_tabla(tabla)
        if not columnas:
            return
        columnas_str = ", ".join(columnas)
        placeholders = ", ".join(["?" for _ in columnas])
        update_cols = ", ".join([f"{col}=excluded.{col}" for col in columnas if col not in ("id", "created_at")])
        for fila in rows_dict:
            valores = [fila.get(col) for col in columnas]
            ejecutar_consulta(f"""
                INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})
                ON CONFLICT(id) DO UPDATE SET {update_cols}
            """, valores, commit=True)
        max_ts = max(r["created_at"] for r in rows_dict)
        actualizar_ultimo_timestamp_sync(tabla, max_ts, "down")
        print(f"[BAJADA] {tabla}: {len(rows_dict)} filas actualizadas. Último TS: {max_ts}")
    except Exception as e:
        print(f"[ERROR] Bajando {tabla}: {e}")

def sincronizacion_completa():
    print(f"[SYNC] Iniciando a las {datetime.now()}")
    for tabla in TABLAS_SUBIDA:
        subir_tabla(tabla)
    for tabla in TABLAS_BAJADA:
        bajar_tabla(tabla)

def main():
    print("=== CENTRAL SYNC - Sincronización completa con Turso ===")
    print(f"Subida cada {SUBIDA_INTERVALO}s | Bajada cada {BAJADA_INTERVALO}s")
    while True:
        try:
            sincronizacion_completa()
        except Exception as e:
            print(f"[ERROR] General: {e}")
        time.sleep(min(SUBIDA_INTERVALO, BAJADA_INTERVALO))

if __name__ == "__main__":
    main()