import os
import base64
import customtkinter as ctk
from tkinter import messagebox
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def get_encryption_engine(password: str, target_folder: str) -> Fernet:
    salt_file = os.path.join(target_folder, ".salt.key")

    if os.path.exists(salt_file):
        with open(salt_file, "rb") as f:
            salt = f.read()
    else:
        # If the folder does not exist or is specified incorrectly, os.walk will not fail, but it will do nothing.
        # We create the route if necessary.
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        salt = os.urandom(16)
        with open(salt_file, "wb") as f:
            f.write(salt)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    clave = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return Fernet(clave)


def process_folder(action: str):

    target_folder = entry_ruta.get()
    password = entry_pass.get()
    archivo_salt = os.path.join(target_folder, ".salt.key")

    if not target_folder or not password:
        messagebox.showwarning("Attention!", "Please fill in all the fields.")
        return

    try:
        engine = get_encryption_engine(password, target_folder)

        for current_route, folders, files in os.walk(target_folder):
            for file_name in files:
                if file_name == ".salt.key":
                    continue

                complete_path = os.path.join(current_route, file_name)

                with open(complete_path, "rb") as f:
                    original_data = f.read()

                if action == "Encrypt":
                    processed_data = engine.encrypt(original_data)
                elif action == "Decrypt":
                    processed_data = engine.decrypt(original_data)

                with open(complete_path, "wb") as f:
                    f.write(processed_data)

        messagebox.showinfo("Success", f"{action} operation completed successfully.")

    except Exception as e:
        messagebox.showerror("Error", "Incorrect password or damaged files.")


# --- GRAPHICAL USER INTERFACE DESIGN ---
window = ctk.CTk()
window.title("CryptoFolder AES-256")
window.geometry("600x350")

# Main title
title = ctk.CTkLabel(window, text="SECURE ENCRYPTION", font=("Arial", 16, "bold"))
title.pack(pady=20)

# Field for the Route
lbl_ruta = ctk.CTkLabel(window, text="Folder's path:")
lbl_ruta.pack(anchor="w", padx=40)
entry_ruta = ctk.CTkEntry(window, width=420, placeholder_text="/Users/iml15/folder's_path")
entry_ruta.pack(pady=5)

# Password field
lbl_pass = ctk.CTkLabel(window, text="Master Password:")
lbl_pass.pack(anchor="w", padx=40)
entry_pass = ctk.CTkEntry(window, width=420, show="*", placeholder_text="Enter a secure password")
entry_pass.pack(pady=5)

# Container for aligning the buttons side by side
buttons = ctk.CTkFrame(window, fg_color="transparent")
buttons.pack(pady=30)

# We use lambda functions to pass the 'encrypt' or 'decrypt' argument to our function.
btn_encrypt = ctk.CTkButton(buttons, text="Encrypt Folder", fg_color="firebrick", hover_color="maroon",
                            command=lambda: process_folder("Encrypt"))
btn_encrypt.pack(side="left", padx=10)

btn_decrypt = ctk.CTkButton(buttons, text="Decrypt Folder", fg_color="green", hover_color="darkgreen",
                            command=lambda: process_folder("Decrypt"))
btn_decrypt.pack(side="left", padx=10)

# Start the window loop
window.mainloop()