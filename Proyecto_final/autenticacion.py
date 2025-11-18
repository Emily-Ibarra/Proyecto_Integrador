from database import crear_conexion
import hashlib
from mysql.connector import Error

def hash_password(contrasena):
    return hashlib.sha256(contrasena.encode()).hexdigest()

def registrar(nombre_usuario, gmail, contrasena, rol="mesero"):
    # (Esta función está bien, pero no se usa en la UI actual)
    conexion = crear_conexion()
    if not conexion:
        return False
    try:
        contrasena_hash = hash_password(contrasena)
        sql = "INSERT INTO usuarios (usuario, gmail, password_hash, rol) VALUES (%s, %s, %s, %s)"
        val = (nombre_usuario, gmail, contrasena_hash, rol)
        cursor = conexion.cursor()
        cursor.execute(sql, val)
        conexion.commit()
        print(f"✅ Usuario '{nombre_usuario}' registrado correctamente.")
        return True
    except Error as e:
        print(f"❌ Error al registrar: {e}")
        return False
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def iniciar_sesion(gmail, contrasena):
    """
    (MODIFICADO)
    Verifica correo y contraseña.
    Devuelve todos los datos del usuario (id, nombre, gmail, rol).
    """
    conexion = crear_conexion()
    if not conexion:
        return None
    try:
        # (CORREGIDO) La contraseña 'admin123' debe ser hasheada para compararla
        contrasena_hash = hash_password(contrasena) 
        
        sql = "SELECT id_usuario, usuario, gmail, rol FROM usuarios WHERE gmail=%s AND password_hash=%s"
        val = (gmail, contrasena_hash)
        
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql, val)
        registro = cursor.fetchone()
        
        return registro if registro else None
    except Error as e:
        print(f"❌ Error al iniciar sesión: {e}")
        return None
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()