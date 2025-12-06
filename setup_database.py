import mysql.connector
from mysql.connector import Error
import hashlib

# CONFIGURACIÓN
DB_CONFIG = {"host": "localhost", "user": "root", "password": ""}
DB_NAME = "restaurante_pro_db"

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4")
        cursor.execute(f"USE {DB_NAME}")

        # TABLAS
        cursor.execute("""
            CREATE TABLE usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                rol VARCHAR(50) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE menu (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(150) NOT NULL,
                categoria VARCHAR(50) NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                activo TINYINT DEFAULT 1
            )
        """)

        cursor.execute("""
            CREATE TABLE pedidos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente VARCHAR(100),
                mesa VARCHAR(50),
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                total DECIMAL(10,2) DEFAULT 0,
                estado VARCHAR(50) DEFAULT 'Pendiente',
                items JSON,
                id_usuario INT,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
            )
        """)

        # USUARIOS
        admins = [("Administrador", "admin@correo.com", "admin123", "admin")]
        meseros = [("Mesero Principal", "mesero@correo.com", "mesero123", "mesero")]
        cocina = [("Jefe Cocina", "cocina@correo.com", "cocina123", "cocina")]
        
        for name, mail, pwd, rol in admins + meseros + cocina:
            cursor.execute("INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s,%s,%s,%s)", 
                           (name, mail, hash_pass(pwd), rol))

        # --- MENÚ EQUILIBRADO (Ni muy poco, ni demasiado) ---
        items_iniciales = [
            # GORDITAS ($21.00)
            ("Gordita - ASADO ROJO", "Gorditas", 21.00),
            ("Gordita - ASADO VERDE", "Gorditas", 21.00),
            ("Gordita - DESHEBRADA ROJA", "Gorditas", 21.00),
            ("Gordita - DESHEBRADA VERDE", "Gorditas", 21.00),
            ("Gordita - CHICHARRON PRENSADO", "Gorditas", 21.00),
            ("Gordita - CHICHARRON DE YESCA", "Gorditas", 21.00),
            ("Gordita - PICADILLO", "Gorditas", 21.00),
            ("Gordita - BISTECK", "Gorditas", 21.00),
            ("Gordita - DISCADA", "Gorditas", 21.00),
            ("Gordita - RAJAS C/QUESO", "Gorditas", 21.00),
            ("Gordita - FRIJOLES C/QUESO", "Gorditas", 21.00),
            ("Gordita - REQUESON", "Gorditas", 21.00),
            ("Gordita - NOPALITOS", "Gorditas", 21.00),
            ("Gordita - HUEVO VERDE", "Gorditas", 21.00),
            
            # BURRITOS ($36.00)
            ("Burro - ASADO ROJO", "Burros", 36.00),
            ("Burro - ASADO VERDE", "Burros", 36.00),
            ("Burro - DESHEBRADA", "Burros", 36.00),
            ("Burro - CHICHARRON", "Burros", 36.00),
            ("Burro - PICADILLO", "Burros", 36.00),
            ("Burro - BISTECK", "Burros", 36.00),
            ("Burro - DISCADA", "Burros", 36.00),
            ("Burro - FRIJOLES C/QUESO", "Burros", 36.00),

            # KILOS Y EXTRAS
            ("Carnitas (kg)", "Kilos", 320.00),
            ("Cueritos (kg)", "Kilos", 320.00),
            ("Costillas (kg)", "Kilos", 345.00),
            ("Buche (kg)", "Kilos", 320.00),
            ("Guacamole", "Extras", 35.00),
            ("Chile c/Queso", "Extras", 35.00),
            ("Cebolla Asada", "Extras", 25.00),

            # BEBIDAS
            ("Refresco Lata", "Bebidas", 25.00),
            ("Refresco 600ml", "Bebidas", 30.00),
            ("Agua Fresca (Lt)", "Bebidas", 35.00),
            ("Agua Fresca (Vaso)", "Bebidas", 20.00),
            ("Café", "Bebidas", 20.00)
        ]
        
        cursor.executemany("INSERT INTO menu (nombre, categoria, precio) VALUES (%s, %s, %s)", items_iniciales)

        conn.commit()
        print("✅ Base de datos actualizada con menú completo y equilibrado.")
        
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if conn and conn.is_connected(): conn.close()

if __name__ == "__main__":
    setup()