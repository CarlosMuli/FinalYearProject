# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 15:17:24 2021

@author: Renn
"""

import socket
import cv2 
import pickle 
import struct
import imutils

# Socket Create
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostName = socket.gethostname()
hostIP = socket.gethostbyname(hostName)
print('Host IP: ', hostIP)
port = 8888
socketAddress = (hostIP,port)

# Socket Bind
serverSocket.bind(socketAddress)

# Socket Listen
serverSocket.listen(5)
print('Listening at: ', socketAddress)

# Socket Accept
while True:
	clientSocket, addr = serverSocket.accept()
	print('Got Connection From: ', addr)
	if clientSocket:
		vid = cv2.VideoCapture(0)
		
		while(vid.isOpened()):
			img, frame = vid.read()
			frame = imutils.resize(frame, width = 320)
			a = pickle.dumps(frame)
			message = struct.pack("Q", len(a))+a
			clientSocket.sendall(message)
			
			cv2.imshow('Transmitting Video', frame)
			key = cv2.waitKey(1) & 0xFF
			if key == ord('q'):
				clientSocket.close()
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			