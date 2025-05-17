from controller import Robot, Motor
#pymodsbus == 2.5.3 needed for proper communications
from pymodbus.client.sync import ModbusTcpClient
import time

TIME_STEP = 64

# Gripper positions
OPEN = 0.00
CLOSE = 0.25

# Lift positions
LIFT_UP = 0
LIFT_DOWN = 1.35

# Locations
PICKUP_LOCATION = -5
DROP_LOCATION = 5

# Modbus TCP settings
MODBUS_IP = '127.0.0.1'
MODBUS_PORT = 502
MODBUS_REGISTER_ADDRESS = 32769  # Address for mb_Input_register[0]

def main():
    robot = Robot()

    # Initialize motors
    motors = {
        'bridge': robot.getDevice("bridgemotor"),
        'lift': robot.getDevice("liftmotor"),
        'grip1': robot.getDevice("gripper1"),
        'grip2': robot.getDevice("gripper2"),
        'wheel1': robot.getDevice("wheel1motor"),
        'wheel2': robot.getDevice("wheel2motor"),
        'wheel3': robot.getDevice("wheel3motor"),
        'wheel4': robot.getDevice("wheel4motor")
    }

    for motor in motors.values():
        motor.setVelocity(1.0)
        motor.setPosition(0)

    # Initialize receiver
    receiver = robot.getDevice("CraneReceiver")
    receiver.enable(TIME_STEP)

    # Initialize Modbus TCP client
    client = ModbusTcpClient(MODBUS_IP, port=MODBUS_PORT)
    connection_ok = client.connect()
    if not connection_ok:
        print("Failed to connect to Modbus server.")
    else:
        print("Connected to Modbus TCP server.")

    state = 0
    step_counter = 0

    while robot.step(TIME_STEP) != -1:

        # Crane routine state machine...
        if state == 0:
            while robot.step(TIME_STEP) != -1:
                #Reading from twincat for box detection
                dataHold = client.read_input_registers(MODBUS_REGISTER_ADDRESS, 1)
                BoxPresent = dataHold.registers[0]
                #debug :)
                #print(f"Waiting for PLC register value: {BoxPresent}\n")
                if BoxPresent == 1:
                    client.write_register(MODBUS_REGISTER_ADDRESS, 1)
                    state = 1
                    step_counter = 0
                    break

        # FSM for crane routine (unchanged from previous version)
        if state == 1:
            #Crane moving
            for m in ['wheel1', 'wheel2', 'wheel3', 'wheel4']:
                motors[m].setPosition(PICKUP_LOCATION)
            if step_counter > 100:
                state = 2
                step_counter = 0

        elif state == 2:
            motors['bridge'].setPosition(1.7)
            if step_counter > 100:
                state = 3
                step_counter = 0

        elif state == 3:
            motors['lift'].setPosition(LIFT_DOWN)
            if step_counter > 100:
                state = 4
                step_counter = 0

        elif state == 4:
            motors['grip1'].setPosition(CLOSE)
            motors['grip2'].setPosition(CLOSE)
            if step_counter > 100:
                state = 5
                step_counter = 0

        elif state == 5:
            motors['lift'].setPosition(LIFT_UP)
            if step_counter > 100:
                state = 6
                step_counter = 0

        elif state == 6:
            for m in ['wheel1', 'wheel2', 'wheel3', 'wheel4']:
                motors[m].setPosition(DROP_LOCATION)
            if step_counter > 200:
                state = 7
                step_counter = 0

        elif state == 7:
            motors['bridge'].setPosition(-1.6)
            if step_counter > 100:
                state = 8
                step_counter = 0

        elif state == 8:
            motors['lift'].setPosition(LIFT_DOWN + 0.4)
            if step_counter > 100:
                state = 9
                step_counter = 0

        elif state == 9:
            motors['grip1'].setPosition(OPEN)
            motors['grip2'].setPosition(OPEN)
            if step_counter > 100:
                state = 10
                step_counter = 0

        elif state == 10:
            motors['lift'].setPosition(LIFT_UP)
            if step_counter > 100:
                state = 11
                step_counter = 0

        elif state == 11:
            for m in motors:
                motors[m].setPosition(0)
            if step_counter > 150:
                print("Returning to idle.")
                client.write_register(MODBUS_REGISTER_ADDRESS, 0)
                state = 0
                step_counter = 0

        step_counter += 1

    modbus_client.close()
    print("Exiting and closed Modbus connection.")
    robot.cleanup()

if __name__ == "__main__":
    main()
