# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import imutils
import time
import cv2

trackerInput = 'kcf'
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# extract the OpenCV version info
(major, minor) = cv2.__version__.split(".")[:2]

# if we are using OpenCV 3.2 OR BEFORE, we can use a special factory
# function to create our object tracker
if int(major) == 3 and int(minor) < 3:
	tracker = cv2.Tracker_create(trackerInput.upper())

# otherwise, for OpenCV 3.3 OR NEWER, we need to explicity call the
# approrpiate object tracker constructor:
else:
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

# initialize the bounding box coordinates of the object we are going
# to track
initBB = None

# if a video path was not supplied, grab the reference to the web cam
# if not args.get("video", False):
# 	print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(1.0)

# # otherwise, grab a reference to the video file
# else:
# vs = cv2.VideoCapture(videoInput)

# initialize the FPS throughput estimator
fps = None
chosenBB = 0

# loop over frames from the video stream
while True:
# 	# grab the current frame, then handle if we are using a
# 	# VideoStream or VideoCapture object
	frame = vs.read()

	# resize the frame (so we can process it faster) and grab the
	# frame dimensions
	frame = imutils.resize(frame, width=600)
	(H, W) = frame.shape[:2]

	# check to see if we are currently tracking an object
	if initBB is not None:
		# grab the new bounding box coordinates of the object
		(success, box) = tracker.update(frame)

		# check to see if the tracking was a success
		if success:
			(x, y, w, h) = [int(v) for v in box]
			cv2.rectangle(frame, (x, y), (x + w, y + h),
				(0, 255, 0), 2)

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


# 	while chosenBB == 0:
# 		rects, weights = hog.detectMultiScale(frame, winStride=(8,8))
# 		rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
# 		for (xA, yA, xB, yB) in rects:
# 			cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)

	if chosenBB == 0:
		rects, weights = hog.detectMultiScale(frame, winStride=(8,8))
		rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
		for (xA, yA, xB, yB) in rects:
			cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)

	# show the output frame
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
	else:
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

	# if the 's' key is selected, we are going to "select" a bounding
	# box to track
	if key == ord("s"):
		# select the bounding box of the object we want to track (make
		# sure you press ENTER or SPACE after selecting the ROI)
# 		initBB = cv2.selectROI("Frame", frame, fromCenter=False,
# 			showCrosshair=True)
# 		print(type(initBB))
		rects, weights = hog.detectMultiScale(frame, winStride=(8,8))
# 		print(type(rects[0]))
# 		print(tuple(map(tuple,rects))[0])
		rects = np.array([[x, y, w, h] for (x, y, w, h) in rects])
		for (xA, yA, xB, yB) in rects:
 			if len(rects) == 1:
 				 print('Only one person in frame')
 				 initBB = tuple(map(tuple,rects))[0]
 				 chosenBB = 1  
 			else: 
 				 print('People in frame: %s'%len(rects))
		
		# start OpenCV object tracker using the supplied bounding box
		# coordinates, then start the FPS throughput estimator as well
		tracker.init(frame, initBB)
		fps = FPS().start()

	# if the `q` key was pressed, break from the loop
	elif key == ord("q"):
		break

# close all windows
cv2.destroyAllWindows()
vs.stream.release()
