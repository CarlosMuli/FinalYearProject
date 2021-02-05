from dronekit import connect, VehicleMode
from pymavlink import mavutil
import argparse
import imutils
import socket
import pickle
import struct
import time
import cv2

# Create argument parser to parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--port", default = 55555, help = "Insert Port greater than 1024")
ap.add_argument("-alt", "--altitude", default = 5, help = "Insert altitude")
args = vars(ap.parse_args())

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

def follow_detection(instruction):
    if instruction == 'Left':
        set_yaw_angle(vehicle, 1, 1, 0, -1)
    if instruction == 'Right':
        set_yaw_angle(vehicle, 1, 1, 0, 1)
    
    
# Main Function
#-- Connect to the vehicle
print('Connecting...')
vehicle = connect('udp:127.0.0.1:14550',baud=115200,wait_ready=True)

vid = cv2.VideoCapture(0)
print('Capturing Video')
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
hostIP = '192.168.1.25'

port = int(args["port"])
print('Attempting Connection')
clientSocket.connect((hostIP,port))
print('Connection Successful')

gnd_speed = 5

arm_and_takeoff(args["altitude"])

if clientSocket: 
    set_velocity_body(vehicle, gnd_speed, 0, 0)
    while(vid.isOpened()):
        img, frame = vid.read()
        frame = imutils.resize(frame,width=320)
        a = pickle.dumps(frame)
        message = struct.pack("Q",len(a))+a
        clientSocket.sendall(message)
		
		# Test Receive
        instruction = clientSocket.recv(1024)
        instructionYaw = instruction.decode('utf-8').split("'")[1]
        instructionForward = instruction.decode('utf-8').split("'")[3]
        follow_detection(instructionYaw)
		
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            clientSocket.close()        


































