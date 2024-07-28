import customtkinter as ctk
from tkinter import filedialog
from yt_dlp import YoutubeDL
import os
import datetime
import configparser
import threading
import re

# Define the config file path in the same directory as the script
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(script_dir, 'settings.ini')

def load_settings():
    config = configparser.ConfigParser()
    config.read(config_file)
    if 'Settings' in config and 'save_path' in config['Settings']:
        return config['Settings']['save_path']
    return ''

def save_settings(save_path):
    config = configparser.ConfigParser()
    config['Settings'] = {'save_path': save_path}
    with open(config_file, 'w') as configfile:
        config.write(configfile)

def download_video_thread():
    url = url_entry.get()
    save_path = save_path_entry.get()
    save_settings(save_path)
    ydl_opts = {
        'outtmpl': f'{save_path}/%(title)s.%(ext)s',
        'add-header': 'Accept-Language:ja-JP',
        'embed-thumbnail': True,
        'embed-metadata': True,
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]',
        'progress_hooks': [progress_hook]
    }
    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
        downloaded_file = ydl.prepare_filename(result)
    
    # Update the file's modification time to today
    now = datetime.datetime.now().timestamp()
    os.utime(downloaded_file, (now, now))
    
    # Update status label
    status_label.configure(text="ダウンロード完了")
    progress_bar.set(1.0)

def progress_hook(d):
    if d['status'] == 'downloading':
        progress_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str'])
        progress = float(progress_str.strip('%')) / 100
        progress_bar.set(progress)
    elif d['status'] == 'finished':
        progress_bar.set(1.0)

def download_video():
    status_label.configure(text="ダウンロード中...")
    progress_bar.set(0.0)
    threading.Thread(target=download_video_thread).start()

def browse_directory():
    directory = filedialog.askdirectory()
    save_path_entry.delete(0, ctk.END)
    save_path_entry.insert(0, directory)

def paste_url():
    url_entry.delete(0, ctk.END)
    url_entry.insert(0, root.clipboard_get())

# GUI setup
root = ctk.CTk()
root.title("最強無敵スーパーウルトラ神神神ダウンローダー")
root.geometry("960x540")
root.resizable(False, False)

# Center frame
frame = ctk.CTkFrame(root)
frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

# Title
title_label = ctk.CTkLabel(frame, text="最強無敵スーパーウルトラ神神神ダウンローダー", font=("Yu Gothic", 24))
title_label.grid(row=0, columnspan=3, pady=20)

# URL input
ctk.CTkLabel(frame, text="URL", font=("Yu Gothic", 14)).grid(row=1, column=0, padx=10, pady=10)
url_entry = ctk.CTkEntry(frame, width=600, font=("Yu Gothic", 14))
url_entry.grid(row=1, column=1, padx=10, pady=10)
paste_button = ctk.CTkButton(frame, text="ペースト", command=paste_url, font=("Yu Gothic", 14))
paste_button.grid(row=1, column=2, padx=10, pady=10)

# Save path input
ctk.CTkLabel(frame, text="保存先", font=("Yu Gothic", 14)).grid(row=2, column=0, padx=10, pady=10)
save_path_entry = ctk.CTkEntry(frame, width=600, font=("Yu Gothic", 14))
save_path_entry.grid(row=2, column=1, padx=10, pady=10)
browse_button = ctk.CTkButton(frame, text="参照", command=browse_directory, font=("Yu Gothic", 14))
browse_button.grid(row=2, column=2, padx=10, pady=10)

# Load the last saved path
last_save_path = load_settings()
if last_save_path:
    save_path_entry.insert(0, last_save_path)

# Download button
download_button = ctk.CTkButton(frame, text="ダウンロード", command=download_video, font=("Yu Gothic", 14))
download_button.grid(row=3, columnspan=3, pady=20)

# Progress bar
progress_bar = ctk.CTkProgressBar(frame, width=600)
progress_bar.grid(row=4, columnspan=3, pady=10)
progress_bar.set(0.0)

# Status label
status_label = ctk.CTkLabel(frame, text="", font=("Yu Gothic", 14))
status_label.grid(row=5, columnspan=3, pady=10)

root.mainloop()
