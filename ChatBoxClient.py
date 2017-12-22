import select, socket, sys
from ChatBoxServices import Room, ChatPool, Member
import ChatBoxServices

READ_BUFFER = 5000                                                          # declares size of buffer

if len(sys.argv) < 2:
    print("Usage: client.py [hostname]")
    sys.exit(1)                                                             # exits on error
else:
    server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # Create a new socket using the given address family, socket type and protocol number
    server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_connection.connect((sys.argv[1], ChatBoxServices.PORT))          #connect to ip address and port

def prompt():                                                               #to display next prompt on screen
   sys.stdout.write('< I >')
   sys.stdout.flush()
   
print("Connected Successfully To Server\n")                                 # connected to server
msg_prefix = ''

socket_list = [sys.stdin, server_connection]                                #inputs the list of server connection

while True:
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], []) # waitable objects of read, write and error for socket
    for rs in read_sockets:
        if rs is server_connection:                                                 # incoming message 
            msg = rs.recv(READ_BUFFER)                                              #if message is received in buffer
            if not msg:                                                             # if there is no message 
                print("Server is down.. Try later !")                               # print server down
                sys.exit(2)                                                         # exit
            else:
                if msg == ChatBoxServices.QUIT_STRING.encode():                     # if client quits
                    sys.stdout.write('Bye\n')
                    sys.exit(2)
                else:
                    sys.stdout.write(msg.decode())
                    if 'Please tell us your name' in msg.decode():
                        msg_prefix = 'name: '                                       # prefix for name
                    else:
                        msg_prefix = ''
                    prompt()

        else:
            msg = msg_prefix + sys.stdin.readline()                                
            server_connection.sendall(msg.encode())                                  #send msg to all
