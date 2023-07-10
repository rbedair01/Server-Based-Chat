import socket
import random
import queue
import threading

from subscribers import SUBSCRIBERS
from server_utils import TCP_CLIENT_PORT, UDP_CLIENT_PORT

# define local host
host = '127.0.0.1'  # localhost

# define the UDP and TCP ports
udp_port = UDP_CLIENT_PORT
tcp_port = TCP_CLIENT_PORT

# binding UDP socket to UDP port
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((host, udp_port))



# UDP Transport for protocol messages
protocol = queue.Queue()

# All connected clients
clients = []
clients_tcp = []

# broadcasts messages to each of the clients
def broadcast_tcp(msg):
    for client in clients_tcp:
        try:
            client.send(msg)
        except:
            clients.remove(client)

def handle_messages(tcp_connection: socket):
    while True:
        try:
            # messages are received into the server and sent to the broadcast_tcp to send to all clients
            msg = tcp_connection.recv(1024)
            print('Received', msg) #DEBUG STATEMENT

            broadcast_tcp(msg)
        except:
            clients.remove(tcp_connection)
            tcp_connection.close()
            break

# first messages received through UDP connection
# using a queue to hold messages correctly
def receive():
    while True:
        try:
            message, address = udp_socket.recvfrom(1024)
            protocol.put((message, address))
        except:
            pass


def broadcast():
    # tcp connection defined
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((host, tcp_port))
    tcp_socket.listen()


    while True:
        while not protocol.empty():
            # messages received from udp
            message, address = protocol.get()
            print(message.decode())

            # appending address to client list to follow correct clients through UDP connection
            if address not in clients:
                clients.append(address)

            # verify authentication of client, if correct client is allowed access to TCP connection to chat
            for client in clients:
                try:
                    if message.decode().startswith("HELLO "):
                        # receiveing clientID
                        clientID = message.decode().partition(' ')[2]
                        clientID = clientID[1:-1]

                        # verify clientID is in list of subscribers
                        if clientID in SUBSCRIBERS:
                            # generate a random challenge and send it to the client
                            challenge = random.randint(1, 1000000)
                            udp_socket.sendto(f'CHALLENGE {challenge}'.encode(), address)

                            # wait for the client's response to the challenge (Secret key)
                            message, address = protocol.get()
                            entered_key = message.decode()
                            print(entered_key)
                            key = entered_key.partition(' ')[2]
                            key = key[1:-1]

                            # if secret key is valid
                            if key == SUBSCRIBERS[clientID]:
                                # encryption key for TCP connection
                                encryption_key = f'CK-{clientID}'

                                # send suthentication success to client
                                rand_cookie = random.randint(1, 1000000)
                                encrypted_message = f'AUTH_SUCCESS {rand_cookie}, {tcp_port}'.encode()
                                udp_socket.sendto(encrypted_message, address)

                                # loop used to handle TCP chat after successful authentication
                                while True:
                                    try:
                                        print('after authentication') # DEBUG STATEMENT

                                        # tcp connection accepted
                                        tcp_connection, addr = tcp_socket.accept()
                                        # appending client to list of clients in the tcp connection
                                        clients_tcp.append(tcp_connection)

                                        print('tcp accepted connection') # DEBUG STATEMENT

                                        try:
                                            tcp_connection.recv(1024).decode('ascii')
                                            tcp_connection.send('CONNECTED'.encode('ascii'))
                                            print('after CONNECTED message') # DEBUG STATEMENT

                                            # handle messages between clients
                                            thread = threading.Thread(target=handle_messages, args=(tcp_connection,))
                                            thread.start()
                                        except:
                                            tcp_connection.close()
                                        break
                                    except:
                                        break
                            else:
                                udp_socket.sendto("AUTH_FAIL".encode(), address)
                                continue
                        else:
                            # not in subscriber list
                            pass
                    else:
                        if message.decode().startswith("RESPONSE "):
                            continue
                        else:
                            udp_socket.sendto(message, address)
                            """tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            tcp_socket.bind((host, tcp_port))
                            tcp_socket.listen()

                            tcp_connection, addr = tcp_socket.accept()
                            thread = threading.Thread(target=receive_tcp, args=(tcp_connection,))
                            thread.start()"""
                except:
                    clients.remove(client)
                    #udp_socket.close()
                    break

def main():
    print('Server is live...')

    # Defining TCP socket
    t1 = threading.Thread(target=receive)
    t2 = threading.Thread(target=broadcast)

    t1.start()
    t2.start()



if __name__ == '__main__':
    main()


