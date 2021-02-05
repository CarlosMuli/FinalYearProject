import cv2
import socket
import pickle
import struct
import imutils
import argparse

# Create argument parser to parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--port", default = 55555, help = "Insert Port greater than 1024")
args = vars(ap.parse_args())

vid = cv2.VideoCapture(0)
print('Capturing Video')
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
hostIP = '192.168.1.25'

port = int(args["port"])
print('Attempting Connection')
clientSocket.connect((hostIP,port))
print('Connection Successful')

if clientSocket: 
    while (vid.isOpened()):

        img, frame = vid.read()
        frame = imutils.resize(frame,width=320)
        a = pickle.dumps(frame)
        message = struct.pack("Q",len(a))+a
        clientSocket.sendall(message)
        cv2.imshow(f"Client Sending to: {hostIP}",frame)
		
		# Test Receive
        print(clientSocket.recv(1024))
		
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            clientSocket.close()