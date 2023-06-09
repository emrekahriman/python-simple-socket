import socket
import threading

HOST = 'localhost'
PORT = 12345
BUFFER_SIZE = 2048

username = input("Enter your username -> ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

client_socket.sendall(username.encode())

def receive_messages():
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode()
            print(message)
        except:
            client_socket.close()
            break

def send_message():
    try:
        while True:
            message = input()
            client_socket.sendall(message.encode())
    except:
        client_socket.close()
        exit()

receive_thread = threading.Thread(target=receive_messages)
send_thread = threading.Thread(target=send_message)

receive_thread.start()
send_thread.start()