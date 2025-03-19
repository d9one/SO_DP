import socket
import threading
import sys

nickname = input("Choose a nickname: ")
room = input("Choose a room: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 9999))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if not message:
                break
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            elif message == 'ROOM':
                client.send(room.encode('ascii'))
            else:
                print(message)
        except:
            break

    client.close()
    sys.exit(0)

def write():
    while True:
        try:
            message = input("")
            if message.lower() == 'quit':
                client.send(message.encode('ascii'))
                client.close()
                break
            else:
                client.send(message.encode('ascii'))
        except:
            break

    print("You left the chat.")
    sys.exit(0)

receive_thread = threading.Thread(target=receive, daemon=True)
receive_thread.start()

write_thread = threading.Thread(target=write, daemon=True)
write_thread.start()

receive_thread.join()
write_thread.join()
