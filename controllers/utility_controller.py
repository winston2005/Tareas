"""
Utility Controller
Handles utility functions and data retrieval
"""

from models import State, Priority, History

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