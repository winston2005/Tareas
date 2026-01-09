"""
Controllers for Task Management System
Handles business logic and connects routes with models
"""

from models import User, Task, Category, Tag, State, Priority, Reminder, History, AccessLog
from datetime import datetime, timedelta


# ================================
# USER CONTROLLER
# ================================
class UserController:
    @staticmethod
    def register(name, lastname, email, password):
        """Register a new user"""
        try:
            # Check if email already exists
            existing_user = User.get_by_email(email)
            if existing_user:
                return {'success': False, 'message': 'Email already registered'}
            
            # Create user
            user_id = User.create(name, lastname, email, password)
            
            if user_id:
                # Log registration
                History.create(user_id, None, 'user_registered', 'New user account created')
                return {'success': True, 'message': 'User registered successfully', 'user_id': user_id}
            
            return {'success': False, 'message': 'Failed to create user'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def login(email, password, ip=None, user_agent=None):
        """Authenticate user"""
        try:
            user = User.verify_password(email, password)
            
            if user:
                # Update last access
                User.update_last_access(user['usuario_id'])
                
                # Log access
                AccessLog.create(user['usuario_id'], ip, user_agent, 'login')
                
                return {
                    'success': True, 
                    'message': 'Login successful',
                    'user': user
                }
            
            return {'success': False, 'message': 'Invalid email or password'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def update_profile(user_id, name, lastname, email):
        """Update user profile"""
        try:
            result = User.update(user_id, name, lastname, email)
            
            if result:
                History.create(user_id, None, 'profile_updated', 'User profile information updated')
                return {'success': True, 'message': 'Profile updated successfully'}
            
            return {'success': False, 'message': 'Failed to update profile'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Change user password"""
        try:
            user = User.get_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Verify old password
            from werkzeug.security import check_password_hash
            if not check_password_hash(user['password_hash'], old_password):
                return {'success': False, 'message': 'Current password is incorrect'}
            
            # Update password
            result = User.update_password(user_id, new_password)
            
            if result:
                History.create(user_id, None, 'password_changed', 'User password updated')
                return {'success': True, 'message': 'Password changed successfully'}
            
            return {'success': False, 'message': 'Failed to change password'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_user_info(user_id):
        """Get user information"""
        try:
            user = User.get_by_id(user_id)
            if user:
                # Remove sensitive data
                user.pop('password_hash', None)
                return {'success': True, 'user': user}
            
            return {'success': False, 'message': 'User not found'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}


# ================================
# TASK CONTROLLER
# ================================
class TaskController:
    @staticmethod
    def create_task(user_id, title, description=None, due_date=None, state_id=1, priority_id=2, category_id=None):
        """Create a new task"""
        try:
            task_id = Task.create(user_id, title, description, due_date, state_id, priority_id, category_id)
            
            if task_id:
                History.create(user_id, task_id, 'task_created', f'Task created: {title}')
                return {'success': True, 'message': 'Task created successfully', 'task_id': task_id}
            
            return {'success': False, 'message': 'Failed to create task'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_task(task_id):
        """Get task details"""
        try:
            task = Task.get_by_id(task_id)
            
            if task:
                # Get tags
                tags = Tag.get_by_task(task_id)
                task['tags'] = tags
                
                # Get reminders
                reminders = Reminder.get_by_task(task_id)
                task['reminders'] = reminders
                
                return {'success': True, 'task': task}
            
            return {'success': False, 'message': 'Task not found'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_user_tasks(user_id, state_id=None, priority_id=None, category_id=None):
        """Get all tasks for a user with filters"""
        try:
            tasks = Task.get_by_user(user_id, state_id, priority_id, category_id)
            return {'success': True, 'tasks': tasks, 'count': len(tasks)}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def update_task(task_id, user_id, title, description=None, due_date=None, state_id=None, priority_id=None, category_id=None):
        """Update a task"""
        try:
            result = Task.update(task_id, title, description, due_date, state_id, priority_id, category_id)
            
            if result:
                History.create(user_id, task_id, 'task_updated', f'Task updated: {title}')
                return {'success': True, 'message': 'Task updated successfully'}
            
            return {'success': False, 'message': 'Failed to update task'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def complete_task(task_id, user_id):
        """Mark task as completed"""
        try:
            result = Task.update_state(task_id, 3)  # 3 = Completed
            
            if result:
                task = Task.get_by_id(task_id)
                History.create(user_id, task_id, 'task_completed', f'Task completed: {task["titulo"]}')
                return {'success': True, 'message': 'Task completed successfully'}
            
            return {'success': False, 'message': 'Failed to complete task'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def delete_task(task_id, user_id):
        """Delete a task"""
        try:
            task = Task.get_by_id(task_id)
            
            if not task:
                return {'success': False, 'message': 'Task not found'}
            
            result = Task.delete(task_id)
            
            if result:
                History.create(user_id, None, 'task_deleted', f'Task deleted: {task["titulo"]}')
                return {'success': True, 'message': 'Task deleted successfully'}
            
            return {'success': False, 'message': 'Failed to delete task'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_dashboard_stats(user_id):
        """Get dashboard statistics for a user"""
        try:
            all_tasks = Task.get_by_user(user_id)
            
            stats = {
                'total': len(all_tasks),
                'pending': len([t for t in all_tasks if t['estado_id'] == 1]),
                'in_progress': len([t for t in all_tasks if t['estado_id'] == 2]),
                'completed': len([t for t in all_tasks if t['estado_id'] == 3]),
                'high_priority': len([t for t in all_tasks if t['prioridad_id'] == 3]),
                'overdue': 0
            }
            
            # Count overdue tasks
            today = datetime.now().date()
            for task in all_tasks:
                if task['fecha_vencimiento'] and task['estado_id'] != 3:
                    due_date = datetime.strptime(task['fecha_vencimiento'], '%Y-%m-%d %H:%M:%S').date()
                    if due_date < today:
                        stats['overdue'] += 1
            
            return {'success': True, 'stats': stats}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}


# ================================
# CATEGORY CONTROLLER
# ================================
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
            
            if result:
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
            
            if result:
                History.create(user_id, None, 'category_deleted', f'Category deleted: {category["nombre"]}')
                return {'success': True, 'message': 'Category deleted successfully'}
            
            return {'success': False, 'message': 'Failed to delete category'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}


# ================================
# TAG CONTROLLER
# ================================
class TagController:
    @staticmethod
    def create_tag(user_id, name):
        """Create a new tag"""
        try:
            tag_id = Tag.create(user_id, name)
            
            if tag_id:
                return {'success': True, 'message': 'Tag created successfully', 'tag_id': tag_id}
            
            return {'success': False, 'message': 'Failed to create tag'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_user_tags(user_id):
        """Get all tags for a user"""
        try:
            tags = Tag.get_by_user(user_id)
            return {'success': True, 'tags': tags}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def assign_tag_to_task(task_id, tag_id):
        """Assign a tag to a task"""
        try:
            result = Tag.add_to_task(task_id, tag_id)
            
            if result:
                return {'success': True, 'message': 'Tag assigned successfully'}
            
            return {'success': False, 'message': 'Failed to assign tag'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def remove_tag_from_task(task_id, tag_id):
        """Remove a tag from a task"""
        try:
            result = Tag.remove_from_task(task_id, tag_id)
            
            if result:
                return {'success': True, 'message': 'Tag removed successfully'}
            
            return {'success': False, 'message': 'Failed to remove tag'}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}


# ================================
# UTILITY CONTROLLER
# ================================
class UtilityController:
    @staticmethod
    def get_states():
        """Get all available states"""
        try:
            states = State.get_all()
            return {'success': True, 'states': states}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_priorities():
        """Get all available priorities"""
        try:
            priorities = Priority.get_all()
            return {'success': True, 'priorities': priorities}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_user_history(user_id, limit=50):
        """Get user activity history"""
        try:
            history = History.get_by_user(user_id, limit)
            return {'success': True, 'history': history}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_task_history(task_id):
        """Get task activity history"""
        try:
            history = History.get_by_task(task_id)
            return {'success': True, 'history': history}
        
        except Exception as e:
            return {'success': False, 'message': str(e)}