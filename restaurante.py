from database import crear_conexion, cerrar_conexion
import json

# Menu del restaurante
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
    {"nombre": "Yescas (kg)", "precio": 310.0},
    {"nombre": "Chile c/queso", "precio": 35.0},
    {"nombre": "Chile c/carne", "precio": 48.0},
    {"nombre": "Chile c/cuero", "precio": 48.0},
    {"nombre": "Guacamole", "precio": 0.0},
    {"nombre": "Cebolla Asada", "precio": 25.0},
    {"nombre": "Refresco", "precio": 25.0},
    {"nombre": "Agua Fresca", "precio": 20.0}
])

def get_menu():
    return MENU_RESTAURANTE

#FUNCIONES BASE DE DATOS ¿

def agregar_pedido(nombre_cliente, mesa, items, total, id_usuario, estado="Pendiente"):
    conexion = crear_conexion()
    if not conexion: return None
    try:
        cursor = conexion.cursor()
        items_json = json.dumps(items, ensure_ascii=False)
        
        query = """
            INSERT INTO restaurante (nombre_cliente, mesa, items, total, estado, id_usuario)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nombre_cliente, mesa, items_json, total, estado, id_usuario))
        id_registro = cursor.lastrowid
        
        # Registra las ventas
        cursor.execute("INSERT INTO ventas (id_registro, total, id_usuario) VALUES (%s, %s, %s)", 
                       (id_registro, total, id_usuario))
        
        conexion.commit()
        return id_registro
    except Exception as e:
        print(f"Error al agregar pedido: {e}")
        conexion.rollback()
        return None
    finally:
        cerrar_conexion(conexion)

def mostrar_pedidos():

    conexion = crear_conexion()
    if not conexion: return []
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

def mostrar_pedidos_cocina():
    """
    Obtiene solo los pedidos que NO están entregados ni cancelados.
    Muestra 'Pendiente' y 'Listo' para que cocina sepa qué falta.
    Ordena por los más viejos para que salgan en orden
    """
    conexion = crear_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        # Filtramos para no mostrar los que ya se entregaron/cobraron totalmente o borrados
        query = """
            SELECT r.*, u.usuario 
            FROM restaurante r
            LEFT JOIN usuarios u ON r.id_usuario = u.id_usuario
            WHERE r.esta_activo = 1 
            AND r.estado IN ('Pendiente', 'En Preparacion')
            ORDER BY r.fecha_hora ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        for r in rows:
            if isinstance(r["items"], str):
                r["items"] = json.loads(r["items"])
        return rows
    except Exception as e:
        print(f"Error al mostrar pedidos cocina: {e}")
        return []
    finally:
        cerrar_conexion(conexion)

def cambiar_estado_pedido(id_registro, nuevo_estado):
    """(NUEVO) Cambia el estado (Ej. Pendiente -> Listo)"""
    conexion = crear_conexion()
    if not conexion: return False
    try:
        cursor = conexion.cursor()
        query = "UPDATE restaurante SET estado = %s WHERE id_registro = %s"
        cursor.execute(query, (nuevo_estado, id_registro))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al cambiar estado: {e}")
        return False
    finally:
        cerrar_conexion(conexion)

def borrar_pedido(id_registro):
    conexion = crear_conexion()
    if not conexion: return False
    try:
        cursor = conexion.cursor()
        
        cursor.execute("UPDATE restaurante SET esta_activo = 0 WHERE id_registro = %s", (id_registro,))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al borrar pedido: {e}")
        return False
    finally:
        cerrar_conexion(conexion)

def get_pedido_por_id(id_registro):
    conexion = crear_conexion()
    if not conexion: return None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM restaurante WHERE id_registro = %s AND esta_activo = 1", (id_registro,))
        pedido = cursor.fetchone()
        if pedido and isinstance(pedido["items"], str):
            pedido["items"] = json.loads(pedido["items"])
        return pedido
    except Exception as e:
        print(f"Error get_pedido_id: {e}")
        return None
    finally:
        cerrar_conexion(conexion)

def actualizar_pedido_completo(id_registro, cliente, mesa, items, total, id_usuario_modifico):
    conexion = crear_conexion()
    if not conexion: return False
    try:
        cursor = conexion.cursor()
        items_json = json.dumps(items, ensure_ascii=False)
        
        query_update = """
            UPDATE restaurante 
            SET nombre_cliente = %s, mesa = %s, items = %s, total = %s
            WHERE id_registro = %s
        """
        cursor.execute(query_update, (cliente, mesa, items_json, total, id_registro))
        
        # Historial
        descripcion = f"Pedido actualizado. Nuevo total: {total}"
        cursor.execute("INSERT INTO historial_cambios (id_registro, id_usuario_modifico, descripcion_cambio) VALUES (%s, %s, %s)", 
                       (id_registro, id_usuario_modifico, descripcion))
        
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error actualizar completo: {e}")
        conexion.rollback()
        return False
    finally:
        cerrar_conexion(conexion)