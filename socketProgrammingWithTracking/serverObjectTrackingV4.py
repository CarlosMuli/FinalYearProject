# Import necessary packages
from imutils.video import FPS
import numpy as np
import cv2
import socket
import pickle 
import struct
import imutils
import argparse

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


	# initialize a dictionary that maps strings to their corresponding
	# OpenCV object tracker implementations
OPENCV_OBJECT_TRACKERS = {
	"csrt": cv2.TrackerCSRT_create,
	"kcf": cv2.TrackerKCF_create,
	"boosting": cv2.TrackerBoosting_create,
	"mil": cv2.TrackerMIL_create,
	"tld": cv2.TrackerTLD_create,
	"medianflow": cv2.TrackerMedianFlow_create,
	"mosse": cv2.TrackerMOSSE_create
}

# grab the appropriate object tracker using our dictionary of
# OpenCV object tracker objects
tracker = OPENCV_OBJECT_TRACKERS[trackerInput]()

# Initialise the bounding box coordinates to track and the bounding box selected
initBB = None
chosenBB = False

# Initialise the FPS counter
fps = None

# Initialise the message to be sent
coordinates = [0, 0]
coordinatesStatus = False
previousCoordinates = [0, 0]
message = ['','']

# Create a socket object
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket Sucessfully Created')
hostName = socket.gethostname()
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

# If a client socket exists
if clientSocket:
    data = b""
    payloadSize = struct.calcsize("Q")
    while True:
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
    
        # Resize the image 
        frame = imutils.resize(frame, width = 320)
        (H, W) = frame.shape[:2]
        cv2.drawMarker(frame, (int(W/2), int(H/2)), (0,0,0), cv2.MARKER_CROSS, 320, 1, cv2.LINE_4)
    
        # check to see if we are currently tracking an object
        if initBB is not None:
            # grab the new bounding box coordinates of the object
            (success, box) = tracker.update(frame)

            xCoord = (box[0] + box[2]/2)
            yCoord = (box[1] + box[3]/2)

            #previousCoordinates = coordinates
            coordinates = [xCoord, yCoord]
            #difference = [coordinates[0] - previousCoordinates[0], coordinates[1] - previousCoordinates[1]]

            if coordinates[1] > H/2 + 10:
                message[1] = 'Go Up'
            elif coordinates[1] < H/2 - 10:
                message[1] = 'Go Down'
            else:
                message[1] = 'Centre'
                
            if coordinates[0] > W/2 + 10:
                message[0] = 'Go Right'
            elif coordinates[0] < W/2 - 10:
                message[0] = 'Go Left'
            else:
                message[0] = 'Centre'

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
   			
            rects, weights = hog.detectMultiScale(frame, winStride=(8,8))
            rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
            for (xA, yA, xB, yB) in rects:
                cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
   	
            clientSocket.send(str(message).encode('utf-8'))
            
            # show the output frame
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
        else:
            clientSocket.send(str(message).encode('utf-8'))
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

        # if the 's' key is selected, we are going to "select" a bounding
        # box to track
        if key == ord("s"):
            # select the bounding box of the object we want to track (make
            # sure you press ENTER or SPACE after selecting the ROI)
            rects, weights = hog.detectMultiScale(frame, winStride=(8,8))
            rects = np.array([[x, y, w, h] for (x, y, w, h) in rects])
            for (xA, yA, xB, yB) in rects:
                if len(rects) == 1:
                    print('Only one person in frame')
                    initBB = tuple(map(tuple,rects))[0]
                    chosenBB = True  
                elif len(rects) > 1: 
                    print('People in frame: %s'%len(rects))
                else:
                    print('No one in frame')
   			
            # start OpenCV object tracker using the supplied bounding box
            # coordinates, then start the FPS throughput estimator as well
            tracker.init(frame, initBB)
            fps = FPS().start()
   	
        # if the `q` key was pressed, break from the loop
        elif key == ord("q"):
            break		
    clientSocket.close()



































