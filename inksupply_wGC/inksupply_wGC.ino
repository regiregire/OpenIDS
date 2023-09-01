#include <AccelStepper.h>
#include <Wire.h>
/*아두이노에 연결된 Pin번호*/
/* SET PIN NUMBER */

int x_direction = 2;
int y_direction = 3;
int z_direction = 4;

int x_pulse = 5;
int y_pulse = 6;
int z_pulse = 7;

bool x_flag = false;
bool y_flag = false;
bool z_flag = false;

long last_x;
long last_y;
long last_z;

int Enable = 8;

int x_air_sensor = A0;
int y_air_sensor = A1;
int z_air_sensor = A2;

AccelStepper x_motor(AccelStepper::DRIVER, x_pulse, x_direction);
AccelStepper y_motor(AccelStepper::DRIVER, y_pulse, y_direction);
AccelStepper z_motor(AccelStepper::DRIVER, z_pulse, z_direction);


String command;

unsigned long current_msTime;
unsigned long last_check_msTime;



void z_damper(){
  digitalWrite(Enable,LOW);
  z_motor.setMaxSpeed(100);  
  z_motor.setCurrentPosition(0); 
  z_motor.moveTo(3000);  
  if(analogRead(z_air_sensor)>800){
    while(analogRead(z_air_sensor)>800&&z_motor.run()){
    }
  last_z = millis();

  }

  if (millis() - last_z > 10000){
    z_motor.setCurrentPosition(0); 
    z_motor.moveTo(-3000);
    while(analogRead(z_air_sensor)<800&&z_motor.run()){
    }
    last_z = millis();
    Serial.println(millis() - last_z);
  }
  digitalWrite(Enable,HIGH);
}

void y_damper(){
  digitalWrite(Enable,LOW);
  y_motor.setMaxSpeed(100);  
  y_motor.setCurrentPosition(0); 
  y_motor.moveTo(3000);  

  if(analogRead(y_air_sensor)>800){
    while(analogRead(y_air_sensor)>800&&y_motor.run()){

    }
  last_y = millis();

  }

  if (millis() - last_y > 10000){
    y_motor.setCurrentPosition(0); 
    y_motor.moveTo(-3000);
    while(analogRead(y_air_sensor)<800&&y_motor.run()){
    }
    last_y = millis();
    Serial.println(millis() - last_y);
  }
  digitalWrite(Enable,HIGH);
}

void x_waste(){
  digitalWrite(Enable,LOW);
  x_motor.setMaxSpeed(1000);  
  x_motor.setCurrentPosition(0); 
  x_motor.moveTo(5000);  
  x_motor.runToPosition();
  
  digitalWrite(Enable,HIGH);
}

/* SETUP */
void setup() {
  Wire.begin(2);
  Wire.onReceive(receiveEvent);
  Serial.begin(9600);
  x_motor.setAcceleration(15000);
  y_motor.setAcceleration(15000);
  z_motor.setAcceleration(15000);


  pinMode(Enable,OUTPUT);
  pinMode(y_air_sensor,INPUT);
  pinMode(z_air_sensor,INPUT);




  last_check_msTime = millis();
  Serial.println("Setup");
}

void receiveEvent(int bytes) {
  command = "";
  while(Wire.available()){
  char c = Wire.read();
  command += String(c); 
  }
  Serial.println(command);
}



/* LOOP */
void loop() {

    if(command =="Waste-"){
    x_flag = true;
    Serial.println("됐어");
    command = "";
    
    }
  
    if(command =="Waste+"){
      x_flag = false;
      digitalWrite(Enable,LOW);
      Serial.println("Waste+");
      x_motor.setMaxSpeed(1000); 
      x_motor.setCurrentPosition(0);
      x_motor.moveTo(1500);
      x_motor.runToPosition();
      digitalWrite(Enable,HIGH);
      command = "";
    }
  

    if(command =="G-"){
    y_flag = true;
    command = "";
    }
  
    if(command =="G+"){
      y_flag = false;
      digitalWrite(Enable,LOW);
      Serial.println("G+");
      y_motor.setMaxSpeed(1000); 
      y_motor.setCurrentPosition(0);
      y_motor.moveTo(-1500);
      y_motor.runToPosition();
      digitalWrite(Enable,HIGH);
      command = "";
    }
  
    if(command =="C-"){
    z_flag = true;
    command = "";
    }
  
    if(command =="C+"){
      z_flag = false;
      digitalWrite(Enable,LOW);
      Serial.println("C+");
      z_motor.setMaxSpeed(1000); 
      z_motor.setCurrentPosition(0);
      z_motor.moveTo(-1500);
      z_motor.runToPosition();
      digitalWrite(Enable,HIGH);
      command = "";

    }

   if (x_flag==true){
    x_waste();
   }

   if (y_flag==true){
    y_damper();
   }

   if (z_flag==true){
    z_damper();
   }

   
    
  
}
