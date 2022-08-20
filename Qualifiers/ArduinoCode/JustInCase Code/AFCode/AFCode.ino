//including the libraries
#include <AFMotor.h>

//defining pins and variables
#define lefts A0 
#define rights A1

//defining motors
AF_DCMotor motor1(4, MOTOR12_8KHZ); 
AF_DCMotor motor2(3, MOTOR12_8KHZ);

void setup() {
  //setting the speed of motors
  motor1.setSpeed(200); // max 255 i think
  motor2.setSpeed(200);
  
  //declaring pin types
  //begin serial communication
  Serial.begin(9600);
  
  motor.run(FORWARD);
  delay(1000);  // run forward for 1 second
  motor.run(RELEASE);
  delay(100);  // 'coast' for 1/10 second
  motor.run(BACKWARD);  // run in reverse
  
}

void loop(){
  //printing values of the sensors to the serial monitor
  Serial.println(String(analogRead(lefts)) + " " + String(analogRead(rights)));
}
