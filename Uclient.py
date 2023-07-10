import socket
import threading
import random
from server_utils import TCP_CLIENT_PORT, UDP_CLIENT_PORT

host = '127.0.0.1'
# socket connection to UDP
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((host, random.randint(8000, 9000)))

# socket connection to TCP
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# client inputs name (ex. client-A)
clientID = input("")

# Receieves first incoming messages in UDP and once authentication is successful
# 2 functions are called to handle the messages in TCP
def receive():
    while True:
        try:
            message, address = udp_socket.recvfrom(1024)
            print(message.decode())

            if message.startswith(b'AUTH_SUCCESS'):
                # establish a TCP connection to the server's address and TCP port number
                #tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_socket.connect((host, TCP_CLIENT_PORT))

                # send a CONNECT message to the server over the TCP connection
                rand_cookie = random.randint(1, 1000000)
                tcp_socket.send(f'CONNECT {rand_cookie}'.encode('ascii'))
                tcp_socket.recv(1024).decode('ascii')

                # Starting Threads For Listening And Writing
                receive_thread = threading.Thread(target=receive_tcp, args=(tcp_socket,))
                receive_thread.start()

                write_thread = threading.Thread(target=write, args=(tcp_socket,))
                write_thread.start()
        except:
            tcp_socket.close()
            pass


# receive messages through tcp connection
def receive_tcp(tcp_socket: socket):
    while True:
        try:
            # receive message from server
            message = tcp_socket.recv(1024).decode('ascii') #For ID
            print(message)
        except:
            # Close Connection When Error
            print("An error occurred!")
            #tcp_socket.close()
            break


# Sending Messages through tcp connection
def write(tcp_socket: socket):
    while True:
        try:
            user_input = input()
            message = '{}: {}'.format(clientID, user_input)
            tcp_socket.send(message.encode('ascii'))
        except:
            break


# call receive() function
t = threading.Thread(target=receive)
t.start()

# udp formats input from user to send to server
udp_socket.sendto(f"HELLO ({clientID})".encode(), (host, UDP_CLIENT_PORT))
key = input("")
udp_socket.sendto(f"RESPONSE ({key})".encode(), (host, UDP_CLIENT_PORT))







