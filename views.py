import customtkinter as ctk
from tkinter import messagebox
import autenticacion
import restaurante


class Theme:
    RED_PRIMARY = "#B71C1C"       # Rojo oscuro elegante
    RED_HOVER = "#D32F2F"         # Rojo más vivo para hover
    BG_MAIN = "#F5F5F5"           # Fondo gris muy claro
    BG_CARD = "#FFFFFF"           # Blanco puro
    TEXT_DARK = "#212121"         # Negro suave
    TEXT_LIGHT = "#FFFFFF"        # Blanco
    GRAY_LIGHT = "#E0E0E0"        # Bordes
    GRAY_HOVER = "#BDBDBD"
    
    
    STATUS_PENDING = "#FF9800"    # Naranja
    STATUS_READY = "#4CAF50"      # Verde
    
    # Fuentes
    FONT_TITLE = ("Roboto Medium", 28)
    FONT_SUBTITLE = ("Roboto", 20)
    FONT_BUTTON = ("Roboto", 14, "bold")
    FONT_TEXT = ("Roboto", 14)
    FONT_SMALL = ("Roboto", 12)


# 2. Para scroll y layout
class BaseScrollablePage(ctk.CTkFrame):
    def __init__(self, master, title_text="Título", **kwargs):
        super().__init__(master, fg_color=Theme.BG_MAIN, **kwargs)
        
        # Header
        self.header = ctk.CTkFrame(self, fg_color=Theme.RED_PRIMARY, height=70, corner_radius=0)
        self.header.pack(fill="x", side="top")
        
        self.title_label = ctk.CTkLabel(
            self.header, 
            text=title_text.upper(), 
            font=Theme.FONT_TITLE,
            text_color=Theme.TEXT_LIGHT
        )
        self.title_label.pack(pady=20)

        # Scroll
        self.scroll_content = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_content.pack(fill="both", expand=True, padx=20, pady=20)


# LOGIN FRAME

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, app_instance, **kwargs): 
        super().__init__(master, fg_color=Theme.RED_PRIMARY)
        self.app = app_instance

       
        card = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=20, width=400)
        card.place(relx=0.5, rely=0.5, anchor="center")

        if self.app.logo_image:
            logo_label = ctk.CTkLabel(card, image=self.app.logo_image, text="")
            logo_label.pack(pady=(30, 10))

        ctk.CTkLabel(card, text="BIENVENIDO", font=Theme.FONT_TITLE, text_color=Theme.RED_PRIMARY).pack(pady=10)
        ctk.CTkLabel(card, text="Inicie sesión para continuar", font=Theme.FONT_SMALL, text_color="gray").pack(pady=(0, 20))

        self.entry_correo = ctk.CTkEntry(card, placeholder_text="Correo Electrónico", width=300, height=45, font=Theme.FONT_TEXT)
        self.entry_correo.pack(pady=10)
        

        self.entry_pass = ctk.CTkEntry(card, placeholder_text="Contraseña", show="*", width=300, height=45, font=Theme.FONT_TEXT)
        self.entry_pass.pack(pady=10)
        

        btn_login = ctk.CTkButton(
            card, text="INGRESAR", command=self.intentar_login,
            width=300, height=50, font=Theme.FONT_BUTTON,
            fg_color=Theme.RED_PRIMARY, hover_color=Theme.RED_HOVER, corner_radius=10
        )
        btn_login.pack(pady=30)

    def intentar_login(self):
        gmail = self.entry_correo.get()
        password = self.entry_pass.get()
        usuario = autenticacion.iniciar_sesion(gmail, password)
        if usuario:
            self.app.login_exitoso(usuario) 
        else:
            messagebox.showerror("Error", "Credenciales incorrectas.")


# MENÚ PRINCIPAL

class MainFrame(ctk.CTkFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, fg_color=Theme.BG_MAIN)
        self.app = app_instance
        
        # Recuperar datos usuario
        user = self.app.usuario_data.get('usuario', 'Usuario')
        rol_raw = self.app.usuario_data.get('rol', 'mesero')
        
        rol = rol_raw.strip().lower() if rol_raw else "mesero"

        # HEADER
        header = ctk.CTkFrame(self, fg_color=Theme.RED_PRIMARY, height=80, corner_radius=0)
        header.pack(fill="x", side="top")
        
        
        ctk.CTkLabel(header, text=f"Hola, {user}", font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_LIGHT).pack(side="left", padx=30)
        
        ctk.CTkLabel(header, text=f"ROL: {rol.upper()}", font=("Roboto", 12, "bold"), text_color="#FFCDD2").pack(side="left", padx=5)
        
        ctk.CTkButton(header, text="SALIR", command=self.app.cerrar_sesion, width=80, fg_color="transparent", border_width=1, border_color="white", hover_color=Theme.RED_HOVER).pack(side="right", padx=20)

        
        grid_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)


        opciones = [
            ("NUEVO PEDIDO", "➕", AddOrderFrame, ["admin", "mesero"]),
            ("VER PEDIDOS / ESTADO", "📋", ViewOrdersFrame, ["admin", "mesero"]),
            ("COCINA / COMANDAS", "👨‍🍳", KitchenFrame, ["admin", "cocina"]),
            ("ACTUALIZAR PEDIDO", "✏️", UpdateOrderFrame, ["admin"]),
            ("ELIMINAR PEDIDO", "🗑️", DeleteOrderFrame, ["admin"]),
        ]

        row, col = 0, 0
        botones_creados = 0

        for texto, icon, frame_class, roles_permitidos in opciones:
            permiso = False
            
            # Lógica de permisos
            if "admin" in roles_permitidos and rol == "admin":
                permiso = True
            elif rol in roles_permitidos:
                permiso = True
            
            # Excepciones lógicas
            if rol == "mesero" and frame_class == KitchenFrame: permiso = False
            if rol == "cocina" and frame_class != KitchenFrame: permiso = False

            if permiso:
                self.crear_boton_menu(grid_frame, texto, icon, frame_class, row, col)
                botones_creados += 1
                col += 1
                if col > 1:
                    col = 0
                    row += 1
        
        if botones_creados == 0:
            ctk.CTkLabel(grid_frame, text=f"No tienes permisos asignados.\nRol detectado: '{rol}'", font=Theme.FONT_SUBTITLE, text_color="gray").pack(pady=50)

    def crear_boton_menu(self, parent, text, icon, frame_class, r, c):
        btn = ctk.CTkButton(
            parent,
            text=f"{icon}\n\n{text}",
            command=lambda: self.app.show_frame(frame_class),
            font=("Roboto", 18, "bold"),
            width=250, height=150,
            fg_color=Theme.BG_CARD,
            text_color=Theme.TEXT_DARK,
            hover_color=Theme.GRAY_LIGHT,
            corner_radius=15,
            border_width=1,
            border_color=Theme.GRAY_LIGHT
        )
        btn.grid(row=r, column=c, padx=20, pady=20, sticky="nsew")


# OTRAS VISTAS (ADD, KITCHEN, VIEW, DELETE, UPDATE)
# AGREGAR PEDIDO
class AddOrderFrame(BaseScrollablePage):
    def __init__(self, master, app_instance, pedido_id_a_editar=None):
        titulo = "EDITAR PEDIDO" if pedido_id_a_editar else "NUEVO PEDIDO"
        super().__init__(master, title_text=titulo)
        self.app = app_instance
        self.pedido_id = pedido_id_a_editar
        self.item_widgets = []

        # Formulario Datos Cliente
        form_frame = ctk.CTkFrame(self.scroll_content, fg_color=Theme.BG_CARD, corner_radius=10)
        form_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(form_frame, text="Datos del Cliente", font=Theme.FONT_BUTTON, text_color=Theme.RED_PRIMARY).pack(anchor="w", padx=20, pady=(15,5))
        
        self.entry_cliente = ctk.CTkEntry(form_frame, placeholder_text="Nombre del Cliente", height=40, font=Theme.FONT_TEXT)
        self.entry_cliente.pack(fill="x", padx=20, pady=5)
        
        self.entry_mesa = ctk.CTkEntry(form_frame, placeholder_text="Número de Mesa", height=40, font=Theme.FONT_TEXT)
        self.entry_mesa.pack(fill="x", padx=20, pady=(5, 20))

        # Menú de Platillos
        ctk.CTkLabel(self.scroll_content, text="Selección de Platillos", font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_DARK).pack(anchor="w", pady=(20, 10))
        
        menu_list = restaurante.get_menu()
        current_cat = ""
        
        for item in menu_list:
            cat = self.detectar_categoria(item["nombre"])
            if cat != current_cat:
                current_cat = cat
                ctk.CTkLabel(self.scroll_content, text=cat, font=("Roboto", 16, "bold"), text_color="gray").pack(anchor="w", pady=(15, 5))

            row = ctk.CTkFrame(self.scroll_content, fg_color=Theme.BG_CARD, corner_radius=8)
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=item['nombre'], font=Theme.FONT_TEXT, text_color=Theme.TEXT_DARK).pack(side="left", padx=15, pady=10)
            ctk.CTkLabel(row, text=f"${item['precio']:.2f}", font=Theme.FONT_TEXT, text_color="gray").pack(side="left", padx=5)
            
            entry_cant = ctk.CTkEntry(row, width=60, placeholder_text="0", justify="center")
            entry_cant.pack(side="right", padx=15, pady=5)
            
            self.item_widgets.append((item, entry_cant))

        # Botones de Acción
        btn_frame = ctk.CTkFrame(self.scroll_content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=30)

        texto_btn = "ACTUALIZAR" if self.pedido_id else "GUARDAR ORDEN"
        ctk.CTkButton(btn_frame, text=texto_btn, command=self.guardar, height=50, font=Theme.FONT_BUTTON, fg_color=Theme.RED_PRIMARY, hover_color=Theme.RED_HOVER).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(btn_frame, text="CANCELAR", command=lambda: self.app.show_frame(MainFrame), height=50, font=Theme.FONT_BUTTON, fg_color="gray", hover_color="#616161").pack(side="right", fill="x", expand=True, padx=(10, 0))

        if self.pedido_id:
            self.cargar_datos()

    def detectar_categoria(self, nombre):
        if "Gordita" in nombre: return "GORDITAS"
        if "Burro" in nombre: return "BURROS"
        if "kg" in nombre: return "POR KILO"
        return "BEBIDAS Y EXTRAS"

    def cargar_datos(self):
        pedido = restaurante.get_pedido_por_id(self.pedido_id)
        if pedido:
            self.entry_cliente.insert(0, pedido["nombre_cliente"])
            self.entry_mesa.insert(0, pedido["mesa"])
            items_guardados = {i['nombre']: i['cantidad'] for i in pedido.get('items', [])}
            for item_data, entry in self.item_widgets:
                if item_data["nombre"] in items_guardados:
                    entry.insert(0, str(items_guardados[item_data["nombre"]]))

    def guardar(self):
        cliente = self.entry_cliente.get().strip()
        mesa = self.entry_mesa.get().strip()
        if not cliente or not mesa:
            messagebox.showerror("Error", "Faltan datos del cliente o mesa.")
            return

        items_final = []
        total = 0
        for item, entry in self.item_widgets:
            val = entry.get().strip()
            if val and val != "0":
                try:
                    cant = float(val) if "kg" in item["nombre"] else int(val)
                    if cant > 0:
                        sub = cant * item["precio"]
                        total += sub
                        items_final.append({
                            "nombre": item["nombre"], "cantidad": cant, "precio_unitario": item["precio"], "subtotal": sub
                        })
                except ValueError:
                    pass

        if not items_final:
            messagebox.showerror("Error", "El pedido está vacío.")
            return

        user_id = self.app.usuario_data["id_usuario"]
        exito = False
        
        if self.pedido_id:
            exito = restaurante.actualizar_pedido_completo(self.pedido_id, cliente, mesa, items_final, total, user_id)
        else:
            exito = restaurante.agregar_pedido(cliente, mesa, items_final, total, user_id)
            
        if exito:
            messagebox.showinfo("Éxito", "Operación realizada correctamente.")
            self.app.show_frame(MainFrame)
        else:
            messagebox.showerror("Error", "Hubo un problema con la base de datos.")

# VISTA COCINA
class KitchenFrame(BaseScrollablePage):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, title_text="COMANDA DE COCINA")
        self.app = app_instance

        # --- BARRA DE HERRAMIENTAS ---
        tool_bar = ctk.CTkFrame(self.scroll_content, fg_color="transparent")
        tool_bar.pack(fill="x", pady=10)

        # Botón REGRESAR (Alineado a la izquierda)
        ctk.CTkButton(
            tool_bar, 
            text="⬅️ REGRESAR", 
            command=lambda: self.app.show_frame(MainFrame), 
            width=120, 
            fg_color="gray",
            hover_color="#616161"
        ).pack(side="left")

        # Botón ACTUALIZAR (Alineado a la derecha)
        ctk.CTkButton(
            tool_bar, 
            text="🔄 ACTUALIZAR LISTA", 
            command=self.cargar_pedidos, 
            width=200
        ).pack(side="right")

        # Contenedor de las tarjetas
        self.orders_container = ctk.CTkFrame(self.scroll_content, fg_color="transparent")
        self.orders_container.pack(fill="both", expand=True, pady=10)

        self.cargar_pedidos()

    def cargar_pedidos(self):
        for widget in self.orders_container.winfo_children():
            widget.destroy()

        pedidos = restaurante.mostrar_pedidos_cocina()
        
        if not pedidos:
            ctk.CTkLabel(self.orders_container, text="No hay órdenes pendientes.", font=Theme.FONT_SUBTITLE, text_color="gray").pack(pady=50)
            return

        self.orders_container.grid_columnconfigure(0, weight=1)
        self.orders_container.grid_columnconfigure(1, weight=1)

        row, col = 0, 0
        for p in pedidos:
            self.crear_tarjeta_comanda(p, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

    def crear_tarjeta_comanda(self, pedido, r, c):
        color_borde = Theme.STATUS_PENDING if pedido['estado'] == 'Pendiente' else Theme.STATUS_READY
        
        card = ctk.CTkFrame(self.orders_container, fg_color=Theme.BG_CARD, border_width=2, border_color=color_borde)
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

        header = ctk.CTkFrame(card, fg_color=color_borde, height=30, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=f"MESA: {pedido['mesa']}", font=("Roboto", 16, "bold"), text_color="white").pack()

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(padx=10, pady=10, fill="both", expand=True)
        
        ctk.CTkLabel(content, text=f"Cliente: {pedido['nombre_cliente']}", font=("Roboto", 12, "bold")).pack(anchor="w")
        
        items_txt = ""
        items_lista = pedido.get('items', [])
        if isinstance(items_lista, list):
            for it in items_lista:
                items_txt += f"• {it['cantidad']} x {it['nombre']}\n"
        
        text_box = ctk.CTkTextbox(content, height=100, fg_color="#FAFAFA")
        text_box.insert("0.0", items_txt)
        text_box.configure(state="disabled")
        text_box.pack(fill="x", pady=5)

        if pedido['estado'] == 'Pendiente':
            ctk.CTkButton(card, text="MARCAR LISTO ✅", 
                          command=lambda pid=pedido['id_registro']: self.marcar_listo(pid),
                          fg_color=Theme.STATUS_READY).pack(fill="x", padx=10, pady=10)

    def marcar_listo(self, id_registro):
        if restaurante.cambiar_estado_pedido(id_registro, "Listo"):
            self.cargar_pedidos()

# --- VER PEDIDOS ---
class ViewOrdersFrame(BaseScrollablePage):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, title_text="HISTORIAL")
        self.app = app_instance
        
        ctk.CTkButton(self.scroll_content, text="⬅️ REGRESAR", command=lambda: self.app.show_frame(MainFrame), width=120, fg_color="gray").pack(anchor="w", pady=10)
        ctk.CTkButton(self.scroll_content, text="🔄 REFRESCAR", command=self.cargar_tabla, width=150).pack(anchor="e", pady=(0, 10))

        self.table_frame = ctk.CTkFrame(self.scroll_content, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True)
        self.cargar_tabla()

    def cargar_tabla(self):
        for w in self.table_frame.winfo_children(): w.destroy()
        pedidos = restaurante.mostrar_pedidos()
        
        headers = ["ID", "MESA", "CLIENTE", "TOTAL", "ESTADO"]
        h_frame = ctk.CTkFrame(self.table_frame, fg_color=Theme.GRAY_LIGHT)
        h_frame.pack(fill="x", pady=2)
        for h in headers:
            ctk.CTkLabel(h_frame, text=h, font=("Roboto", 12, "bold"), width=100).pack(side="left", padx=5)

        for p in pedidos:
            row = ctk.CTkFrame(self.table_frame, fg_color="white")
            row.pack(fill="x", pady=2)
            color_estado = "orange" if p['estado'] == "Pendiente" else "green"
            
            datos = [str(p['id_registro']), str(p['mesa']), p['nombre_cliente'][:15], f"${p['total']:.2f}"]
            for d in datos:
                ctk.CTkLabel(row, text=d, width=100, font=Theme.FONT_TEXT).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=p['estado'], width=100, text_color=color_estado, font=("Roboto", 12, "bold")).pack(side="left", padx=5)

#ELIMINAR PEDIDO 
class DeleteOrderFrame(BaseScrollablePage):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, title_text="ELIMINAR PEDIDO")
        self.app = app_instance
        
        container = ctk.CTkFrame(self.scroll_content, fg_color="white", corner_radius=10)
        container.pack(pady=50, padx=100, fill="both")

        ctk.CTkLabel(container, text="ID del Pedido:", font=Theme.FONT_SUBTITLE).pack(pady=20)
        self.entry_id = ctk.CTkEntry(container, placeholder_text="Ej: 5")
        self.entry_id.pack(pady=10)

        ctk.CTkButton(container, text="ELIMINAR", command=self.borrar, fg_color="#D32F2F").pack(pady=20)
        ctk.CTkButton(container, text="VOLVER", command=lambda: self.app.show_frame(MainFrame), fg_color="gray").pack(pady=10)

    def borrar(self):
        try:
            if restaurante.borrar_pedido(int(self.entry_id.get())):
                messagebox.showinfo("Éxito", "Eliminado.")
                self.app.show_frame(MainFrame)
            else:
                messagebox.showerror("Error", "No encontrado.")
        except:
            messagebox.showerror("Error", "ID inválido.")

# ACTUALIZAR PEDIDO 
class UpdateOrderFrame(BaseScrollablePage):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, title_text="MODIFICAR PEDIDO")
        self.app = app_instance
        
        container = ctk.CTkFrame(self.scroll_content, fg_color="white", corner_radius=10)
        container.pack(pady=50, padx=100, fill="both")

        ctk.CTkLabel(container, text="ID del Pedido:", font=Theme.FONT_SUBTITLE).pack(pady=20)
        self.entry_id = ctk.CTkEntry(container, placeholder_text="Ej: 10")
        self.entry_id.pack(pady=10)

        ctk.CTkButton(container, text="BUSCAR", command=self.buscar, fg_color=Theme.RED_PRIMARY).pack(pady=20)
        ctk.CTkButton(container, text="VOLVER", command=lambda: self.app.show_frame(MainFrame), fg_color="gray").pack(pady=10)

    def buscar(self):
        try:
            id_reg = int(self.entry_id.get())
            if restaurante.get_pedido_por_id(id_reg):
                self.app.show_frame(AddOrderFrame, pedido_id_a_editar=id_reg)
            else:
                messagebox.showerror("Error", "No encontrado.")
        except:
            messagebox.showerror("Error", "ID numérico requerido.")