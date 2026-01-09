"""
Task Blueprint
Handles task management operations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .task_controller import TaskController
from .category_controller import CategoryController
from .utility_controller import UtilityController

# Create blueprint
task_bp = Blueprint('task', __name__, url_prefix='/tasks')

@task_bp.route('/')
def list_tasks():
    """List all tasks for current user"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario_id']
    
    # Get filters from request
    state_id = request.args.get('state', type=int)
    priority_id = request.args.get('priority', type=int)
    category_id = request.args.get('category', type=int)
    
    # Get user tasks
    result = TaskController.get_user_tasks(user_id, state_id, priority_id, category_id)
    tasks = result['tasks'] if result['success'] else []
    
    # Get filter options
    states_result = UtilityController.get_states()
    states = states_result['states'] if states_result['success'] else []
    
    priorities_result = UtilityController.get_priorities()
    priorities = priorities_result['priorities'] if priorities_result['success'] else []
    
    categories_result = CategoryController.get_user_categories(user_id)
    categories = categories_result['categories'] if categories_result['success'] else []
    
    return render_template('user/tareas.html', 
                         tasks=tasks, 
                         states=states, 
                         priorities=priorities, 
                         categories=categories,
                         current_filters={
                             'state': state_id,
                             'priority': priority_id,
                             'category': category_id
                         })

@task_bp.route('/calendar')
def task_calendar():
    """Show tasks in a calendar view"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario_id']
    
    # Get all user tasks (for calendar, we usually want all pending/recent)
    result = TaskController.get_user_tasks(user_id)
    tasks = result['tasks'] if result['success'] else []
    
    return render_template('user/calendario.html', tasks=tasks)

@task_bp.route('/create', methods=['GET', 'POST'])
def create_task():
    """Create a new task"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario_id']
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        state_id = request.form.get('state_id', type=int)
        priority_id = request.form.get('priority_id', type=int)
        category_id = request.form.get('category_id', type=int)
        
        # Create task
        result = TaskController.create_task(user_id, title, description, due_date, state_id, priority_id, category_id)
        
        if result['success']:
            flash('Task created successfully!', 'success')
            return redirect(url_for('task.list_tasks'))
        else:
            flash(result['message'], 'error')
    
    # Get options for form
    states_result = UtilityController.get_states()
    states = states_result['states'] if states_result['success'] else []
    
    priorities_result = UtilityController.get_priorities()
    priorities = priorities_result['priorities'] if priorities_result['success'] else []
    
    categories_result = CategoryController.get_user_categories(user_id)
    categories = categories_result['categories'] if categories_result['success'] else []
    
    return render_template('user/crear_tarea.html', 
                         states=states, 
                         priorities=priorities, 
                         categories=categories)

@task_bp.route('/<int:task_id>')
def view_task(task_id):
    """View a specific task"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Get task details
    result = TaskController.get_task(task_id)
    
    if result['success']:
        task = result['task']
        return render_template('user/ver_tarea.html', task=task)
    else:
        flash('Task not found', 'error')
        return redirect(url_for('task.list_tasks'))

@task_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    """Edit a task"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario_id']
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        state_id = request.form.get('state_id', type=int)
        priority_id = request.form.get('priority_id', type=int)
        category_id = request.form.get('category_id', type=int)
        
        # Update task
        result = TaskController.update_task(task_id, user_id, title, description, due_date, state_id, priority_id, category_id)
        
        if result['success']:
            flash('Task updated successfully!', 'success')
            return redirect(url_for('task.view_task', task_id=task_id))
        else:
            flash(result['message'], 'error')
    
    # Get task details
    task_result = TaskController.get_task(task_id)
    if not task_result['success']:
        flash('Task not found', 'error')
        return redirect(url_for('task.list_tasks'))
    
    task = task_result['task']
    
    # Get options for form
    states_result = UtilityController.get_states()
    states = states_result['states'] if states_result['success'] else []
    
    priorities_result = UtilityController.get_priorities()
    priorities = priorities_result['priorities'] if priorities_result['success'] else []
    
    categories_result = CategoryController.get_user_categories(user_id)
    categories = categories_result['categories'] if categories_result['success'] else []
    
    return render_template('user/editar_tarea.html', 
                         task=task,
                         states=states, 
                         priorities=priorities, 
                         categories=categories)

@task_bp.route('/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Mark task as completed"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario_id']
    
    # Complete task
    result = TaskController.complete_task(task_id, user_id)
    
    if result['success']:
        flash('Task marked as completed!', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('task.list_tasks'))

@task_bp.route('/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Delete a task"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario_id']
    
    # Delete task
    result = TaskController.delete_task(task_id, user_id)
    
    if result['success']:
        flash('Task deleted successfully!', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('task.list_tasks'))