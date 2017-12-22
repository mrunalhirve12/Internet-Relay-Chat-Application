# implementing 3-tier structure: ChatPool --> Room --> Clients; 

import select, socket, sys, pdb
from ChatBoxServices import ChatPool, Room, Member
import ChatBoxServices

READ_BUFFER = 5000                                                                      # declares READ_BUFFER size

host = sys.argv[1] if len(sys.argv) >= 2 else ''
listen_sock = ChatBoxServices.create_socket((host, ChatBoxServices.PORT))               #created socket with host address, and port

chatpool = ChatPool()                                                                   # craeted object for ChatPool class
connection_list = []                                                                    # to store connections 
connection_list.append(listen_sock)                                                     # add socket to connection list

while True:
    # Member.fileno()
    read_member, write_member, error_sockets = select.select(connection_list, [], [])   # waitable objects of read, write and error
    for member in read_member:                                                          # for all members in read member list do
        if member is listen_sock:                                                       # if new connection, member is a socket
            new_socket, add = member.accept()                                           # returns connection and address
            new_member = Member(new_socket)                                             # set connection to new_member
            connection_list.append(new_member)                                          # append to connection list	                                      
            chatpool.welcome_new(new_member)                                            # message to welcome new_member

        else:                                                                           # handle messages of member 
            msg = member.socket.recv(READ_BUFFER)
            if msg:
                msg = msg.decode().lower()
                chatpool.handle_msg(member, msg)                                        # check what service to provie depending upon the member input 
            else:                                                                       # if client does not send message
                member.socket.close()                                                   # close the socket
                connection_list.remove(member)                                          # removes member from the connection list

    for sock in error_sockets:                                      # closes error sockets object
        sock.close()
        connection_list.remove(sock)
