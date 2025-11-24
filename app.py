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

# Configuración de MySQL para XAMPP
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'gimnasio_db')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', '3306'))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# --- INICIALIZACIÓN DE BASE DE DATOS MEJORADA ---
def init_database():
    import time
    max_retries = 5
    retry_delay = 5  # segundos
    
    for attempt in range(max_retries):
        try:
            print(f"🔧 Intentando conectar a la BD (intento {attempt + 1}/{max_retries})...")
            cur = mysql.connection.cursor()
            
            # Verificar si la tabla usuarios existe
            cur.execute("SHOW TABLES LIKE 'usuarios'")
            if not cur.fetchone():
                print("📦 Creando estructura inicial...")
                
                # Crear tabla usuarios
                cur.execute("""
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
                
                # Crear tabla miembros
                cur.execute("""
                    CREATE TABLE miembros (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        codigo_miembro VARCHAR(20) UNIQUE NOT NULL,
                        nombre VARCHAR(100) NOT NULL,
                        apellido VARCHAR(100) NOT NULL,
                        email VARCHAR(100),
                        telefono VARCHAR(15),
                        fecha_nacimiento DATE,
                        direccion TEXT,
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        activo BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # Insertar usuario admin
                import bcrypt
                hashed_pwd = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cur.execute("INSERT IGNORE INTO usuarios (username, password, rol, nombre, email) VALUES (%s, %s, %s, %s, %s)", 
                          ('admin', hashed_pwd, 'admin', 'Administrador', 'admin@gimnasio.com'))
                
                mysql.connection.commit()
                print("✅ Base de datos inicializada exitosamente")
            else:
                print("✅ Base de datos ya está inicializada")
            
            cur.close()
            return True
            
        except Exception as e:
            print(f"❌ Intento {attempt + 1} falló: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Reintentando en {retry_delay} segundos...")
                time.sleep(retry_delay)
            else:
                print("🚨 Todos los intentos fallaron")
                return False

# Ejecutar de forma segura
def safe_init():
    try:
        with app.app_context():
            init_database()
    except Exception as e:
        print(f"⚠️ Init seguro falló: {e}")

# Llamar de forma asíncrona después de 10 segundos
import threading
def delayed_init():
    time.sleep(10)
    safe_init()

# Iniciar en segundo plano
threading.Thread(target=delayed_init, daemon=True).start()

# ========== DECORADORES ==========
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

# ========== FUNCIONES AUXILIARES ==========
def registrar_log(accion, tabla_afectada, registro_id=None, detalles=None):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO logs (usuario_id, accion, tabla_afectada, registro_id, detalles)
            VALUES (%s, %s, %s, %s, %s)
        """, (session['user_id'], accion, tabla_afectada, registro_id, detalles))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print(f"Error al registrar log: {e}")

# ========== RUTAS DE AUTENTICACIÓN ==========
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios WHERE username = %s AND activo = TRUE", (username,))
            user = cur.fetchone()
            cur.close()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session['user_id'] = user['id']
                session['user_rol'] = user['rol']
                session['user_nombre'] = user['nombre']
                registrar_log('LOGIN', 'usuarios', user['id'], 'Inicio de sesión exitoso')
                flash(f'¡Bienvenido, {user["nombre"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Usuario o contraseña incorrectos', 'error')
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

# ========== DASHBOARD ==========
@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    
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
    
    return render_template('dashboard.html', 
                         total_miembros=total_miembros,
                         pagos_hoy=pagos_hoy,
                         asistencias_hoy=asistencias_hoy,
                         clases_activas=clases_activas,
                         ultimos_logs=ultimos_logs)

# ========== GESTIÓN COMPLETA DE MIEMBROS (CRUD) ==========
@app.route('/miembros')
@login_required
@role_required(['admin', 'responsable'])
def miembros():
    search = request.args.get('search', '')
    cur = mysql.connection.cursor()
    
    if search:
        cur.execute("""
            SELECT m.*, 
                   (SELECT fecha_fin FROM pagos WHERE miembro_id = m.id ORDER BY fecha_pago DESC LIMIT 1) as membresia_vigente_hasta
            FROM miembros m 
            WHERE m.activo = TRUE AND (m.nombre LIKE %s OR m.apellido LIKE %s OR m.codigo_miembro LIKE %s)
            ORDER BY m.nombre
        """, (f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        cur.execute("""
            SELECT m.*, 
                   (SELECT fecha_fin FROM pagos WHERE miembro_id = m.id ORDER BY fecha_pago DESC LIMIT 1) as membresia_vigente_hasta
            FROM miembros m 
            WHERE m.activo = TRUE 
            ORDER BY m.nombre
        """)
    
    miembros = cur.fetchall()
    cur.close()
    return render_template('miembros.html', miembros=miembros, search=search)

@app.route('/miembros/agregar', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'responsable'])
def agregar_miembro():
    if request.method == 'POST':
        codigo_miembro = request.form['codigo_miembro']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        telefono = request.form['telefono']
        fecha_nacimiento = request.form['fecha_nacimiento']
        direccion = request.form['direccion']
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO miembros (codigo_miembro, nombre, apellido, email, telefono, fecha_nacimiento, direccion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (codigo_miembro, nombre, apellido, email, telefono, fecha_nacimiento, direccion))
            mysql.connection.commit()
            miembro_id = cur.lastrowid
            
            registrar_log('INSERT', 'miembros', miembro_id, f'Nuevo miembro: {nombre} {apellido} - Código: {codigo_miembro}')
            flash('Miembro agregado exitosamente', 'success')
            return redirect(url_for('miembros'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al agregar miembro: {str(e)}', 'error')
        finally:
            cur.close()
    
    return render_template('agregar_miembro.html')

@app.route('/miembros/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'responsable'])
def editar_miembro(id):
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        telefono = request.form['telefono']
        fecha_nacimiento = request.form['fecha_nacimiento']
        direccion = request.form['direccion']
        
        try:
            cur.execute("""
                UPDATE miembros 
                SET nombre = %s, apellido = %s, email = %s, telefono = %s, fecha_nacimiento = %s, direccion = %s
                WHERE id = %s
            """, (nombre, apellido, email, telefono, fecha_nacimiento, direccion, id))
            mysql.connection.commit()
            
            registrar_log('UPDATE', 'miembros', id, f'Actualización de datos del miembro ID: {id}')
            flash('Miembro actualizado exitosamente', 'success')
            return redirect(url_for('miembros'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al actualizar miembro: {str(e)}', 'error')
    
    cur.execute("SELECT * FROM miembros WHERE id = %s", (id,))
    miembro = cur.fetchone()
    cur.close()
    
    if not miembro:
        flash('Miembro no encontrado', 'error')
        return redirect(url_for('miembros'))
    
    return render_template('editar_miembro.html', miembro=miembro)

@app.route('/miembros/eliminar/<int:id>')
@login_required
@role_required(['admin', 'responsable'])
def eliminar_miembro(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE miembros SET activo = FALSE WHERE id = %s", (id,))
        mysql.connection.commit()
        
        registrar_log('DELETE', 'miembros', id, 'Miembro marcado como inactivo')
        flash('Miembro eliminado exitosamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar miembro: {str(e)}', 'error')
    finally:
        cur.close()
    
    return redirect(url_for('miembros'))

# ========== SISTEMA DE PAGOS ==========
@app.route('/pagos')
@login_required
@role_required(['admin', 'responsable'])
def pagos():
    search = request.args.get('search', '')
    cur = mysql.connection.cursor()
    
    if search:
        cur.execute("""
            SELECT p.*, m.nombre, m.apellido, m.codigo_miembro, ms.nombre as membresia_nombre,
                   ms.precio as precio_membresia
            FROM pagos p
            JOIN miembros m ON p.miembro_id = m.id
            JOIN membresias ms ON p.membresia_id = ms.id
            WHERE m.nombre LIKE %s OR m.apellido LIKE %s OR m.codigo_miembro LIKE %s
            ORDER BY p.fecha_pago DESC
        """, (f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        cur.execute("""
            SELECT p.*, m.nombre, m.apellido, m.codigo_miembro, ms.nombre as membresia_nombre,
                   ms.precio as precio_membresia
            FROM pagos p
            JOIN miembros m ON p.miembro_id = m.id
            JOIN membresias ms ON p.membresia_id = ms.id
            ORDER BY p.fecha_pago DESC
        """)
    
    pagos = cur.fetchall()
    cur.close()
    
    # Pasar la fecha de hoy al template
    hoy = datetime.datetime.now().date()
    
    return render_template('pagos.html', pagos=pagos, search=search, hoy=hoy)

@app.route('/pagos/registrar', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'responsable'])
def registrar_pago():
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        try:
            miembro_id = request.form['miembro_id']
            membresia_id = request.form['membresia_id']
            monto = float(request.form['monto'])
            fecha_inicio = request.form['fecha_inicio']
            metodo_pago = request.form['metodo_pago']
            
            # Obtener duración de la membresía
            cur.execute("SELECT duracion_dias, precio FROM membresias WHERE id = %s", (membresia_id,))
            membresia = cur.fetchone()
            
            if not membresia:
                flash('Membresía no encontrada', 'error')
                return redirect(url_for('registrar_pago'))
            
            # Calcular fecha fin
            fecha_inicio_obj = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin = fecha_inicio_obj + datetime.timedelta(days=membresia['duracion_dias'])
            
            # Insertar pago
            cur.execute("""
                INSERT INTO pagos (miembro_id, membresia_id, monto, fecha_inicio, fecha_fin, metodo_pago)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (miembro_id, membresia_id, monto, fecha_inicio, fecha_fin.date(), metodo_pago))
            
            mysql.connection.commit()
            pago_id = cur.lastrowid
            
            # Obtener nombre del miembro para el log
            cur.execute("SELECT nombre, apellido FROM miembros WHERE id = %s", (miembro_id,))
            miembro = cur.fetchone()
            
            registrar_log('INSERT', 'pagos', pago_id, f'Pago registrado: ${monto} - Miembro: {miembro["nombre"]} {miembro["apellido"]}')
            flash('Pago registrado exitosamente', 'success')
            return redirect(url_for('pagos'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al registrar pago: {str(e)}', 'error')
            print(f"ERROR DETALLADO: {str(e)}")  # Para debug
    
    # Obtener datos para el formulario (GET request)
    try:
        cur.execute("SELECT id, codigo_miembro, nombre, apellido FROM miembros WHERE activo = TRUE ORDER BY nombre")
        miembros = cur.fetchall()
        
        cur.execute("SELECT * FROM membresias ORDER BY nombre")
        membresias = cur.fetchall()
        
    except Exception as e:
        flash(f'Error al cargar datos: {str(e)}', 'error')
        miembros = []
        membresias = []
    finally:
        cur.close()
    
    return render_template('registrar_pago.html', miembros=miembros, membresias=membresias)

@app.route('/pagos/eliminar/<int:id>')
@login_required
@role_required(['admin', 'responsable'])
def eliminar_pago(id):
    cur = mysql.connection.cursor()
    try:
        # Obtener info del pago antes de eliminar para el log
        cur.execute("""
            SELECT p.id, m.nombre, m.apellido, p.monto 
            FROM pagos p 
            JOIN miembros m ON p.miembro_id = m.id 
            WHERE p.id = %s
        """, (id,))
        pago = cur.fetchone()
        
        cur.execute("DELETE FROM pagos WHERE id = %s", (id,))
        mysql.connection.commit()
        
        registrar_log('DELETE', 'pagos', id, f'Pago eliminado: ${pago["monto"]} - Miembro: {pago["nombre"]} {pago["apellido"]}')
        flash('Pago eliminado exitosamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar pago: {str(e)}', 'error')
    finally:
        cur.close()
    
    return redirect(url_for('pagos'))

# ========== GESTIÓN DE CLASES ==========
@app.route('/clases')
@login_required
@role_required(['admin', 'responsable'])
def clases():
    """Admin y Responsable pueden gestionar clases"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM clases ORDER BY nombre")
    clases = cur.fetchall()
    cur.close()
    
    # Convertir timedelta a string para el template
    for clase in clases:
        if isinstance(clase['horario'], datetime.timedelta):
            # Convertir timedelta a datetime y luego a string
            dummy_date = datetime.datetime(2000, 1, 1)  # Fecha dummy
            horario_datetime = dummy_date + clase['horario']
            clase['horario_str'] = horario_datetime.strftime('%H:%M')
        else:
            clase['horario_str'] = str(clase['horario'])
    return render_template('clases.html', clases=clases)

@app.route('/clases/agregar', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'responsable'])
def agregar_clase():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        instructor = request.form['instructor']
        horario = request.form['horario']
        duracion_minutos = request.form['duracion_minutos']
        capacidad_maxima = request.form['capacidad_maxima']
        dias_semana = request.form['dias_semana']
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO clases (nombre, descripcion, instructor, horario, duracion_minutos, capacidad_maxima, dias_semana)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nombre, descripcion, instructor, horario, duracion_minutos, capacidad_maxima, dias_semana))
            mysql.connection.commit()
            clase_id = cur.lastrowid
            
            registrar_log('INSERT', 'clases', clase_id, f'Nueva clase: {nombre} - Instructor: {instructor}')
            flash('Clase agregada exitosamente', 'success')
            return redirect(url_for('clases'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al agregar clase: {str(e)}', 'error')
        finally:
            cur.close()
    
    return render_template('agregar_clase.html')

@app.route('/clases/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'responsable'])
def editar_clase(id):
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        instructor = request.form['instructor']
        horario = request.form['horario']
        duracion_minutos = request.form['duracion_minutos']
        capacidad_maxima = request.form['capacidad_maxima']
        dias_semana = request.form['dias_semana']
        activa = 1 if request.form.get('activa') else 0
        
        try:
            cur.execute("""
                UPDATE clases 
                SET nombre = %s, descripcion = %s, instructor = %s, horario = %s, 
                    duracion_minutos = %s, capacidad_maxima = %s, dias_semana = %s, activa = %s
                WHERE id = %s
            """, (nombre, descripcion, instructor, horario, duracion_minutos, capacidad_maxima, dias_semana, activa, id))
            mysql.connection.commit()
            
            registrar_log('UPDATE', 'clases', id, f'Actualización de clase: {nombre}')
            flash('Clase actualizada exitosamente', 'success')
            return redirect(url_for('clases'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al actualizar clase: {str(e)}', 'error')
    
    cur.execute("SELECT * FROM clases WHERE id = %s", (id,))
    clase = cur.fetchone()
    cur.close()
    
    if not clase:
        flash('Clase no encontrada', 'error')
        return redirect(url_for('clases'))
    
    return render_template('editar_clase.html', clase=clase)

@app.route('/clases/eliminar/<int:id>')
@login_required
@role_required(['admin', 'responsable'])
def eliminar_clase(id):
    cur = mysql.connection.cursor()
    try:
        # Obtener info de la clase antes de eliminar para el log
        cur.execute("SELECT nombre FROM clases WHERE id = %s", (id,))
        clase = cur.fetchone()
        
        cur.execute("DELETE FROM clases WHERE id = %s", (id,))
        mysql.connection.commit()
        
        registrar_log('DELETE', 'clases', id, f'Clase eliminada: {clase["nombre"]}')
        flash('Clase eliminada exitosamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar clase: {str(e)}', 'error')
    finally:
        cur.close()
    
    return redirect(url_for('clases'))

# ========== CONSULTAS PARA USUARIOS REGULARES ==========
@app.route('/consultas/miembros')
@login_required
def consultas_miembros():
    """Usuarios normales solo ven esta versión de solo lectura"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT codigo_miembro, nombre, apellido, email, telefono, fecha_registro 
        FROM miembros 
        WHERE activo = TRUE 
        ORDER BY nombre
    """)
    miembros = cur.fetchall()
    cur.close()
    return render_template('consultas_miembros.html', miembros=miembros, datetime=datetime)

@app.route('/consultas/pagos')
@login_required  
def consultas_pagos():
    """Usuarios normales solo ven esta versión de solo lectura"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.fecha_pago, m.codigo_miembro, m.nombre, m.apellido, 
               ms.nombre as membresia_nombre, p.monto, p.metodo_pago,
               p.fecha_inicio, p.fecha_fin
        FROM pagos p
        JOIN miembros m ON p.miembro_id = m.id
        JOIN membresias ms ON p.membresia_id = ms.id
        ORDER BY p.fecha_pago DESC
        LIMIT 50
    """)
    pagos = cur.fetchall()
    cur.close()
    
    hoy = datetime.datetime.now().date()
    return render_template('consultas_pagos.html', pagos=pagos, hoy=hoy)

@app.route('/consultas/clases')
@login_required
def consultas_clases():
    """Todos los usuarios pueden ver las clases (solo lectura)"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM clases WHERE activa = TRUE ORDER BY nombre")
    clases = cur.fetchall()
    cur.close()
    return render_template('consultas_clases.html', clases=clases)

# ========== LOGS DEL SISTEMA ==========
@app.route('/logs')
@login_required
@role_required(['admin'])
def ver_logs():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT l.*, u.username, u.nombre as usuario_nombre
        FROM logs l
        JOIN usuarios u ON l.usuario_id = u.id
        ORDER BY l.fecha DESC
        LIMIT 100
    """)
    logs = cur.fetchall()
    cur.close()
    return render_template('logs.html', logs=logs)

# ========== EJECUCIÓN ==========
if __name__ == '__main__':
    # Verificar si está en Render (producción) o local (desarrollo)
    if 'RENDER' in os.environ:
        # 🚀 CONFIGURACIÓN PARA RENDER (PRODUCCIÓN)
        port = int(os.environ.get('PORT', 5000))
        print(f"🚀 Iniciando servidor en modo producción - Puerto: {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # 💻 CONFIGURACIÓN PARA DESARROLLO LOCAL
        print("=" * 60)
        print("🚀 Sistema de Gimnasio - VERSIÓN COMPLETA CON GESTIÓN DE CLASES")
        print("=" * 60)
        print("📊 Usuarios de prueba:")
        print("   👤 admin / contraseña: password123 (Control total)")
        print("   👤 responsable1 / contraseña: password123 (Gestión sin borrar base)")  
        print("   👤 usuario1 / contraseña: password123 (Solo consultas)")
        print("=" * 60)
        print("🌐 Abre tu navegador y ve a: http://localhost:5000")
        print("=" * 60)
        app.run(debug=True, host='0.0.0.0', port=5000)
