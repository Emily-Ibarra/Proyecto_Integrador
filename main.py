import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
import os

from views import (
    LoginFrame, 
    MainFrame, 
    AddOrderFrame, 
    ViewOrdersFrame, 
    DeleteOrderFrame, 
    UpdateOrderFrame
)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    
    def __init__(self):
        super().__init__()

        self.title("Carnitas & Gorditas EL PUEBLITO")
        
        # (MODIFICADO) Inicia la ventana maximizada (pantalla completa)
        self.state('zoomed') 
        
        # (MODIFICADO) Comentamos la geometría fija
        # self.geometry("400x750") 
        
        # (MODIFICADO) Permitimos que la ventana cambie de tamaño
        self.resizable(True, True) 

        # Guarda todos los datos del usuario (id, nombre, rol, email)
        self.usuario_data = None 
        
        logo_path = "logo.PNG"
        if os.path.exists(logo_path):
            # (MODIFICADO) Hacemos el logo un poco más grande para la pantalla completa
            self.logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                size=(200, 200) # Era 150x150
            )
        else:
            print("Error: No se encontró 'logo.PNG'. Asegúrate que esté en la misma carpeta.")
            self.logo_image = None

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True)

        self._frame = None
        self.show_frame(LoginFrame)

    
    def show_frame(self, frame_class, **kwargs):
        
        if self._frame:
            self._frame.destroy()
        
       
        self._frame = frame_class(master=self.container, app_instance=self, **kwargs) 
        self._frame.pack(fill="both", expand=True)

    def login_exitoso(self, usuario_data):
        # Muestra el mensaje de bienvenida
        messagebox.showinfo(
            "Inicio de Sesión Exitoso", 
            f"¡Bienvenido, {usuario_data['usuario']}!"
        )
        
        self.usuario_data = usuario_data
        self.show_frame(MainFrame)

    def cerrar_sesion(self):
        confirmar = messagebox.askyesno(
            title="Cerrar Sesión",
            message="¿Desea cerrar la sesión?"
        )
        if confirmar:
            self.usuario_data = None
            self.show_frame(LoginFrame)

# Ejecuta la app
if __name__ == "__main__":
    app = App()
    app.mainloop()