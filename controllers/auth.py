"""
Authentication Blueprint
Handles user login, logout, and registration
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User
from .user_controller import UserController
import json

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        
        # Get IP and user agent for logging
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        # Authenticate user
        result = UserController.login(email, password, ip_address, user_agent)
        
        print(f"🔍 Login result: {result}")
        
        if result['success']:
            user = result['user']
            
            # Check if user account is active
            if not user.get('activo', False):
                flash('Tu cuenta ha sido desactivada. Contacta al administrador.', 'error')
                return render_template('auth/login.html')
            
            print(f"👤 User data: {dict(user)}")
            
            # Set session data
            session.permanent = True  # Use permanent session
            session['usuario_id'] = user['usuario_id']
            session['nombre'] = user['nombre']
            session['apellido'] = user['apellido']
            session['email'] = user['email']
            session['rol'] = user['rol']
            
            print(f"📝 Session after login: {dict(session)}")
            
            flash('¡Bienvenido de nuevo!', 'success')
            
            # Redirect based on role
            user_role = user['rol']
            
            if user_role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            print(f"❌ Login failed: {result['message']}")
            flash('Email o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html')
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        lastname = request.form.get('lastname')
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        # Register user
        result = UserController.register(name, lastname, email, password)
        
        if result['success']:
            # Iniciar sesión automáticamente después del registro
            user = User.get_by_email(email)
            if user:
                session['usuario_id'] = user['usuario_id']
                session['nombre'] = user['nombre']
                session['apellido'] = user['apellido']
                session['email'] = user['email']
                session['rol'] = user['rol']
                
                flash('¡Registro exitoso! Bienvenido!', 'success')
                return redirect(url_for('user.dashboard'))  # Siempre redirige al dashboard de usuario
            else:
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('auth.login'))
        else:
            flash(result['message'], 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Haz cerrado sesión', 'info')
    return redirect(url_for('auth.login'))