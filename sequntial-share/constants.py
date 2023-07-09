
import socket 
import threading 
import sys
import time
from random import randint

BYTE_SIZE = 1024
#ip address of server
HOST = '128.6.5.29'
PORT = 5001
PEER_BYTE_DIFFERENTIATOR = b'\x11' 
RAND_TIME_START = 1
RAND_TIME_END = 2
REQUEST_STRING = "req"
TRANSFER_COMPLETE = b'\x14'
UPLOAD_START = b'\x13'

