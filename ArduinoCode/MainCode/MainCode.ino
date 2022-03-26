//including the libraries
#include <AFMotor.h>
#include <Servo.h>

// servos stuff
Servo servo1, servo2, servo3;

#define Servo1Pin 9 
#define Servo2Pin 10 
#define Servo3Pin 11 

//defining pins and variables
#define lefts A0 
#define rights A1

bool driving = false;
bool pick_up = false, put_down = false;
String msg = "";

//defining motors
AF_DCMotor motor1(4, MOTOR12_8KHZ); 
AF_DCMotor motor2(3, MOTOR12_8KHZ);
/*
AF_DCMotor motor1(3, MOTOR12_8KHZ); 
AF_DCMotor motor2(4, MOTOR12_8KHZ);
 */


void setup() {
  //setting the speed of motors
  motor1.setSpeed(200); // max 255 i think
  motor2.setSpeed(200);

  // init sensors
  pinMode(lefts, INPUT);
  pinMode(rights, INPUT);

  // servos
  servo1.attach(Servo1Pin);
  servo2.attach(Servo2Pin);
  servo3.attach(Servo3Pin);
  
  //declaring pin types
  //begin serial communication
  Serial.begin(9600);
  Serial.setTimeout(1);
  
}


int currentRobotArmStep = 0;
int last_robot_arm_movement=0;
int last_Step = 2;
void loop(){
  //printing values of the sensors to the serial monitor
  
  //Serial.println(String(analogRead(lefts)) + " " + String(analogRead(rights)));
  readSerial();


  // this just suggests to the robot arm to keep moving to do the pickup act
  if(pick_up){
    if(millis() - last_robot_arm_movement > 200){
      currentRobotArmStep += 1;
      last_robot_arm_movement = millis();
      if(currentRobotArmStep>last_Step) currentRobotArmStep = last_Step;
    }

    // apply the currently wanted position
    switch(currentRobotArmStep){ // these steps need to perform an action and then completely come back to rest position
      case 0:
        servo1.write(0);
        servo2.write(0);
        servo3.write(0);
        break;
      case 1:
        servo1.write(90);
        servo2.write(90);
        servo3.write(90);
        break;
      case 2: // the last step is supposed to be identical to first step
        servo1.write(0);
        servo2.write(0);
        servo3.write(0);
        break;
    }
  }
  
  if(driving){
    //line detected by both
    if(analogRead(lefts)<=400 && analogRead(rights)<=400){
      //stop
      motor1.run(RELEASE);
      motor2.run(RELEASE);
    }
    //line detected by left sensor
    else if(analogRead(lefts)<=400 && !analogRead(rights)<=400){
      //turn left
      motor1.run(BACKWARD);
      motor2.run(FORWARD);
    }
    //line detected by right sensor
    else if(!analogRead(lefts)<=400 && analogRead(rights)<=400){
      //turn right
      motor1.run(FORWARD);
      motor2.run(BACKWARD);
    }
    //line detected by none
    else if(!analogRead(lefts)<=400 && !analogRead(rights)<=400){
      //stop
      motor1.run(FORWARD);
      motor2.run(FORWARD);
    }
  }
  
}


void treat_command(){
  Serial.println(msg);
  
  String command = getValue(msg, ' ', 0);
  if (command == "INIT") {
    driving = true;
    Serial.println("Ok, inited");
    return;
  }
  
  if (command == "MOVE") {
    driving = true;
    Serial.println("Ok, moving");
    return;
  }

  if (command == "STOP") {
    driving = true; 
    Serial.println("Ok, stopping");
    return;
  }

  if (command == "PICKUP") {
    pick_up = true;
    currentRobotArmStep = 0;
    Serial.println("Ok, gonna pick up");
    return;
  }

  Serial.println("OOF, Unknown command " + String(msg));
}


void readSerial(){
  /*if (Serial.available()) {
    char lil = Serial.read();
    if (lil == '\n') {
      treat_command();
      msg = "";
    } else {
      msg.concat(lil);
    }
  }*/
  if(Serial.available()){
    msg = Serial.readStringUntil('\n');
    treat_command();
  }
}

String getValue(String data, char separator, int index) {
  int found = 0;
  int strIndex[] = { 0, -1 };
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++) {
    if (data.charAt(i) == separator || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}
