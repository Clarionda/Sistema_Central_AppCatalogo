-- ============================================================
-- SCRIPT PARA APP CATALOGO - SOLO ESTRUCTURA
-- Los datos (preventistas, clientes, productos) vienen desde Turso
-- ============================================================

-- Tabla de configuración general
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
    longitud REAL
);

-- Clientes
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

-- Preventistas (SOLO ESTRUCTURA, sin datos)
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

-- Categorías
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- Productos
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

-- Índices
CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(descripcion);
CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria_id);

-- Notas de Venta
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

-- Cobros
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

-- Movimientos de Cuenta Corriente
CREATE TABLE IF NOT EXISTS cuenta_corriente_movimientos (
    id TEXT PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    fecha DATE DEFAULT (date('now')),
    tipo_movimiento TEXT CHECK(tipo_movimiento IN ('FACTURA','COBRO','NOTA_CREDITO','AJUSTE')),
    referencia_id TEXT,
    importe REAL NOT NULL,
    saldo_resultante REAL NOT NULL,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- Usuarios (SOLO ESTRUCTURA, sin datos)
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

-- Posiciones y visitas
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

-- Tablas de control de sincronización
CREATE TABLE IF NOT EXISTS sync_log (
    tabla TEXT PRIMARY KEY,
    last_timestamp TEXT DEFAULT '1970-01-01T00:00:00'
);

CREATE TABLE IF NOT EXISTS sync_log_reverse (
    tabla TEXT PRIMARY KEY,
    last_timestamp TEXT DEFAULT '1970-01-01T00:00:00'
);

-- INICIALIZACIÓN DE TABLAS DE CONTROL (SOLO ESTRUCTURA)
INSERT OR IGNORE INTO sync_log (tabla) VALUES 
    ('clientes'),('productos'),('preventistas'),('categorias'),
    ('notas_venta'),('nota_venta_detalle'),('cobros'),('cuenta_corriente_movimientos'),
    ('usuarios'),('posiciones_preventistas'),('visitas_clientes');

INSERT OR IGNORE INTO sync_log_reverse (tabla) VALUES 
    ('clientes'),('productos'),('preventistas'),('categorias'),('usuarios');

-- NO INSERTAR preventistas, clientes, productos, usuarios (vienen desde Turso)
-- SOLO se inserta admin por defecto (para que haya un usuario inicial)
INSERT OR IGNORE INTO usuarios (username, password_hash, rol) 
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin');

-- Parámetros por defecto
INSERT OR IGNORE INTO parametros (id, moneda, nombre_distribuidora, punto_venta, ultimo_numero_factura)
VALUES (1, 'ARS', 'Mi Distribuidora', '0001', 1);