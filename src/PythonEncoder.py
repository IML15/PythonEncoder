import os
import base64
import customtkinter as ctk
from tkinter import messagebox
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def obtener_motor_cifrado(password: str, carpeta_objetivo: str) -> Fernet:
    archivo_salt = os.path.join(carpeta_objetivo, ".salt.key")

    if os.path.exists(archivo_salt):
        with open(archivo_salt, "rb") as f:
            salt = f.read()
    else:
        # Si la carpeta no existe o está mal puesta, os.walk no fallará pero no hará nada.
        # Creamos la ruta si es necesario
        if not os.path.exists(carpeta_objetivo):
            os.makedirs(carpeta_objetivo)
        salt = os.urandom(16)
        with open(archivo_salt, "wb") as f:
            f.write(salt)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    clave = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return Fernet(clave)


def procesar_carpeta(accion: str):

    carpeta_objetivo = entry_ruta.get()
    password = entry_pass.get()
    archivo_salt = os.path.join(carpeta_objetivo, ".salt.key")

    if not carpeta_objetivo or not password:
        messagebox.showwarning("Atención", "Por favor, rellena todos los campos.")
        return

    try:
        motor = obtener_motor_cifrado(password, carpeta_objetivo)

        for ruta_actual, carpetas, archivos in os.walk(carpeta_objetivo):
            for nombre_archivo in archivos:
                if nombre_archivo == ".salt.key":
                    continue

                ruta_completa = os.path.join(ruta_actual, nombre_archivo)

                with open(ruta_completa, "rb") as f:
                    datos_originales = f.read()

                if accion == "cifrar":
                    datos_procesados = motor.encrypt(datos_originales)
                elif accion == "descifrar":
                    datos_procesados = motor.decrypt(datos_originales)

                with open(ruta_completa, "wb") as f:
                    f.write(datos_procesados)

        messagebox.showinfo("Éxito", f"Operación de {accion} completada correctamente.")

    except Exception as e:
        messagebox.showerror("Error", "Contraseña incorrecta o archivos dañados.")


# --- DISEÑO DE LA INTERFAZ GRÁFICA ---
ventana = ctk.CTk()
ventana.title("CryptoFolder Resguardo AES-256")
ventana.geometry("600x350")

# Título principal
titulo = ctk.CTkLabel(ventana, text="HERRAMIENTA DE CIFRADO SEGURO", font=("Arial", 16, "bold"))
titulo.pack(pady=20)

# Campo para la Ruta
lbl_ruta = ctk.CTkLabel(ventana, text="Ruta de la carpeta:")
lbl_ruta.pack(anchor="w", padx=40)
entry_ruta = ctk.CTkEntry(ventana, width=420, placeholder_text="/Users/iml15/carpeta_prueba")
entry_ruta.pack(pady=5)

# Campo para la Contraseña
lbl_pass = ctk.CTkLabel(ventana, text="Contraseña Maestra:")
lbl_pass.pack(anchor="w", padx=40)
entry_pass = ctk.CTkEntry(ventana, width=420, show="*", placeholder_text="Introduce una contraseña segura")
entry_pass.pack(pady=5)

# Contenedor para alinear los botones uno al lado del otro
marco_botones = ctk.CTkFrame(ventana, fg_color="transparent")
marco_botones.pack(pady=30)

# Usamos funciones lambda para pasarle el argumento 'cifrar' o 'descifrar' a nuestra función
btn_cifrar = ctk.CTkButton(marco_botones, text="Cifrar Carpeta", fg_color="firebrick", hover_color="maroon",
                           command=lambda: procesar_carpeta("cifrar"))
btn_cifrar.pack(side="left", padx=10)

btn_descifrar = ctk.CTkButton(marco_botones, text="Descifrar Carpeta", fg_color="green", hover_color="darkgreen",
                              command=lambda: procesar_carpeta("descifrar"))
btn_descifrar.pack(side="left", padx=10)

# Iniciar el bucle de la ventana
ventana.mainloop()