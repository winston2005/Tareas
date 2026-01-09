"""
Main entry point for Task Management System
Flask application with MVC architecture
"""

from flask import Flask, render_template, session, request, jsonify
import os
from datetime import datetime

# Import database initialization
from models import init_db

# Import controllers
from controllers import (
    auth_bp,
    user_bp, 
    admin_bp,
    task_bp,
    category_bp
)


def create_app():
    """
    Factory function to create and configure Flask application
    
    Returns:
        Configured Flask application
    """
    
    # Create Flask instance
    app = Flask(__name__)
    
    # Application configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DATABASE_PATH'] = os.path.join(os.path.dirname(__file__), 'database', 'tareas.db')
    app.config['SESSION_COOKIE_SECURE'] = False  # Set True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    
    # Initialize database
    try:
        print("🔧 Initializing database...")
        init_db()
        print("✅ Database ready")
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # Register blueprints (controllers)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(task_bp, url_prefix='/tasks')
    app.register_blueprint(category_bp, url_prefix='/categories')
    
    # ================================
    # CHATBOT CONFIGURATION
    # ================================
    
    # Diccionario de respuestas del chatbot (Expandido al 100%)
    chatbot_responses = {
        # Saludos y Conversación General
        'hola': '¡Hola! ¿Cómo puedo ayudarte con tus tareas hoy?',
        'hey': '¡Hola! Qué gusto saludarte. ¿En qué puedo apoyarte con tus tareas?',
        'buenos dias': '¡Buenos días! Espero que tengas una jornada muy productiva. ¿En qué te ayudo?',
        'buenas tardes': '¡Buenas tardes! ¿Cómo va tu día? ¿Necesitas ayuda con tus pendientes?',
        'buenas noches': '¡Buenas noches! ¿Revisando las tareas para mañana? ¿En qué puedo ayudarte?',
        'como estas': 'Estoy muy bien, gracias por preguntar. 😊 Siempre listo para ayudarte a organizar tu día. ¿Y tú, en qué necesitas ayuda?',
        'gracias': '¡De nada! Es un placer ayudarte. Estoy aquí siempre que me necesites para organizar tu trabajo. 😊',
        'adios': '¡Hasta luego! Que tengas un día excelente y muy productivo. 👋',
        'chao': '¡Hasta pronto! Aquí estaré cuando necesites gestionar más tareas.',
        
        # Calendario y Fechas
        'calendario': 'Para ingresar al calendario, busca la opción "Calendario" en el menú lateral izquierdo. Allí verás tus tareas organizadas por fecha.',
        'ver calendario': 'El calendario está en el menú lateral. Es la mejor forma de visualizar tus fechas de entrega.',
        'fecha': 'Si necesitas cambiar la fecha de una tarea, edítala y selecciona una nueva fecha de vencimiento en el formulario.',
        'plazo': 'Mantén atenta la fecha de vencimiento. El calendario te ayudará a no perder ningún plazo importante.',

        # Gestión de Tareas
        'crear tarea': 'Para crear una tarea, haz clic en el botón "+ Nueva Tarea" en el menú lateral o en el Dashboard. Llena los datos y guarda.',
        'nueva tarea': 'Puedes registrar una nueva tarea desde el botón "Nueva Tarea" del menú. ¡Es muy rápido!',
        'editar tarea': 'Para editar una tarea, ve a "Mis Tareas", busca la tarea y haz clic en el botón de editar (el lápiz).',
        'borrar tarea': 'Para eliminar una tarea, usa el botón de eliminar (basura) que aparece junto a cada tarea en tu lista.',
        'eliminar': 'Ten cuidado al eliminar tareas. Si solo ya no la necesitas, considera marcarla como Cancelada o Completada.',
        'completar': 'Marca una tarea como completada usando el checkbox o cambiando su estado a "Completada" en la edición.',
        'mis tareas': 'En la sección "Mis Tareas" del menú verás todo tu listado. Usa los filtros superiores para ordenar por prioridad o estado.',
        
        # Categorías y Etiquetas
        'categorias': 'Las categorías organanizan tus tareas (ej. Trabajo, Personal). Adminístralas desde el menú "Categorías".',
        'crear categoria': 'Ve a "Categorías" y pulsa "Nueva Categoría". Asignales un color para distinguirlas rápidamente.',
        'etiquetas': 'Usa etiquetas para añadir detalles extra a tus tareas. Puedes gestionarlas al crear o editar una tarea.',
        
        # Perfil y Cuenta
        'perfil': 'En "Mi Perfil" (menú lateral) puedes ver tus datos, cambiar tu foto de perfil y actualizar tu información personal.',
        'contraseña': 'Para cambiar tu contraseña, ve a "Mi Perfil" y busca la opción de seguridad. Te pedirá tu contraseña actual.',
        'cerrar sesion': 'Para salir, haz clic en tu nombre en la esquina superior derecha y selecciona "Cerrar Sesión".',
        
        # Prioridades y Estados
        'prioridad': 'Manejamos 4 prioridades: Baja (Gris), Media (Amarillo), Alta (Naranja) y Urgente (Rojo). ¡Úsalas para enfocarte!',
        'estados': 'Las tareas pueden estar: Pendientes, En Progreso, Completadas o Canceladas. Actualízalas según vayas avanzando.',
        'urgente': 'Las tareas Urgentes se destacan en rojo. ¡Dales prioridad en tu día!',
        
        # Dashboard y Ayuda
        'dashboard': 'El Dashboard es tu centro de control: ves tareas para hoy, estadísticas y un resumen de tu productividad.',
        'ayuda': 'Estoy aquí para guiarte. Pregúntame sobre "calendario", "crear tarea", "perfil" o cualquier duda del sistema.',
        'productividad': '💡 Tip: Revisa tu Dashboard cada mañana y ataca primero las tareas de prioridad Alta y Urgente.',
        
        # Default fallback context keys
        'tarea': 'Gestión de tareas: ¿Quieres crear, editar o ver tus tareas? Pregúntame "cómo crear tarea" por ejemplo.',
        'si': '¡Genial! Cuéntame más.',
        'no': 'Entendido. Avísame si necesitas algo más.',
        'claro': 'Me alegra que nos entendamos. ¿Qué más necesitas?'
    }
    
    def get_chatbot_response(user_message, user_name=''):
        """
        Función que genera la respuesta del chatbot
        Analiza el mensaje y busca la mejor coincidencia en el diccionario
        """
        msg = user_message.lower().strip()
        
        # Primero buscamos frases exactas o saludos
        if msg in chatbot_responses:
            if user_name and msg == 'hola':
                 return f'¡Hola {user_name}! ¿Cómo puedo ayudarte con tus tareas hoy?'
            return chatbot_responses[msg]

        # Luego buscamos palabras clave dentro del mensaje
        for key, value in chatbot_responses.items():
            if key in msg:
                # Personalización especial para el saludo
                if user_name and key == 'hola':
                    return f'¡Hola {user_name}! ¿Cómo puedo ayudarte con tus tareas hoy?'
                return value
        
        # Respuestas contextuales
        if 'cuantas tareas' in user_message or 'cuántas tareas' in user_message:
            return 'Puedes ver el resumen de tus tareas en las tarjetas de estadísticas del dashboard.'
        
        if 'urgente' in user_message or 'prioridad' in user_message:
            return 'Las tareas urgentes aparecen marcadas en rojo. Te recomiendo atenderlas primero.'
        
        if 'completada' in user_message or 'terminada' in user_message:
            return 'Para marcar una tarea como completada, ve a la tarea y cambia su estado.'

        if 'frase' in user_message or 'motivacion' in user_message or 'motivacional' in user_message:
            import random
            frases = [
                "El éxito es la suma de pequeños esfuerzos repetidos día tras día.",
                "No cuentes los días, haz que los días cuenten.",
                "Tu único límite es tu mente.",
                "La mejor forma de predecir el futuro es creándolo.",
                "Organizar tu tiempo es organizar tu éxito."
            ]
            return f"Aquí tienes una frase para hoy: \"{random.choice(frases)}\" 💪"
        
        # Respuesta por defecto
        return 'Interesante. ¿Hay algo específico sobre tus tareas en lo que pueda ayudarte? Puedes preguntarme sobre cómo crear tareas, ver estadísticas o consejos de productividad.'
    
    # ================================
    # CHATBOT ENDPOINT
    # ================================
    
    @app.route('/chat', methods=['POST'])
    def chat():
        """
        Endpoint del chatbot - Recibe mensajes y devuelve respuestas
        """
        try:
            data = request.get_json()
            user_message = data.get('message', '')
            
            if not user_message:
                return jsonify({'error': 'No se recibió ningún mensaje'}), 400
            
            # Obtener nombre del usuario de la sesión
            user_name = session.get('nombre', '')
            
            # Obtener respuesta del bot
            bot_response = get_chatbot_response(user_message, user_name)
            
            # Log (opcional)
            print(f"[CHATBOT] Usuario: {user_message}")
            print(f"[CHATBOT] Bot: {bot_response}")
            
            return jsonify({
                'response': bot_response,
                'timestamp': datetime.now().isoformat()
            })
        
        except Exception as e:
            print(f"[CHATBOT ERROR] {e}")
            return jsonify({'error': 'Error al procesar el mensaje'}), 500
    
    # ================================
    # MAIN ROUTES
    # ================================
    
    @app.route('/')
    def index():
        """Home page - always show the main landing page"""
        return render_template('index.html')
    
    @app.route('/about')
    def about():
        """About page"""
        return render_template('about.html')
    
    @app.route('/info')
    def info():
        """Info page"""
        return render_template('info.html')
    
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        """Contact page with form submission handling"""
        if request.method == 'POST':
            from flask import flash, redirect, url_for
            
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            message = request.form.get('message')
            
            # Here we would normally send an email
            # For now, we simulate success and notify the user
            print(f"[CONTACT FORM] De: {name} ({email}) - Asunto: {subject}")
            print(f"[MESSAGE] {message}")
            
            flash(f'¡Gracias {name}! Tu mensaje ha sido enviado correctamente a winstonalvarado94@gmail.com.', 'success')
            return redirect(url_for('contact'))
            
        return render_template('contact.html')

    # ================================
    # RESOURCE ROUTES
    # ================================

    @app.route('/resources/blog')
    def blog():
        """Blog resources page"""
        return render_template('resources/blog.html')

    @app.route('/resources/help')
    def help_page():
        """Help resources page"""
        return render_template('resources/help.html')

    @app.route('/resources/tutorials')
    def tutorials():
        """Tutorials resources page"""
        return render_template('resources/tutorials.html')

    @app.route('/resources/api')
    def api_docs():
        """API documentation page"""
        return render_template('resources/api.html')
        
    @app.route('/resources/article/<int:article_id>')
    def article(article_id):
        """Generic article detail page"""
        print(f"Accessing article: {article_id}")
        # Simulated data store with REAL content
        articles = {
            1: {
                'title': '5 Tips para Organizar tu Día', 
                'date': '8 Enero, 2026', 
                'image': 'https://picsum.photos/id/175/800/400',
                'subtitle': 'Descubre cómo pequeños cambios en tu rutina matutina pueden duplicar tu productividad.',
                'content': '''
                    <p>La organización diaria es la clave para alcanzar tus metas a largo plazo. Aquí te presentamos 5 consejos prácticos:</p>
                    <ol>
                        <li><strong>La Regla de los 2 Minutos:</strong> Si una tarea te toma menos de dos minutos, hazla de inmediato. No la postergues.</li>
                        <li><strong>Prioriza con la Matriz de Eisenhower:</strong> Divide tus tareas en urgentes/importantes. Enfócate primero en lo importante, no solo en lo urgente.</li>
                        <li><strong>Prepara tu día la noche anterior:</strong> Dedica 10 minutos antes de dormir a listar tus 3 objetivos principales para el día siguiente.</li>
                        <li><strong>Usa la técnica Pomodoro:</strong> Trabaja 25 minutos concentrado y descansa 5. Esto mantiene tu mente fresca.</li>
                        <li><strong>Elimina distracciones:</strong> Durante tus bloques de trabajo profundo, silencia las notificaciones del celular.</li>
                    </ol>
                    <p>Implementar estos hábitos puede parecer difícil al principio, pero la consistencia es lo que marcará la diferencia.</p>
                '''
            },
            2: {
                'title': 'Lo Nuevo en la Versión 2.0', 
                'date': '5 Enero, 2026', 
                'image': 'https://picsum.photos/id/1/800/400',
                'subtitle': 'Hemos actualizado el dashboard y agregado nuevas funciones de colaboración.',
                'content': '''
                    <p>Estamos emocionados de anunciar la llegada de la versión 2.0 de nuestro Gestor de Tareas. Esta actualización se centra en la usabilidad y la colaboración.</p>
                    <h3>Novedades Principales:</h3>
                    <ul>
                        <li><strong>Dashboard Interactivo:</strong> Ahora puedes ver gráficos de tu rendimiento semanal en tiempo real.</li>
                        <li><strong>Modo Oscuro:</strong> Para esos momentos de trabajo nocturno, hemos añadido un tema oscuro que cuida tu vista.</li>
                        <li><strong>Etiquetas Personalizadas:</strong> Organiza tus tareas con colores y nombres que tengan sentido para ti.</li>
                    </ul>
                    <p>Gracias por sus comentarios continuos. ¡Seguimos trabajando para mejorar!</p>
                '''
            },
            3: {
                'title': 'Salud Mental y Trabajo Remoto', 
                'date': '28 Diciembre, 2025', 
                'image': 'https://picsum.photos/id/10/800/400',
                'subtitle': 'Estrategias para mantener un equilibrio saludable.',
                'content': '''
                    <p>El trabajo remoto ofrece flexibilidad, pero también puede difuminar la línea entre la vida laboral y personal. Aquí tienes algunas estrategias para mantener el equilibrio:</p>
                    <p><strong>Establece un horario fijo:</strong> Aunque estés en casa, tener una hora de inicio y fin ayuda a tu cerebro a desconectar.</p>
                    <p><strong>Crea un espacio de trabajo dedicado:</strong> Evita trabajar desde la cama o el sofá. Tu cerebro necesita asociar un lugar específico con la productividad.</p>
                    <p><strong>Toma descansos activos:</strong> Levántate, estírate o camina un poco cada hora. Tu cuerpo te lo agradecerá.</p>
                    <p>Recuerda que tu bienestar es lo más importante para ser productivo a largo plazo.</p>
                '''
            }
        }
        
        # Get article or default
        article_data = articles.get(article_id, {
            'title': 'Artículo No Encontrado',
            'date': 'N/A',
            'subtitle': 'El contenido solicitado no está disponible.',
            'content': '<p>Disculpa, no pudimos encontrar el artículo que buscas.</p>'
        })
        
        return render_template('resources/article_detail.html', **article_data)
    
    # ================================
    # ERROR HANDLERS
    # ================================
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 errors"""
        return render_template('errors/403.html'), 403
    
    # ================================
    # CONTEXT PROCESSORS
    # ================================
    
    @app.context_processor
    def inject_user():
        """Inject user information into all templates"""
        return {
            'current_user': {
                'id': session.get('usuario_id'),
                'name': session.get('nombre'),
                'lastname': session.get('apellido'),
                'email': session.get('email'),
                'role': session.get('rol'),
                'is_admin': session.get('rol') == 'admin',
                'is_authenticated': 'usuario_id' in session
            }
        }
    
    # ================================
    # TEMPLATE FILTERS
    # ================================
    
    @app.template_filter('datetime_format')
    def datetime_format(value, format='%Y-%m-%d %H:%M'):
        """Format datetime in templates"""
        if value is None:
            return ''
        try:
            from datetime import datetime
            if isinstance(value, str):
                # Handle ISO format
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime(format)
            return value.strftime(format)
        except:
            return value
    
    @app.template_filter('date_format')
    def date_format(value):
        """Format date only (no time)"""
        if value is None:
            return ''
        try:
            from datetime import datetime
            if isinstance(value, str):
                # Extract date part if datetime string
                if 'T' in value or ' ' in value:
                    date_str = value.split('T')[0].split(' ')[0]
                    dt = datetime.fromisoformat(date_str)
                else:
                    dt = datetime.fromisoformat(value)
                return dt.strftime('%Y-%m-%d')
            return value.strftime('%Y-%m-%d')
        except:
            return value
    
    @app.template_filter('time_ago')
    def time_ago(value):
        """Show relative time (e.g., '2 hours ago')"""
        if value is None:
            return ''
        try:
            from datetime import datetime
            if isinstance(value, str):
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                dt = value
            
            now = datetime.now()
            diff = now - dt
            
            seconds = diff.total_seconds()
            
            if seconds < 60:
                return 'justo ahora'
            elif seconds < 3600:
                minutes = int(seconds / 60)
                return f'hace {minutes} minuto{"s" if minutes != 1 else ""}'
            elif seconds < 86400:
                hours = int(seconds / 3600)
                return f'hace {hours} hora{"s" if hours != 1 else ""}'
            elif seconds < 604800:
                days = int(seconds / 86400)
                return f'hace {days} día{"s" if days != 1 else ""}'
            else:
                return dt.strftime('%Y-%m-%d')
        except:
            return value
    
    @app.template_filter('status_badge')
    def status_badge(estado):
        """Return Bootstrap badge class for status"""
        badges = {
            'Pendiente': 'warning',
            'En Progreso': 'info',
            'Completada': 'success',
            'Cancelada': 'danger'
        }
        return badges.get(estado, 'secondary')
    
    @app.template_filter('priority_badge')
    def priority_badge(prioridad):
        """Return Bootstrap badge class for priority"""
        badges = {
            'Baja': 'secondary',
            'Media': 'warning',
            'Alta': 'orange',
            'Urgente': 'danger'
        }
        return badges.get(prioridad, 'secondary')
    
    return app


def main():
    """Main function to run the application"""
    
    # Create application
    app = create_app()
    
    # Display startup information
    print("\n" + "=" * 70)
    print("🚀 TASK MANAGEMENT SYSTEM WITH CHATBOT")
    print("=" * 70)
    print(f"📁 Database: {app.config['DATABASE_PATH']}")
    print(f"🌐 Server: http://localhost:5000")
    print(f"🤖 Chatbot: Enabled")
    print(f"🔒 Debug Mode: {app.debug}")
    print("=" * 70)
    print("\n📝 AVAILABLE ROUTES:")
    print("\n  🏠 PUBLIC:")
    print("     → Home:     http://localhost:5000/")
    print("     → About:    http://localhost:5000/about")
    print("     → Info:     http://localhost:5000/info")
    print("     → Contact:  http://localhost:5000/contact")
    print("\n  🔐 AUTHENTICATION:")
    print("     → Login:    http://localhost:5000/auth/login")
    print("     → Register: http://localhost:5000/auth/register")
    print("     → Logout:   http://localhost:5000/auth/logout")
    print("\n  👤 USER AREA:")
    print("     → Dashboard: http://localhost:5000/user/dashboard")
    print("     → Profile:   http://localhost:5000/user/profile")
    print("\n  📋 TASKS:")
    print("     → List:      http://localhost:5000/tasks/")
    print("     → Create:    http://localhost:5000/tasks/create")
    print("     → View:      http://localhost:5000/tasks/<id>")
    print("\n  🏷️  CATEGORIES:")
    print("     → List:      http://localhost:5000/categories/")
    print("     → Create:    http://localhost:5000/categories/create")
    print("\n  👑 ADMIN AREA:")
    print("     → Dashboard: http://localhost:5000/admin/dashboard")
    print("     → Users:     http://localhost:5000/admin/users")
    print("\n  🤖 CHATBOT:")
    print("     → Endpoint:  POST http://localhost:5000/chat")
    print("\n" + "=" * 70)
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")
    
    # Run application
    )
if __name__ == '__main__':

    main()
