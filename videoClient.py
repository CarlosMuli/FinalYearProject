# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 15:19:58 2021

@author: Renn
"""

import cv2
import socket
import pickle
import struct

# Create socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostIP = '192.168.1.25'
port = 8888
clientSocket.connect((hostIP, port)) # a tuple
data = b""
payloadSize = struct.calcsize("Q")
while True:
	while len(data) < payloadSize:
		packet = clientSocket.recv(4*1024) # 4K
		if not packet: break
		data += packet
	packedMessageSize = data[:payloadSize]
	data = data[payloadSize:]
	messageSize = struct.unpack("Q", packedMessageSize)[0]
	
	while len(data) < messageSize:
		data += clientSocket.recv(4*1024)
	frameData = data [:messageSize]
	data = data[messageSize:]
	frame = pickle.loads(frameData)
	cv2.imshow('Received', frame)
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		break
clientSocket.close()
		   
	
	
	
	
	
	
	
	
	
	
	