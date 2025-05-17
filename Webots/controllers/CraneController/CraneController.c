#include <stdlib.h>
#include <stdio.h>
#include <webots/motor.h>
#include <webots/robot.h>
#include <webots/receiver.h>
#define TIME_STEP 64


// Gripper positions
#define OPEN 0.00
#define CLOSE 0.25

// Lift positions
#define LIFT_UP 0
#define LIFT_DOWN 1.35

#define PICKUP_LOCATION -5
#define DROP_LOCATION 5


int main(int argc, char **argv) {
  wb_robot_init();

  // Declare motors
  WbDeviceTag bridge = wb_robot_get_device("bridgemotor");
  WbDeviceTag lift = wb_robot_get_device("liftmotor");
  WbDeviceTag grip1 = wb_robot_get_device("gripper1");
  WbDeviceTag grip2 = wb_robot_get_device("gripper2");
  WbDeviceTag wheel1 = wb_robot_get_device("wheel1motor");
  WbDeviceTag wheel2 = wb_robot_get_device("wheel2motor");
  WbDeviceTag wheel3 = wb_robot_get_device("wheel3motor");
  WbDeviceTag wheel4 = wb_robot_get_device("wheel4motor");
  WbDeviceTag crane_receiver = wb_robot_get_device("CraneReceiver");
  
  wb_receiver_enable(crane_receiver, TIME_STEP);
  

 
  wb_motor_set_position(lift, 0);
  wb_motor_set_position(bridge, 0);
  
  wb_motor_set_position(wheel1, 0);
  wb_motor_set_position(wheel2, 0);
  wb_motor_set_position(wheel3, 0);
  wb_motor_set_position(wheel4, 0);
  
  wb_motor_set_velocity(wheel1, 1.0);
  wb_motor_set_velocity(wheel2, 1.0);
  wb_motor_set_velocity(wheel3, 1.0);
  wb_motor_set_velocity(wheel4, 1.0);
  
  wb_motor_set_velocity(lift, 1.0);
  wb_motor_set_velocity(bridge, 1.0);
  wb_motor_set_velocity(grip1, 1.0);
  wb_motor_set_velocity(grip2, 1.0);

  int step_counter = 0;
  int state = 0;
  
  //waiting for emitter signal


  while (wb_robot_step(TIME_STEP) != -1) {
    switch (state) {
    
    case 0:
        printf("Waiting for box\n");
          while (wb_robot_step(TIME_STEP) != -1) {
    if (wb_receiver_get_queue_length(crane_receiver) > 0) {
      const void *data = wb_receiver_get_data(crane_receiver);
      int signal = *((int *)data);
      wb_receiver_next_packet(crane_receiver);
      if (signal == 1) {
        printf("Signal received. Starting crane operations.\n");
        state = 1;
        break;
      }
    }
  }
    
    case 1: // Lower the lift
        printf("Wheeling\n");
         wb_motor_set_position(wheel1, PICKUP_LOCATION);
         wb_motor_set_position(wheel2, PICKUP_LOCATION);
         wb_motor_set_position(wheel3, PICKUP_LOCATION);
         wb_motor_set_position(wheel4, PICKUP_LOCATION);
        
         if (step_counter++ > 100) {
          state = 2;
          step_counter = 0;
        }
        break;
    
    
    case 2: // Lower the lift
        printf("Sliding bridge\n");
        wb_motor_set_position(bridge, 1.7);
        
        if (step_counter++ > 100) {
          state = 3;
          step_counter = 0;
        }
        break;
          
    
      case 3: // Lower the lift
        printf("Lowering crane\n");
        wb_motor_set_position(lift, LIFT_DOWN);
        
        if (step_counter++ > 100) {
          state = 4;
          step_counter = 0;
        }
        break;

      case 4: // Close the gripper
        printf("Closing grips\n");
        wb_motor_set_position(grip1, CLOSE);
        wb_motor_set_position(grip2, CLOSE);
        
        if (step_counter++ > 100) {
          state = 5;
          step_counter = 0;
        }
        break;

      case 5: // Raise the lift
        printf("Raising crane\n");
        wb_motor_set_position(lift, LIFT_UP);
        
        if (step_counter++ > 100) {
          state = 6;
          step_counter = 0;
        }
        break;
        
        case 6: // Lower the lift
        printf("Wheeling\n");
         wb_motor_set_position(wheel1, DROP_LOCATION);
         wb_motor_set_position(wheel2, DROP_LOCATION);
         wb_motor_set_position(wheel3, DROP_LOCATION);
         wb_motor_set_position(wheel4, DROP_LOCATION);
        
         if (step_counter++ > 200) {
          state = 7;
          step_counter = 0;
        }
        break;
        
        case 7: // Lower the lift
        printf("Sliding bridge\n");
        wb_motor_set_position(bridge, -1.6);
        
        if (step_counter++ > 100) {
          state = 8;
          step_counter = 0;
        }
        break;
        
        case 8: // Raise the lift
        printf("Lowering crane\n");
        wb_motor_set_position(lift, LIFT_DOWN+0.4);
        
        if (step_counter++ > 100) {
          state = 9;
          step_counter = 0;
        }
        break;

      case 9: // Open the gripper (drop the crate)
        printf("Opening grips\n");
        wb_motor_set_position(grip1, OPEN);
        wb_motor_set_position(grip2, OPEN);
        if (step_counter++ > 100) {
          state = 10;
          step_counter = 0;
        }
        break;

      case 10:         
        printf("Raising crane\n");
        wb_motor_set_position(lift, LIFT_UP);
        
        if (step_counter++ > 100) {
          state = 11;
          step_counter = 0;
        }
        break;
        
        case 11:    
             
        printf("Reseting...\n");
        wb_motor_set_position(lift, 0);
        wb_motor_set_position(bridge, 0);
        wb_motor_set_position(wheel1, 0);
        wb_motor_set_position(wheel2, 0);
        wb_motor_set_position(wheel3, 0);
        wb_motor_set_position(wheel4, 0);
        
        if (step_counter++ > 150) {
          state = 0;
          step_counter = 0;
        }
        break;
    }
  }

  wb_robot_cleanup();
  return 0;
}