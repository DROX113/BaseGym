import mysql.connector
import bcrypt
import os

def create_database():
    try:
        print("🔧 Configurando base de datos del gimnasio...")
        
        # Conectar a MySQL
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            port='3306'
        )
        cursor = conn.cursor()
        
        # Crear base de datos
        cursor.execute("CREATE DATABASE IF NOT EXISTS gimnasio_db")
        cursor.execute("USE gimnasio_db")
        print("✅ Base de datos creada")
        
        # Tabla de usuarios del sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
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
        
        # Tabla de miembros
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS miembros (
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
        
        # Tabla de membresías
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS membresias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(50) NOT NULL,
                descripcion TEXT,
                precio DECIMAL(10,2) NOT NULL,
                duracion_dias INT NOT NULL,
                acceso_clases BOOLEAN DEFAULT FALSE,
                acceso_area_pesas BOOLEAN DEFAULT TRUE,
                acceso_cardio BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Tabla de pagos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pagos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                miembro_id INT NOT NULL,
                membresia_id INT NOT NULL,
                monto DECIMAL(10,2) NOT NULL,
                fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_inicio DATE NOT NULL,
                fecha_fin DATE NOT NULL,
                metodo_pago ENUM('efectivo', 'tarjeta', 'transferencia') NOT NULL,
                FOREIGN KEY (miembro_id) REFERENCES miembros(id),
                FOREIGN KEY (membresia_id) REFERENCES membresias(id)
            )
        """)
        
        # Tabla de clases
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clases (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                instructor VARCHAR(100) NOT NULL,
                horario TIME NOT NULL,
                duracion_minutos INT NOT NULL,
                capacidad_maxima INT NOT NULL,
                dias_semana VARCHAR(50) NOT NULL,
                activa BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Tabla de asistencias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asistencias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                miembro_id INT NOT NULL,
                clase_id INT,
                fecha_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_salida TIMESTAMP NULL,
                tipo ENUM('area_pesas', 'cardio', 'clase') NOT NULL,
                FOREIGN KEY (miembro_id) REFERENCES miembros(id),
                FOREIGN KEY (clase_id) REFERENCES clases(id)
            )
        """)
        
        # Tabla de logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                accion VARCHAR(100) NOT NULL,
                tabla_afectada VARCHAR(50) NOT NULL,
                registro_id INT,
                detalles TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        print("✅ Todas las tablas creadas")
        
        # Insertar datos iniciales
        hashed_password = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Usuarios del sistema
        usuarios_data = [
            ('admin', hashed_password, 'admin', 'Administrador Principal', 'admin@gimnasio.com'),
            ('responsable1', hashed_password, 'responsable', 'Responsable Operativo', 'responsable@gimnasio.com'),
            ('usuario1', hashed_password, 'usuario', 'Usuario Consulta', 'usuario@gimnasio.com')
        ]
        
        cursor.executemany("INSERT IGNORE INTO usuarios (username, password, rol, nombre, email) VALUES (%s, %s, %s, %s, %s)", usuarios_data)
        
        # Membresías
        membresias_data = [
            ('Básica', 'Acceso a área de pesas y cardio', 300.00, 30, False, True, True),
            ('Premium', 'Acceso completo incluyendo clases grupales', 500.00, 30, True, True, True)
        ]
        
        cursor.executemany("INSERT IGNORE INTO membresias (nombre, descripcion, precio, duracion_dias, acceso_clases, acceso_area_pesas, acceso_cardio) VALUES (%s, %s, %s, %s, %s, %s, %s)", membresias_data)
        
        # Clases
        clases_data = [
            ('Yoga Matutino', 'Clase de yoga para principiantes', 'Ana García', '07:00:00', 60, 20, 'Lunes,Miércoles,Viernes'),
            ('Spinning Intenso', 'Entrenamiento cardiovascular en bicicleta', 'Carlos López', '18:00:00', 45, 15, 'Martes,Jueves')
        ]
        
        cursor.executemany("INSERT IGNORE INTO clases (nombre, descripcion, instructor, horario, duracion_minutos, capacidad_maxima, dias_semana) VALUES (%s, %s, %s, %s, %s, %s, %s)", clases_data)
        
        conn.commit()
        print("🎉 BASE DE DATOS CONFIGURADA EXITOSAMENTE!")
        print("\n📋 CREDENCIALES DE PRUEBA:")
        print("   👤 admin / password: password123")
        print("   👤 responsable1 / password: password123")  
        print("   👤 usuario1 / password: password123")
        
    except mysql.connector.Error as e:
        print(f"❌ Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_database()
