"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Productos – Sincroniza con Turso SOLO los datos (SIN FOTOS)
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from modelos.producto import Producto
from utilidades.central_sync import enviar_a_turso


class ControladorProductos:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.modelo = Producto(db)

    def crear_producto(self, codigo: str, descripcion: str,
                       precio_costo: float = 0.0, precio_venta: float = 0.0,
                       stock_critico: float = 0.0, unidad_medida: str = 'unidad',
                       categoria_id: int = None, foto: bytes = None,
                       detalle: str = None, precio_oferta: float = None,
                       destacado: int = 0) -> int:
        """Crea un producto (la foto se guarda SOLO en Central)"""
        codigo = codigo.strip()
        if not codigo:
            raise ValueError("El código del producto es obligatorio.")
        if self.modelo.obtener_por_codigo(codigo):
            raise ValueError("El código de producto ya existe.")
        if precio_costo < 0 or precio_venta < 0:
            raise ValueError("Los precios no pueden ser negativos.")

        producto_id = self.modelo.crear(
            codigo=codigo,
            descripcion=descripcion.strip(),
            precio_costo=precio_costo,
            precio_venta=precio_venta,
            stock_critico=stock_critico,
            unidad_medida=unidad_medida,
            categoria_id=categoria_id,
            foto=foto,  # ✅ Se guarda en Central pero NO se sube a Turso
            detalle=detalle,
            precio_oferta=precio_oferta,
            destacado=destacado
        )

        # ✅ Replicar en Turso SIN LA FOTO
        try:
            enviar_a_turso(
                """INSERT INTO productos (id, codigo, descripcion, precio_costo, precio_venta,
                   stock_actual, stock_critico, unidad_medida, categoria_id,
                   detalle, precio_oferta, destacado, activo,
                   created_at, updated_at, version)
                   VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, 1, ?, ?, 1)""",
                [producto_id, codigo, descripcion.strip(), precio_costo, precio_venta,
                 stock_critico, unidad_medida, categoria_id,
                 detalle, precio_oferta, destacado,
                 datetime.now().isoformat(), datetime.now().isoformat()]
            )
        except Exception as e:
            print(f"⚠️ Error replicando producto a Turso: {e}")

        return producto_id

    def modificar_producto(self, producto_id: int, **campos) -> bool:
        """Actualiza un producto y replica el cambio en Turso (SIN FOTO)"""
        if 'codigo' in campos:
            nuevo_codigo = campos['codigo'].strip()
            existente = self.modelo.obtener_por_codigo(nuevo_codigo)
            if existente and existente['id'] != producto_id:
                raise ValueError("El código ya está en uso por otro producto.")

        resultado = self.modelo.actualizar(producto_id, **campos)

        if campos:
            # Quitar foto de los campos a replicar (no se sube a Turso)
            campos_sin_foto = {k: v for k, v in campos.items() if k != 'foto'}
            if campos_sin_foto:
                set_clause = ", ".join(f"{col} = ?" for col in campos_sin_foto.keys())
                valores = list(campos_sin_foto.values())
                valores.append(producto_id)
                try:
                    enviar_a_turso(
                        f"UPDATE productos SET {set_clause} WHERE id = ?",
                        valores
                    )
                except Exception as e:
                    print(f"⚠️ Error replicando modificación de producto a Turso: {e}")

        return resultado

    def eliminar_producto(self, producto_id: int) -> bool:
        """Elimina un producto (baja lógica) y replica el cambio en Turso."""
        resultado = self.modelo.eliminar(producto_id)

        try:
            enviar_a_turso(
                "UPDATE productos SET activo = 0 WHERE id = ?",
                [producto_id]
            )
        except Exception as e:
            print(f"⚠️ Error replicando eliminación de producto a Turso: {e}")

        return resultado

    def obtener_producto(self, producto_id: int) -> Optional[Dict[str, Any]]:
        return self.modelo.obtener_por_id(producto_id)

    def obtener_producto_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        return self.modelo.obtener_por_codigo(codigo)

    def listar_productos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        return self.modelo.listar_todos(solo_activos=solo_activos)

    def obtener_stock_critico(self) -> List[Dict[str, Any]]:
        return self.modelo.stock_bajo_minimo()