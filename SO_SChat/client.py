import socket
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter.constants import RIGHT

client = None
nickname = ""
room = ""
shutdown_event = threading.Event()  # Event to signal shutdown

def start_client():
    global ip_entry, port_entry, client

    ip = ip_entry.get()
    port = port_entry.get()

    if not ip or not port:
        messagebox.showerror("Error", "Please enter ip and port")
        return

    port = int(port)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))
    root.withdraw()
    show_nickname_window()

def show_nickname_window():
    global nickname_entry, room_entry, nickname_window

    nickname_window = tk.Toplevel(root)
    nickname_window.title("Nickname and room")

    tk.Label(nickname_window, text="Nickname").grid(row=0, column=0)
    nickname_entry = tk.Entry(nickname_window)
    nickname_entry.grid(row=0, column=1)

    tk.Label(nickname_window, text="Room").grid(row=1, column=0)
    room_entry = tk.Entry(nickname_window)
    room_entry.grid(row=1, column=1)

    tk.Button(nickname_window, text="Join", command=join_chat).grid(row=2, column=0, columnspan=2, pady=10)

def join_chat():
    global nickname, room, nickname_window

    nickname = nickname_entry.get()
    room = room_entry.get()

    if not nickname or not room:
        messagebox.showerror("Error", "Please enter nickname and room")
        return

    nickname_window.destroy()
    show_chat_window()

    # Start the receive thread
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

def show_chat_window():
    global chat_box, message_entry

    chat_window = tk.Toplevel(root)
    chat_window.title("Chat")

    chat_box = scrolledtext.ScrolledText(chat_window, state=tk.DISABLED, wrap=tk.WORD)
    chat_box.pack(expand=True, fill="both")

    message_entry = tk.Entry(chat_window, width=40)
    message_entry.pack(side=tk.LEFT, padx=10, pady=5)
    message_entry.bind("<Return>", send_message)

    send_button = tk.Button(chat_window, text="Send", command=send_message)
    send_button.pack(side=tk.LEFT, padx=10, pady=5)

    disconnect_button = tk.Button(chat_window, text="Quit", command=disconnect)
    disconnect_button.pack(side=RIGHT, padx=10, pady=5)

root = tk.Tk()
root.title("Chat Client")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="IP:").grid(row=0, column=0)
ip_entry = tk.Entry(frame)
ip_entry.grid(row=0, column=1)
ip_entry.insert(0, "127.0.0.1")

tk.Label(frame, text="Port:").grid(row=1, column=0)
port_entry = tk.Entry(frame)
port_entry.grid(row=1, column=1)
port_entry.insert(0, "9999")

tk.Button(frame, text="Connect", command=start_client).grid(row=2, column=0, columnspan=2, pady=10)

def receive():
    client.settimeout(1) # Set a timeout for the socket
    while not shutdown_event.is_set():
        try:
            message = client.recv(1024).decode('ascii')
            if not message:
                break
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            elif message == 'ROOM':
                client.send(room.encode('ascii'))
            else:
                display_message(message)
        except socket.timeout:
            continue
        except (OSError, ConnectionResetError):
            break

    client.close()

def send_message(event=None):
    global client, message_entry

    message = message_entry.get()
    if message:
        try:
            client.send(message.encode('ascii'))
            message_entry.delete(0, tk.END)
            display_message(f"You: {message}")
        except:
            display_message("Cannot send message")

def display_message(message):
    chat_box.config(state="normal")
    chat_box.insert(tk.END, message + "\n")
    chat_box.yview(tk.END)
    chat_box.config(state="disabled")

def disconnect():
    global client
    shutdown_event.set()
    try:
        client.close()
    except:
        pass
    root.quit()

root.mainloop()