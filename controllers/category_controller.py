"""
Category Controller
Handles category-related business logic
"""

from models import Category, History

class CategoryController:
    @staticmethod
    def create_category(user_id, name, color='#6366f1', description=None):
        """Create a new category"""
        try:
            category_id = Category.create(user_id, name, color, description)
            
            if category_id:
                History.create(user_id, None, 'category_created', f'Category created: {name}')
                return {'success': True, 'message': 'Category created successfully', 'category_id': category_id}
            
            return {'success': False, 'message': 'Failed to create category'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_by_id(category_id):
        """Get category by ID"""
        try:
            category = Category.get_by_id(category_id)
            return {'success': True, 'category': category}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_user_categories(user_id):
        """Get all categories for a user"""
        try:
            categories = Category.get_by_user(user_id)
            return {'success': True, 'categories': categories}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def update_category(category_id, user_id, name, color, description=None):
        """Update a category"""
        try:
            result = Category.update(category_id, name, color, description)
            
            if result is not None:
                History.create(user_id, None, 'category_updated', f'Category updated: {name}')
                return {'success': True, 'message': 'Category updated successfully'}
            
            return {'success': False, 'message': 'Failed to update category'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def delete_category(category_id, user_id):
        """Delete a category"""
        try:
            category = Category.get_by_id(category_id)
            
            if not category:
                return {'success': False, 'message': 'Category not found'}
            
            result = Category.delete(category_id)
            
            if result is not None:
                History.create(user_id, None, 'category_deleted', f'Category deleted: {category["nombre"]}')
                return {'success': True, 'message': 'Category deleted successfully'}
            
            return {'success': False, 'message': 'Failed to delete category'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}