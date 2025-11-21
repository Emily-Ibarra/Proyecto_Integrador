import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
import os
import customtkinter as ctk
from views import (
    LoginFrame, 
    MainFrame, 
    AddOrderFrame, 
    ViewOrdersFrame, 
    DeleteOrderFrame, 
    UpdateOrderFrame,
    KitchenFrame 
)

ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    
    def __init__(self):
        super().__init__()

        self.title("Carnitas & Gorditas EL PUEBLITO - Sistema de Gestión")
        
        # Configuración de ventana
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}")
        self.state('zoomed') 
        self.resizable(True, True) 

        self.usuario_data = None 
        
        # Logo
        logo_path = "logo.PNG"
        self.logo_image = None
        if os.path.exists(logo_path):
            try:
                self.logo_image = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    size=(180, 180)
                )
            except Exception as e:
                print(f"Error cargando imagen: {e}")

        # Contenedor principal
        self.container = ctk.CTkFrame(self, fg_color="#F5F5F5")
        self.container.pack(side="top", fill="both", expand=True)

        self._frame = None
        self.show_frame(LoginFrame)

    def show_frame(self, frame_class, **kwargs):
        if self._frame:
            self._frame.destroy()
        
        self._frame = frame_class(master=self.container, app_instance=self, **kwargs) 
        self._frame.pack(fill="both", expand=True)

    def login_exitoso(self, usuario_data):
        self.usuario_data = usuario_data
        self.show_frame(MainFrame)

    def cerrar_sesion(self):
        if messagebox.askyesno("Salir", "¿Cerrar sesión?"):
            self.usuario_data = None
            self.show_frame(LoginFrame)

if __name__ == "__main__":
    app = App()
    app.mainloop()