"""
Data Models for Task Management System
Handles all database queries and data operations
"""
from middlewares.database.db import ejecutar_consulta, ejecutar_actualizacion, obtener_fecha_actual
from werkzeug.security import generate_password_hash, check_password_hash


# ================================
# HELPER FUNCTION TO CONVERT ROWS
# ================================
def row_to_dict(row):
    """Convert sqlite3.Row to dict"""
    if row:
        return dict(row)
    return None

def rows_to_dict_list(rows):
    """Convert list of sqlite3.Row to list of dicts"""
    if rows:
        return [dict(row) for row in rows]
    return []


# ================================
# USER MODEL (ACTUALIZADO Y CORREGIDO)
# ================================
class User:
    @staticmethod
    def create(name, lastname, email, password, role='usuario'):
     """Create a new user"""
     password_hash = generate_password_hash(password)
     query = """
        INSERT INTO usuarios (nombre, apellido, email, password_hash, rol, activo, fecha_registro)
        VALUES (?, ?, ?, ?, ?, 1, ?)
       """
     return ejecutar_actualizacion(query, (name, lastname, email, password_hash, role, obtener_fecha_actual()))
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        query = "SELECT * FROM usuarios WHERE usuario_id = ?"
        row = ejecutar_consulta(query, (user_id,), obtener_una=True)
        return row_to_dict(row)
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        query = "SELECT * FROM usuarios WHERE email = ?"
        row = ejecutar_consulta(query, (email,), obtener_una=True)
        return row_to_dict(row)
    
    @staticmethod
    def get_all():
        """Get all users"""
        query = """
            SELECT usuario_id, nombre, apellido, email, rol, activo, 
                   fecha_registro, ultimo_acceso
            FROM usuarios 
            ORDER BY fecha_registro DESC
        """
        rows = ejecutar_consulta(query)
        return rows_to_dict_list(rows)
    
    @staticmethod
    def update(user_id, name, lastname, email, photo_filename=None, rol=None, activo=None):
        """Update user information"""
        if rol is not None and activo is not None:
            # Admin update with role and status
            if photo_filename:
                query = """
                    UPDATE usuarios 
                    SET nombre = ?, apellido = ?, email = ?, rol = ?, activo = ?, foto_perfil = ?
                    WHERE usuario_id = ?
                """
                return ejecutar_actualizacion(query, (name, lastname, email, rol, activo, photo_filename, user_id))
            else:
                query = """
                    UPDATE usuarios 
                    SET nombre = ?, apellido = ?, email = ?, rol = ?, activo = ?
                    WHERE usuario_id = ?
                """
                return ejecutar_actualizacion(query, (name, lastname, email, rol, activo, user_id))
        else:
            # Regular profile update
            if photo_filename:
                query = """
                    UPDATE usuarios 
                    SET nombre = ?, apellido = ?, email = ?, foto_perfil = ?
                    WHERE usuario_id = ?
                """
                return ejecutar_actualizacion(query, (name, lastname, email, photo_filename, user_id))
            else:
                query = """
                    UPDATE usuarios 
                    SET nombre = ?, apellido = ?, email = ?
                    WHERE usuario_id = ?
                """
                return ejecutar_actualizacion(query, (name, lastname, email, user_id))
    
    @staticmethod
    def update_password(user_id, new_password):
        """Update user password"""
        password_hash = generate_password_hash(new_password)
        query = "UPDATE usuarios SET password_hash = ? WHERE usuario_id = ?"
        return ejecutar_actualizacion(query, (password_hash, user_id))
    
    @staticmethod
    def update_last_access(user_id):
        """Update last access timestamp"""
        query = "UPDATE usuarios SET ultimo_acceso = ? WHERE usuario_id = ?"
        return ejecutar_actualizacion(query, (obtener_fecha_actual(), user_id))
    
    @staticmethod
    def verify_password(email, password):
        """Verify user credentials"""
        user = User.get_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None
    
    @staticmethod
    def delete(user_id):
        """Delete user"""
        query = "DELETE FROM usuarios WHERE usuario_id = ?"
        return ejecutar_actualizacion(query, (user_id,))
    
    @staticmethod
    def toggle_active(user_id):
        """Toggle user active status"""
        query = "UPDATE usuarios SET activo = NOT activo WHERE usuario_id = ?"
        return ejecutar_actualizacion(query, (user_id,))
    
    @staticmethod
    def get_statistics():
        """Get user statistics"""
        query = """
            SELECT 
                COUNT(*) as total_usuarios,
                SUM(CASE WHEN activo = 1 THEN 1 ELSE 0 END) as usuarios_activos,
                SUM(CASE WHEN activo = 0 THEN 1 ELSE 0 END) as usuarios_inactivos,
                SUM(CASE WHEN rol = 'admin' THEN 1 ELSE 0 END) as admins
            FROM usuarios
        """
        result = ejecutar_consulta(query, obtener_una=True)
        
        if result:
            result = dict(result)
            return {
                'total_usuarios': result['total_usuarios'] or 0,
                'usuarios_activos': result['usuarios_activos'] or 0,
                'usuarios_inactivos': result['usuarios_inactivos'] or 0,
                'admins': result['admins'] or 0
            }
        
        return {
            'total_usuarios': 0,
            'usuarios_activos': 0,
            'usuarios_inactivos': 0,
            'admins': 0
        }


# ================================
# TASK MODEL
# ================================
class Task:
    @staticmethod
    def create(user_id, title, description=None, due_date=None, state_id=1, priority_id=2, category_id=None):
        """Create a new task"""
        query = """
            INSERT INTO tareas (usuario_id, titulo, descripcion, fecha_vencimiento, estado_id, prioridad_id, categoria_id, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return ejecutar_actualizacion(query, (user_id, title, description, due_date, state_id, priority_id, category_id, obtener_fecha_actual()))
    
    @staticmethod
    def get_by_id(task_id):
        """Get task by ID with related data"""
        query = """
            SELECT t.tarea_id as id,
                   t.usuario_id,
                   t.titulo,
                   t.descripcion,
                   t.fecha_creacion,
                   t.fecha_vencimiento,
                   t.fecha_completado,
                   t.estado_id,
                   t.prioridad_id,
                   t.categoria_id,
                   e.nombre as estado_nombre, 
                   e.color as estado_color,
                   p.nombre as prioridad_nombre, 
                   p.color as prioridad_color, 
                   p.nivel as prioridad_nivel,
                   c.nombre as categoria_nombre, 
                   c.color as categoria_color,
                   u.nombre || ' ' || u.apellido as usuario_nombre
            FROM tareas t
            LEFT JOIN estados e ON t.estado_id = e.estado_id
            LEFT JOIN prioridades p ON t.prioridad_id = p.prioridad_id
            LEFT JOIN categorias c ON t.categoria_id = c.categoria_id
            LEFT JOIN usuarios u ON t.usuario_id = u.usuario_id
            WHERE t.tarea_id = ?
        """
        row = ejecutar_consulta(query, (task_id,), obtener_una=True)
        return row_to_dict(row)
    
    @staticmethod
    def get_by_user(user_id, state_id=None, priority_id=None, category_id=None):
        """Get all tasks for a user with optional filters"""
        query = """
            SELECT t.tarea_id as id,
                   t.usuario_id,
                   t.titulo,
                   t.descripcion,
                   t.fecha_creacion,
                   t.fecha_vencimiento,
                   t.fecha_completado,
                   t.estado_id,
                   t.prioridad_id,
                   t.categoria_id,
                   e.nombre as estado_nombre, 
                   e.color as estado_color,
                   p.nombre as prioridad_nombre, 
                   p.color as prioridad_color,
                   c.nombre as categoria_nombre, 
                   c.color as categoria_color
            FROM tareas t
            LEFT JOIN estados e ON t.estado_id = e.estado_id
            LEFT JOIN prioridades p ON t.prioridad_id = p.prioridad_id
            LEFT JOIN categorias c ON t.categoria_id = c.categoria_id
            WHERE t.usuario_id = ?
        """
        params = [user_id]
        
        if state_id:
            query += " AND t.estado_id = ?"
            params.append(state_id)
        
        if priority_id:
            query += " AND t.prioridad_id = ?"
            params.append(priority_id)
        
        if category_id:
            query += " AND t.categoria_id = ?"
            params.append(category_id)
        
        query += " ORDER BY t.fecha_creacion DESC"
        rows = ejecutar_consulta(query, tuple(params))
        return rows_to_dict_list(rows)
    
    @staticmethod
    def update(task_id, title, description=None, due_date=None, state_id=None, priority_id=None, category_id=None):
        """Update task"""
        query = """
            UPDATE tareas 
            SET titulo = ?, descripcion = ?, fecha_vencimiento = ?, 
                estado_id = ?, prioridad_id = ?, categoria_id = ?
            WHERE tarea_id = ?
        """
        return ejecutar_actualizacion(query, (title, description, due_date, state_id, priority_id, category_id, task_id))
    
    @staticmethod
    def update_state(task_id, state_id):
        """Update task state"""
        completed_date = obtener_fecha_actual() if state_id == 3 else None
        
        if completed_date:
            query = "UPDATE tareas SET estado_id = ?, fecha_completado = ? WHERE tarea_id = ?"
            return ejecutar_actualizacion(query, (state_id, completed_date, task_id))
        
        query = "UPDATE tareas SET estado_id = ? WHERE tarea_id = ?"
        return ejecutar_actualizacion(query, (state_id, task_id))
    
    @staticmethod
    def delete(task_id):
        """Delete task"""
        query = "DELETE FROM tareas WHERE tarea_id = ?"
        return ejecutar_actualizacion(query, (task_id,))
    
    @staticmethod
    def get_pending_by_user(user_id):
        """Get pending tasks"""
        query = """
            SELECT t.tarea_id as id, t.*, 
                   e.nombre as estado_nombre, 
                   p.nombre as prioridad_nombre
            FROM tareas t
            LEFT JOIN estados e ON t.estado_id = e.estado_id
            LEFT JOIN prioridades p ON t.prioridad_id = p.prioridad_id
            WHERE t.usuario_id = ? AND t.estado_id = 1
            ORDER BY t.fecha_vencimiento ASC
        """
        rows = ejecutar_consulta(query, (user_id,))
        return rows_to_dict_list(rows)
    
    @staticmethod
    def get_completed_by_user(user_id):
        """Get completed tasks"""
        query = """
            SELECT t.tarea_id as id, t.*, 
                   e.nombre as estado_nombre
        FROM tareas t
            LEFT JOIN estados e ON t.estado_id = e.estado_id
            WHERE t.usuario_id = ? AND t.estado_id = 3
            ORDER BY t.fecha_completado DESC
        """
        rows = ejecutar_consulta(query, (user_id,))
        return rows_to_dict_list(rows)

    @staticmethod
    def get_global_statistics():
        """Get system-wide task statistics"""
        # Tasks by status
        query_status = """
            SELECT e.nombre, COUNT(t.tarea_id) as total
            FROM estados e
            LEFT JOIN tareas t ON e.estado_id = t.estado_id
            GROUP BY e.nombre
        """
        status_rows = ejecutar_consulta(query_status)
        
        # Tasks by priority
        query_priority = """
            SELECT p.nombre, COUNT(t.tarea_id) as total
            FROM prioridades p
            LEFT JOIN tareas t ON p.prioridad_id = t.prioridad_id
            GROUP BY p.nombre
        """
        priority_rows = ejecutar_consulta(query_priority)
        
        # General counts
        query_general = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN estado_id = 3 THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN estado_id = 1 THEN 1 ELSE 0 END) as pending
            FROM tareas
        """
        general = ejecutar_consulta(query_general, obtener_una=True)
        
        return {
            'by_status': rows_to_dict_list(status_rows),
            'by_priority': rows_to_dict_list(priority_rows),
            'total': general['total'] if general else 0,
            'completed': general['completed'] if general else 0,
            'pending': general['pending'] if general else 0
        }


# ================================
# CATEGORY MODEL
# ================================
class Category:
    @staticmethod
    def create(user_id, name, color='#6366f1', description=None):
        """Create a new category"""
        query = """
            INSERT INTO categorias (usuario_id, nombre, color, descripcion)
            VALUES (?, ?, ?, ?)
        """
        return ejecutar_actualizacion(query, (user_id, name, color, description))
    
    @staticmethod
    def get_by_id(category_id):
        """Get category by ID"""
        query = "SELECT categoria_id as id, * FROM categorias WHERE categoria_id = ?"
        row = ejecutar_consulta(query, (category_id,), obtener_una=True)
        return row_to_dict(row)
    
    @staticmethod
    def get_by_user(user_id):
        """Get all categories for a user with task counts"""
        query = """
            SELECT c.categoria_id as id, c.*, 
                   (SELECT COUNT(*) FROM tareas t WHERE t.categoria_id = c.categoria_id) as total_tareas
            FROM categorias c
            WHERE c.usuario_id = ? 
            ORDER BY c.nombre
        """
        rows = ejecutar_consulta(query, (user_id,))
        return rows_to_dict_list(rows)
    
    @staticmethod
    def update(category_id, name, color, description=None):
        """Update category"""
        query = """
            UPDATE categorias 
            SET nombre = ?, color = ?, descripcion = ?
            WHERE categoria_id = ?
        """
        return ejecutar_actualizacion(query, (name, color, description, category_id))
    
    @staticmethod
    def delete(category_id):
        """Delete category"""
        query = "DELETE FROM categorias WHERE categoria_id = ?"
        return ejecutar_actualizacion(query, (category_id,))


# ================================
# TAG MODEL
# ================================
class Tag:
    @staticmethod
    def create(user_id, name):
        """Create a new tag"""
        query = "INSERT INTO etiquetas (usuario_id, nombre) VALUES (?, ?)"
        return ejecutar_actualizacion(query, (user_id, name))
    
    @staticmethod
    def get_by_user(user_id):
        """Get all tags for a user"""
        query = "SELECT etiqueta_id as id, * FROM etiquetas WHERE usuario_id = ? ORDER BY nombre"
        rows = ejecutar_consulta(query, (user_id,))
        return rows_to_dict_list(rows)
    
    @staticmethod
    def add_to_task(task_id, tag_id):
        """Add tag to task"""
        query = "INSERT INTO tareas_etiquetas (tarea_id, etiqueta_id) VALUES (?, ?)"
        return ejecutar_actualizacion(query, (task_id, tag_id))
    
    @staticmethod
    def remove_from_task(task_id, tag_id):
        """Remove tag from task"""
        query = "DELETE FROM tareas_etiquetas WHERE tarea_id = ? AND etiqueta_id = ?"
        return ejecutar_actualizacion(query, (task_id, tag_id))
    
    @staticmethod
    def get_by_task(task_id):
        """Get all tags for a task"""
        query = """
            SELECT e.etiqueta_id as id, e.nombre
            FROM etiquetas e
            INNER JOIN tareas_etiquetas te ON e.etiqueta_id = te.etiqueta_id
            WHERE te.tarea_id = ?
        """
        rows = ejecutar_consulta(query, (task_id,))
        return rows_to_dict_list(rows)
    
    @staticmethod
    def delete(tag_id):
        """Delete tag"""
        query = "DELETE FROM etiquetas WHERE etiqueta_id = ?"
        return ejecutar_actualizacion(query, (tag_id,))


# ================================
# STATE MODEL
# ================================
class State:
    @staticmethod
    def get_all():
        """Get all states"""
        query = "SELECT estado_id as id, * FROM estados ORDER BY estado_id"
        rows = ejecutar_consulta(query)
        return rows_to_dict_list(rows)
    
    @staticmethod
    def get_by_id(state_id):
        """Get state by ID"""
        query = "SELECT estado_id as id, * FROM estados WHERE estado_id = ?"
        row = ejecutar_consulta(query, (state_id,), obtener_una=True)
        return row_to_dict(row)


# ================================
# PRIORITY MODEL
# ================================
class Priority:
    @staticmethod
    def get_all():
        """Get all priorities"""
        query = "SELECT prioridad_id as id, * FROM prioridades ORDER BY nivel"
        rows = ejecutar_consulta(query)
        return rows_to_dict_list(rows)
    
    @staticmethod
    def get_by_id(priority_id):
        """Get priority by ID"""
        query = "SELECT prioridad_id as id, * FROM prioridades WHERE prioridad_id = ?"
        row = ejecutar_consulta(query, (priority_id,), obtener_una=True)
        return row_to_dict(row)


# ================================
# REMINDER MODEL
# ================================
class Reminder:
    @staticmethod
    def create(task_id, reminder_date):
        """Create a new reminder"""
        query = """
            INSERT INTO recordatorios (tarea_id, fecha_recordatorio)
            VALUES (?, ?)
        """
        return ejecutar_actualizacion(query, (task_id, reminder_date))
    
    @staticmethod
    def get_by_task(task_id):
        """Get all reminders for a task"""
        query = "SELECT recordatorio_id as id, * FROM recordatorios WHERE tarea_id = ? ORDER BY fecha_recordatorio"
        rows = ejecutar_consulta(query, (task_id,))
        return rows_to_dict_list(rows)
    
    @staticmethod
    def mark_as_sent(reminder_id):
        """Mark reminder as sent"""
        query = "UPDATE recordatorios SET enviado = 1 WHERE recordatorio_id = ?"
        return ejecutar_actualizacion(query, (reminder_id,))
    
    @staticmethod
    def delete(reminder_id):
        """Delete reminder"""
        query = "DELETE FROM recordatorios WHERE recordatorio_id = ?"
        return ejecutar_actualizacion(query, (reminder_id,))


# ================================
# HISTORY MODEL
# ================================
class History:
    @staticmethod
    def create(user_id, task_id, action, details=None):
        """Create a history entry"""
        query = """
            INSERT INTO historial (usuario_id, tarea_id, accion, detalles, fecha)
            VALUES (?, ?, ?, ?, ?)
        """
        return ejecutar_actualizacion(query, (user_id, task_id, action, details, obtener_fecha_actual()))
    
    @staticmethod
    def get_by_user(user_id, limit=50):
        """Get history for a user"""
        query = """
            SELECT h.historial_id as id, h.*, t.titulo as tarea_titulo
            FROM historial h
            LEFT JOIN tareas t ON h.tarea_id = t.tarea_id
            WHERE h.usuario_id = ?
            ORDER BY h.fecha DESC
            LIMIT ?
        """
        rows = ejecutar_consulta(query, (user_id, limit))
        return rows_to_dict_list(rows)
    
    @staticmethod
    def get_by_task(task_id):
        """Get history for a specific task"""
        query = """
            SELECT h.historial_id as id, h.*, u.nombre || ' ' || u.apellido as usuario_nombre
            FROM historial h
            LEFT JOIN usuarios u ON h.usuario_id = u.usuario_id
            WHERE h.tarea_id = ?
            ORDER BY h.fecha DESC
        """
        rows = ejecutar_consulta(query, (task_id,))
        return rows_to_dict_list(rows)


# ================================
# ACCESS LOG MODEL
# ================================
class AccessLog:
    @staticmethod
    def create(user_id, ip=None, user_agent=None, action=None):
        """Create an access log entry"""
        query = """
            INSERT INTO accesos (usuario_id, fecha_acceso, ip, user_agent, accion)
            VALUES (?, ?, ?, ?, ?)
        """
        return ejecutar_actualizacion(query, (user_id, obtener_fecha_actual(), ip, user_agent, action))
    
    @staticmethod
    def get_by_user(user_id, limit=20):
        """Get recent access logs for a user"""
        query = """
            SELECT acceso_id as id, * FROM accesos 
            WHERE usuario_id = ?
            ORDER BY fecha_acceso DESC
            LIMIT ?
        """
        rows = ejecutar_consulta(query, (user_id, limit))
        return rows_to_dict_list(rows)
    
    @staticmethod
    def get_all(limit=100):
        """Get all access logs"""
        query = """
            SELECT a.acceso_id as id, a.*, u.nombre, u.apellido, u.email
            FROM accesos a
            LEFT JOIN usuarios u ON a.usuario_id = u.usuario_id
            ORDER BY a.fecha_acceso DESC
            LIMIT ?
        """
        rows = ejecutar_consulta(query, (limit,))
        return rows_to_dict_list(rows)


# ================================
# SYSTEM SETTINGS MODEL
# ================================
class SystemSetting:
    @staticmethod
    def get(clave, default=None):
        """Get a setting by key"""
        query = "SELECT valor FROM configuracion WHERE clave = ?"
        row = ejecutar_consulta(query, (clave,), obtener_una=True)
        # Convert row to dict to access by key safely
        if row:
            return dict(row)['valor']
        return default
    
    @staticmethod
    def set(clave, valor):
        """Set a setting value"""
        query = "INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)"
        return ejecutar_actualizacion(query, (clave, valor))


def init_db():
    """Initialize database"""
    pass