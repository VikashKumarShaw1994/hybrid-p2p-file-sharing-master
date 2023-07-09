
import socket 
import threading 
import sys
import time
from random import randint

BYTE_SIZE = 1024
#set ip of server here
HOST = '128.6.5.29'
PORT = 5000
PEER_BYTE_DIFFERENTIATOR = b'\x11'
CONNECT_BYTE_DIFFERENTIATOR = b'\x12'
UPLOAD_START = b'\x13'
TRANSFER_COMPLETE = b'\x14'
RAND_TIME_START = 1
RAND_TIME_END = 2
REQUEST_STRING = "req"
SERVER_IP_PORT = (HOST,PORT)
