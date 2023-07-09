from constants import *
import os 
import struct
import queue
import time



class Server:
    master={}
    def __init__(self, input_filename, num_clients):
        try:
            self.num_clients = num_clients
            self.is_first_client = True
            hostname=socket.gethostname()   
            IPAddr=socket.gethostbyname(hostname) 
            print("Your Computer Name is:"+hostname)   
            print("Your Computer IP Address is:"+IPAddr)   

            # the message to upload in bytes
            self.input_filename = input_filename
            # define a socket
            self.server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.connections = []
            self.connect_peer = {}

            # make a list of peers
            self.peers = []

            # bind the socket
            self.server_soc.bind((HOST, PORT))

            # listen for connection
            self.server_soc.listen(10)

            self.producer_pool = queue.Queue()
            self.producer_pool.put((HOST,PORT))
            
            self.ip_conn_dict = {}

            print("-" * 12 + "Server Running" + "-" * 21)
            print("server bound to socket:",self.server_soc.getsockname()[1])

            self.run()
        except Exception as e:
            sys.exit()


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

    def disconnect(self, connection, a):
        self.connections.remove(connection)
        self.peers.remove(a)
        connection.close()
        self.send_peers()
        print("{}, disconnected".format(a))
        print("-" * 50)

    """
        This method is use to run the server
        This method creates a different thread for each client
    """

    def run(self):
        # constantly listeen for connections
        while True:
            connection, a = self.server_soc.accept()

            if(self.is_first_client):
                self.is_first_client = False
                self.start_time = time.time()
            

            print("Accepted Client Connection:",a)
            self.peers.append(connection)
            c_thread3 = threading.Thread(target=self.consumer_thread, args=(connection,))
            c_thread3.start()



    def consumer_thread(self, consumer_soc):

        init_msg = consumer_soc.recv(BYTE_SIZE) # IP|PORT on which the client is listening on
        init_msg_str = init_msg.decode("utf-8")
        print("Received consumer init:" + init_msg_str)

        consumer_conn_details = init_msg_str.strip("()").split(",") 
        consumer_ip = consumer_conn_details[0][1:-1]
        consumer_port = int(consumer_conn_details[1])
        consumer_conn_tuple = (consumer_ip, consumer_port)

        self.ip_conn_dict[consumer_conn_tuple] = {"listening_ip":consumer_ip, "listening_port":consumer_port, "send_soc": consumer_soc}
        print("added to dict")
        # print(self.ip_conn_dict)
        print()

        producer = self.producer_pool.get(True)
        print("Producer:", producer)
        if producer[0] == HOST and producer[1] == PORT:
            print("\n Server Sending Data")
            print("------------------------")

            consumer_soc.send(UPLOAD_START)
            self.send_file(consumer_soc)
            self.producer_pool.put(consumer_conn_tuple)
            self.producer_pool.put(SERVER_IP_PORT)
            consumer_soc.recv(1)
            print("Transfer Complete Message Received From",consumer_conn_tuple)

            print("Added to producer pool:",consumer_conn_tuple)
            print("Added to producer pool:",consumer_soc.getsockname())
        else:
            sender_details = self.ip_conn_dict[producer]
            sender_soc = sender_details["send_soc"]
            sender_soc.send(CONNECT_BYTE_DIFFERENTIATOR)

            print("\n Assigned peer to send Data")
            print("------------------------")
            sender_soc.send(init_msg)
            transfer_complete_msg = consumer_soc.recv(1)
            print("Transfer Complete Message Received From",consumer_conn_tuple)

            self.producer_pool.put(producer)
            self.producer_pool.put(consumer_conn_tuple)
            print("Added to producer pool:",producer)
            print("Added to producer pool:",consumer_conn_tuple)

        self.num_clients -= 1
        print("num clients: ", self.num_clients)
        if(self.num_clients == 0):
            print("Total time:", time.time() - self.start_time)
            for con in self.peers:
                con.close()
            self.server_soc.close()

        # time.sleep(10000)





if __name__ == "__main__":

    input_filename = "test.bin"
    num_clients = 10
    if len(sys.argv) > 1:
        print("Usage: python script.py [argument]")
        input_filename = sys.argv[1]
        if len(sys.argv) > 2:
            num_clients = int(sys.argv[2])

    try :
        server = Server(input_filename,num_clients)
        
    except KeyboardInterrupt as e:
            sys.exit(0)