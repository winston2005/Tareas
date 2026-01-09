"""
Task Controller
Handles task-related business logic
"""

from models import Task, Tag, Reminder, History
from datetime import datetime

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