import customtkinter as ctk
from tkinter import messagebox
import autenticacion
import restaurante

# (Definición de colores igual)
COLOR_FONDO_ROJO = "#C00000"
COLOR_BOTON_ROSA = "#E57373"
COLOR_CAMPO_GRIS = "#F0F0F0"
COLOR_TEXTO = "#333333"
COLOR_TEXTO_BLANCO = "#FFFFFF"

# (Definición de fuentes igual)
FONT_TITULO = ("Arial", 30, "bold")
FONT_SUBTITULO = ("Arial", 22, "bold")
FONT_BOTON = ("Arial", 16, "bold")
FONT_TEXTO = ("Arial", 16)
FONT_PEDIDO_HEADER = ("Courier", 18, "bold")
FONT_PEDIDO_BODY = ("Courier", 16)


# (MODIFICADO) Ahora es un CTkScrollableFrame
class LoginFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, app_instance, **kwargs): 
        super().__init__(master, fg_color=COLOR_FONDO_ROJO)
        self.app = app_instance

        if self.app.logo_image:
            logo_label = ctk.CTkLabel(self, image=self.app.logo_image, text="")
            logo_label.pack(pady=(80, 20)) 

        title_label = ctk.CTkLabel(self, text="INICIO DE SESION", 
                                   font=FONT_TITULO,
                                   text_color=COLOR_TEXTO_BLANCO)
        title_label.pack(pady=20)

        self.entry_correo = ctk.CTkEntry(self, placeholder_text="Correo:", 
                                         width=400, height=50, 
                                         fg_color=COLOR_CAMPO_GRIS,
                                         border_width=0,
                                         text_color=COLOR_TEXTO,
                                         font=FONT_TEXTO,
                                         placeholder_text_color=COLOR_TEXTO)
        self.entry_correo.pack(pady=10)
        self.entry_correo.insert(0, "admin@correo.com")

        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Contraseña:", 
                                       show="*", width=400, height=50,
                                       fg_color=COLOR_CAMPO_GRIS,
                                       border_width=0,
                                       font=FONT_TEXTO,
                                       text_color=COLOR_TEXTO,
                                       placeholder_text_color=COLOR_TEXTO)
        self.entry_pass.pack(pady=10)
        self.entry_pass.insert(0, "admin123")

        btn_login = ctk.CTkButton(self, text="INICIAR SESIÓN", 
                                  command=self.intentar_login,
                                  width=400, height=50,
                                  font=FONT_BOTON,
                                  fg_color=COLOR_BOTON_ROSA,
                                  hover_color="#D32F2F",
                                  text_color=COLOR_TEXTO_BLANCO)
        btn_login.pack(pady=30)

    # (Lógica de intentar_login sin cambios)
    def intentar_login(self):
        gmail = self.entry_correo.get()
        password = self.entry_pass.get()

        if not gmail or not password:
            messagebox.showerror("Error", "Correo y contraseña son requeridos.")
            return

        usuario = autenticacion.iniciar_sesion(gmail, password)
        
        if usuario:
            self.app.login_exitoso(usuario) 
        else:
            messagebox.showerror("Error", "Correo o contraseña incorrectos.")


# (MODIFICADO) Ahora es un CTkScrollableFrame
class MainFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, fg_color=COLOR_FONDO_ROJO)
        self.app = app_instance
        
        usuario_nombre = self.app.usuario_data.get('usuario', 'N/A')
        usuario_rol = self.app.usuario_data.get('rol', 'mesero')

        if self.app.logo_image:
            logo_label = ctk.CTkLabel(self, image=self.app.logo_image, text="")
            logo_label.pack(pady=(60, 10))

        title_label = ctk.CTkLabel(self, text="MENU PRINCIPAL", 
                                   font=FONT_TITULO,
                                   text_color=COLOR_TEXTO_BLANCO)
        title_label.pack(pady=10)
        
        user_info_label = ctk.CTkLabel(self, text=f"Usuario: {usuario_nombre} ({usuario_rol})",
                                       font=FONT_SUBTITULO,
                                       text_color=COLOR_TEXTO_BLANCO)
        user_info_label.pack(pady=(0, 20))

        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(pady=20, fill="x", padx=300) 

        botones = {
            "AGREGAR PEDIDO": AddOrderFrame,
            "VER PEDIDOS": ViewOrdersFrame,
            "ACTUALIZAR PEDIDO": UpdateOrderFrame,
            "ELIMINAR PEDIDO": DeleteOrderFrame,
        }

        for texto, frame_class in botones.items():
            
            if (texto == "ACTUALIZAR PEDIDO" or texto == "ELIMINAR PEDIDO") and usuario_rol != "admin":
                continue

            btn = ctk.CTkButton(
                frame_botones, 
                text=texto, 
                command=lambda fc=frame_class: self.app.show_frame(fc),
                height=50, 
                font=FONT_BOTON, 
                fg_color=COLOR_CAMPO_GRIS,
                hover_color="#DCDCDC",
                text_color=COLOR_TEXTO
            )
            btn.pack(fill="x", pady=8)
        
        btn_logout = ctk.CTkButton(
            frame_botones, 
            text="CERRAR SESIÓN",
            command=self.app.cerrar_sesion,
            height=50, 
            font=FONT_BOTON, 
            fg_color=COLOR_BOTON_ROSA,
            hover_color="#D32F2F",
            text_color=COLOR_TEXTO_BLANCO
        )
        btn_logout.pack(fill="x", pady=8, side="bottom")


# (MODIFICADO) Ahora es un CTkScrollableFrame
class AddOrderFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, app_instance, pedido_id_a_editar=None):
        super().__init__(master, fg_color="white")
        self.app = app_instance
        self.menu_list = restaurante.get_menu()
        self.item_widgets = []
        
        self.pedido_id = pedido_id_a_editar

        frame_top = ctk.CTkFrame(self, fg_color=COLOR_FONDO_ROJO, height=80)
        frame_top.pack(fill="x", side="top", pady=0)
        if self.app.logo_image:
            logo_pequeno = ctk.CTkImage(
                light_image=self.app.logo_image.cget("light_image"),
                size=(100, 100) 
            )
            logo_label = ctk.CTkLabel(frame_top, image=logo_pequeno, text="")
            logo_label.pack(pady=5)

        content_frame = ctk.CTkFrame(self, fg_color="white")
        content_frame.pack(fill="both", expand=True, padx=200, pady=10) 

        
        titulo = "EDITAR PEDIDO" if self.pedido_id else "NUEVO PEDIDO"
        title_label = ctk.CTkLabel(content_frame, text=titulo, 
                                   font=FONT_TITULO,
                                   text_color=COLOR_TEXTO)
        title_label.pack(pady=10)

        self.entry_cliente = ctk.CTkEntry(content_frame, placeholder_text="Nombre Cliente:",
                                          height=45, font=FONT_TEXTO)
        self.entry_cliente.pack(pady=5, fill="x")
        
        self.entry_mesa = ctk.CTkEntry(content_frame, placeholder_text="Mesa:",
                                       height=45, font=FONT_TEXTO)
        self.entry_mesa.pack(pady=5, fill="x")
        
        # (MODIFICADO) Ya no es un "ScrollableFrame", es un CTkFrame normal.
        # La página entera (la clase) se encarga de deslizar.
        # También se quitó el 'height=400' para que muestre todos los items.
        menu_scroll_frame = ctk.CTkFrame(content_frame, fg_color=COLOR_CAMPO_GRIS)
        menu_scroll_frame.pack(fill="x", expand=True, pady=10)
        
        current_category = ""
        
        for item in self.menu_list:
            # (Lógica de categorías sin cambios)
            is_gordita = "Gordita" in item["nombre"] and current_category != "Gorditas"
            is_burro = "Burro" in item["nombre"] and current_category != "Burros"
            is_kilo = "kg" in item["nombre"] and current_category != "Kilo"
            is_extra = not ("Gordita" in item["nombre"] or "Burro" in item["nombre"] or "kg" in item["nombre"]) and current_category != "Extras"

            if is_gordita:
                current_category = "Gorditas"
                ctk.CTkLabel(menu_scroll_frame, text="--- GORDITAS ---", font=FONT_SUBTITULO).pack(fill="x", pady=(10,2))
            elif is_burro:
                current_category = "Burros"
                ctk.CTkLabel(menu_scroll_frame, text="--- BURROS ---", font=FONT_SUBTITULO).pack(fill="x", pady=(10,2))
            elif is_kilo:
                current_category = "Kilo"
                ctk.CTkLabel(menu_scroll_frame, text="--- POR KILO ---", font=FONT_SUBTITULO).pack(fill="x", pady=(10,2))
            elif is_extra:
                current_category = "Extras"
                ctk.CTkLabel(menu_scroll_frame, text="--- EXTRAS ---", font=FONT_SUBTITULO).pack(fill="x", pady=(10,2))

            row_frame = ctk.CTkFrame(menu_scroll_frame, fg_color="white")
            row_frame.pack(fill="x", pady=2, padx=5)

            label_text = f"{item['nombre']} (${item['precio']:.2f})"
            item_label = ctk.CTkLabel(row_frame, text=label_text, anchor="w", text_color=COLOR_TEXTO,
                                      font=FONT_TEXTO) 
            item_label.pack(side="left", fill="x", expand=True, padx=5)
            
            item_entry = ctk.CTkEntry(row_frame, width=80, placeholder_text="0", justify="center",
                                      height=35, font=FONT_TEXTO) 
            item_entry.pack(side="right", padx=5)
            
            self.item_widgets.append( (item, item_entry) )
        # (Fin del frame del menú)

        frame_botones_control = ctk.CTkFrame(content_frame, fg_color="transparent")
        frame_botones_control.pack(pady=5, fill="x")

       
        btn_texto = "ACTUALIZAR PEDIDO" if self.pedido_id else "GUARDAR PEDIDO"
        btn_guardar = ctk.CTkButton(frame_botones_control, text=btn_texto, 
                                    command=self.guardar_o_actualizar_pedido, 
                                    height=50, font=FONT_BOTON) 
        btn_guardar.pack(side="left", expand=True, padx=5)

        btn_cancelar = ctk.CTkButton(frame_botones_control, text="CANCELAR", 
                                     command=lambda: self.app.show_frame(MainFrame),
                                     fg_color="gray", height=50, font=FONT_BOTON) 
        btn_cancelar.pack(side="right", expand=True, padx=5)

        
        if self.pedido_id:
            self.cargar_datos_pedido()

    # (Lógica de cargar_datos_pedido y guardar_o_actualizar_pedido sin cambios)
    def cargar_datos_pedido(self):
        pedido = restaurante.get_pedido_por_id(self.pedido_id)
        if not pedido:
            messagebox.showerror("Error", "No se encontró el pedido para editar.")
            self.app.show_frame(MainFrame)
            return

        self.entry_cliente.insert(0, pedido["nombre_cliente"])
        self.entry_mesa.insert(0, pedido["mesa"])
        
        items_guardados_lista = pedido.get('items', [])
        if not isinstance(items_guardados_lista, list):
             items_guardados_lista = []

        items_guardados = {item['nombre']: item['cantidad'] for item in items_guardados_lista}
        
        for item_data, entry_widget in self.item_widgets:
            if item_data["nombre"] in items_guardados:
                cantidad = items_guardados[item_data["nombre"]]
                entry_widget.insert(0, str(cantidad))

    def guardar_o_actualizar_pedido(self):
        cliente = self.entry_cliente.get().strip()
        mesa = self.entry_mesa.get().strip()
        
        if not cliente or not mesa:
            messagebox.showerror("Error", "Cliente y Mesa son requeridos.")
            return

        items_pedido_actual = []
        total = 0

        for item_data, entry_widget in self.item_widgets:
            cantidad_str = entry_widget.get().strip()

            if not cantidad_str or cantidad_str == "0":
                continue 

            try:
                if "kg" in item_data["nombre"].lower():
                    cantidad = float(cantidad_str)
                else:
                    cantidad = int(cantidad_str)
                
                if cantidad < 0:
                    messagebox.showerror("Error", f"Cantidad negativa no válida para '{item_data['nombre']}'")
                    return

                subtotal = cantidad * item_data["precio"]
                total += subtotal
                
                items_pedido_actual.append({
                    "nombre": item_data["nombre"],
                    "cantidad": cantidad,
                    "precio_unitario": item_data["precio"],
                    "subtotal": subtotal
                })

            except ValueError:
                messagebox.showerror("Error", f"Cantidad inválida para '{item_data['nombre']}'. Debe ser un número.")
                return

        if not items_pedido_actual:
            messagebox.showerror("Error", "No se ha agregado ningún ítem al pedido.")
            return

        id_usuario = self.app.usuario_data["id_usuario"]

        if self.pedido_id:
            if restaurante.actualizar_pedido_completo(self.pedido_id, cliente, mesa, items_pedido_actual, total, id_usuario):
                messagebox.showinfo("Éxito", f"Pedido {self.pedido_id} actualizado. Nuevo Total: ${total:.2f}")
                self.app.show_frame(MainFrame)
            else:
                messagebox.showerror("Error", "No se pudo actualizar el pedido.")
        else:
           
            if restaurante.agregar_pedido(cliente, mesa, items_pedido_actual, total, id_usuario):
                messagebox.showinfo("Éxito", f"Pedido para '{cliente}' guardado. Total: ${total:.2f}")
                self.app.show_frame(MainFrame)
            else:
                messagebox.showerror("Error", "No se pudo guardar el pedido. Revise la consola.")


# (MODIFICADO) Ahora es un CTkScrollableFrame
class ViewOrdersFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, fg_color="white")
        self.app = app_instance

        frame_top = ctk.CTkFrame(self, fg_color=COLOR_FONDO_ROJO, height=80)
        frame_top.pack(fill="x", side="top")
        if self.app.logo_image:
            logo_pequeno = ctk.CTkImage(
                light_image=self.app.logo_image.cget("light_image"),
                size=(100, 100)
            )
            logo_label = ctk.CTkLabel(frame_top, image=logo_pequeno, text="")
            logo_label.pack(pady=5)

        title_label = ctk.CTkLabel(self, text="VER PEDIDOS", 
                                   font=FONT_TITULO,
                                   text_color=COLOR_TEXTO)
        title_label.pack(pady=10)

        btn_regresar = ctk.CTkButton(self, text="REGRESAR", 
                                     command=lambda: self.app.show_frame(MainFrame),
                                     height=50, font=FONT_BOTON, 
                                     width=400, 
                                     fg_color="gray")
        btn_regresar.pack(pady=10)

        # (MODIFICADO) Ya no es "Scrollable", es un CTkFrame normal.
        # La página entera (la clase) se encarga de deslizar.
        scroll_frame = ctk.CTkFrame(self, fg_color=COLOR_CAMPO_GRIS)
        scroll_frame.pack(fill="both", expand=True, padx=100, pady=10) 

        pedidos = restaurante.mostrar_pedidos()
        if not pedidos:
            ctk.CTkLabel(scroll_frame, text="No hay pedidos registrados.", 
                         font=FONT_SUBTITULO, text_color=COLOR_TEXTO).pack()
        
        header_text = f"{'ID':<5} {'Cliente':<25} {'Mesa':<10} {'Total':<15}"
        ctk.CTkLabel(scroll_frame, text=header_text, 
                     font=FONT_PEDIDO_HEADER,
                     text_color=COLOR_TEXTO).pack(anchor="w")

        for p in pedidos:
            pedido_frame = ctk.CTkFrame(scroll_frame, fg_color="white", border_width=1, border_color="gray")
            
            info_str = f"{p['id_registro']:<5} {p['nombre_cliente']:<25} {p['mesa']:<10} ${p['total']:<14.2f}"
            fecha_str = p['fecha_hora'].strftime('%Y-%m-%d')
            
            nombre_mesero = p.get('usuario', 'Sistema')
            
            ctk.CTkLabel(pedido_frame, text=info_str, 
                         font=FONT_PEDIDO_BODY,
                         text_color=COLOR_TEXTO).pack(anchor="w", padx=5)
            
            ctk.CTkLabel(pedido_frame, text=f"  Fecha: {fecha_str} | Estado: {p['estado']} | Atendió: {nombre_mesero}",
                         font=FONT_TEXTO, text_color="gray").pack(anchor="w", padx=5)

            ctk.CTkLabel(pedido_frame, text="  Items:", 
                         font=FONT_TEXTO, text_color=COLOR_TEXTO).pack(anchor="w", padx=5)
            
            items_str = ""
            items_lista = p.get("items", [])
            if not isinstance(items_lista, list): items_lista = []

            for it in items_lista:
                items_str += f"    {it['cantidad']:<5} x {it['nombre']:<30} (${it['subtotal']:.2f})\n"
            
            ctk.CTkLabel(pedido_frame, text=items_str, 
                         font=FONT_TEXTO, text_color=COLOR_TEXTO, justify="left").pack(anchor="w", padx=5)

            pedido_frame.pack(fill="x", pady=5, padx=5)


# (MODIFICADO) Ahora es un CTkScrollableFrame
class DeleteOrderFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, fg_color="white")
        self.app = app_instance

        frame_top = ctk.CTkFrame(self, fg_color=COLOR_FONDO_ROJO, height=80)
        frame_top.pack(fill="x", side="top")
        if self.app.logo_image:
            logo_pequeno = ctk.CTkImage(
                light_image=self.app.logo_image.cget("light_image"),
                size=(100, 100)
            )
            logo_label = ctk.CTkLabel(frame_top, image=logo_pequeno, text="")
            logo_label.pack(pady=5)

        title_label = ctk.CTkLabel(self, text="Eliminar Pedidos", 
                                   font=FONT_TITULO,
                                   text_color=COLOR_TEXTO)
        title_label.pack(pady=40)
        
        ctk.CTkLabel(self, text="Ingrese el ID del pedido a eliminar:", 
                     font=FONT_SUBTITULO, text_color=COLOR_TEXTO).pack(pady=5)
        
        self.entry_id = ctk.CTkEntry(self, placeholder_text="ID de Pedido", width=400,
                                     height=45, font=FONT_TEXTO) 
        self.entry_id.pack(pady=10)

        btn_confirmar = ctk.CTkButton(self, text="Confirmar", 
                                      command=self.confirmar_borrado,
                                      width=400, height=50, font=FONT_BOTON, 
                                      fg_color=COLOR_BOTON_ROSA, text_color=COLOR_TEXTO_BLANCO)
        btn_confirmar.pack(pady=10)

        btn_volver = ctk.CTkButton(self, text="Volver", 
                                   command=lambda: self.app.show_frame(MainFrame),
                                   width=400, height=50, font=FONT_BOTON, 
                                   fg_color="gray")
        btn_volver.pack(pady=5)

    # (Lógica de confirmar_borrado sin cambios)
    def confirmar_borrado(self):
        if self.app.usuario_data['rol'] != 'admin':
            messagebox.showerror("Permiso Denegado", "Solo los administradores pueden eliminar.")
            return
            
        try:
            id_registro = int(self.entry_id.get())
        except ValueError:
            messagebox.showerror("Error", "El ID debe ser un número.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar", 
            f"¿Seguro que desea eliminar el pedido {id_registro}?\n(Se ocultará de la lista pero quedará en la base de datos)."
        )
        
        if confirmar:
            if restaurante.borrar_pedido(id_registro):
                messagebox.showinfo("Éxito", f"Pedido {id_registro} eliminado (ocultado).")
                self.app.show_frame(MainFrame)
            else:
                messagebox.showerror("Error", f"No se encontró el pedido {id_registro}.")


# (MODIFICADO) Ahora es un CTkScrollableFrame
class UpdateOrderFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, fg_color="white")
        self.app = app_instance

        frame_top = ctk.CTkFrame(self, fg_color=COLOR_FONDO_ROJO, height=80)
        frame_top.pack(fill="x", side="top")
        if self.app.logo_image:
            logo_pequeno = ctk.CTkImage(
                light_image=self.app.logo_image.cget("light_image"),
                size=(100, 100)
            )
            logo_label = ctk.CTkLabel(frame_top, image=logo_pequeno, text="")
            logo_label.pack(pady=5)

        title_label = ctk.CTkLabel(self, text="Actualizar Pedido", 
                                   font=FONT_TITULO,
                                   text_color=COLOR_TEXTO)
        title_label.pack(pady=40)
        
        ctk.CTkLabel(self, text="Ingrese el ID del pedido a editar:", 
                     font=FONT_SUBTITULO, text_color=COLOR_TEXTO).pack(pady=5)
        
        self.entry_id = ctk.CTkEntry(self, placeholder_text="ID de Pedido", width=400,
                                     height=45, font=FONT_TEXTO) 
        self.entry_id.pack(pady=10)

        btn_cargar = ctk.CTkButton(self, text="Cargar Pedido para Editar", 
                                      command=self.cargar_para_editar,
                                      width=400, height=50, font=FONT_BOTON, 
                                      fg_color=COLOR_BOTON_ROSA, text_color=COLOR_TEXTO_BLANCO)
        btn_cargar.pack(pady=10)

        btn_volver = ctk.CTkButton(self, text="Volver al Menú", 
                                   command=lambda: self.app.show_frame(MainFrame),
                                   width=400, height=50, font=FONT_BOTON, 
                                   fg_color="gray")
        btn_volver.pack(pady=5)

    # (Lógica de cargar_para_editar sin cambios)
    def cargar_para_editar(self):
        if self.app.usuario_data['rol'] != 'admin':
            messagebox.showerror("Permiso Denegado", "Solo los administradores pueden actualizar.")
            return

        try:
            id_registro = int(self.entry_id.get())
        except ValueError:
            messagebox.showerror("Error", "El ID debe ser un número.")
            return
        
        pedido = restaurante.get_pedido_por_id(id_registro)
        if pedido:
            self.app.show_frame(AddOrderFrame, pedido_id_a_editar=id_registro)
        else:
            messagebox.showerror("Error", f"No se encontró ningún pedido activo con el ID {id_registro}.")