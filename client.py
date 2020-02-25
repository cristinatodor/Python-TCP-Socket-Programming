import socket
import sys
import time 

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_name = sys.argv[1]
server_port = int(sys.argv[2])
server_address = (server_name, server_port)
print('connecting to {} port {}'.format(*server_address))

#Attempt connection to the server
try:
    sock.connect(server_address)
    print('current client is', sock.getsockname())

    # Send data
    message = 'GET_BOARDS'
    print('sending {!r}'.format(message))
    sock.sendall(message.encode('utf-8'))

    # Look for the response
    data = sock.recv(4096).decode('utf-8')
    print('received {!r}'.format(data))

    print('\nEnter one of the messages: ')
    print('A board number to request a list of messages in that board;')
    print('POST to post a message;')
    print('QUIT to close the connection;\n')

    while True: 
        message2 = input("\nPlease enter your message: ")
        
        if message2 == 'QUIT':
            break

        else:
            if message2 == 'POST':
                message2 = ''
                board_number = input("Enter board number: ")
                message_title = input("Enter message title: ")
                message_content = input("Enter message: ")
                message2 = "POST_MESSAGE(Message_board_" + board_number + ", " + message_title + ", " + message_content + ")"

            print(message2)
            print('sending {!r}'.format(message2))
            sock.sendall(message2.encode('utf-8'))
            time1 = time.time()

            if time.time() - time1 > 10:
                print('Server did not respond in 10 seconds')
            else:
                data2 = sock.recv(4096).decode('utf-8')
                print('received {!r}'.format(data2))

        
except socket.error:
    print('Error: cannot connect to server')
    
finally:
    print('closing socket')
    sock.close()
