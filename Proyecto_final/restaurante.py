from database import crear_conexion, cerrar_conexion
import json

# (El menú de GUISOS y MENU_RESTAURANTE sigue igual...)
GUISOS = [
    "ASADO C/ROJO", "ASADO C/VERDE", "BISTECK", "CHICHARRON PRENSADO",
    "DESHEBRADA", "DESHEBRADA S/CHILE", "MOLE ROJO", "DISCADA", "ASIENTOS",
    "CARNITAS", "PICADILLO S/CHILE", "PICADILLO C/ROJO", "PICADILLO C/VERDE",
    "RAJAS C/QUESO", "MORONGA", "FRIJOLES C/QUESO", "CHICHARRON DE YESCA",
    "REQUESON", "QUESO", "HUEVO VERDE", "HUEVO PERDIDO", "HUEVO A LA MEXICANA",
    "NOPALITOS C/ROJO", "NOPALITOS C/HUEVO", "PAPAS C/QUESO"
]

MENU_RESTAURANTE = []

for guiso in GUISOS:
    MENU_RESTAURANTE.append({"nombre": f"Gordita - {guiso}", "precio": 21.0})
for guiso in GUISOS:
    MENU_RESTAURANTE.append({"nombre": f"Burro - {guiso}", "precio": 36.0})

MENU_RESTAURANTE.extend([
    {"nombre": "Carnitas (kg)", "precio": 320.0},
    {"nombre": "Cueritos (kg)", "precio": 320.0},
    {"nombre": "Costillas (kg)", "precio": 345.0},
    {"nombre": "Yescas (kg)", "precio": 310.0}
])
MENU_RESTAURANTE.extend([
    {"nombre": "Chile c/queso", "precio": 35.0},
    {"nombre": "Chile c/carne", "precio": 48.0},
    {"nombre": "Chile c/cuero", "precio": 48.0},
    {"nombre": "Guacamole", "precio": 0.0},
    {"nombre": "Cebolla Asada", "precio": 25.0}
])
# (Fin del menú)

def get_menu():
    return MENU_RESTAURANTE

# (get_menu_string sigue igual...)

def agregar_pedido(nombre_cliente, mesa, items, total, id_usuario, estado="Pendiente"):
    # (Esta función ya guardaba el id_usuario, estaba correcta)
    conexion = crear_conexion()
    if not conexion:
        return None
    try:
        cursor = conexion.cursor()
        items_json = json.dumps(items, ensure_ascii=False)
        
        query_restaurante = """
            INSERT INTO restaurante (nombre_cliente, mesa, items, total, estado, id_usuario)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        valores_restaurante = (nombre_cliente, mesa, items_json, total, estado, id_usuario)
        
        cursor.execute(query_restaurante, valores_restaurante)
        id_registro = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO ventas (id_registro, total, id_usuario) 
            VALUES (%s, %s, %s)
        """, (id_registro, total, id_usuario))
        
        conexion.commit()
        return id_registro
    except Exception as e:
        print(f"Error al agregar pedido: {e}")
        conexion.rollback()
        return None
    finally:
        cerrar_conexion(conexion)

def mostrar_pedidos():
    # (MODIFICADO)
    # Ahora usa un JOIN para obtener el nombre del mesero (u.usuario)
    # Y filtra por 'esta_activo = 1' para el "soft delete"
    conexion = crear_conexion()
    if not conexion:
        return []
    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
            SELECT r.*, u.usuario 
            FROM restaurante r
            LEFT JOIN usuarios u ON r.id_usuario = u.id_usuario
            WHERE r.esta_activo = 1
            ORDER BY r.fecha_hora DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        for r in rows:
            if isinstance(r["items"], str):
                r["items"] = json.loads(r["items"])
        return rows
    except Exception as e:
        print(f"Error al mostrar pedidos: {e}")
        return []
    finally:
        cerrar_conexion(conexion)

def borrar_pedido(id_registro):
    # (MODIFICADO) Implementa el "Soft Delete"
    # Ya no usamos DELETE, sino UPDATE para marcarlo como inactivo.
    conexion = crear_conexion()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        query = "UPDATE restaurante SET esta_activo = 0 WHERE id_registro = %s"
        cursor.execute(query, (id_registro,))
        conexion.commit()
        borrados = cursor.rowcount
        return borrados > 0
    except Exception as e:
        print(f"Error al 'borrar' lógicamente el pedido: {e}")
        conexion.rollback()
        return False
    finally:
        cerrar_conexion(conexion)

def get_pedido_por_id(id_registro):
    # (NUEVO) Función que faltaba para corregir el bug de "Actualizar".
    # Busca un pedido activo por su ID.
    conexion = crear_conexion()
    if not conexion:
        return None
    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
            SELECT * FROM restaurante 
            WHERE id_registro = %s AND esta_activo = 1
        """
        cursor.execute(query, (id_registro,))
        pedido = cursor.fetchone()
        
        if pedido and isinstance(pedido["items"], str):
            pedido["items"] = json.loads(pedido["items"])
            
        return pedido
    except Exception as e:
        print(f"Error al obtener pedido por ID: {e}")
        return None
    finally:
        cerrar_conexion(conexion)

def actualizar_pedido_completo(id_registro, cliente, mesa, items, total, id_usuario_modifico):
    # (NUEVO) Función que faltaba para corregir el bug de "Actualizar".
    # Actualiza el pedido y guarda un registro en la nueva tabla 'historial_cambios'.
    conexion = crear_conexion()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        items_json = json.dumps(items, ensure_ascii=False)
        
        # 1. Actualizar el pedido
        query_update = """
            UPDATE restaurante 
            SET nombre_cliente = %s, mesa = %s, items = %s, total = %s
            WHERE id_registro = %s
        """
        cursor.execute(query_update, (cliente, mesa, items_json, total, id_registro))
        
        # 2. Registrar el cambio en el historial
        query_historial = """
            INSERT INTO historial_cambios (id_registro, id_usuario_modifico, descripcion_cambio)
            VALUES (%s, %s, %s)
        """
        descripcion = f"Pedido actualizado. Nuevo total: {total}"
        cursor.execute(query_historial, (id_registro, id_usuario_modifico, descripcion))
        
        conexion.commit()
        return cursor.rowcount > 0 # Devuelve True si la actualización fue exitosa
    except Exception as e:
        print(f"Error al actualizar pedido completo: {e}")
        conexion.rollback()
        return False
    finally:
        cerrar_conexion(conexion)

# (La función 'actualizar_nombre_cliente' se deja, pero ya no la usa la UI principal)
def actualizar_nombre_cliente(id_registro, nuevo_nombre):
    conexion = crear_conexion()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE restaurante 
            SET nombre_cliente = %s 
            WHERE id_registro = %s
        """, (nuevo_nombre, id_registro))
        
        conexion.commit()
        actualizados = cursor.rowcount
        return actualizados > 0
    except Exception as e:
        print(f"Error al actualizar nombre: {e}")
        conexion.rollback()
        return False
    finally:
        cerrar_conexion(conexion)