"""
User Blueprint
Handles user dashboard and profile management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .user_controller import UserController
from .task_controller import TaskController
from models import SystemSetting

# Create blueprint
user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario_id']
    
    # Get dashboard statistics
    stats_result = TaskController.get_dashboard_stats(user_id)
    stats = stats_result['stats'] if stats_result['success'] else {}
    
    # Get recent tasks (últimas 5 tareas)
    tasks_result = TaskController.get_user_tasks(user_id)
    all_tasks = tasks_result['tasks'] if tasks_result['success'] else []
    tareas_recientes = all_tasks[:5] if all_tasks else []
    
    # Get user categories
    from .category_controller import CategoryController
    categories_result = CategoryController.get_user_categories(user_id)
    categorias = categories_result['categories'] if categories_result['success'] else []
    
    # Get tip of the day
    consejo = SystemSetting.get('consejo_dia', 'Establece prioridades claras para tus tareas.')
    
    return render_template(
        'user/dashboard_user.html', 
        stats=stats, 
        pending_tasks=all_tasks,
        tareas_recientes=tareas_recientes,
        categorias=categorias,
        consejo=consejo
    )

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """User profile management"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario_id']
    
    if request.method == 'POST':
        name = request.form.get('name')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        
        # Handle profile photo upload
        photo_filename = None
        if 'profile_photo' in request.files:
            photo = request.files['profile_photo']
            if photo and photo.filename:
                # Validate file extension
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                file_ext = photo.filename.rsplit('.', 1)[1].lower() if '.' in photo.filename else ''
                
                if file_ext in allowed_extensions:
                    # Generate secure filename
                    import os
                    from werkzeug.utils import secure_filename
                    import uuid
                    
                    # Create unique filename
                    unique_filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
                    
                    # Ensure upload directory exists
                    upload_dir = os.path.join('static', 'uploads', 'profiles')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Save file
                    photo_path = os.path.join(upload_dir, unique_filename)
                    photo.save(photo_path)
                    photo_filename = unique_filename
                else:
                    flash('Formato de imagen no válido. Use PNG, JPG, JPEG, GIF o WEBP.', 'error')
        
        # Update profile
        result = UserController.update_profile(user_id, name, lastname, email, photo_filename)
        
        if result['success']:
            # Update session data
            session['nombre'] = name
            session['apellido'] = lastname
            session['email'] = email
            flash('¡Perfil actualizado exitosamente!', 'success')
        else:
            flash(result['message'], 'error')
    
    # Get current user info
    user_result = UserController.get_user_info(user_id)
    user = user_result['user'] if user_result['success'] else None
    
    return render_template('user/perfil.html', user=user)

@user_bp.route('/change_password', methods=['POST'])
def change_password():
    """Change user password"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario_id']
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validate passwords match
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('user.profile'))
    
    # Change password
    result = UserController.change_password(user_id, old_password, new_password)
    
    if result['success']:
        flash('Password changed successfully!', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('user.profile'))

@user_bp.route('/statistics')
def statistics():
    """User statistics page (placeholder)"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Por ahora redirige al dashboard
    flash('Página de estadísticas en desarrollo', 'info')
    return redirect(url_for('user.dashboard'))
@user_bp.route('/lista')
def lista_usuarios():
    """Lista de todos los usuarios (solo admin)"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('rol') != 'admin':
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Obtener todos los usuarios
    result = UserController.get_all_users()
    usuarios = result['users'] if result['success'] else []
    
    return render_template('admin/lista_usuarios.html', usuarios=usuarios)

@user_bp.route('/crear', methods=['GET', 'POST'])
def crear_usuario():
    """Crear nuevo usuario (solo admin)"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('rol') != 'admin':
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        rol = request.form.get('rol', 'user')
        
        result = UserController.create_user(name, lastname, email, password, rol)
        
        if result['success']:
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('user.lista_usuarios'))
        else:
            flash(result['message'], 'error')
    
    return render_template('admin/crear_usuario.html')

@user_bp.route('/editar/<int:user_id>', methods=['GET', 'POST'])
def editar_usuario(user_id):
    """Editar usuario (solo admin)"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('rol') != 'admin':
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        rol = request.form.get('rol')
        activo = request.form.get('activo') == 'on'
        
        result = UserController.update_user(user_id, name, lastname, email, rol, activo)
        
        if result['success']:
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('user.lista_usuarios'))
        else:
            flash(result['message'], 'error')
    
    # Obtener datos del usuario
    user_result = UserController.get_user_info(user_id)
    usuario = user_result['user'] if user_result['success'] else None
    
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('user.lista_usuarios'))
    
    return render_template('admin/editar_usuario.html', usuario=usuario)

@user_bp.route('/estadisticas')
def estadisticas():
    """Estadísticas generales (solo admin)"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('rol') != 'admin':
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Obtener estadísticas
    result = UserController.get_statistics()
    stats = result['stats'] if result['success'] else {}
    
    return render_template('admin/estadisticas_admin.html', stats=stats)