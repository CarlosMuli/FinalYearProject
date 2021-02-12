from imutils.video import WebcamVideoStream
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

vid = WebcamVideoStream(src=0).start()
print('Capturing Video')
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
hostIP = '192.168.1.25'

port = int(args["port"])
print('Attempting Connection')
clientSocket.connect((hostIP,port))
print('Connection Successful')

if clientSocket: 
    while True:

        frame = vid.read()
        frame = imutils.resize(frame,width=320)

        a = pickle.dumps(frame)
        message = struct.pack("Q",len(a))+a
        clientSocket.sendall(message)
        
        cv2.imshow(f"Client Sending to: {hostIP}",frame)

        instruction = clientSocket.recv(1024)
        instructionYaw = instruction.decode('utf-8').split("'")[1]
        instructionForward = instruction.decode('utf-8').split("'")[3]
        
        if instructionYaw == 'Left': print(instructionYaw)
        elif instructionYaw == 'Right': print(instructionYaw)
        elif instructionYaw == 'Centre': print(instructionYaw)
		
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            clientSocket.close()
            break