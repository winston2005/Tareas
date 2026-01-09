"""
Configuración del proyecto
Centraliza todas las configuraciones de la aplicación
"""

import os
from datetime import timedelta

# ============ CONFIGURACIÓN BASE ============

class Config:
    """Configuración base de la aplicación"""
    
    # Directorio base del proyecto
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Secret key para sesiones (CAMBIAR EN PRODUCCIÓN)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Base de datos
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'tareas.db')

    # Configuración de la aplicación Flask
    DEBUG = False
    TESTING = False
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Configuración de seguridad para passwords
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # PBKDF2 iterations para hash de passwords
    PBKDF2_ITERATIONS = 150000
    
    # Paginación
    TASKS_PER_PAGE = 20
    CATEGORIES_PER_PAGE = 10
    LOGS_PER_PAGE = 50
    
    # Formato de fechas
    DATE_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Límites
    MAX_TITLE_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 2000
    MAX_CATEGORY_NAME_LENGTH = 50
    MAX_EMAIL_LENGTH = 100
    
    # Roles disponibles
    ROLES = {
        'ADMIN': 'admin',
        'USER': 'usuario'
    }
    
    # Estados de tareas (sincronizar con BD)
    TASK_STATES = {
        'PENDING': 1,
        'IN_PROGRESS': 2,
        'COMPLETED': 3,
        'CANCELLED': 4
    }
    
    # Prioridades de tareas (sincronizar con BD)
    TASK_PRIORITIES = {
        'LOW': 1,
        'MEDIUM': 2,
        'HIGH': 3,
        'URGENT': 4
    }
    
    # Colores por defecto
    DEFAULT_COLORS = [
        '#007bff',  # Azul
        '#28a745',  # Verde
        '#dc3545',  # Rojo
        '#ffc107',  # Amarillo
        '#17a2b8',  # Cyan
        '#6f42c1',  # Púrpura
        '#fd7e14',  # Naranja
        '#20c997',  # Teal
        '#e83e8c',  # Rosa
        '#6c757d'   # Gris
    ]
    
    # Configuración de logs del sistema
    LOG_RETENTION_DAYS = 90  # Días que se mantienen los logs
    
    # Mensajes flash personalizados
    FLASH_MESSAGES = {
        'login_success': 'Bienvenido/a de vuelta!',
        'login_error': 'Credenciales inválidas',
        'logout_success': 'Sesión cerrada exitosamente',
        'task_created': 'Tarea creada exitosamente',
        'task_updated': 'Tarea actualizada exitosamente',
        'task_deleted': 'Tarea eliminada exitosamente',
        'category_created': 'Categoría creada exitosamente',
        'category_updated': 'Categoría actualizada exitosamente',
        'category_deleted': 'Categoría eliminada exitosamente',
        'user_created': 'Usuario creado exitosamente',
        'user_updated': 'Usuario actualizado exitosamente',
        'user_deleted': 'Usuario eliminado exitosamente',
        'access_denied': 'No tiene permisos para acceder a esta sección',
        'not_found': 'Recurso no encontrado',
        'error': 'Ha ocurrido un error. Intente nuevamente'
    }


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
    # En producción, SECRET_KEY debe venir de variable de entorno
    SECRET_KEY = os.environ.get('SECRET_KEY')


class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DEBUG = True
    DATABASE_PATH = ':memory:'  # Base de datos en memoria para tests


# Diccionario de configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name='default'):
    """
    Obtener configuración por nombre
    
    Args:
        config_name: Nombre de la configuración ('development', 'production', 'testing')
    
    Returns:
        Clase de configuración
    """
    cfg = config.get(config_name, config['default'])
    if cfg is ProductionConfig and not os.environ.get('SECRET_KEY'):
        raise ValueError('SECRET_KEY debe estar definida en producción')
    return cfg
