import mysql.connector
from mysql.connector import Error
import hashlib

DB_SERVER_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": ""  
}
DB_NAME = "bd_restaurante"

def hash_password(password):
    """Encripta la contraseña con SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def configurar_bd():
    conexion = None
    try:
        conexion = mysql.connector.connect(**DB_SERVER_CONFIG)
        cursor = conexion.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4")
        cursor.execute(f"USE {DB_NAME}")

        # --- 1. TABLA DE USUARIOS ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(100) NOT NULL UNIQUE,
            gmail VARCHAR(150) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(50) DEFAULT 'mesero'
        )
        """)

        # --- 2. TABLA DE PEDIDOS (RESTAURANTE) ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurante (
            id_registro INT AUTO_INCREMENT PRIMARY KEY,
            nombre_cliente VARCHAR(200) NOT NULL,
            mesa VARCHAR(50),
            fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            items JSON NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            estado VARCHAR(50) DEFAULT 'Pendiente',
            id_usuario INT,
            esta_activo TINYINT(1) NOT NULL DEFAULT 1, 
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
        )
        """)
        
        # --- 3. TABLA DE VENTAS ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id_venta INT AUTO_INCREMENT PRIMARY KEY,
            id_registro INT NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            total DECIMAL(10,2) NOT NULL,
            id_usuario INT,
            FOREIGN KEY (id_registro) REFERENCES restaurante(id_registro) ON DELETE CASCADE,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
        )
        """)

        # --- 4. NUEVA TABLA: MESAS ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mesas (
            id_mesa INT AUTO_INCREMENT PRIMARY KEY,
            numero_mesa VARCHAR(10) NOT NULL UNIQUE,
            estado VARCHAR(50) DEFAULT 'disponible'
        )
        """)

        # --- 5. NUEVA TABLA: HISTORIAL DE CAMBIOS ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_cambios (
            id_historial INT AUTO_INCREMENT PRIMARY KEY,
            id_registro INT NOT NULL,
            id_usuario_modifico INT,
            fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
            descripcion_cambio TEXT,
            FOREIGN KEY (id_registro) REFERENCES restaurante(id_registro) ON DELETE CASCADE,
            FOREIGN KEY (id_usuario_modifico) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
        )
        """)
        
        # --- 6. NUEVA TABLA: CATEGORIAS (Ejemplo de 3ra tabla) ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias_menu (
            id_categoria INT AUTO_INCREMENT PRIMARY KEY,
            nombre_categoria VARCHAR(100) NOT NULL UNIQUE
        )
        """)

        # --- CREACIÓN DE USUARIOS ---
        
        # 1. Insertar el administrador
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE gmail = 'admin@correo.com'")
        if cursor.fetchone()[0] == 0:
            admin_user = "Administrador"
            admin_email = "admin@correo.com"
            admin_pass = hash_password("admin123")
            cursor.execute("""
                INSERT INTO usuarios (usuario, gmail, password_hash, rol)
                VALUES (%s, %s, %s, %s)
            """, (admin_user, admin_email, admin_pass, "admin"))
            print("✅ Usuario administrador creado: admin@correo.com / admin123")

        # 2. (NUEVO) Crear 7 meseros
        
        # Contraseña única para todos los meseros de prueba
        pass_mesero = hash_password("mesero123")
        
        meseros = [
            ("Ana Torres", "ana@correo.com", "mesero"),
            ("Luis Cruz", "luis@correo.com", "mesero"),
            ("Maria Solis", "maria@correo.com", "mesero"),
            ("Carlos Diaz", "carlos@correo.com", "mesero"),
            ("Sofia Vera", "sofia@correo.com", "mesero"),
            ("Javier Ruiz", "javier@correo.com", "mesero"),
            ("Laura Mendi", "laura@correo.com", "mesero")
        ]
        
        query_insertar_mesero = """
            INSERT INTO usuarios (usuario, gmail, password_hash, rol)
            VALUES (%s, %s, %s, %s)
        """
        
        for nombre, email, rol in meseros:
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE gmail = %s", (email,))
            if cursor.fetchone()[0] == 0:
                cursor.execute(query_insertar_mesero, (nombre, email, pass_mesero, rol))
                print(f"✅ Mesero creado: {email} / mesero123")

        conexion.commit()
        print("✅ Base de datos configurada correctamente.")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    configurar_bd()