from controller import Robot, Motor, LightSensor
#pymodsbus == 2.5.3 needed for proper communications
from pymodbus.client.sync import ModbusTcpClient
import sys
import time

MODBUS_IP = '127.0.0.1'
MODBUS_PORT = 502
MODBUS_REGISTER_ADDRESS = 32769  # Address for mb_Input_register[0]

# Initialize the robot
robot = Robot()

# Ensure proper number of arguments (speed and timer)
if len(sys.argv) != 3:
    print("Usage: controller <speed> <timer>")
    sys.exit(1)

# Get simulation timestep
timestep = int(robot.getBasicTimeStep())

# Parse speed and timer arguments
speed = float(sys.argv[1])
timer = float(sys.argv[2])

# Get and enable devices
ls1 = robot.getDevice("Pillar_LS1")
ls2 = robot.getDevice("Pillar_LS2")
belt_emitter = robot.getDevice("BeltEmitter")

ls1.enable(timestep)
ls2.enable(timestep)

belt_motor = robot.getDevice("belt_motor")
belt_motor.setPosition(float('inf'))  # Set to velocity control mode
belt_motor.setVelocity(0.0)  # Initially stopped

belt_running = False

# Initialize Modbus TCP client
modbus_client = ModbusTcpClient(MODBUS_IP, port=MODBUS_PORT)
connection_ok = modbus_client.connect()
if not connection_ok:
    print("Failed to connect to Modbus server.")
    sys.exit(1)
else:
    print("Connected to Modbus TCP server.")

# Wait for Modbus input register to be 1 before starting
#print("Waiting for start signal (mb_Input_register[0] == 1)...")
while robot.step(timestep) != -1:
    result = modbus_client.read_input_registers(MODBUS_REGISTER_ADDRESS - 1, 1)
    if result.isError():
        print("Modbus read error.")
    else:
        value = result.registers[0]
        if value == 1:
            print("Start signal received. Starting conveyor.")
            belt_motor.setVelocity(speed)
            belt_running = True
            break  # Exit waiting loop

# Main loop
while robot.step(timestep) != -1:
    ls1_value = ls1.getValue()
    ls2_value = ls2.getValue()
    current_time = robot.getTime()

    # Read Modbus holding register
    result = modbus_client.read_input_registers(MODBUS_REGISTER_ADDRESS - 1, 1)
    if result.isError():
        print("Modbus read error.")
        continue

    control_signal = result.registers[0]  # Value from PLC (or TwinCAT)

    # Stop on timer if specified
    if timer > 0 and current_time >= timer:
        belt_motor.setVelocity(0.0)
        print("Timer expired. Stopping conveyor.")
        break

    # Conveyor runs only if Modbus register == 1 and sensors permit
    if control_signal == 1:
        # Resume if sensors detect object and belt is not running
        if ls1_value >= 100.0 and ls2_value >= 100.0 and not belt_running:
            belt_motor.setVelocity(speed)
            belt_running = True
            modbus_client.write_register(MODBUS_REGISTER_ADDRESS - 1, 0)  # No box
        # Stop if sensors detect nothing
        elif ls1_value < 100.0 and ls2_value < 100.0 and belt_running:
            belt_motor.setVelocity(0.0)
            belt_running = False
            modbus_client.write_register(MODBUS_REGISTER_ADDRESS - 1, 1)  # Box detected
    else:
        if belt_running:
            print("Modbus control signal is 0. Stopping belt.")
            belt_motor.setVelocity(0.0)
            belt_running = False

# Clean up
robot.cleanup()
