"""
User Controller
Handles user-related business logic
"""

from models import User, History, AccessLog

class UserController:
    @staticmethod
    def register(name, lastname, email, password):
        """Register a new user"""
        try:
            # Check if email already exists
            existing_user = User.get_by_email(email)
            if existing_user:
                return {'success': False, 'message': 'Email already registered'}
            
            # Create user with default role 'usuario'
            user_id = User.create(name, lastname, email, password, 'usuario')
            
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
    def update_profile(user_id, name, lastname, email, photo_filename=None):
        """Update user profile"""
        try:
            result = User.update(user_id, name, lastname, email, photo_filename)
            
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
        
    @staticmethod
    def get_all_users():
        """Obtiene todos los usuarios del sistema"""
        try:
            users = User.get_all()
            return {
                'success': True,
                'users': users
            }
        except Exception as e:
            print(f"❌ Error getting all users: {e}")
            return {
                'success': False,
                'message': f'Error al obtener usuarios: {str(e)}',
                'users': []
            }
    @staticmethod
    def create_user(name, lastname, email, password, rol='usuario'):
        """Crear nuevo usuario"""
        try:
            user_id = User.create(name, lastname, email, password, rol)
            if user_id:
                return {'success': True, 'user_id': user_id}
            return {'success': False, 'message': 'Error al crear usuario'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def update_user(user_id, name, lastname, email, rol, activo):
        """Actualizar usuario"""
        try:
            result = User.update(user_id, name, lastname, email, rol, activo)
            return {'success': result, 'message': 'Usuario actualizado' if result else 'Error al actualizar'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def get_statistics():
        """Obtener estadísticas de usuarios"""
        try:
            stats = User.get_statistics()
            return {'success': True, 'stats': stats}
        except Exception as e:
            return {'success': False, 'message': str(e)}