# implementing 3-tier structure: ChatPool --> Room --> Clients; 

import socket, pdb

MAX_CLIENTS = 25                                                    # declares number of clients that can connect to the chat box
PORT = 22223                                                        # declares PORT NUMBER
QUIT_STRING = '<$quit$>'                                            # declares QUIT_STRING


def create_socket(address):
    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    cs.setblocking(0)
    cs.bind(address)                                              # bind socket to address
    cs.listen(MAX_CLIENTS)                                        # enables server to listen to client connections 
    print("Now listening at ", address)
    return cs

class ChatPool:
    def __init__(self):
        self.rooms = {} # {room_name: Room}                       # initialize rooms
        self.room_member_map = {} # {pmemberName: roomName}       # initialize rooom_member_map (contains mapping of room to member) 
        self.members_map = {} #{membername : member}

    def welcome_new(self, new_member):
        new_member.socket.sendall(b'Welcome to ChatBox .\nPlease tell us your name:\n')  # sends msg to the new member


    def list_rooms(self, member):
        
        if len(self.rooms) == 0:
            msg = 'No active rooms currently. Create your own!\n' \
                + 'Use [<join> room_name] to create a room.\n'          # displays a msg for no active rooms, and asks member to create/join the room 
            member.socket.sendall(msg.encode())                         # sends above msg to the member
        else:
            msg = 'Listing current rooms available ...\n'
            for room in self.rooms:
                if 'personal' not in room:
                    print (self.rooms[room].members)
                    msg += room + ": " + str(len(self.rooms[room].members)) + " member(s)\n"
            for member1 in self.rooms[room].members:
                msg += member1.name +"\n"
            member.socket.sendall(msg.encode())                                           # sends above msg to the member
    
    def handle_msg(self, member, msg):
        
        instructions = b'Instructions:\n'\
            + b'[<list>] to list all rooms\n'\
            + b'[<join> room_name] to join/create/switch to a room\n' \
            + b'[<personal> member_name] to chat personally\n'\
            + b'[<help>] to show instructions\n' \
            + b'[<quit>] to quit\n' \
            + b' Type!' \
            + b'\n'

        print(member.name + " says: " + msg)
        if "name:" in msg:
            name = msg.split()[1]
            member.name = name
            print("New connection from:", member.name)
            self.members_map[member.name]=member
            member.socket.sendall(instructions)

        elif "<join>" in msg:
            same_room = False                                                           # initialize the flag to state that it is not in same room
            if len(msg.split()) >= 2: # error check
                room_name = msg.split()[1]
                member.currentroomname = room_name
                if member.name+"-"+room_name in self.room_member_map:                   # if player already in room
                    if self.room_member_map[member.name+"-"+room_name] == room_name:
                        member.socket.sendall(b'You are already in room: ' + room_name.encode())
                        same_room = True                                                # initialize the flag to state that it is in same room
                    else: 
                        old_room = self.room_member_map[member.name+"-"+room_name]                          
                        
                if not same_room:                                                       # if not in same room, add/switch 
                    if not room_name in self.rooms:                                     # if new room
                        new_room = Room(room_name)                                    
                        self.rooms[room_name] = new_room
                    
                    self.rooms[room_name].members.append(member)                        # appends member to  room
                    self.rooms[room_name].welcome_new(member)                           # welcome msg
                    self.room_member_map[member.name+"-"+room_name] = room_name         # maps the room with member 
                    
                     
            else:
                member.socket.sendall(instructions)                                     # else send instructions to member

        elif "<list>" in msg:                                                           # lists all rooms
            self.list_rooms(member) 

        elif "<help>" in msg:
            member.socket.sendall(instructions)                                         # displays instructions for guiding member
        
        elif "<quit>" in msg:       
            member.socket.sendall(QUIT_STRING.encode())                                  
            self.remove_member(member)                                                  # quits and remove member

        elif "<personal>" in msg:                                                       # for sending personal messages
	    if len(msg.split()) >= 2:
		    membername = msg.split()[1]
		    if membername in self.members_map:                                          #if member has first been in chat room
			    newmember = self.members_map[membername]
			    personal_room = Room("personal-"+member.name+"-"+membername)
			    self.rooms["personal-"+member.name+"-"+membername] = personal_room
			    self.rooms["personal-"+member.name+"-"+membername].members.append(member)
			    self.rooms["personal-"+member.name+"-"+membername].members.append(newmember)
			    self.room_member_map[member.name+"-"+"personal-"+member.name+"-"+membername] = "personal-"+member.name+"-"+membername
			    self.room_member_map[membername+"-"+"personal-"+member.name+"-"+membername] = "personal-"+member.name+"-"+membername
			    member.currentroomname = "personal-"+member.name+"-"+membername
			    newmember.currentroomname = "personal-"+member.name+"-"+membername
		    else:
			msg = "Entered member does not exsist!!"
			member.socket.sendall(msg.encode())
	    else:
		    member.socket.sendall(instructions)
		
	elif not msg:
	    self.remove_member(member)

        else:
            # check if in a room or not first
            if member.name+"-"+member.currentroomname in self.room_member_map:
                self.rooms[self.room_member_map[member.name+"-"+member.currentroomname]].broadcast(member, msg.encode())
            else:
                msg = 'You are currently not in any room! \n' \
                    + 'Use [<list>] to see available rooms! \n' \
                    + 'Use [<join> room_name] to join a room! \n'
                member.socket.sendall(msg.encode())
    
    def remove_member(self, member):
        if member.name +"-"+member.currentroomname in self.room_member_map:
            self.rooms[self.room_member_map[member.name+"-"+member.currentroomname]].remove_member(member)
            del self.room_member_map[member.name+"-"+member.currentroomname]
        print("Member: " + member.name + " has left the room \n")

    
class Room:
    def __init__(self, name):                                                   
        self.members = []                                                       # a list of sockets
        self.name = name                                                        # initialize name field with the name entered by member

    def welcome_new(self, from_member):                                         # to welcome new member
        msg = self.name + " Welcome: " + from_member.name + '\n'
        for member in self.members:
            member.socket.sendall(msg.encode())
    
    def broadcast(self, from_member, msg):                                      # to broadcast to all members of room 
        msg = from_member.name.encode() + b":" + msg
        for member in self.members:
            member.socket.sendall(msg)

    def remove_member(self, member):                                            # removes member from socket
        self.members.remove(member)
        leave_msg = member.name.encode() + b" has left\n"
        self.broadcast(member, leave_msg)

class Member:                                                                   # class for socket
    def __init__(self, socket, name = "new" , currentroomname="new"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name
        self.currentroomname=currentroomname

    def fileno(self):                                                           # assigns file descriptor to socket
        return self.socket.fileno()
