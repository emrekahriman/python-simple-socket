import socket
import threading
import time
import keyboard
import re

HOST = 'localhost'
PORT = 12345
BUFFER_SIZE = 2048
MAX_CLIENTS = 3

clients = {}
active_users = []
server_start_time = time.time()

def is_valid_username(username):
    pattern = r'^[a-zA-Z0-9_]{4,20}$'
    if not re.match(pattern, username):
        return False
    return True

def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return "%d hours, %d minutes, %d seconds" % (hours, mins, secs)

def handle_client_connection(client_socket, client_address):
    while True:
        username = client_socket.recv(BUFFER_SIZE).decode().strip()

        if not is_valid_username(username):
            client_socket.sendall("Invalid username! Please try again.".encode())
            continue

        if username in clients:
            client_socket.sendall("This username is already taken! Please try again.".encode())
            continue

        clients[username] = client_socket
        active_users.append(username)

        client_socket.sendall(("[SYSTEM MSG] " + "Welcome, " + username + "!").encode())

        for user in active_users:
            if user != username:
                clients[user].sendall(("[SYSTEM MSG] " + username + " joined the chat room.").encode())

        summary = "There are " + str(len(active_users)) + " users in the chat room. The chat started " + humanize_time(time.time() - server_start_time) + " ago."
        client_socket.sendall(summary.encode())

        if len(active_users) > 1:
            try:
              client_socket.sendall("Would you like to greet the users in the chat room? (Y/N)".encode())
              answer = client_socket.recv(BUFFER_SIZE).decode().strip().lower()
              if answer == 'y' or answer == 'Y':
                  for user in active_users:
                      if user != username:
                          msg = username + ": Hi, i'm " + username + ". I just joined the chat room."
                          clients[user].sendall(msg.encode())
                          client_socket.sendall(("Greeting sent to " + str(len(active_users) - 1) + " users.").encode())
              else:
                  client_socket.sendall("Ok, no greeting sent.".encode())
            except:
              client_socket.close()
        break

    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode().strip()

            if message.startswith('@'):
                recipient_username = message[1:].split(' ', 1)[0]
                message = message[1:].split(' ', 1)[1] if len(message.split(' ', 1)) > 1 else ''

                if recipient_username == username:
                    client_socket.sendall(("You cannot send a private message to yourself.").encode())
                elif not message:
                    client_socket.sendall("Please enter a message to send a private message.".encode())
                elif recipient_username in clients:
                    clients[recipient_username].sendall(("[PRIVATE MSG] " + username + ": " + message).encode())
                else:
                    client_socket.sendall(("This user does not exist: " + recipient_username).encode())
            else:
                for user in active_users:
                    if user != username:
                        clients[user].sendall((username + ": " + message).encode())
        except:
            client_socket.close()
            del clients[username]
            active_users.remove(username)

            for user in active_users:
                clients[user].sendall(("[SYSTEM MSG] " + username + " left the chat room.").encode())
            break



server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(MAX_CLIENTS)

print("Chat room started. Host: " + HOST + ", Port: " + str(PORT))

while True:
    client_socket, client_address = server_socket.accept()

    if len(clients) >= MAX_CLIENTS:
        infomsg = "Sorry. This chat room is limited to '" + str(MAX_CLIENTS) + "' users"
        client_socket.send(infomsg.encode())
        time.sleep(0.05)
        client_socket.close()
        keyboard.press_and_release('enter')
        continue

    client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, client_address))
    client_thread.start()