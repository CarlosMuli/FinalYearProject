# Test of connection with an actual autopilot

from dronekit import connect, VehicleMode
import time

# Start the Software In The Loop (SITL)
import dronekit_sitl


connection_string = "/dev/ttyACM0" # for a usb connection use /dev/ttyACM0 or ttyAMA0 for a serial port connection 
baud_rate = 115200 # for usb set baud_rate to 115200 or 57600 for serial port connection

print(">>> Connecting with the UAV <<<")
vehicle = connect(connection_string, baud=baud_rate,wait_ready=True)

# Read information from the autopilot
vehicle.wait_ready('autopilot_version')
print('Autopilot Version: %s'%vehicle.version)

# Does the firmware support the companion pc to set the attitude
print('Supports set attitude from companion: %s'%vehicle.capabilities.set_attitude_target_local_ned)

# Read the actual position
print('Position: %s'%vehicle.location.global_relative_frame)

# Read the actual attitude roll, pitch, yaw
print('Attitude: %s'%vehicle.attitude)

# Read the actual velocity (m/s)
print('Velocity: %s'%vehicle.velocity) # North, East, Down

# When did we receive the last heartbeat
print('Last Heartbeat: %s'%vehicle.last_heartbeat)

# Is the vehicle good to arm?
print('Is the vehicle armable: %s'%vehicle.is_armable)

# What is the actual flight mode?
print('Mode: %s'%vehicle.mode.name)

# Is the vehicle armed?
print('Armed: %s'%vehicle.armed)

# Is the estimation filer ok?
print('EKF Ok: %s'%vehicle.ekf_ok)

# Adding a listener
# dronekit updates the variables as soon as it receives an update from the UAV
# You can define a callback function for predefined messages or define one for any mavlink message

def attitude_callback(self,attr_name,value):
    print(vehicle.attitude)
    
print("")
print("Adding an attitude listener")
vehicle.add_attribute_listener('attitude', attitude_callback) # Message type, callback function
time.sleep(5)

# Now we print the attitude from the callback for 5 seconds, then we remove the callback
vehicle.remove_attribute_listener('attitude', attitude_callback) # (.remove)

# Parameters
print("Maximum Throttle: %d"%vehicle.parameters['THR_MIN'])

# You can read and write the parameters
vehicle.parameters['THR_MIN'] = 50
time.sleep(1)
print("Maximum Throttle: %d"%vehicle.parameters['THR_MIN'])

# Close
vehicle.close()
print('Test Over')  

















