import os
import threading
import yt_dlp as youtube_dl
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk

# Global variable to store URLs
urls = []


def download_video(url, output_path, finish_callback, format_option):
    # Ensure the 'phly' directory inside the chosen output directory
    phly_directory = os.path.join(output_path, 'phly')
    if not os.path.exists(phly_directory):
        os.makedirs(phly_directory)

    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes', 0)
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed', 0)  # Bytes per second

            if total and downloaded:
                try:
                    percentage = (downloaded / total) * 100
                    progress_bar['value'] = percentage
                    speed_kbps = speed / 1024  # Convert speed to KB/s
                    status = (f"Downloading: {percentage:.2f}% complete\n"
                              f"Speed: {speed_kbps:.2f} KB/s")
                    current_url.set(status)  # Update the current status label
                except (TypeError, ZeroDivisionError) as e:
                    # Handle possible errors in calculations
                    progress_bar['value'] = 0
                    current_url.set("Error calculating progress.")
            else:
                progress_bar['value'] = 0
                current_url.set("Waiting for data...")
            root.update_idletasks()
        elif d['status'] == 'finished':
            progress_bar['value'] = 100
            current_url.set("Download complete!")
            root.after(1000, lambda: progress_frame.pack_forget())  # Hide the progress bar frame after 1 second

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best' if format_option != 'mp3' else 'bestaudio/best',
        'outtmpl': os.path.join(phly_directory, '%(title)s.%(ext)s'),
        'quiet': False,
        'progress_hooks': [progress_hook],
        'noplaylist': True,
    }

    if format_option == 'mp4':
        ydl_opts['merge_output_format'] = 'mp4'
    elif format_option == 'mkv':
        ydl_opts['merge_output_format'] = 'mkv'
    elif format_option == 'mp3':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    def handle_error(e):
        error_message = str(e)
        if "format is not available" in error_message:
            error_message = "Requested format is not available. Please check the format options or try a different URL."
        root.after(0, lambda: messagebox.showerror("Error", error_message))

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
        root.after(0, finish_callback)
    except Exception as e:
        handle_error(e)


def download_next_url():
    global urls
    if urls:
        url = urls.pop(0)
        progress_bar['value'] = 0
        progress_frame.pack(pady=10)  # Show the progress bar frame
        current_url.set(f"Starting download: {url}")  # Update the current status label
        thread = threading.Thread(target=download_video, args=(url, dir_entry.get(), download_next_url, format_var.get()))
        thread.start()
    else:
        current_url.set("All videos have been downloaded successfully!")
        progress_bar['value'] = 0
        root.update_idletasks()  # Ensure GUI updates after the last video is processed


def start_download():
    video_url = url_entry.get()
    output_directory = dir_entry.get()

    if not output_directory:
        messagebox.showwarning("Output Directory Required", "Please select an output directory before downloading.")
        return

    if video_url:
        urls.clear()
        urls.append(video_url)
        download_next_url()  # Start downloading the URL
    else:
        messagebox.showwarning("URL Required", "Please enter a video URL.")


def import_masterlist():
    global urls
    output_directory = dir_entry.get()

    if not output_directory:
        messagebox.showwarning("Output Directory Required",
                               "Please select an output directory before importing the masterlist.")
        return

    masterlist_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if masterlist_path:
        try:
            with open(masterlist_path, 'r') as file:
                urls = [line.strip() for line in file.readlines() if line.strip()]
                if len(urls) > 5:
                    urls = urls[:5]  # Limit to 5 URLs
                if urls:
                    messagebox.showinfo("Masterlist Imported", f"{len(urls)} URLs loaded from masterlist.")
                    download_next_url()  # Start downloading the first URL
                else:
                    messagebox.showwarning("No URLs", "No valid URLs found in the masterlist.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import masterlist: {e}")


def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, directory)


def open_settings():
    settings_window = ctk.CTkToplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x300")

    def save_settings():
        color_scheme = color_var.get()
        if color_scheme == "Dark":
            ctk.set_appearance_mode("dark")
        elif color_scheme == "Light":
            ctk.set_appearance_mode("light")
        elif color_scheme == "System":
            ctk.set_appearance_mode("system")
        settings_window.destroy()

    color_var = tk.StringVar(value="Dark")

    # Create a dropdown menu for color scheme selection
    color_label = ctk.CTkLabel(settings_window, text="Select Color Scheme:")
    color_label.pack(pady=10)
    color_menu = ctk.CTkOptionMenu(settings_window, variable=color_var, values=["Dark", "Light", "System"])
    color_menu.pack(pady=10)

    save_button = ctk.CTkButton(settings_window, text="Save", command=save_settings)
    save_button.pack(pady=10)


# Create the main window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("PHLY - Video Downloader")
root.geometry("600x500")

# Create and place the URL label and entry
url_label = ctk.CTkLabel(root, text="Enter the URL of the video:")
url_label.pack(pady=10)
url_entry = ctk.CTkEntry(root, width=500)
url_entry.pack(pady=5)

# Create and place the directory label and entry
dir_label = ctk.CTkLabel(root, text="Select the output directory:")
dir_label.pack(pady=10)

# Frame for directory selection
dir_frame = ctk.CTkFrame(root)
dir_frame.pack(pady=5)

dir_entry = ctk.CTkEntry(dir_frame, width=400)
dir_entry.pack(side=tk.LEFT, padx=5)

browse_button = ctk.CTkButton(dir_frame, text="Browse", command=browse_directory)
browse_button.pack(side=tk.RIGHT)

# Create and place the format label and dropdown menu
format_label = ctk.CTkLabel(root, text="Select the file format:")
format_label.pack(pady=10)

format_var = tk.StringVar(value="mp4")
format_menu = ctk.CTkOptionMenu(root, variable=format_var, values=["mp4", "mp3", "mkv"])
format_menu.pack(pady=5)

# Create and place the action buttons
start_button = ctk.CTkButton(root, text="Start Download", command=start_download)
start_button.pack(pady=20)

import_button = ctk.CTkButton(root, text="Import Masterlist", command=import_masterlist)
import_button.pack(pady=5)

settings_button = ctk.CTkButton(root, text="Settings", command=open_settings)
settings_button.pack(pady=5)

# Create and place the progress frame and status label
progress_frame = ctk.CTkFrame(root)
progress_frame.pack_forget()  # Hide the frame initially

# Create and place the progress bar
progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=500, mode="determinate")
progress_bar.pack(pady=10)

current_url = tk.StringVar()
status_label = ctk.CTkLabel(progress_frame, textvariable=current_url)
status_label.pack(pady=10)

# Run the application
root.mainloop()
