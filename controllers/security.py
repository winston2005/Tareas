"""
Security Decorators
Provides authentication and authorization decorators for route protection
"""

from functools import wraps
from flask import session, redirect, url_for, flash, abort

def login_required(f):
    """
    Decorator to require user authentication
    Redirects to login if user is not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to require admin role
    Returns 403 if user is not admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('rol') != 'admin':
            flash('No tienes permisos para acceder a esta página', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def active_user_required(f):
    """
    Decorator to require active user status
    Checks if user account is active
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('auth.login'))
        
        # Import here to avoid circular imports
        from models import User
        user = User.get_by_id(session.get('usuario_id'))
        
        if not user or not user.get('activo'):
            session.clear()
            flash('Tu cuenta ha sido desactivada. Contacta al administrador.', 'danger')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """
    Decorator to require specific role(s)
    Usage: @role_required('admin', 'moderator')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'usuario_id' not in session:
                flash('Por favor inicia sesión para acceder a esta página', 'warning')
                return redirect(url_for('auth.login'))
            
            user_role = session.get('rol')
            if user_role not in roles:
                flash('No tienes permisos para acceder a esta página', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
