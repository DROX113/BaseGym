from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from mysql.connector import Error
from functools import wraps
import bcrypt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave-secreta-gimnasio')

# --- CONEXIÓN MYSQL MEJORADA ---
def get_db_connection():
    try:
        # Mostrar las variables para debug
        host = os.getenv('MYSQLHOST')
        user = os.getenv('MYSQLUSER')
        print(f"🔌 Conectando a: {host} como {user}")
        
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=os.getenv('MYSQLPASSWORD'),
            database='railway',
            port=int(os.getenv('MYSQLPORT', '3306'))
        )
        print("✅ Conexión exitosa a MySQL")
        return conn
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

# --- INICIALIZACIÓN AUTOMÁTICA DE BD ---
def init_database():
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Verificar si la tabla usuarios existe
            cursor.execute("SHOW TABLES LIKE 'usuarios'")
            if not cursor.fetchone():
                print("📦 Creando estructura de base de datos...")
                
                # Crear tabla usuarios
                cursor.execute("""
                    CREATE TABLE usuarios (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        rol ENUM('admin', 'responsable', 'usuario') NOT NULL,
                        nombre VARCHAR(100) NOT NULL,
                        email VARCHAR(100),
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        activo BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # Insertar usuario admin
                hashed_pwd = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute(
                    "INSERT INTO usuarios (username, password, rol, nombre, email) VALUES (%s, %s, %s, %s, %s)",
                    ('admin', hashed_pwd, 'admin', 'Administrador', 'admin@gimnasio.com')
                )
                
                conn.commit()
                print("✅ Base de datos inicializada correctamente")
            else:
                print("✅ Base de datos ya está inicializada")
            
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"❌ Error inicializando BD: {e}")

# Llamar la función al inicio
init_database()

# --- DECORADORES ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if session.get('user_rol') not in roles:
                flash('No tienes permisos para acceder a esta página', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ========= FUNCIONES AUXILIARES ==========
def registrar_log(accion, tabla_afectada, registro_id=None, detalles=None):
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                INSERT INTO logs (usuario_id, accion, tabla_afectada, registro_id, detalles)
                VALUES (%s, %s, %s, %s, %s)
            """, (session['user_id'], accion, tabla_afectada, registro_id, detalles))
            conn.commit()
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Error al registrar log: {e}")

# --- RUTAS DE AUTENTICACIÓN ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT * FROM usuarios WHERE username = %s AND activo = TRUE", (username,))
                user = cur.fetchone()
                cur.close()
                conn.close()

                if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                    session['user_id'] = user['id']
                    session['user_rol'] = user['rol']
                    session['user_nombre'] = user['nombre']
                    registrar_log('LOGIN', 'usuarios', user['id'], 'Inicio de sesión exitoso')
                    flash(f'¡Bienvenido, {user["nombre"]}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Usuario o contraseña incorrectos', 'error')
            else:
                flash('Error de conexión a la base de datos', 'error')
        except Exception as e:
            flash(f'Error de conexión: {str(e)}', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        registrar_log('LOGOUT', 'usuarios', session['user_id'], 'Cierre de sesión')
        session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('index'))

# ================= DASHBOARD =================
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos', 'error')
        return render_template('dashboard.html', 
                            total_miembros=0, 
                            pagos_hoy=0, 
                            asistencias_hoy=0, 
                            clases_activas=0, 
                            ultimos_logs=[])

    try:
        cur = conn.cursor(dictionary=True)
        
        # Estadísticas
        cur.execute("SELECT COUNT(*) as total FROM miembros WHERE activo = TRUE")
        total_miembros = cur.fetchone()['total']

        cur.execute("SELECT COUNT(*) as total FROM pagos WHERE DATE(fecha_pago) = CURDATE()")
        pagos_result = cur.fetchone()
        pagos_hoy = pagos_result['total'] if pagos_result else 0

        cur.execute("SELECT COUNT(*) as total FROM asistencias WHERE DATE(fecha_entrada) = CURDATE()")
        asistencias_result = cur.fetchone()
        asistencias_hoy = asistencias_result['total'] if asistencias_result else 0

        cur.execute("SELECT COUNT(*) as total FROM clases WHERE activa = TRUE")
        clases_activas = cur.fetchone()['total']

        # Últimos logs
        cur.execute("""
            SELECT l.*, u.username
            FROM logs l
            JOIN usuarios u ON l.usuario_id = u.id
            ORDER BY l.fecha DESC
            LIMIT 5
        """)
        ultimos_logs = cur.fetchall()

        cur.close()
        conn.close()

        return render_template('dashboard.html',
                            total_miembros=total_miembros,
                            pagos_hoy=pagos_hoy,
                            asistencias_hoy=asistencias_hoy,
                            clases_activas=clases_activas,
                            ultimos_logs=ultimos_logs)
    
    except Exception as e:
        conn.close()
        flash(f'Error al cargar dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', 
                            total_miembros=0, 
                            pagos_hoy=0, 
                            asistencias_hoy=0, 
                            clases_activas=0, 
                            ultimos_logs=[])

# --- RUTAS SIMPLIFICADAS PARA PRUEBA ---
@app.route('/miembros')
@login_required
@role_required(['admin', 'responsable'])
def miembros():
    flash('Funcionalidad en desarrollo - Base de datos en configuración', 'info')
    return redirect(url_for('dashboard'))

@app.route('/pagos')
@login_required
@role_required(['admin', 'responsable'])
def pagos():
    flash('Funcionalidad en desarrollo - Base de datos en configuración', 'info')
    return redirect(url_for('dashboard'))

@app.route('/clases')
@login_required
@role_required(['admin', 'responsable'])
def clases():
    flash('Funcionalidad en desarrollo - Base de datos en configuración', 'info')
    return redirect(url_for('dashboard'))

# ================== EJECUCIÓN PARA RAILWAY ==================
if __name__ == '__main__':
    # Solo ejecutar con Flask en desarrollo local
    print("🚀 Ejecutando en modo desarrollo...")
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # En producción, Railway usa gunicorn automáticamente
    print("🎉 Aplicación lista para producción")
