#include <stdlib.h>
#include <webots/motor.h>
#include <webots/robot.h>
#include <webots/light_sensor.h>
#include <webots/emitter.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>

// cppcheck-suppress constParameter
int main(int argc, char *argv[]) {
  wb_robot_init();
  assert(argc == 3);  // speed and timer expected as argument.

  const int timestep = (int)wb_robot_get_basic_time_step();

  double speed;
  sscanf(argv[1], "%lf", &speed);

  double timer;
  sscanf(argv[2], "%lf", &timer);
  
  // Declare and initialize light sensors  
  WbDeviceTag ls1 = wb_robot_get_device("Pillar_LS1");
  WbDeviceTag ls2 = wb_robot_get_device("Pillar_LS2");
  WbDeviceTag belt_emitter = wb_robot_get_device("BeltEmitter");
  wb_light_sensor_enable(ls1, timestep);
  wb_light_sensor_enable(ls2, timestep);
  

  // Set up motor
  WbDeviceTag belt_motor = wb_robot_get_device("belt_motor");
  wb_motor_set_position(belt_motor, INFINITY);
  wb_motor_set_velocity(belt_motor, speed);

  bool belt_running = true;

  while (wb_robot_step(timestep) != -1) {
    double ls1_value = wb_light_sensor_get_value(ls1);
    double ls2_value = wb_light_sensor_get_value(ls2);
 
    // Check timer condition
    if (timer > 0 && wb_robot_get_time() >= timer) {
      wb_motor_set_velocity(belt_motor, 0.0);
      break;
    }

    // Pause conveyor if both sensors < 100
    if (ls1_value < 100.0 && ls2_value < 100.0 && belt_running) {
      wb_motor_set_velocity(belt_motor, 0.0);
      belt_running = false;
      
      //send signal for crane to pickup crate
      const char *signal1 = "1";  // String "1"
      wb_emitter_send(belt_emitter, signal1, strlen(signal1));
      printf("Emitted: %s\n", signal1);
    }

    // Resume conveyor if both sensors >= 100
    if (ls1_value >= 100.0 && ls2_value >= 100.0 && !belt_running) {
      wb_motor_set_velocity(belt_motor, speed);
      belt_running = true;
      const char *signal01 = "0";  // String "0"
      wb_emitter_send(belt_emitter, signal01, strlen(signal01));
      printf("Emitted: %s\n", signal01);
    }
  }

  wb_robot_cleanup();
  return EXIT_SUCCESS;
}
