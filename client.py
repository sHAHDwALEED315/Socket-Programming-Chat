import socket
import threading
import customtkinter as ctk
from tkinter import filedialog
import os
import subprocess
from PIL import Image
import cv2  

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect(("127.0.0.1", 3000))
except:
    print("Could not connect to server")

window = ctk.CTk()
window.title("Chat App")
window.geometry("350x550")
window.configure(fg_color="#FBCFE8") 

main_frame = ctk.CTkFrame(window, fg_color="transparent")
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

chat_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent", label_text="")
chat_frame.pack(fill="both", expand=True)

def get_video_thumbnail(video_path):
    cap = cv2.VideoCapture(video_path)
    success, image = cap.read()
    if success:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(image)
    return None

def add_message(msg, align="left"):
    color = "#E0E7FF" if align == "left" else "#D1FAE5"
    anchor = "w" if align == "left" else "e"
    
    msg_bubble = ctk.CTkLabel(
        chat_frame, 
        text=msg, 
        fg_color=color, 
        corner_radius=15, 
        padx=15, pady=8,
        text_color="black",
        wraplength=250
    )
    msg_bubble.pack(anchor=anchor, pady=5, padx=5)

def add_media(path, media_type="image", align="left"):
    anchor = "w" if align == "left" else "e"
    try:
        if media_type == "video":
            raw_img = get_video_thumbnail(path)
            if not raw_img: raw_img = Image.new('RGB', (200, 150), color='black')
        else:
            raw_img = Image.open(path)

        raw_img.thumbnail((200, 200))
        img = ctk.CTkImage(light_image=raw_img, size=raw_img.size)

        media_btn = ctk.CTkButton(
            chat_frame, 
            image=img, 
            text="▶" if media_type == "video" else "", 
            fg_color="transparent",
            hover_color="#ddd",
            command=lambda: open_file(path),
            corner_radius=15
        )
        media_btn.pack(anchor=anchor, pady=5, padx=5)
    except Exception as e:
        add_message(f"Error loading file: {os.path.basename(path)}", align)

def add_file_button(filename, path, align="left"):
    anchor = "w" if align == "left" else "e"
    
    is_audio = filename.lower().endswith((".mp3", ".wav", ".m4a"))
    icon = "🎵" if is_audio else "📄"
    color = "#8B5CF6" if is_audio else "#3B82F6" # بنفسجي للصوت وأزرق للملفات العادية
    
    file_btn = ctk.CTkButton(
        chat_frame,
        text=f"{icon} {filename}",
        fg_color=color,
        hover_color="#7C3AED" if is_audio else "#2563EB",
        corner_radius=15,
        command=lambda: open_file(path)
    )
    file_btn.pack(anchor=anchor, pady=5, padx=5)

def open_file(path):
    if os.name == 'nt': os.startfile(path)
    else: subprocess.call(["open", path])

def send_message():
    msg = msg_entry.get()
    if msg:
        client.send(("MSG:" + msg).encode())
        add_message(msg, "right")
        msg_entry.delete(0, 'end')

def send_file():
    file_path = filedialog.askopenfilename()
    if not file_path: return
    
    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)
    header = f"FILE|{filename}|{filesize}|".encode()
    client.send(header)

    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            client.send(chunk)

    ext = filename.lower()
    if ext.endswith((".png", ".jpg", ".jpeg")):
        add_media(file_path, "image", "right")
    elif ext.endswith((".mp4", ".avi", ".mov")):
        add_media(file_path, "video", "right")
    else:
        add_file_button(filename, file_path, "right")

def receive():
    while True:
        try:
            data = client.recv(4096)
            if data.startswith(b"MSG:"):
                add_message(data[4:].decode(), "left")
            elif data.startswith(b"FILE|"):
                parts = data.split(b"|", 3)
                filename = parts[1].decode()
                filesize = int(parts[2].decode())
                file_data = parts[3]
                while len(file_data) < filesize:
                    file_data += client.recv(4096)
                
                download_dir = "received_files"
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)
                
                save_path = os.path.join(download_dir, filename)
                
                with open(save_path, "wb") as f: 
                    f.write(file_data)

                ext = filename.lower()
                if ext.endswith((".png", ".jpg", ".jpeg")):
                    add_media(save_path, "image", "left")
                elif ext.endswith((".mp4", ".avi", ".mov")):
                    add_media(save_path, "video", "left")
                else:
                    add_file_button(filename, save_path, "left")
        except: break

input_frame = ctk.CTkFrame(window, fg_color="white", corner_radius=25, height=50)
input_frame.pack(fill="x", side="bottom", padx=20, pady=20)

file_btn = ctk.CTkButton(input_frame, text="+", width=40, corner_radius=20, command=send_file)
file_btn.pack(side="left", padx=5)

msg_entry = ctk.CTkEntry(input_frame, placeholder_text="Message...", border_width=0, fg_color="transparent")
msg_entry.pack(side="left", fill="x", expand=True, padx=5)
msg_entry.bind("<Return>", lambda e: send_message())

send_btn = ctk.CTkButton(input_frame, text="➤", width=40, corner_radius=20, command=send_message)
send_btn.pack(side="right", padx=5)

threading.Thread(target=receive, daemon=True).start()
window.mainloop()