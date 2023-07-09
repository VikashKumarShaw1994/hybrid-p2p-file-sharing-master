

from sqlite3 import Time

from constants import *
import re
import struct
from pathlib import Path


class Client:

    def __init__(self, out_filename): 
        hostname=socket.gethostname()   
        IPAddr=socket.gethostbyname(hostname)  
        # set up socket
        self.server_connection_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # allow python to use recently closed socket
        self.server_connection_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # make the connection
        self.server_connection_soc.connect((HOST, PORT))

              


        dir_path = "client_data/"

        Path(dir_path).mkdir(parents=True, exist_ok=True)
        self.file_path = "client_data/" + IPAddr  + "_" + out_filename 

        print("File will be saved to:", self.file_path)


        server_thread = threading.Thread(target=self.server_listening_thread)
        server_thread.start()

        

        
    def server_listening_thread(self):

        while True:
            print("Listening for mesasge from server")
            msg = self.recieve_message(self.server_connection_soc,1)

            if not msg:
                # means the server has failed
                print("-" * 21 + " Server failed " + "-" * 21)
                break

            elif msg ==  b'\x13':
                print("Got message 13")
                self.receive_file(self.server_connection_soc)
                self.server_connection_soc.send(TRANSFER_COMPLETE)
                




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
 
        print("Transferpper")
        print(peers)
        
        self.s.send(peers)
        print("Sent")


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
    try :
        out_filename = "test.bin"
        if len(sys.argv) > 1:
            print("Usage: python script.py [argument]")
            out_filename = sys.argv[1]
        client = Client(out_filename)
    except KeyboardInterrupt as e:
        sys.exit(0)