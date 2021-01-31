import socket
import cv2 
import pickle 
import struct

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name  = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print('HOST IP:',host_ip)
port = 55555
#socket_address = (host_ip,port)
socket_address = ('192.168.1.25', port)
server_socket.bind(socket_address)
server_socket.listen()
print("Listening at",socket_address)

client_socket,addr = server_socket.accept()
print('CLIENT {} CONNECTED!'.format(addr))
if client_socket: # if a client socket exists
	data = b""
	payload_size = struct.calcsize("Q")
	while True:
		while len(data) < payload_size:
			packet = client_socket.recv(4*1024) # 4K
			if not packet: break
			data+=packet
		packed_msg_size = data[:payload_size]
		data = data[payload_size:]
		msg_size = struct.unpack("Q",packed_msg_size)[0]
		
		while len(data) < msg_size:
			data += client_socket.recv(4*1024)
		frame_data = data[:msg_size]
		data  = data[msg_size:]
		frame = pickle.loads(frame_data, encoding = 'latin1')
		cv2.imshow(f"Server receiving from: {addr}",frame)
		key = cv2.waitKey(1) & 0xFF
		if key  == ord('q'):
			break
	client_socket.close()



			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			