from dronekit import connect, VehicleMode
from pymavlink import mavutil
import cv2
import socket
import pickle
import struct
import imutils
import argparse
import time

#- Importing Tkinter: sudo apt-get install python-tk
import Tkinter as tk

#-- Connect to the vehicle
print('Connecting...')
vehicle = connect('udp:127.0.0.1:14551')

#-- Setup the commanded flying speed
gnd_speed = 5 # [m/s]

#-- Define arm and takeoff
def arm_and_takeoff(altitude):

   while not vehicle.is_armable:
      print("waiting to be armable")
      time.sleep(1)

   print("Arming motors")
   vehicle.mode = VehicleMode("GUIDED")
   vehicle.armed = True

   while not vehicle.armed: time.sleep(1)

   print("Taking Off")
   vehicle.simple_takeoff(altitude)

   while True:
      v_alt = vehicle.location.global_relative_frame.alt
      print(">> Altitude = %.1f m"%v_alt)
      if v_alt >= altitude - 1.0:
          print("Target altitude reached")
          break
      time.sleep(1)
      
 #-- Define the function for sending mavlink velocity command in body frame
def set_velocity_body(vehicle, vx, vy, vz):
    """ Remember: vz is positive downward!!!
    http://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html
    
    Bitmask to indicate which dimensions should be ignored by the vehicle 
    (a value of 0b0000000000000000 or 0b0000001000000000 indicates that 
    none of the setpoint dimensions should be ignored). Mapping: 
    bit 1: x,  bit 2: y,  bit 3: z, 
    bit 4: vx, bit 5: vy, bit 6: vz, 
    bit 7: ax, bit 8: ay, bit 9:
    
    
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
            0,
            0, 0,
            mavutil.mavlink.MAV_FRAME_BODY_NED,
            0b0000111111000111, #-- BITMASK -> Consider only the velocities
            0, 0, 0,        #-- POSITION
            vx, vy, vz,     #-- VELOCITY
            0, 0, 0,        #-- ACCELERATIONS
            0, 0)
    vehicle.send_mavlink(msg)
    vehicle.flush()
    
def set_yaw_angle(vehicle, is_relative, heading, yaw_speed, direction):
    msg = vehicle.message_factory.command_long_encode(
        0, 0,
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,
        0,
        heading,
        yaw_speed,
        direction,
        is_relative,
        0,0,0)
    vehicle.send_mavlink(msg)
    vehicle.flush()
    
    
#-- Key event function
def key(event):
    if event.char == event.keysym: #-- standard keys
        if event.keysym == 'r':
            print("r pressed >> Set the vehicle to RTL")
            vehicle.mode = VehicleMode("RTL")
            
    else: #-- non standard keys
        if event.keysym == 'Up':
            set_velocity_body(vehicle, gnd_speed, 0, 0)
        elif event.keysym == 'Down':
            set_velocity_body(vehicle,-gnd_speed, 0, 0)
        elif event.keysym == 'Left':
            set_yaw_angle(vehicle, 0, 2, 2, -1)
        elif event.keysym == 'Right':
            set_yaw_angle(vehicle, 0, 2, 2, 1)
    
    
#---- MAIN FUNCTION
#- Takeoff
arm_and_takeoff(10)

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
    #- Read the keyboard with tkinter
    root = tk.Tk()
    print(">> Control the drone with the arrow keys. Press r for RTL mode")
    root.bind_all('<Key>', key)
    while (vid.isOpened()):

        img, frame = vid.read()
        frame = imutils.resize(frame,width=320)
        a = pickle.dumps(frame)
        message = struct.pack("Q",len(a))+a
        clientSocket.sendall(message)
        cv2.imshow(f"Client Sending to: {hostIP}",frame)
		
		# Test Receive
        print(clientSocket.recv(1024))
        
        root.update()
		
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            clientSocket.close()
