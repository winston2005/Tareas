import sqlite3
from datetime import datetime
import os
from werkzeug.security import generate_password_hash  
# Crear la carpeta database si no existe
if not os.path.exists('database'):
    os.makedirs('database')
    print("✓ Carpeta 'database' creada")

# Conectar a la base de datos (se creará si no existe)
conn = sqlite3.connect('database/tareas.db')
cursor = conn.cursor()

# Eliminar tablas existentes si existen (para empezar limpio)
tablas = ['accesos', 'historial', 'recordatorios', 'tareas_etiquetas', 
          'etiquetas', 'tareas', 'categorias', 'prioridades', 'estados', 'usuarios']
for tabla in tablas:
    cursor.execute(f'DROP TABLE IF EXISTS {tabla}')

print("Creando estructura de base de datos...")

# 1. Crear tabla usuarios
cursor.execute('''
CREATE TABLE usuarios (
    usuario_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT 'usuario',
    activo INTEGER DEFAULT 1,
    fecha_registro TEXT NOT NULL,
    ultimo_acceso TEXT
)
''')

# 2. Crear tabla estados
cursor.execute('''
CREATE TABLE estados (
    estado_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    color TEXT
)
''')

# 3. Crear tabla prioridades
cursor.execute('''
CREATE TABLE prioridades (
    prioridad_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    nivel INTEGER NOT NULL,
    color TEXT
)
''')

# 4. Crear tabla categorias
cursor.execute('''
CREATE TABLE categorias (
    categoria_id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    color TEXT DEFAULT '#007bff',
    descripcion TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id) ON DELETE CASCADE
)
''')

# 5. Crear tabla tareas
cursor.execute('''
CREATE TABLE tareas (
    tarea_id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    fecha_creacion TEXT NOT NULL,
    fecha_vencimiento TEXT,
    fecha_completado TEXT,
    estado_id INTEGER NOT NULL DEFAULT 1,
    prioridad_id INTEGER NOT NULL DEFAULT 2,
    categoria_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    FOREIGN KEY (estado_id) REFERENCES estados(estado_id),
    FOREIGN KEY (prioridad_id) REFERENCES prioridades(prioridad_id),
    FOREIGN KEY (categoria_id) REFERENCES categorias(categoria_id) ON DELETE SET NULL
)
''')

# 6. Crear tabla etiquetas
cursor.execute('''
CREATE TABLE etiquetas (
    etiqueta_id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id) ON DELETE CASCADE
)
''')

# 7. Crear tabla tareas_etiquetas (relación muchos a muchos)
cursor.execute('''
CREATE TABLE tareas_etiquetas (
    tarea_id INTEGER NOT NULL,
    etiqueta_id INTEGER NOT NULL,
    PRIMARY KEY (tarea_id, etiqueta_id),
    FOREIGN KEY (tarea_id) REFERENCES tareas(tarea_id) ON DELETE CASCADE,
    FOREIGN KEY (etiqueta_id) REFERENCES etiquetas(etiqueta_id) ON DELETE CASCADE
)
''')

# 8. Crear tabla recordatorios
cursor.execute('''
CREATE TABLE recordatorios (
    recordatorio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tarea_id INTEGER NOT NULL,
    fecha_recordatorio TEXT NOT NULL,
    enviado INTEGER DEFAULT 0,
    FOREIGN KEY (tarea_id) REFERENCES tareas(tarea_id) ON DELETE CASCADE
)
''')

# 9. Crear tabla historial
cursor.execute('''
CREATE TABLE historial (
    historial_id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    tarea_id INTEGER,
    accion TEXT NOT NULL,
    detalles TEXT,
    fecha TEXT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id),
    FOREIGN KEY (tarea_id) REFERENCES tareas(tarea_id) ON DELETE SET NULL
)
''')

# 10. Crear tabla accesos
cursor.execute('''
CREATE TABLE accesos (
    acceso_id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    fecha_acceso TEXT NOT NULL,
    ip TEXT,
    user_agent TEXT,
    accion TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id) ON DELETE CASCADE
)
''')

print("Insertando datos iniciales...")

# Función para hashear contraseñas (simple, para desarrollo)
from werkzeug.security import generate_password_hash

def hash_password(password):
    return generate_password_hash(password)

# Insertar usuarios
fecha_actual = datetime.now().isoformat()
usuarios = [
    (1, 'Admin', 'Sistema', 'admin@sistema.com', hash_password('admin123'), 'admin', 1, fecha_actual, None),
    (2, 'Winston', 'Alvarado', 'winston@example.com', hash_password('winston123'), 'usuario', 1, fecha_actual, None),
    (3, 'María', 'Pérez', 'maria@example.com', hash_password('maria123'), 'usuario', 1, fecha_actual, None),
    (4, 'winston', 'alvarado', 'alvaradowintonsaul@gmail.com', hash_password('winston456'), 'usuario', 1, fecha_actual, None)
]

cursor.executemany('''
INSERT INTO usuarios (usuario_id, nombre, apellido, email, password_hash, rol, activo, fecha_registro, ultimo_acceso)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', usuarios)

# Insertar estados
estados = [
    (1, 'Pendiente', '#ffc107'),
    (2, 'En Progreso', '#17a2b8'),
    (3, 'Completada', '#28a745'),
    (4, 'Cancelada', '#dc3545')
]

cursor.executemany('INSERT INTO estados (estado_id, nombre, color) VALUES (?, ?, ?)', estados)

# Insertar prioridades
prioridades = [
    (1, 'Baja', 1, '#6c757d'),
    (2, 'Media', 2, '#ffc107'),
    (3, 'Alta', 3, '#fd7e14'),
    (4, 'Urgente', 4, '#dc3545')
]

cursor.executemany('INSERT INTO prioridades (prioridad_id, nombre, nivel, color) VALUES (?, ?, ?, ?)', prioridades)

# Insertar categorías
categorias = [
    (1, 1, 'Trabajo', '#007bff', 'Tareas laborales'),
    (2, 1, 'Personal', '#28a745', 'Tareas personales'),
    (3, 1, 'Estudios', '#6f42c1', 'Aprendizaje y cursos'),
    (4, 1, 'Casa', '#ffc107', 'Tareas del hogar'),
    (5, 1, 'Ejercicio', '#dc3545', 'Rutinas y deporte')
]

cursor.executemany('''
INSERT INTO categorias (categoria_id, usuario_id, nombre, color, descripcion)
VALUES (?, ?, ?, ?, ?)
''', categorias)

# Insertar tareas de ejemplo
tareas = [
    (1, 2, 'Completar informe mensual', 'Redactar y enviar el informe de actividades', 
     '2025-12-05T12:04:51.520631', '2025-12-10', None, 1, 3, 1),
    
    (2, 2, 'Revisar correos pendientes', 'Responder correos importantes de la semana', 
     '2025-12-05T12:04:51.520631', '2025-12-05', None, 1, 2, 1),
    
    (3, 2, 'Comprar víveres', 'Lista de supermercado para la semana', 
     '2025-12-05T12:04:51.520631', '2025-12-03', None, 1, 2, 4),
    
    (4, 2, 'Llamar al médico', 'Agendar cita de control mensual', 
     '2025-12-05T12:04:51.520631', '2025-12-04', None, 1, 3, 2),
    
    (5, 2, 'Limpiar la casa', 'Limpieza general de fin de semana', 
     '2025-12-05T12:04:51.520631', '2025-12-07', None, 1, 2, 4)
]

cursor.executemany('''
INSERT INTO tareas (tarea_id, usuario_id, titulo, descripcion, fecha_creacion, 
                    fecha_vencimiento, fecha_completado, estado_id, prioridad_id, categoria_id)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', tareas)

# Insertar accesos de ejemplo
accesos = [
    (1, 1, '2025-12-05T12:04:51.520631', '192.168.1.1', 'Mozilla/5.0 Admin Browser', 'login'),
    (2, 2, '2025-12-05T12:04:51.520631', '192.168.1.50', 'Mozilla/5.0 (Windows NT)', 'login'),
    (3, 2, '2025-12-05T12:04:51.520631', '192.168.1.50', 'Mozilla/5.0 (Windows NT)', 'crear_tarea'),
    (4, 3, '2025-12-05T12:04:51.520631', '192.168.1.100', 'Mozilla/5.0 (Android)', 'login')
]

cursor.executemany('''
INSERT INTO accesos (acceso_id, usuario_id, fecha_acceso, ip, user_agent, accion)
VALUES (?, ?, ?, ?, ?, ?)
''', accesos)

# Confirmar cambios
conn.commit()

print("\n✓ Base de datos creada exitosamente!")
print(f"✓ Ubicación: database/tareas.db")
print(f"\nUsuarios creados:")
print("  - admin@sistema.com (password: admin123) - ROL: admin")
print("  - winston@example.com (password: winston123) - ROL: usuario")
print("  - maria@example.com (password: maria123) - ROL: usuario")
print("  - alvaradowintonsaul@gmail.com (password: winston456) - ROL: usuario")
print(f"\n✓ {len(estados)} estados")
print(f"✓ {len(prioridades)} prioridades")
print(f"✓ {len(categorias)} categorías")
print(f"✓ {len(tareas)} tareas de ejemplo")
print(f"✓ {len(accesos)} registros de acceso")

# Cerrar conexión
conn.close()

print("\n¡Listo! La base de datos está recreada y lista para usar.")