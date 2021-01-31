import cv2
import socket
import pickle
import struct
import imutils

vid = cv2.VideoCapture(0)
print('Capturing Video')
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '192.168.1.25' # Here according to your server ip write the address

port = 55555
print('Attempting Connection')
client_socket.connect((host_ip,port))
print('Connection Successful')

if client_socket: 
	while (vid.isOpened()):

		img, frame = vid.read()
		frame = imutils.resize(frame,width=320)
		a = pickle.dumps(frame)
		message = struct.pack("Q",len(a))+a
		client_socket.sendall(message)
		cv2.imshow(f"Client Sending to: {host_ip}",frame)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			client_socket.close()

		   
	
	
	
	
	
	
	
	
	
	
	