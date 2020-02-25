import socket
import sys
from datetime import datetime
import os
import glob
import _thread

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

path = os.getcwd()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_name = sys.argv[1]
server_port = int(sys.argv[2])
server_address = (server_name, server_port)
print('starting up on {} port {}'.format(*server_address))

#Function for checking if the port is already in use
def is_port_in_use(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return s.connect_ex(('localhost', port)) == 0

#Function to start new thread for each client connection
def on_new_client(connection,client_address):
        try:
            #Connect to client and write to log file
            print('connection from', client_address)
            os.chdir(path)
            with open("server.log","a") as f:
                f.write(client_address[0] + ":" + str(client_address[1]) + "\t")
                f.write(dt_string + "\n")
            
            # Receive the data and transmit response
            while True:
                data = connection.recv(64).decode('utf-8')
				
                print('received {!r}'.format(data))

                if data:
                    print('sending data back to the client')
                    work_data(data, connection)                               
                else:
                    print('no data from', client_address)
                    break
                

        finally:
            # Clean up the connection
            connection.close()


#Function for data
def work_data(data, connection):
    #GET_BOARDS message is received 
    if data.startswith('GET_BOARDS'):
        os.chdir(path)
        with open("server.log","a") as f:
            f.write(client_address[0] + ":" + str(client_address[1]) + "\t")
            f.write(dt_string + "\t")
            f.write(data + "\t")
        
        os.chdir(path + "/board")
        content = glob.glob('Message_board_*')

        #Check whether there are any message boards 
        if not content:
            connection.sendall('Error: no message boards defined'.encode('utf-8'))
            os.chdir(path)
            with open("server.log","a") as f:
                f.write("Error \n") 
        else:
            os.chdir(path)
            with open("server.log","a") as f:
                f.write("OK \n")
            content.sort()
                            
            folders = ""
            i = 1
            for el in content:
                folders += str(i) + ". " + el + "; " 
                i += 1 
                                
            connection.sendall(folders.encode('utf-8')) #send the list of message boards to client


    #GET_MESSAGES message is received     
    elif data.isdigit():
        with open("server.log","a") as f:
            os.chdir(path)
            f.write(client_address[0] + ":" + str(client_address[1]) + "\t")
            f.write(dt_string + "\t")
            f.write("GET_MESSAGES(" + data + ") \t")
                       
        board_title = data 

        os.chdir(path + "/board")
                        
        #Check whether the board title is transmitted as parameter
        if not board_title:
            connection.sendall('No message board specified'.encode('utf-8'))
            os.chdir(path)
            with open("server.log","a") as f:
                f.write("Error \n") 
        else:
            #Check whether the given board exists
            if os.path.isdir('./' + "Message_board_" + board_title):
                os.chdir(path)
                with open("server.log","a") as f:
                    f.write("OK \n")

                os.chdir(path + "/board")
                os.chdir(os.getcwd() + '/' + "Message_board_" + board_title)
                                
                message_titles = os.listdir(os.curdir)
                #Check whether there are any messages in the given board
                if not message_titles:
                    connection.sendall('Empty board'.encode('utf-8'))
                    os.chdir(path)
                else:
                    message_titles.sort(reverse=True)
                    del message_titles[100:] #send the list of the 100 most recent messages  
                                    
                    content = ""
                    for element in message_titles:
                        if element.endswith('.txt'):
                            content += element + ': '
                            f2 = open(element, "r") #read message from file
                            content += f2.read() + '; ' 
                            f2.close()
                                                        
                    connection.sendall(content.encode('utf-8')) #send the messages from the specified board to client 
                    os.chdir(path)
            
            else:
                connection.sendall('No such board'.encode('utf-8'))
                os.chdir(path)
                with open("server.log","a") as f:
                    f.write("Error \n")
                
                
    #POST_MESSAGE message is received  
    elif data.startswith('POST_MESSAGE'):
        os.chdir(path)
        with open("server.log","a") as f:
            f.write(client_address[0] + ":" + str(client_address[1]) + "\t")
            f.write(dt_string + "\t")
            f.write(data + "\t")

        os.chdir(path + "/board")

        parameters = data.replace('POST_MESSAGE(', '')
        parameters = parameters.replace(')', '')
        parameters = parameters.split(', ')

        #Check whether enough parameters were specified 
        if len(parameters) != 3:
            connection.sendall('Not enough parameters specified'.encode('utf-8'))
            os.chdir(path)
            with open("server.log","a") as f:
                f.write("Error \n") 
        else:
            board_title = parameters[0]
            post_title = parameters[1]
            message_content = parameters[2]

            #Check whether the given board exists
            if os.path.isdir('./' + board_title):
                os.chdir(os.getcwd() + '/' + board_title)

                now = datetime.now()
                dt_string2 = now.strftime("%Y%m%d-%H%M%S")

                f2 = open(dt_string2 + "-" + post_title + ".txt","w+")
                with open(dt_string2 + "-" + post_title + ".txt","w+") as f2:
                    f2.write(message_content)
                f2.close()

                connection.sendall('Message posted'.encode('utf-8'))
                os.chdir(path)
                with open("server.log","a") as f:
                    f.write("OK \n")

            else:
                connection.sendall('No such board'.encode('utf-8'))
                os.chdir(path)
                with open("server.log","a") as f:
                    f.write("Error \n")
            

        
    #UNKNOWN message is received  
    else:
        connection.sendall('Unknown Message'.encode('utf-8'))
        os.chdir(path)
        with open("server.log","a") as f:
            f.write(client_address[0] + ":" + str(client_address[1]) + "\t")
            f.write(dt_string + "\t")
            f.write(data + "\t")
            f.write("Error \n") 

					

if not is_port_in_use(server_port):
    sock.bind(server_address)
    
    os.chdir(path)
    with open("server.log","a") as f:
        f.write("\n Server started \t" + dt_string + "\n")

    # Listen for incoming connections
    sock.listen(1)

    while True:
        # Wait for a connection
        print('waiting for a connection')
        connection, client_address = sock.accept()

        _thread.start_new_thread(on_new_client,(connection,client_address))
                   
else:
   print('Error: port already in use')

f.close()
sock.close()

