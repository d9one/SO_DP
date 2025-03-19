import queue
import socket
import threading

host = '127.0.0.1'
port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(5)

clients = {} #{client_socket: (nickname, room)}
rooms = {} #{room_name: [client_sockets]}
messages_que = queue.Queue() # fifo que for messages

def broadcast(room, message, sender_client=None): # broadcast message to all clients in the room
    with threading.Lock(): # mutex to lock the broadcast function
        for client in rooms.get(room, []):
            if client != sender_client:
                client.send(message.encode('ascii'))
                save_message(room, message)

def messages_handler(): # handle messages from the que
    while True:
        room, message, client = messages_que.get()
        broadcast(room, message, client)

def save_message(room, message): # save message to the chat history
    with threading.Lock():
        print(f"Saving message to {room}.txt: {message}")
        with open(f'./ChatArchives/{room}.txt', 'a', encoding="utf-8") as f:
            f.write(message + '\n')

def load_chat_history(room): # load chat history from the file
        try:
            with open(f'./ChatArchives/{room}.txt', 'r', encoding="utf-8") as f:
                return f.readlines()
        except FileNotFoundError:
            return ''

def handle_client(client): # handle client connection
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
            while True:
                try:
                    message = client.recv(1024).decode('ascii')
                    if message == 'quit':
                        break
                    messages_que.put((room, f'{nickname}: {message}', client))
                except (OSError, ConnectionResetError) as e:
                    print(f"Client connection error: {e}")
                    break

        except (ConnectionResetError, ConnectionAbortedError) as e:
            print(f"Client connection error: {e}")
        finally:
                disconnect_client(client)

def disconnect_client(client): # disconnect client from the server
    if client in clients:
        nickname, room = clients[client]
        rooms[room].remove(client)
        del clients[client]
        broadcast(room, f'{nickname} left room', client)
        print(f'{nickname} left the room: {room}')
    client.close()

def receive(): # accept client connections
    while True:
        try:
            client, _ = server.accept()
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
            server.close()
            break

print("Server started")
messages_handler_thread = threading.Thread(target=messages_handler, daemon=True)
messages_handler_thread.start()
receive()
