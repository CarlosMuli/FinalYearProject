# Import necessary packages
from numba import jit
from imutils.video import FPS
import numpy as np
import argparse
import socket
import pickle 
import struct
import cv2

# Create argument parser to parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--port", default = 55555, help = "Insert Port greater than 1024")
ap.add_argument("-t", "--tracker", default = 'kcf', help = "insert tracker type")
args = vars(ap.parse_args())

# Initialise the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Set the tracker input
trackerInput = args["tracker"]

def setTracker(trackerInput):
    if trackerInput == "kcf":
        return cv2.TrackerKCF_create()
    if trackerInput == "boosting":
        return cv2.TrackerBoosting_create()
    
def getFrame(data, payloadSize):
    while len(data) < payloadSize:
        # Receive video from the client
        packet = clientSocket.recv(4*1024)
        if not packet: break
        data += packet
    packedMessageSize = data[:payloadSize]
    data = data[payloadSize:]
    messageSize = struct.unpack("Q", packedMessageSize)[0]

    while len(data) < messageSize:
        data += clientSocket.recv(4*1024)
    frameData = data[:messageSize]
    data = data[messageSize:]
    frame = pickle.loads(frameData, encoding = 'latin1')
    return frame

def setConnection():
    # Create a socket object
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket Sucessfully Created')
    hostIP = '192.168.1.25'
    print('Host IP: ', hostIP)
    
    # Reserve a port on computer 
    port = int(args["port"])
    
    socketAddress = (hostIP, port)
    
    # Bind to the port
    serverSocket.bind(socketAddress)
    
    # Put the socket into listening mode
    serverSocket.listen(5)
    print('Listening at: ', socketAddress)
    
    # Establish connection with the client
    (clientSocket, addr) = serverSocket.accept()
    print('Client {} Connected'.format(addr))
    return clientSocket

@jit(nopython=True)
def getCoordinates(box):
    xCoord = (box[0] + box[2]/2)
    yCoord = (box[1] + box[3]/2)
    return [xCoord, yCoord]

tracker = setTracker(trackerInput)

# Initialise the bounding box coordinates to track and the bounding box selected
initBB = None
chosenBB = False

# Initialise the FPS counter
fps = None

# Initialise the message to be sent
coordinates = [0, 0]
message = ['','']
centreBuffer = 20

gpuFrame = cv2.cuda_GpuMat()

clientSocket = setConnection()

# If a client socket exists
if clientSocket:
    data = b""
    payloadSize = struct.calcsize("Q")
    while True:
        frame = getFrame(data, payloadSize)
    
        # Resize the image 
        # frame = imutils.resize(frame, width = 320)
        
        gpuFrame.upload(frame)
        resized = cv2.cuda.resize(gpuFrame, (320, 240))
        gray = cv2.cuda.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        gray = gray.download()
        frame = resized.download()
        
        (H, W) = frame.shape[:2]
        cv2.drawMarker(frame, (int(W/2), int(H/2)), (0,0,0), cv2.MARKER_CROSS, 320, 1, cv2.LINE_4)
        cv2.rectangle(frame, (int((W/2)-centreBuffer), int((H/2)-centreBuffer)), (int((W/2)+centreBuffer), int((H/2)+centreBuffer)), (0, 0, 0), 1)
    
        # check to see if we are currently tracking an object
        if initBB is not None:
            # grab the new bounding box coordinates of the object
            (success, box) = tracker.update(frame)

            coordinates = getCoordinates(box)
            if coordinates[1] > H/2 + centreBuffer: message[1] = 'Go Up'
            elif coordinates[1] < H/2 - centreBuffer: message[1] = 'Go Down'
            else: message[1] = 'Centre'
                
            if coordinates[0] > W/2 + centreBuffer: message[0] = 'Right'
            elif coordinates[0] < W/2 - centreBuffer: message[0] = 'Left'
            else: message[0] = 'Centre'

            # check to see if the tracking was a success
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, (int(x + (w/2)), int(y + (h/2))), 3, (255, 0, 0),-1)

            # update the FPS counter
            fps.update()
            fps.stop()
   	
            # initialize the set of information we'll be displaying on
            # the frame
            info = [
   				("Tracker", trackerInput),
   				("Success", "Yes" if success else "No"),
   				("FPS", "{:.2f}".format(fps.fps())),
   			]
   	
            # loop over the info tuples and draw them on our frame
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
   					cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
   
        if chosenBB == False:
            cv2.putText(frame, 'Not Tracking',(10, H - 20 + 20), 
   			   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
   			
            rects, weights = hog.detectMultiScale(gray, winStride=(8,8))
            rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
            for i, (xA, yA, xB, yB) in enumerate(rects):
                if weights[i] < 0.13:
                    continue
                elif weights[i] < 0.3 and weights[i] > 0.13: cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 0, 255), 2)
                if weights[i] < 0.7 and weights[i] > 0.3: cv2.rectangle(frame, (xA, yA), (xB, yB), (50, 122, 255), 2)
                if weights[i] > 0.7: cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
                cv2.putText(frame, str(weights[i])[1:5],(xA, yA),  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            clientSocket.send(str(message).encode('utf-8'))
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
        else:
            clientSocket.send(str(message).encode('utf-8'))
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

        # if the 's' key is selected, we are going to "select" a bounding
        # box to track
        if key == ord("s"):
            rects, weights = hog.detectMultiScale(gray, winStride=(8,8))
            rects = np.array([[x, y, w, h] for (x, y, w, h) in rects])
            for (xA, yA, xB, yB) in rects:
                if len(rects) == 1:
                    print('Only one person in frame')
                    initBB = tuple(map(tuple,rects))[0]
                    chosenBB = True  
                elif len(rects) > 1: 
                    print('People in frame: %s'%len(rects))
   			
            # start OpenCV object tracker using the supplied bounding box
            # coordinates, then start the FPS throughput estimator as well
            try:
                tracker.init(frame, initBB)
            except:
                print('No bounding box detected')
                pass
            fps = FPS().start()
   	
        # if the `q` key was pressed, break from the loop
        elif key == ord("q"):
            break		
    clientSocket.close()



































