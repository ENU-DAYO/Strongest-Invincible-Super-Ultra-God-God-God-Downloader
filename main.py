import customtkinter as ctk
from tkinter import filedialog, messagebox
from yt_dlp import YoutubeDL
import os
import datetime
import configparser
import threading
import re
import subprocess

# Define the config file path in the same directory as the script
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(script_dir, 'settings.ini')
log_file = os.path.join(script_dir, 'download_log.txt')

# Add ffmpeg directory to PATH
ffmpeg_dir = script_dir  # Assuming ffmpeg is in the same directory as the script
os.environ['PATH'] += os.pathsep + ffmpeg_dir

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

def write_log(message):
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f'{datetime.datetime.now()}: {message}\n')

def check_and_update_ytdlp():
    try:
        # Check for updates
        result = subprocess.run(['yt-dlp', '--update'], capture_output=True, text=True)
        if 'Updated yt-dlp' in result.stdout or 'yt-dlp is up to date' in result.stdout:
            write_log("yt-dlpは最新の状態です。")
        else:
            write_log("yt-dlpの更新中にエラーが発生しました。")
            write_log(result.stdout)
            write_log(result.stderr)
    except FileNotFoundError:  # Ignore the specific error when the file is not found
        pass  # Simply ignore this error
    except Exception as e:
        write_log(f"yt-dlpの更新に失敗しました: {str(e)}")

def download_video_thread():
    url = url_entry.get()
    save_path = save_path_entry.get()  # ここでsave_pathを取得
    file_name = file_name_entry.get()

    # ファイル形式の選択
    if format_var.get() == "mp4":
        ext = "mp4"
        ydl_opts = {
            'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]',  # MP4動画フォーマット
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
        }
    elif format_var.get() == "mp3":
        ext = "mp3"
        ydl_opts = {
            'format': 'bestaudio/best',  # 最良の音声フォーマット
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }]
        }
    elif format_var.get() == "wav":
        ext = "wav"
        ydl_opts = {
            'format': 'bestaudio/best',  # 最良の音声フォーマット
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        }
    else:
        messagebox.showerror("エラー", "少なくとも1つの形式を選択してください。")
        return

    save_settings(save_path)

    # ファイル名が空の場合、デフォルトのファイル名を使用
    if not file_name:
        file_name = '%(title)s'

    # ダウンロード設定に出力パスとファイル名を追加
    ydl_opts['outtmpl'] = os.path.join(save_path, f'{file_name}.%(ext)s')  # ここでsave_pathを使います
    ydl_opts['add-header'] = 'Accept-Language:ja-JP'
    ydl_opts['progress_hooks'] = [progress_hook]

    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(result)

        # Update the file's modification time to today
        now = datetime.datetime.now().timestamp()
        os.utime(downloaded_file, (now, now))

        # Update status label
        status_label.configure(text="ダウンロード完了")
        progress_bar.set(1.0)
        write_log(f"ダウンロード完了: {downloaded_file}")
    except FileNotFoundError:  # Ignore the specific error when the file is not found
        pass  # Simply ignore this error
    except Exception as e:
        error_message = f"ダウンロードに失敗しました: {str(e)}"
        status_label.configure(text="ダウンロードに失敗しました")
        write_log(error_message)
        messagebox.showerror("エラー", error_message)

def progress_hook(d):
    if d['status'] == 'downloading':
        progress_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str'])
        progress = float(progress_str.strip('%')) / 100
        progress_bar.set(progress)
    elif d['status'] == 'finished':
        progress_bar.set(1.0)
        status_label.configure(text="ダウンロード完了！")  # ここでテキストを変更します

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

# ファイル名入力欄
ctk.CTkLabel(frame, text="ファイル名", font=("Yu Gothic", 14)).grid(row=3, column=0, padx=10, pady=10)
file_name_entry = ctk.CTkEntry(frame, width=600, font=("Yu Gothic", 14))
file_name_entry.grid(row=3, column=1, padx=10, pady=10)

# フォーマット選択ラジオボタン (横並び)
format_var = ctk.StringVar(value="mp4")  # デフォルトでmp4を選択

ctk.CTkLabel(frame, text="フォーマット", font=("Yu Gothic", 14)).grid(row=4, column=0, padx=10, pady=10)

# MP4, MP3, WAV のラジオボタンを横に並べる
radio_frame = ctk.CTkFrame(frame)
radio_frame.grid(row=4, column=1, columnspan=2, pady=10)  # 横に広げる

mp4_radio = ctk.CTkRadioButton(radio_frame, text="mp4", variable=format_var, value="mp4", font=("Yu Gothic", 14))
mp4_radio.grid(row=0, column=0, padx=10)

mp3_radio = ctk.CTkRadioButton(radio_frame, text="wav", variable=format_var, value="mp3", font=("Yu Gothic", 14))
mp3_radio.grid(row=0, column=1, padx=10)

wav_radio = ctk.CTkRadioButton(radio_frame, text="mp3", variable=format_var, value="wav", font=("Yu Gothic", 14))
wav_radio.grid(row=0, column=2, padx=10)

# Download button
download_button = ctk.CTkButton(frame, text="ダウンロード", command=download_video, font=("Yu Gothic", 14))
download_button.grid(row=5, columnspan=3, pady=20)

# Status label and progress bar
status_label = ctk.CTkLabel(frame, text="", font=("Yu Gothic", 14))
status_label.grid(row=6, columnspan=3, pady=10)

progress_bar = ctk.CTkProgressBar(frame)
progress_bar.grid(row=7, columnspan=3, padx=10, pady=10)

# Check for updates on startup
check_and_update_ytdlp()

# Start the GUI loop
root.mainloop()
