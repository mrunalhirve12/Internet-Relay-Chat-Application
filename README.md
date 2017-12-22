# Internet-Relay-Chat-Application
Developed in Python

1. ChatBoxServer.py : Listens and accepts connections from clients(members) 
2. ChatBoxClient.py : Makes connection to a server , Select and enter one of the choice from the options that available in the menu: a. List all rooms b. Join/Create/Switch a room c. Send personal message to a person d. Help (to show instructions or menu) e. Quit the ChatBox
3. ChatBoxServices.py : Has the implementation of a ChatBox , code for the various options that the server offers the client in the menu mentioned in step 2.

Steps for running a program: a.	Start server. (On linux/unix machine open terminal, reach through cd command till the file location and type the command : python ChatBoxServer.py )  b.	Start 1 client or multiple clients (from single terminal or different terminal using command : python ChatBoxClient.py 127.0.0.1 (ip address for localhost))  c.	Program will ask for name of client. d.	Enter the name e.	And then follow the instructions given in the menu and select your choice accordingly.
