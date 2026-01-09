"""
Database helper functions
Manages all database connections and queries
"""
import sqlite3
import os
from datetime import datetime


def get_db_path():
    """Get the absolute path to the database"""
    # Subir 2 niveles desde middlewares/database hasta la raíz del proyecto
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'database', 'tareas.db')
    return db_path


def get_db_connection():
    """Create and return a database connection"""
    db_path = get_db_path()
    
    # Verificar que el archivo existe
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
    return conn


def ejecutar_consulta(query, params=None, obtener_una=False):
    """
    Execute a SELECT query and return results
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or list)
        obtener_una: If True, return only first result
    
    Returns:
        List of Row objects or single Row object if obtener_una=True
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if obtener_una:
            resultado = cursor.fetchone()
        else:
            resultado = cursor.fetchall()
        
        conn.close()
        return resultado
        
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return None if obtener_una else []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None if obtener_una else []


def ejecutar_actualizacion(query, params=None):
    """
    Execute an INSERT, UPDATE, or DELETE query
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or list)
    
    Returns:
        ID of last inserted row (for INSERT) or number of affected rows
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        
        return last_id
        
    except sqlite3.Error as e:
        print(f"Error executing update: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def obtener_fecha_actual():
    """
    Get current datetime in ISO format
    
    Returns:
        Current datetime string in ISO format
    """
    return datetime.now().isoformat()


def verificar_base_datos():
    """
    Verify database exists and is accessible
    
    Returns:
        True if database is OK, False otherwise
    """
    try:
        db_path = get_db_path()
        
        if not os.path.exists(db_path):
            print(f"❌ Database not found: {db_path}")
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que la tabla usuarios existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        tabla_existe = cursor.fetchone()
        
        conn.close()
        
        if tabla_existe:
            print(f"✅ Database OK: {db_path}")
            return True
        else:
            print(f"⚠️ Database exists but 'usuarios' table not found")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False