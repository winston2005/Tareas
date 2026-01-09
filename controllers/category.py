"""
Category Blueprint
Handles category management operations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .category_controller import CategoryController

# Create blueprint
category_bp = Blueprint('category', __name__, url_prefix='/categories')

@category_bp.route('/')
def list_categories():
    """List all categories for current user"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario_id']
    
    # Get user categories
    result = CategoryController.get_user_categories(user_id)
    categories = result['categories'] if result['success'] else []
    
    # Ordenar alfabéticamente
    categories.sort(key=lambda x: x['nombre'].lower())
    
    return render_template('user/categorias.html', categories=categories)

@category_bp.route('/create', methods=['GET', 'POST'])
def create_category():
    """Create a new category"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario_id']
    
    if request.method == 'POST':
        name = request.form.get('name')
        color = request.form.get('color', '#007bff')
        description = request.form.get('description')
        
        # Create category
        result = CategoryController.create_category(user_id, name, color, description)
        
        if result['success']:
            flash('Category created successfully!', 'success')
            return redirect(url_for('category.list_categories'))
        else:
            flash(result['message'], 'error')
    
    return render_template('user/crear_categoria.html')

@category_bp.route('/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    """Edit a category"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario_id']
    
    # Get category details
    # (In a real implementation, we would verify the category belongs to the user)
    
    if request.method == 'POST':
        name = request.form.get('name')
        color = request.form.get('color', '#007bff')
        description = request.form.get('description')
        
        # Update category
        result = CategoryController.update_category(category_id, user_id, name, color, description)
        
        if result['success']:
            flash('Category updated successfully!', 'success')
            return redirect(url_for('category.list_categories'))
        else:
            flash(result['message'], 'error')
    
    # Get category details for form
    result = CategoryController.get_by_id(category_id)
    category = result['category'] if result['success'] else None
    
    if not category:
        flash('Categoría no encontrada', 'error')
        return redirect(url_for('category.list_categories'))
    
    return render_template('user/editar_categoria.html', category=category)

@category_bp.route('/<int:category_id>/delete', methods=['POST'])
def delete_category(category_id):
    """Delete a category"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario_id']
    
    # Delete category
    result = CategoryController.delete_category(category_id, user_id)
    
    if result['success']:
        flash('Category deleted successfully!', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('category.list_categories'))