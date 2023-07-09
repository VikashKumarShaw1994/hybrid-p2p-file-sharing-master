
from constants import *
import time
import os
import struct

class Server:

    def __init__(self, input_filename, num_clients):
        try:
            self.input_filename =input_filename
            self.num_clients = num_clients            

            self.is_first_client = True
            # define a socket
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.connections = []
            self.connections2 = []

            # make a list of peers
            self.peers = []

            # bind the socket
            self.s.bind((HOST, PORT))

            # listen for connection
            self.s.listen(10)

            print("-" * 12 + "Server Running" + "-" * 21)

            self.run()
        except Exception as e:
            sys.exit()




    def disconnect(self, connection, a):
        self.connections.remove(connection)
        self.peers.remove(a)
        connection.close()
        self.send_peers()
        print("{}, disconnected".format(a))
        print("-" * 50)



    def run(self):
        # constantly listeen for connections
        # c_thread = threading.Thread(target=self.handler)
        # c_thread.daemon = True
        # c_thread.start()
        while True:
            connection, a = self.s.accept()
            print("accepted")
            self.connections.append((connection,a))
            

            self.num_clients -= 1

            if(self.num_clients == 0):
                
                self.start_time = time.time()
                for conn,a in self.connections:
                    print(a)
                    conn.send(UPLOAD_START)
                    print("sent upload starrt")
                    self.send_file(conn)
                    conn.recv(1)
                print("Total time:", time.time() - self.start_time)






    def send_file(self, connection):
        file_path = self.input_filename
        file_size = os.path.getsize(file_path)
        print("Sending size:",file_size)
        self.send_size(connection, file_size)

        remaining_bytes = file_size
        with open(file_path, 'rb') as file:
            remaining_bytes = file_size
            while remaining_bytes > 0:
                data = file.read(min(remaining_bytes, 1024))
                connection.sendall(data)
                remaining_bytes -= len(data)

 

    def send_size(self, connection, size):
        packed_size = struct.pack("!Q", size)
        connection.sendall(packed_size)


    def send_peers(self):
        peer_list = ""
        for peer in self.peers:
            peer_list = peer_list + str(peer[0]) + ","

        for connection in self.connections:
            # we add a byte '\x11' at the begning of the our byte
            # This way we can differentiate if we recieved a message or a a list of peers
            data = PEER_BYTE_DIFFERENTIATOR + bytes(peer_list, 'utf-8')
            connection.send(PEER_BYTE_DIFFERENTIATOR + bytes(peer_list, 'utf-8'))



if __name__ == "__main__":

    input_filename = "test.bin"
    num_clients = 10
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
        if len(sys.argv) > 2:
            num_clients = int(sys.argv[2])

    try :
        server = Server(input_filename,num_clients)
        
    except KeyboardInterrupt as e:
            sys.exit(0)