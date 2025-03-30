import os
import queue
import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

clients = {}  #{client_socket: (nickname, room)}
rooms = {}  #{room_name: [client_sockets]}
messages_que = queue.Queue()  # fifo que for messages
server = None # server socket
shutdown_event = threading.Event()  # Event to signal shutdown

def start_server(): # start server
    global ip_entry, port_entry, server

    ip = ip_entry.get()
    port = port_entry.get()
    if not ip or not port:
        messagebox.showerror("Error", "Please enter ip and port")
        return
    try:
        port = int(port)
    except ValueError:
        messagebox.showerror("Error", "Invalid port")
        return
    def run_server():
        global server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ip, port))
        server.listen(5)
        print(f"Server started on {ip}:{port}")
        receive()
    threading.Thread(target=run_server, daemon=True).start()
    messagebox.showinfo("Server", "Server started")

def browse_chat_history(): # browse chat history
    folder_path = "./ChatArchives"
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)
    file_path = filedialog.askopenfilename(initialdir=folder_path, title="Select chat file",
                                           filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))

    if file_path:
        with open(file_path, "r") as file:
            chat_history = file.read()
        chat_window = tk.Toplevel(root)
        chat_window.title("Chat")
        text_area = tk.Text(chat_window, wrap="word")
        text_area.insert("1.0", chat_history)
        text_area.pack(expand=True, fill="both")


def delete_chat_room(): # delete chat room
    folder_path = "./ChatArchives"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = filedialog.askopenfilename(initialdir=folder_path, title="Select room to delete",
                                           filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    if file_path:
        os.remove(file_path)
        messagebox.showinfo("Success", "Chat room deleted successfully!")

def close_server(): # close server
    global server
    shutdown_event.set()
    if server:
        server.close()
    messagebox.showinfo("Server", "Server closed")


root = tk.Tk()
root.title("Server")

frame = tk.Frame(root)
frame.pack(padx=5, pady=5)

tk.Label(frame, text="IP:").grid(row=0, column=0, sticky=tk.W)
ip_entry = tk.Entry(frame)
ip_entry.grid(row=0, column=1)
ip_entry.insert(0, "127.0.0.1")

tk.Label(frame, text="Port:").grid(row=1, column=0, sticky=tk.W)
port_entry = tk.Entry(frame)
port_entry.grid(row=1, column=1)
port_entry.insert(0, "9999")

tk.Button(frame, text="Start Server", command=start_server).grid(row=2, column=0, columnspan=2, pady=5)
tk.Button(frame, text="View Chat History", command=browse_chat_history).grid(row=3, column=0, columnspan=2, pady=5)
tk.Button(frame, text="Delete Chat Room", command=delete_chat_room).grid(row=4, column=0, columnspan=2, pady=5)
tk.Button(frame, text="Close Server", command=close_server).grid(row=5, column=0, columnspan=2, pady=5)


def broadcast(room, message, sender_client=None):  # broadcast message to all clients in the room
    with threading.Lock():  # mutex to lock the broadcast function
        for client in rooms.get(room, []):
            if client != sender_client:
                client.send(message.encode('ascii'))
                save_message(room, message)


def messages_handler():  # handle messages from the que
    while not shutdown_event.is_set():
        try:
            room, message, client = messages_que.get(timeout=1)
            broadcast(room, message, client)
        except queue.Empty:
            continue


def save_message(room, message):  # save message to the chat history
    with threading.Lock():
        print(f"Saving message to {room}.txt: {message}")
        with open(f'./ChatArchives/{room}.txt', 'a', encoding="utf-8") as f:
            f.write(message + '\n')


def load_chat_history(room):  # load chat history from the file
    try:
        with open(f'./ChatArchives/{room}.txt', 'r', encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        return ''


def handle_client(client):  # handle client connection
    while True:
        try:
            # get client nickname
            try:
                client.send('NICK'.encode('ascii'))
                nickname = client.recv(1024).decode('ascii')
                if not nickname:
                    client.close()
                    return
            except (OSError, ConnectionResetError) as e:
                print(f"Error while getting nickname: {e}")
                break

            # get client room
            try:
                client.send('ROOM'.encode('ascii'))
                room = client.recv(1024).decode('ascii')
                if not room:
                    client.close()
                    return
            except (OSError, ConnectionResetError) as e:
                print(f"Error while getting room: {e}")
                break

            # add client to dictionary
            clients[client] = (nickname, room)
            if room not in rooms:
                rooms[room] = []
            rooms[room].append(client)

            # load chat history
            history = load_chat_history(room)
            for line in history:
                try:
                    client.send(line.encode('ascii'))
                except (OSError, ConnectionResetError) as e:
                    print(f"Error while sending chat history: {e}")
                    break

            # send messages to the room and client
            print(f'{nickname} joined room: {room}')
            broadcast(room, f'{nickname} joined room: {room}', client)
            try:
                client.send(f'Connected to the room: {room}'.encode('ascii'))
            except (OSError, ConnectionResetError) as e:
                print(f"Error while sending connected message: {e}")
                break

            # receive messages from the client and manage them
            while not shutdown_event.is_set():
                try:
                    message = client.recv(1024).decode('ascii')
                    if not message:
                        break
                    messages_que.put((room, f'{nickname}: {message}', client))
                except socket.error:
                    break
        finally:
            disconnect_client(client)


def disconnect_client(client):  # disconnect client from the server
    if client in clients:
        nickname, room = clients[client]
        rooms[room].remove(client)
        del clients[client]
        broadcast(room, f'{nickname} left room', client)
        print(f'{nickname} left the room: {room}')
    client.close()


def receive():  # accept client connections
    while not shutdown_event.is_set():
        try:
            client, _ = server.accept()
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
        except socket.error:
            break


messages_handler_thread = threading.Thread(target=messages_handler, daemon=True)
messages_handler_thread.start()
root.mainloop()
