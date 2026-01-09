"""
Admin Blueprint
Handles administrative functions
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User, SystemSetting
from .user_controller import UserController

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def require_admin():
    """Require admin role for all admin routes"""
    if 'usuario_id' not in session or session.get('rol') != 'admin':
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('auth.login'))

@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard"""
    # Get comprehensive statistics
    all_users = User.get_all() or []
    total_users = len(all_users)
    active_users = len([u for u in all_users if u['activo']])
    inactive_users = len([u for u in all_users if not u['activo']])
    admin_users = len([u for u in all_users if u['rol'] == 'admin'])
    
    # Prepare stats
    stats_usuarios = {
        'total_usuarios': total_users,
        'usuarios_activos': active_users,
        'usuarios_inactivos': inactive_users,
        'admins': admin_users
    }
    
    # Get recent users
    usuarios_recientes = all_users[:5]  # Last 5 users
    
    # Get recent access logs (using a placeholder for now)
    # In a real implementation, we would fetch from AccessLog model
    accesos_recientes = []
    
    return render_template('admin/dashboard_admin.html', 
                         stats_usuarios=stats_usuarios,
                         usuarios_recientes=usuarios_recientes,
                         accesos_recientes=accesos_recientes)

@admin_bp.route('/users')
def list_users():
    """List all users"""
    users = User.get_all() or []
    return render_template('admin/lista_usuarios.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle_active', methods=['POST'])
def toggle_user_active(user_id):
    """Toggle user active status"""
    result = User.toggle_active(user_id)
    
    if result:
        flash('User status updated successfully!', 'success')
    else:
        flash('Failed to update user status', 'error')
    
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete a user"""
    # Prevent deleting oneself
    if user_id == session.get('usuario_id'):
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin.list_users'))
    
    result = User.delete(user_id)
    
    if result:
        flash('User deleted successfully!', 'success')
    else:
        flash('Failed to delete user', 'error')
    
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/acces_logs')
def access_logs():
    """View access logs"""
    from models import AccessLog
    
    # Get access logs
    logs = AccessLog.get_all() or []
    
    # Get all users for the filter dropdown
    all_users = User.get_all() or []
    
    return render_template('admin/logs_accesos.html', logs=logs, usuarios=all_users)

@admin_bp.route('/statistics')
def statistics():
    """View system statistics"""
    from models import Task, User
    
    # Get user statistics
    user_stats = User.get_statistics()
    
    # Get task statistics
    task_stats = Task.get_global_statistics()
    
    # Combine stats
    stats = {
        'total_usuarios': user_stats['total_usuarios'],
        'usuarios_activos': user_stats['usuarios_activos'],
        'usuarios_inactivos': user_stats['usuarios_inactivos'],
        'admins': user_stats['admins'],
        'total_tasks': task_stats['total'],
        'completed_tasks': task_stats['completed'],
        'pending_tasks': task_stats['pending'],
        'by_status': task_stats['by_status'],
        'by_priority': task_stats['by_priority']
    }
    
    return render_template('admin/estadisticas_admin.html', stats=stats)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
def create_user():
    """Create new user (admin only)"""
    if request.method == 'POST':
        name = request.form.get('name')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        rol = request.form.get('rol', 'usuario')
        
        result = UserController.create_user(name, lastname, email, password, rol)
        
        if result['success']:
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('admin.list_users'))
        else:
            flash(result['message'], 'error')
    
    return render_template('admin/crear_usuario.html')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """Edit user (admin only)"""
    if request.method == 'POST':
        name = request.form.get('name')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        rol = request.form.get('rol')
        activo = request.form.get('activo') == 'on'
        
        result = UserController.update_user(user_id, name, lastname, email, rol, activo)
        
        if result['success']:
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('admin.list_users'))
        else:
            flash(result['message'], 'error')
    
    # Get user data
    user_result = UserController.get_user_info(user_id)
    usuario = user_result['user'] if user_result['success'] else None
    
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('admin.list_users'))
    
    return render_template('admin/editar_usuario.html', usuario=usuario)

@admin_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """System settings management"""
    if request.method == 'POST':
        tip = request.form.get('tip_of_the_day')
        SystemSetting.set('consejo_dia', tip)
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))
    
    tip = SystemSetting.get('consejo_dia', '')
    return render_template('admin/configuracion.html', tip=tip)
