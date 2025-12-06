import mysql.connector
import hashlib
import json
import pandas as pd
from tkinter import filedialog
import decimal

# Configuración de conexión
DB_CONFIG = {
    "host": "localhost", "user": "root", "password": "", 
    "database": "restaurante_pro_db", "auth_plugin": "mysql_native_password"
}

def get_conn():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Error conexión: {e}")
        return None

# Función auxiliar para convertir Decimal a float al guardar JSON
def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

# --- USUARIOS ---
def login(email, password):
    conn = get_conn()
    if not conn: return None
    try:
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email=%s AND password=%s", (email, pwd_hash))
        return cursor.fetchone()
    finally:
        if conn: conn.close()

def crear_usuario(nombre, email, password, rol):
    conn = get_conn()
    if not conn: return False
    try:
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s,%s,%s,%s)", 
                       (nombre, email, pwd_hash, rol))
        conn.commit()
        return True
    except:
        return False
    finally:
        if conn: conn.close()

# --- MENÚ ---
def get_menu(filtro=""):
    conn = get_conn()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM menu WHERE activo=1"
        if filtro:
            sql += f" AND (nombre LIKE '%{filtro}%' OR categoria LIKE '%{filtro}%')"
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        if conn: conn.close()

def agregar_producto(nombre, categoria, precio):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO menu (nombre, categoria, precio) VALUES (%s,%s,%s)", (nombre, categoria, precio))
        conn.commit()
        return True
    except: return False
    finally: 
        if conn: conn.close()

# --- PEDIDOS ---
def guardar_pedido(cliente, mesa, items, total, id_user, id_pedido=None):
    conn = get_conn()
    if not conn: return False
    try:
        cursor = conn.cursor()
        
        # CORRECCION AQUI: Agregamos default=decimal_default para arreglar el error JSON
        items_json = json.dumps(items, default=decimal_default)
        
        # Si se modifica (id_pedido existe), regresa a estado 'Pendiente'
        if id_pedido:
            sql = """UPDATE pedidos SET cliente=%s, mesa=%s, items=%s, total=%s, estado='Pendiente' 
                     WHERE id=%s"""
            cursor.execute(sql, (cliente, mesa, items_json, total, id_pedido))
        else:
            sql = """INSERT INTO pedidos (cliente, mesa, items, total, id_usuario, estado) 
                     VALUES (%s, %s, %s, %s, %s, 'Pendiente')"""
            cursor.execute(sql, (cliente, mesa, items_json, total, id_user))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al guardar: {e}")
        return False
    finally:
        if conn: conn.close()

def obtener_pedidos(filtro_estado=None, busqueda=""):
    conn = get_conn()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT p.*, u.nombre as mesero FROM pedidos p LEFT JOIN usuarios u ON p.id_usuario = u.id"
        conditions = []
        
        if filtro_estado == "cocina":
            conditions.append("p.estado IN ('Pendiente', 'En Preparacion')")
        
        if busqueda:
            conditions.append(f"(p.cliente LIKE '%{busqueda}%' OR p.mesa LIKE '%{busqueda}%')")
            
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
            
        sql += " ORDER BY p.fecha DESC"
        if filtro_estado == "cocina":
            sql = sql.replace("DESC", "ASC")
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        for r in rows:
            if isinstance(r['items'], str): 
                r['items'] = json.loads(r['items'])
            # Convertir Decimales a float para evitar errores visuales
            r['total'] = float(r['total'])
        return rows
    finally:
        if conn: conn.close()

def cambiar_estado(id_pedido, nuevo_estado):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE pedidos SET estado=%s WHERE id=%s", (nuevo_estado, id_pedido))
        conn.commit()
        return True
    except: return False
    finally: 
        if conn: conn.close()

def eliminar_pedido(id_pedido):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pedidos WHERE id=%s", (id_pedido,))
        conn.commit()
        return True
    except: return False
    finally: 
        if conn: conn.close()

# --- EXCEL ---
def exportar_excel():
    conn = get_conn()
    try:
        df = pd.read_sql("SELECT * FROM pedidos", conn)
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if filename:
            df.to_excel(filename, index=False)
            return True
    except Exception as e:
        print(f"Error Excel: {e}")
        return False
    finally:
        if conn: conn.close()
    return False