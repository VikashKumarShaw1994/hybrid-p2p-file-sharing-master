
from sqlite3 import Time

from constants import *
import re
import struct
from pathlib import Path
import os


class Client:

    def __init__(self, addr, out_filename): 
        hostname=socket.gethostname()   
        IPAddr=socket.gethostbyname(hostname)  
        # set up socket
        self.server_connection_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # allow python to use recently closed socket
        self.server_connection_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # make the connection
        self.server_connection_soc.connect((HOST, PORT))

        self.self_server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.self_server_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.self_server_soc.bind((IPAddr,0))
        self.self_server_soc.listen(10)
        print("Client listening on port", self.self_server_soc.getsockname()[1])

        init_msg = str( (IPAddr, self.self_server_soc.getsockname()[1])).encode("utf-8")
        #TODO: send after receive while loop is written        


        dir_path = "client_data/"

        Path(dir_path).mkdir(parents=True, exist_ok=True)
        self.file_path = "client_data/" + str(self.self_server_soc.getsockname()[1])  + "_" + out_filename 

        print("File will be saved to:", self.file_path)


        server_thread = threading.Thread(target=self.server_listening_thread)
        server_thread.start()
        self.server_connection_soc.send(init_msg)

        peer_thread = threading.Thread(target=self.listening_thread, args=(self.self_server_soc,))
        peer_thread.start()



        


    def listening_thread(self, listening_socket):
        try :
            peer_socket,a =  listening_socket.accept()
            print("peer incoming connection accepted")
            msg = self.recieve_message(peer_socket, 1)
            print("Upload start from from peer message:",msg)
            self.receive_file(peer_socket)
            self.server_connection_soc.send(TRANSFER_COMPLETE)
        except ConnectionError as e:
            # Handle connection error or closure
            print("Exiting")

        return

        

        
    def server_listening_thread(self):

        while True:
            print("Listening for mesasge from server")
            msg = self.recieve_message(self.server_connection_soc,1)

            if not msg:
                # means the server has failed
                print("-" * 21 + " Server Disconnected " + "-" * 21)
                self.self_server_soc.close()
                break

            elif msg ==  b'\x13':
                print("Got message 13")
                self.receive_file(self.server_connection_soc)
                self.server_connection_soc.send(TRANSFER_COMPLETE)

            elif msg == b'\x12':
                print("Got 12")
                    
                conn_str = self.recieve_message(self.server_connection_soc,BYTE_SIZE).decode("utf-8")
                peer_conn_details = conn_str.strip("()").split(",") 
                peer_conn_ip = peer_conn_details[0][1:-1]
                peer_conn_port = int(peer_conn_details[1])

                print("Received peer con details:", peer_conn_ip)

                peer_send_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # allow python to use recently closed socket
                peer_send_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # make the connection
                peer_send_soc.connect((peer_conn_ip,peer_conn_port))
                print("Peer Connection made")
                
                peer_send_soc.send(UPLOAD_START)
                self.send_file(peer_send_soc)
                peer_send_soc.close()



    def send_size(self, connection, size):
        packed_size = struct.pack("!Q", size)
        connection.sendall(packed_size)
    def send_file(self, connection):
        
        file_size = os.path.getsize( self.file_path)
        self.send_size(connection, file_size)

        remaining_bytes = file_size
        print("starting to send file to peer")
        with open( self.file_path, 'rb') as file:
            remaining_bytes = file_size
            while remaining_bytes > 0:
                data = file.read(min(remaining_bytes, 1024))
                connection.sendall(data)
                remaining_bytes -= len(data)


    def transfer_to_peer(self, ip, port):
        self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # allow python to use recently closed socket
        self.peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # make the connection
        self.peer_socket.connect((ip, port))



    """
        This thread will deal with printing the recieved message
    """

    def receive_file(self, conn):
        file_size = self.receive_size(conn)
                
        with open(self.file_path, 'wb') as file:
            remaining_bytes = file_size
            while remaining_bytes > 0:
                data = conn.recv(min(remaining_bytes, 1024))
                file.write(data)
                remaining_bytes -= len(data)


    def receive_size(self, conn):
        packed_size = conn.recv(struct.calcsize("!Q"))
        file_size = struct.unpack("!Q", packed_size)[0]
        print("received file size:", file_size)
        return file_size

    def recieve_message(self, connection, size):
        try:
            print("Recieving -------")
            data = connection.recv(size)
            print(str(size) + "\nRecieved flag on the client side is:")
            print(data)

            return data
        except KeyboardInterrupt:
            self.send_disconnect_signal()

    """
        This method updates the list of peers
    """

    def update_peers(self, peers):
        import p2p
        # our peers list would lool like 127.0.0.1, 192.168.1.1,
        # we do -1 to remove the last value which would be None
        p2p.peers = str(peers, "utf-8").split(',')[:-1]

    def transfer_peers(self, peers):
        import p2p
        # our peers list would lool like 127.0.0.1, 192.168.1.1,
        # we do -1 to remove the last value which would be None
        # Time.sleep(100)
        ####Laksh You code goes here Response aise hi rakhna

        print("Transferpper")
        print(peers)
        
        self.s.send(peers)
        print("Sent")

    """
        This method is used to send the message
        :param: msg -> The optional message to send 
    """

    def send_message(self):
        try:


            req_string = REQUEST_STRING
            self_ip = self.s.getsockname()[0]
            self_port = self.s.getsockname()[1]

            req_string += "|" + self_ip + "|"+ str(self_port)

            req_string = req_string.encode('utf-8')
            print ("sending req_string:",req_string)
            self.s.send(req_string)




        except KeyboardInterrupt as e:
            # If a user turns the server off due to KeyboardInterrupt
            self.send_disconnect_signal()
            return

    def send_disconnect_signal(self):
        print("Disconnected from server")
        # signal the server that the connection has closed
        self.s.send("q".encode('utf-8'))
        sys.exit()

    def handle_incoming_connection(self):
        server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # allow python to use recently closed socket
        server_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


        server_soc.bind((HOST, 0))
        # make the connection

        while True:
            data = self.recieve_message(self.s,1)


        


if __name__ == "__main__":
    server_ip = '127.0.0.1'
    try :
        out_filename = "test.bin"
        if len(sys.argv) > 1:
            print("Usage: python script.py [argument]")
            out_filename = sys.argv[1]
        client = Client(server_ip,out_filename)
    except KeyboardInterrupt as e:
        sys.exit(0)