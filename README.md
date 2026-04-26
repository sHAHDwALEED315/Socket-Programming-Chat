# 💬 Real-Time Chat Application
> A lightweight, full-duplex chat app built from scratch in Python — supports text messaging and file sharing across multiple clients.

---

## 📌 Overview

This project is a **real-time multi-client chat application** built entirely in Python. It uses raw TCP sockets for networking, allowing multiple users to connect to a central server and exchange messages and files simultaneously — with no external networking frameworks involved.

The server acts as a **broadcast hub**: every message or file sent by one client is instantly forwarded to all other connected clients. The client side features a clean, modern GUI with chat bubbles, file previews, and media thumbnails.

---

## ✨ Features

- 🔁 **Full-duplex communication** — send and receive simultaneously with no blocking
- 👥 **Multi-client support** — multiple users can connect at the same time
- 💬 **Real-time text messaging** — messages delivered instantly across all clients
- 📁 **File sharing** — send images, videos, audio, and documents
- 🖼️ **Media previews** — images and video thumbnails rendered inline in the chat
- 🎵 **Audio file support** — audio files displayed with a dedicated button
- 🎨 **Modern GUI** — clean chat bubble interface with light theme

---

## 🛠️ Technologies & Skills

### 🔌 Socket Programming (TCP/IP)
The core of the project. Built using Python's built-in `socket` library with:
- **`AF_INET`** — IPv4 addressing
- **`SOCK_STREAM`** — TCP protocol, ensuring reliable and ordered data delivery
- Manual implementation of a **custom binary protocol** using prefixes (`MSG:` for text, `FILE|name|size|` for files) to distinguish message types at the receiver side

### 🧵 Multithreading
Each connected client is handled in its **own dedicated thread** using Python's `threading` library. This enables:
- The server to handle multiple clients concurrently without blocking
- The client to receive incoming messages in the background while the GUI stays responsive
- `daemon=True` threads that shut down cleanly when the app closes

### 🖥️ GUI Development (customtkinter + tkinter)
The client GUI is built with `customtkinter`, a modern wrapper around Python's `tkinter`:
- Dynamic **chat bubbles** aligned left/right based on message direction
- `CTkScrollableFrame` for an auto-scrolling chat window
- File picker via `tkinter.filedialog`
- Event binding (e.g. `<Return>` key to send messages)

### 🖼️ Media Handling
- **Pillow (PIL)** — opens and resizes images for inline display
- **OpenCV (cv2)** — extracts the first frame of video files to generate thumbnails

### 📡 Custom Application Protocol
Rather than using a high-level messaging library, a lightweight protocol was designed from scratch:
```
Text message  →  MSG:<content>
File transfer →  FILE|<filename>|<filesize>|<raw bytes>
```
The receiver inspects the prefix of each incoming byte stream to determine how to handle it — a pattern similar to how real-world protocols (HTTP, FTP) work.

---

## 📂 Project Structure

```
chat-app/
│
├── server.py        # TCP server — accepts connections, broadcasts messages
└── client.py        # GUI client — send/receive messages and files
```

---

## 🚀 How to Run

**1. Install dependencies**
```bash
pip install customtkinter pillow opencv-python
```

**2. Start the server**
```bash
python server.py
```

**3. Launch one or more clients** (each in a separate terminal)
```bash
python client.py
```

> Make sure the server is running before launching any client.

---

## 🧠 Key Concepts Demonstrated

| Concept | Where Applied |
|---|---|
| TCP socket programming | `server.py` — `socket.bind()`, `accept()`, `recv()`, `send()` |
| Concurrent server design | `server.py` — one thread per client via `threading.Thread` |
| Full-duplex communication | `client.py` — background `receive()` thread + GUI send |
| Binary data handling | File transfer — reading/sending raw bytes in chunks |
| Custom protocol design | `MSG:` / `FILE|` prefix system |
| GUI event loop | `client.py` — `mainloop()`, widget binding, dynamic layout |
| Media processing | Image resizing with PIL, video thumbnail with OpenCV |

---

## 📦 Dependencies

| Library | Purpose |
|---|---|
| `socket` | TCP networking (built-in) |
| `threading` | Concurrent client handling (built-in) |
| `tkinter` | Base GUI framework (built-in) |
| `customtkinter` | Modern GUI styling |
| `Pillow` | Image loading and resizing |
| `opencv-python` | Video thumbnail extraction |

---

*Built with Python 3.x*
