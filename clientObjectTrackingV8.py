# USAGE
# python clientObjectTrackingV8.py --input videos/inputVideo.mp4

from imutils.video import WebcamVideoStream
import cv2
import socket
import pickle
import struct
import imutils
import argparse
import time

# Create argument parser to parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--port", default = 55555, help = "Insert Port greater than 1024")
ap.add_argument("-i", "--input", default = "none", type = str, help="path to input video")
args = vars(ap.parse_args())

print(args["input"])

if args["input"] == 'none':
    vid = WebcamVideoStream(src=0).start()
else:
    vid = cv2.VideoCapture(args["input"])
    
time.sleep(2)
print('Capturing Video')
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
hostIP = '192.168.1.34'

port = int(args["port"])
print('Attempting Connection')
clientSocket.connect((hostIP,port))
print('Connection Successful')

if clientSocket: 
    while True:
        if args["input"] == 'none':
            frame  = vid.read()
        else:
            (grabbed, frame) = vid.read()
            if not grabbed: break
        
        frame = imutils.resize(frame,width=320)

        a = pickle.dumps(frame)
        message = struct.pack("Q",len(a))+a
        clientSocket.sendall(message)
        
        cv2.imshow(f"Client Sending to: {hostIP}",frame)
        
        try:

            instruction = clientSocket.recv(1024)
            instructionYaw = instruction.decode('utf-8').split("'")[1]
            instructionForward = instruction.decode('utf-8').split("'")[3]
            
            if instructionYaw == 'Left': print(instructionYaw)
            elif instructionYaw == 'Right': print(instructionYaw)
            elif instructionYaw == 'Centre': print(instructionYaw)
        except:
            break
		
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            clientSocket.close()
            break

try:
    vid.release()
except:
    pass
cv2.destroyAllWindows()
