from controller import Robot, Motor, Receiver
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

    state = 0
    step_counter = 0

    while robot.step(TIME_STEP) != -1:

        # Continuously check for new signal in idle state
        if state == 0:
            while receiver.getQueueLength() > 0:
                data = receiver.getString()
                receiver.nextPacket()  # Clear current packet
                print(f"Received data: {data}")
                if data == "1":
                    state = 1
                    step_counter = 0
                    break  # Exit loop and start crane operation

        # State machine for crane routine
        if state == 1:
            print("Wheeling to pickup")
            for m in ['wheel1', 'wheel2', 'wheel3', 'wheel4']:
                motors[m].setPosition(PICKUP_LOCATION)
            if step_counter > 100:
                state = 2
                step_counter = 0

        elif state == 2:
            print("Sliding bridge")
            motors['bridge'].setPosition(1.7)
            if step_counter > 100:
                state = 3
                step_counter = 0

        elif state == 3:
            print("Lowering crane")
            motors['lift'].setPosition(LIFT_DOWN)
            if step_counter > 100:
                state = 4
                step_counter = 0

        elif state == 4:
            print("Closing gripper")
            motors['grip1'].setPosition(CLOSE)
            motors['grip2'].setPosition(CLOSE)
            if step_counter > 100:
                state = 5
                step_counter = 0

        elif state == 5:
            print("Raising crane")
            motors['lift'].setPosition(LIFT_UP)
            if step_counter > 100:
                state = 6
                step_counter = 0

        elif state == 6:
            print("Wheeling to drop location")
            for m in ['wheel1', 'wheel2', 'wheel3', 'wheel4']:
                motors[m].setPosition(DROP_LOCATION)
            if step_counter > 200:
                state = 7
                step_counter = 0

        elif state == 7:
            print("Sliding bridge back")
            motors['bridge'].setPosition(-1.6)
            if step_counter > 100:
                state = 8
                step_counter = 0

        elif state == 8:
            print("Lowering crane to drop")
            motors['lift'].setPosition(LIFT_DOWN + 0.4)
            if step_counter > 100:
                state = 9
                step_counter = 0

        elif state == 9:
            print("Opening gripper")
            motors['grip1'].setPosition(OPEN)
            motors['grip2'].setPosition(OPEN)
            if step_counter > 100:
                state = 10
                step_counter = 0

        elif state == 10:
            print("Raising crane post-drop")
            motors['lift'].setPosition(LIFT_UP)
            if step_counter > 100:
                state = 11
                step_counter = 0

        elif state == 11:
            print("Resetting position")
            for m in motors:
                motors[m].setPosition(0)
            if step_counter > 150:
                print("Returning to idle.")
                state = 0
                step_counter = 0

        step_counter += 1

    print("Exiting.")
    robot.cleanup()

if __name__ == "__main__":
    main()
