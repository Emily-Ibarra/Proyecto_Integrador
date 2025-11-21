from database import crear_conexion
import hashlib
from mysql.connector import Error

def hash_password(contrasena):
    return hashlib.sha256(contrasena.encode()).hexdigest()

def registrar(nombre_usuario, gmail, contrasena, rol="mesero"):
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
    Verifica correo y contraseña.
    Devuelve diccionario con datos del usuario.
    """
    conexion = crear_conexion()
    if not conexion:
        return None
    try:
        
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
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()