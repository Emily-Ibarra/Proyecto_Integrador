class Color:
    PRIMARY = "#8B0000"      # Rojo oscuro (Marca)
    SECONDARY = "#B71C1C"    # Rojo hover
    BG_MAIN = "#ECEFF1"      # Gris azulado muy claro (Fondo)
    BG_CARD = "#FFFFFF"      # Blanco puro
    TEXT_MAIN = "#263238"    # Gris muy oscuro
    TEXT_LIGHT = "#FFFFFF"
    
    # Categorías (Punto 2)
    CAT_GORDITA = "#FFECB3"  # Amarillo pastel
    CAT_BURRO = "#D7CCC8"    # Café claro
    CAT_BEBIDA = "#BBDEFB"   # Azul claro
    CAT_KILO = "#C8E6C9"     # Verde claro
    DEFAULT = "#F5F5F5"

    SUCCESS = "#2E7D32"
    DANGER = "#C62828"
    WARNING = "#EF6C00"

# Fuentes escalables
def font_title(): return ("Segoe UI", 24, "bold")
def font_subtitle(): return ("Segoe UI", 18, "bold")
def font_normal(): return ("Segoe UI", 14)
def font_bold(): return ("Segoe UI", 14, "bold")