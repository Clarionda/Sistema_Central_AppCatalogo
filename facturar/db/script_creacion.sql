CREATE TABLE IF NOT EXISTS parametros (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    moneda TEXT NOT NULL DEFAULT 'ARS',
    nombre_distribuidora TEXT NOT NULL,
    direccion TEXT,
    telefono1 TEXT,
    telefono2 TEXT,
    whatsapp TEXT,
    email TEXT,
    logo BLOB,
    encabezado_factura TEXT,
    encabezado_reporte TEXT,
    tasa_municipal_porcentaje REAL DEFAULT 0.0,
    punto_venta TEXT DEFAULT '0001',
    ultimo_numero_factura INTEGER DEFAULT 1,
    calle TEXT,
    numero TEXT,
    localidad TEXT,
    provincia TEXT,
    pais TEXT DEFAULT 'Argentina',
    latitud REAL,
    longitud REAL,
    escala_visual REAL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    razon_social TEXT NOT NULL,
    cuit TEXT UNIQUE,
    condicion_iva TEXT CHECK(condicion_iva IN ('RI','M','EX','CF','MT')) DEFAULT 'RI',
    domicilio TEXT,
    telefono TEXT,
    whatsapp TEXT,
    email TEXT,
    aplica_tasa_municipal BOOLEAN DEFAULT 0,
    limite_credito REAL DEFAULT 0,
    saldo_cuenta_corriente REAL DEFAULT 0,
    fecha_alta DATE DEFAULT (date('now')),
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    latitud REAL,
    longitud REAL,
    preventista_id INTEGER,
    localidad TEXT,
    provincia TEXT,
    calle TEXT,
    numero TEXT
);

CREATE TABLE IF NOT EXISTS preventistas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    legajo TEXT UNIQUE,
    telefono TEXT,
    email TEXT,
    zona TEXT,
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    precio_costo REAL DEFAULT 0,
    precio_venta REAL DEFAULT 0,
    stock_actual REAL DEFAULT 0,
    stock_critico REAL DEFAULT 0,
    unidad_medida TEXT DEFAULT 'unidad',
    categoria_id INTEGER REFERENCES categorias(id),
    url_foto TEXT,
    foto BLOB,
    detalle TEXT,
    precio_oferta REAL,
    destacado INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS lotes (
    id TEXT PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    numero_lote TEXT,
    fecha_vencimiento DATE NOT NULL,
    cantidad_inicial REAL NOT NULL,
    cantidad_actual REAL NOT NULL,
    fecha_ingreso DATE DEFAULT (date('now')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS notas_venta (
    id TEXT PRIMARY KEY,
    preventista_id INTEGER NOT NULL REFERENCES preventistas(id),
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    fecha DATE DEFAULT (date('now')),
    numero_nota TEXT,
    total REAL DEFAULT 0,
    observaciones TEXT,
    estado TEXT DEFAULT 'PENDIENTE',
    procesado_central BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_notas_venta_procesado ON notas_venta(procesado_central);
CREATE INDEX IF NOT EXISTS idx_notas_venta_created_at ON notas_venta(created_at);

CREATE TABLE IF NOT EXISTS nota_venta_detalle (
    id TEXT PRIMARY KEY,
    nota_venta_id TEXT NOT NULL REFERENCES notas_venta(id),
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad REAL NOT NULL,
    precio_unitario REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS facturas (
    id TEXT PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    preventista_id INTEGER REFERENCES preventistas(id),
    tipo_comprobante TEXT CHECK(tipo_comprobante IN ('A','B','C','X')) DEFAULT 'B',
    numero_factura TEXT NOT NULL,
    fecha DATE DEFAULT (date('now')),
    subtotal REAL DEFAULT 0,
    iva REAL DEFAULT 0,
    tasa_municipal REAL DEFAULT 0,
    total REAL DEFAULT 0,
    observaciones TEXT,
    nota_venta_id TEXT REFERENCES notas_venta(id),
    estado TEXT DEFAULT 'EMITIDA',
    saldo_anterior_cliente REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS factura_detalle (
    id TEXT PRIMARY KEY,
    factura_id TEXT NOT NULL REFERENCES facturas(id),
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad REAL NOT NULL,
    precio_unitario REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS cuenta_corriente_movimientos (
    id TEXT PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    fecha DATE DEFAULT (date('now')),
    tipo_movimiento TEXT CHECK(tipo_movimiento IN ('FACTURA','COBRO','NOTA_CREDITO','AJUSTE','ANULACION','REVERSO_COBRO')),
    referencia_id TEXT,
    importe REAL NOT NULL,
    saldo_resultante REAL NOT NULL,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS cobros (
    id TEXT PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    fecha DATE DEFAULT (date('now')),
    importe REAL NOT NULL,
    medio_pago TEXT,
    tipo_pago TEXT DEFAULT 'EFECTIVO',
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS cheques (
    id TEXT PRIMARY KEY,
    cobro_id TEXT NOT NULL,
    cliente_id INTEGER NOT NULL,
    banco TEXT NOT NULL,
    numero_cheque TEXT NOT NULL,
    fecha_emision DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    importe REAL NOT NULL,
    estado TEXT DEFAULT 'EN_CARTERA',
    fecha_acreditacion DATE,
    vendido_a TEXT,
    factura_ids TEXT,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    FOREIGN KEY (cobro_id) REFERENCES cobros(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE IF NOT EXISTS catalogo_importaciones (
    id TEXT PRIMARY KEY,
    fecha_importacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nombre_archivo TEXT,
    procesado_por TEXT,
    total_productos_nuevos INTEGER DEFAULT 0,
    total_actualizaciones INTEGER DEFAULT 0,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT CHECK(rol IN ('preventista','admin','cliente')) DEFAULT 'preventista',
    preventista_id INTEGER REFERENCES preventistas(id),
    cliente_id INTEGER REFERENCES clientes(id),
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS posiciones_preventistas (
    id TEXT PRIMARY KEY,
    preventista_id INTEGER NOT NULL,
    latitud REAL NOT NULL,
    longitud REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS visitas_clientes (
    id TEXT PRIMARY KEY,
    preventista_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    latitud REAL,
    longitud REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    args TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retries INTEGER DEFAULT 0,
    last_error TEXT,
    next_retry TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sync_log_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    args TEXT,
    success BOOLEAN,
    error TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sync_queue_next_retry ON sync_queue(next_retry);

CREATE TABLE IF NOT EXISTS sync_conflictos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tabla TEXT NOT NULL,
    registro_id TEXT NOT NULL,
    version_local INTEGER,
    version_remota INTEGER,
    resolucion TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sync_conflictos_tabla ON sync_conflictos(tabla);
CREATE INDEX IF NOT EXISTS idx_sync_conflictos_timestamp ON sync_conflictos(timestamp);

CREATE TABLE IF NOT EXISTS sync_log (
    tabla TEXT PRIMARY KEY,
    last_timestamp TEXT DEFAULT '1970-01-01T00:00:00'
);

CREATE TABLE IF NOT EXISTS sync_log_reverse (
    tabla TEXT PRIMARY KEY,
    last_timestamp TEXT DEFAULT '1970-01-01T00:00:00'
);

CREATE TRIGGER IF NOT EXISTS update_clientes_updated_at 
AFTER UPDATE ON clientes
BEGIN
    UPDATE clientes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_preventistas_updated_at 
AFTER UPDATE ON preventistas
BEGIN
    UPDATE preventistas SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_categorias_updated_at 
AFTER UPDATE ON categorias
BEGIN
    UPDATE categorias SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_productos_updated_at 
AFTER UPDATE ON productos
BEGIN
    UPDATE productos SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_lotes_updated_at 
AFTER UPDATE ON lotes
BEGIN
    UPDATE lotes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_notas_venta_updated_at 
AFTER UPDATE ON notas_venta
BEGIN
    UPDATE notas_venta SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_nota_venta_detalle_updated_at 
AFTER UPDATE ON nota_venta_detalle
BEGIN
    UPDATE nota_venta_detalle SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_facturas_updated_at 
AFTER UPDATE ON facturas
BEGIN
    UPDATE facturas SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_factura_detalle_updated_at 
AFTER UPDATE ON factura_detalle
BEGIN
    UPDATE factura_detalle SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_cuenta_corriente_movimientos_updated_at 
AFTER UPDATE ON cuenta_corriente_movimientos
BEGIN
    UPDATE cuenta_corriente_movimientos SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_cobros_updated_at 
AFTER UPDATE ON cobros
BEGIN
    UPDATE cobros SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_cheques_updated_at 
AFTER UPDATE ON cheques
BEGIN
    UPDATE cheques SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_usuarios_updated_at 
AFTER UPDATE ON usuarios
BEGIN
    UPDATE usuarios SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

INSERT OR IGNORE INTO usuarios (username, password_hash, rol) 
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin');

INSERT OR IGNORE INTO preventistas (id, nombre, apellido, legajo) VALUES (1, 'Juan', 'Perez', 'P001');

INSERT OR IGNORE INTO usuarios (username, password_hash, rol, preventista_id) 
VALUES ('preventista1', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'preventista', 1);

INSERT OR IGNORE INTO clientes (id, razon_social, cuit, latitud, longitud, localidad, provincia) 
VALUES (1, 'Cliente Ejemplo', '20-12345678-9', -34.6037, -58.3816, 'CABA', 'Buenos Aires');

INSERT OR IGNORE INTO parametros (id, moneda, nombre_distribuidora, punto_venta, ultimo_numero_factura, escala_visual)
VALUES (1, 'ARS', 'Mi Distribuidora', '0001', 1, 1.0);

INSERT OR IGNORE INTO sync_log (tabla) VALUES 
('clientes'),
('productos'),
('preventistas'),
('categorias'),
('lotes'),
('notas_venta'),
('nota_venta_detalle'),
('facturas'),
('factura_detalle'),
('cuenta_corriente_movimientos'),
('cobros'),
('cheques'),
('usuarios'),
('posiciones_preventistas'),
('visitas_clientes');

INSERT OR IGNORE INTO sync_log_reverse (tabla) VALUES 
('clientes'),
('productos'),
('preventistas'),
('categorias'),
('usuarios'),
('visitas_clientes');