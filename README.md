# hybrid-p2p-file-sharing

Steps to run p2p-share
- clone repo into server and client machine
- add files you want to share in the folder
- cd into p2p-share 
- set HOST variable in constants.py to the ip address of the server machine in both server and client machine
- on server machine run python3 server.py <filename> <number_of_clients> 
- on <number_of_clients> client machines run python3 client.py 
- the shared file is saved inside client_data folder

Steps to run sequential-share for comparison
- add files you want to share in the folder
- cd into sequential-share 
- set HOST variable in constants.py to the ip address of the server machine in both server and client machine
- on server machine run python3 server.py <filename> <number_of_clients> 
- on <number_of_clients> client machines run python3 client.py 
- the shared file is saved inside client_data folder
