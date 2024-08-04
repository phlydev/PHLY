import os
import requests
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path
import win32com.client
from PIL import Image


def download_file(url, dest_folder, filename):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    file_path = os.path.join(dest_folder, filename)
    response = requests.get(url, stream=True)
    try:
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    file.write(chunk)
    except Exception as e:
        raise RuntimeError(f"Error downloading file: {e}")
    return file_path


def convert_to_ico(input_path, output_path):
    try:
        with Image.open(input_path) as image:
            image = image.convert("RGBA")  # Ensure image is in RGBA mode
            image.save(output_path, format='ICO', sizes=[(256, 256)])  # Standard icon size
    except Exception as e:
        raise RuntimeError(f"Error converting image to ICO: {e}")


def create_shortcut(target_path, shortcut_name):
    desktop = Path(os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"], "Desktop"))
    shortcut_path = desktop / f"{shortcut_name}.lnk"

    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = os.path.dirname(target_path)
        shortcut.save()
    except Exception as e:
        raise RuntimeError(f"Error creating shortcut: {e}")


def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, directory)


def install():
    download_url = "https://getphly.xyz/phlydownloader.exe"
    icon_url = "https://getphly.xyz/phlylog.ico"
    install_dir = dir_entry.get()
    if not install_dir:
        messagebox.showwarning("Input Required", "Please select a directory.")
        return

    try:
        exe_path = os.path.join(install_dir, "phlydownloader.exe")
        icon_path = os.path.join(install_dir, "temp_icon.png")
        ico_path = os.path.join(install_dir, "phlylog.ico")

        # Download and replace the .exe file
        download_file(download_url, install_dir, "phlydownloader.exe")

        # Download and convert the icon
        download_file(icon_url, install_dir, "temp_icon.png")
        convert_to_ico(icon_path, ico_path)
        os.remove(icon_path)  # Clean up temp icon file

        # Create or replace the desktop shortcut
        create_shortcut(exe_path, "PHLY Downloader")

        # Notify success and close
        messagebox.showinfo("Success", "Installation completed successfully.")
        root.destroy()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Initialize customtkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Create the installer window
root = ctk.CTk()
root.title("PHLY Downloader Installer")
root.geometry("400x200")

# Set the icon for the window
icon_url = "https://getphly.xyz/phlylog.ico"
icon_path = download_file(icon_url, ".", "temp_icon.png")
ico_path = os.path.join(".", "temp_icon.ico")
convert_to_ico(icon_path, ico_path)
root.iconbitmap(ico_path)

# Create and place the directory label and entry
dir_label = ctk.CTkLabel(root, text="Select Installation Directory:")
dir_label.pack(pady=10)

dir_entry = ctk.CTkEntry(root, width=300)
dir_entry.pack(pady=5, padx=10)

browse_button = ctk.CTkButton(root, text="Browse", command=browse_directory)
browse_button.pack(pady=5)

install_button = ctk.CTkButton(root, text="Install", command=install)
install_button.pack(pady=20)


# Clean up the temporary icon file when the application closes
def cleanup():
    if os.path.exists(ico_path):
        os.remove(ico_path)
    root.destroy()


root.protocol("WM_DELETE_WINDOW", cleanup)

# Run the installer application
root.mainloop()
