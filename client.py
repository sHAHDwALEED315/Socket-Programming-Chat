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

# ── Identity assigned by server ──────────────────────────────────────────────
my_color  = "#D1FAE5"   # default until server sends IDENTITY
my_avatar = "🙂"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect(("127.0.0.1", 3000))
except Exception as e:
    print("Could not connect to server:", e)

# ── Window ───────────────────────────────────────────────────────────────────
window = ctk.CTk()
window.title("Chat App")
window.geometry("370x600")
window.configure(fg_color="#FBCFE8")

main_frame = ctk.CTkFrame(window, fg_color="transparent")
main_frame.pack(fill="both", expand=True, padx=20, pady=(20, 0))

# Header showing our own identity
identity_label = ctk.CTkLabel(
    main_frame,
    text=f"{my_avatar}  You",
    font=ctk.CTkFont(size=14, weight="bold"),
    text_color="#6D28D9"
)
identity_label.pack(anchor="e", pady=(0, 6))

chat_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent", label_text="")
chat_frame.pack(fill="both", expand=True)

# ── Media helpers ─────────────────────────────────────────────────────────────
def get_video_thumbnail(video_path):
    cap = cv2.VideoCapture(video_path)
    success, image = cap.read()
    if success:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(image)
    return None

def open_file(path):
    if os.name == 'nt':
        os.startfile(path)
    else:
        subprocess.call(["open", path])

# ── UI builders ───────────────────────────────────────────────────────────────
def add_message(msg, align="left", color="#E0E7FF", avatar="👤"):
    """
    Renders a chat bubble.
    - align="right"  → our own message (no avatar label)
    - align="left"   → incoming message (show sender avatar)
    """
    row = ctk.CTkFrame(chat_frame, fg_color="transparent")
    row.pack(fill="x", pady=3, padx=4)

    if align == "left":
        # Avatar badge
        av_lbl = ctk.CTkLabel(row, text=avatar, font=ctk.CTkFont(size=20),
                               fg_color="white", corner_radius=20,
                               width=36, height=36, text_color="black")
        av_lbl.pack(side="left", padx=(0, 6), anchor="s")

        bubble = ctk.CTkLabel(
            row, text=msg, fg_color=color,
            corner_radius=15, padx=12, pady=8,
            text_color="#1E1E1E", wraplength=230, anchor="w", justify="left"
        )
        bubble.pack(side="left", anchor="w")
    else:
        bubble = ctk.CTkLabel(
            row, text=msg, fg_color=my_color,
            corner_radius=15, padx=12, pady=8,
            text_color="#1E1E1E", wraplength=230, anchor="e", justify="right"
        )
        bubble.pack(side="right", anchor="e")

        av_lbl = ctk.CTkLabel(row, text=my_avatar, font=ctk.CTkFont(size=20),
                               fg_color="white", corner_radius=20,
                               width=36, height=36, text_color="black")
        av_lbl.pack(side="right", padx=(6, 0), anchor="s")

    # Auto-scroll
    chat_frame._parent_canvas.yview_moveto(1.0)


def add_media(path, media_type="image", align="left", color="#E0E7FF", avatar="👤"):
    row = ctk.CTkFrame(chat_frame, fg_color="transparent")
    row.pack(fill="x", pady=3, padx=4)

    try:
        if media_type == "video":
            raw_img = get_video_thumbnail(path) or Image.new('RGB', (200, 150), color='gray')
        else:
            raw_img = Image.open(path)

        raw_img.thumbnail((200, 200))
        img = ctk.CTkImage(light_image=raw_img, size=raw_img.size)

        media_btn = ctk.CTkButton(
            row, image=img,
            text="▶" if media_type == "video" else "",
            fg_color="transparent", hover_color="#ddd",
            command=lambda: open_file(path), corner_radius=15
        )

        if align == "left":
            av_lbl = ctk.CTkLabel(row, text=avatar, font=ctk.CTkFont(size=20),
                                   fg_color="white", corner_radius=20,
                                   width=36, height=36, text_color="black")
            av_lbl.pack(side="left", anchor="s", padx=(0, 6))
            media_btn.pack(side="left", anchor="w")
        else:
            media_btn.pack(side="right", anchor="e")
            av_lbl = ctk.CTkLabel(row, text=my_avatar, font=ctk.CTkFont(size=20),
                                   fg_color="white", corner_radius=20,
                                   width=36, height=36, text_color="black")
            av_lbl.pack(side="right", anchor="s", padx=(6, 0))
    except Exception as e:
        add_message(f"⚠ Error loading file: {os.path.basename(path)}", align, color, avatar)

    chat_frame._parent_canvas.yview_moveto(1.0)


def add_file_button(filename, path, align="left", color="#E0E7FF", avatar="👤"):
    row = ctk.CTkFrame(chat_frame, fg_color="transparent")
    row.pack(fill="x", pady=3, padx=4)

    is_audio = filename.lower().endswith((".mp3", ".wav", ".m4a"))
    icon = "🎵" if is_audio else "📄"
    btn_color = "#8B5CF6" if is_audio else "#3B82F6"
    hover = "#7C3AED" if is_audio else "#2563EB"

    file_btn = ctk.CTkButton(
        row, text=f"{icon} {filename}",
        fg_color=btn_color, hover_color=hover,
        corner_radius=15, command=lambda: open_file(path)
    )

    if align == "left":
        av_lbl = ctk.CTkLabel(row, text=avatar, font=ctk.CTkFont(size=20),
                               fg_color="white", corner_radius=20,
                               width=36, height=36, text_color="black")
        av_lbl.pack(side="left", anchor="s", padx=(0, 6))
        file_btn.pack(side="left", anchor="w")
    else:
        file_btn.pack(side="right", anchor="e")
        av_lbl = ctk.CTkLabel(row, text=my_avatar, font=ctk.CTkFont(size=20),
                               fg_color="white", corner_radius=20,
                               width=36, height=36, text_color="black")
        av_lbl.pack(side="right", anchor="s", padx=(6, 0))

    chat_frame._parent_canvas.yview_moveto(1.0)

# ── Send actions ──────────────────────────────────────────────────────────────
def send_message():
    msg = msg_entry.get().strip()
    if msg:
        client.send(("MSG:" + msg).encode())
        add_message(msg, "right")
        msg_entry.delete(0, 'end')

def send_file():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

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

# ── Receive thread ────────────────────────────────────────────────────────────
def receive():
    global my_color, my_avatar

    while True:
        try:
            data = client.recv(65536)
            if not data:
                break

            # Server tells us our own identity
            if data.startswith(b"IDENTITY:"):
                payload = data[9:].decode()
                color_part, avatar_part = payload.split("|", 1)
                my_color  = color_part
                my_avatar = avatar_part
                window.after(0, lambda: identity_label.configure(
                    text=f"{my_avatar}  You"))
                continue

            # Incoming text message: MSG:<color>|<avatar>|<text>
            if data.startswith(b"MSG:"):
                rest = data[4:]
                parts = rest.split(b"|", 2)
                color  = parts[0].decode()
                avatar = parts[1].decode()
                text   = parts[2].decode()
                window.after(0, lambda t=text, c=color, a=avatar:
                             add_message(t, "left", c, a))
                continue

            # Incoming file: FILE|<color>|<avatar>|<filename>|<size>|<bytes>
            if data.startswith(b"FILE|"):
                parts = data.split(b"|", 5)
                color    = parts[1].decode()
                avatar   = parts[2].decode()
                filename = parts[3].decode()
                filesize = int(parts[4].decode())
                file_data = parts[5]

                while len(file_data) < filesize:
                    file_data += client.recv(65536)

                download_dir = "received_files"
                os.makedirs(download_dir, exist_ok=True)
                save_path = os.path.join(download_dir, filename)
                with open(save_path, "wb") as f:
                    f.write(file_data)

                ext = filename.lower()
                if ext.endswith((".png", ".jpg", ".jpeg")):
                    window.after(0, lambda p=save_path, c=color, a=avatar:
                                 add_media(p, "image", "left", c, a))
                elif ext.endswith((".mp4", ".avi", ".mov")):
                    window.after(0, lambda p=save_path, c=color, a=avatar:
                                 add_media(p, "video", "left", c, a))
                else:
                    window.after(0, lambda fn=filename, p=save_path, c=color, a=avatar:
                                 add_file_button(fn, p, "left", c, a))

        except Exception as e:
            print("Receive error:", e)
            break

# ── Bottom input bar ──────────────────────────────────────────────────────────
input_frame = ctk.CTkFrame(window, fg_color="white", corner_radius=25, height=50)
input_frame.pack(fill="x", side="bottom", padx=20, pady=20)

file_btn = ctk.CTkButton(input_frame, text="+", width=40, corner_radius=20, command=send_file)
file_btn.pack(side="left", padx=5)

msg_entry = ctk.CTkEntry(input_frame, placeholder_text="Message...",
                          border_width=0, fg_color="transparent")
msg_entry.pack(side="left", fill="x", expand=True, padx=5)
msg_entry.bind("<Return>", lambda e: send_message())

send_btn = ctk.CTkButton(input_frame, text="➤", width=40, corner_radius=20, command=send_message)
send_btn.pack(side="right", padx=5)

threading.Thread(target=receive, daemon=True).start()
window.mainloop()