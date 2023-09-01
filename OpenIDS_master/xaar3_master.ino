#include <Wire.h>
#include <AccelStepper.h>
#include <Servo.h>
#include "Seeed_SHT35.h"

/*SAMD core* 습도센서 핀 설정. else쪽은 무시*/
#ifdef ARDUINO_SAMD_VARIANT_COMPLIANCE
  #define SDAPIN  20
  #define SCLPIN  21
  #define RSTPIN  7
  #define SERIAL SerialUSB
#else
  #define SDAPIN  A4
  #define SCLPIN  A5
  #define RSTPIN  2

  #define SERIAL Serial
#endif


Servo ACN_servo1;
Servo ACN_servo2;

Servo Detritylation_servo1;
Servo Detritylation_servo2;

Servo Oxidation_servo1;
Servo Oxidation_servo2;

Servo Blow_servo1; 
Servo Blow_servo2;

int bulk__solution_arduino = 0;
int aAT_arduino = 1;
int wGC_arduino = 2;

int pulse = 2;
int direct = 3;

int limit1 = A2;
int limit2 = A1;
int limit3 = A0;
String command;
long comd;

int limit_1_position = 0;
int limit_2_position = 7994;
int limit_3_position = 15973;
int max_position = 19900;
float temp,hum;

AccelStepper x_motor(AccelStepper::DRIVER, pulse, direct);
SHT35 sensor(SCLPIN);

void setup() {
  Wire.begin();
  // put your setup code here, to run once:

  x_motor.setMaxSpeed(3000);
  x_motor.setAcceleration(10000);
  x_motor.setCurrentPosition(0);

  
  Serial.begin(2400);
  pinMode(pulse, OUTPUT);
  pinMode(direct, OUTPUT);
  pinMode(limit1, INPUT);
  pinMode(limit2, INPUT);
  pinMode(limit3, INPUT);
  pinMode(4,OUTPUT);

  pinMode(12,OUTPUT);
  pinMode(13,OUTPUT);
  pinMode(6,OUTPUT);
  pinMode(7,OUTPUT);

  ACN_servo1.attach(14); 
  ACN_servo2.attach(15); 
  Blow_servo1.attach(16); 
  Blow_servo2.attach(17); 
  Detritylation_servo1.attach(18); 
  Detritylation_servo2.attach(19); 
  Oxidation_servo1.attach(22); 
  Oxidation_servo2.attach(23); 

  sensor.init(); //습도센서 초기화

  
}

void I2C(int arduino, String command){
  char data[100];
  Wire.beginTransmission(arduino);  // 0번 슬레이브와 통신 시작
  command.toCharArray(data, command.length()+1);
  Wire.write(data); // data 전송
  Wire.endTransmission(arduino); // 전송 종료
}

void x_init(){


    //ACN_servo1.write(110);
    //ACN_servo2.write(90);
    //Cover_up(Detritylation_servo1,Detritylation_servo2);
    //Cover_up(Oxidation_servo1,Oxidation_servo2);
    //Cover_up(Blow_servo1,Blow_servo2);
    x_motor.setMaxSpeed(10000);
    //x_motor.setCurrentPosition(0);
    x_motor.moveTo(-100000);
    while(analogRead(limit1)<1000&&analogRead(limit2)<1000&&analogRead(limit3)<1000){
      x_motor.run();
    }

    //Serial.println(x_motor.currentPosition());
    int now_position = x_motor.currentPosition();
    x_motor.setMaxSpeed(1500);
    x_motor.moveTo(now_position+100);
    x_motor.runToPosition();
    x_motor.setMaxSpeed(100);
    x_motor.moveTo(now_position-500);
    while(analogRead(limit1)<1000&&analogRead(limit2)<1000&&analogRead(limit3)<1000){
      x_motor.run();
    }

    //Serial.println(x_motor.currentPosition());
    if (digitalRead(limit1)){
      x_motor.setCurrentPosition(limit_1_position);
    }
    if (digitalRead(limit2)){
      x_motor.setCurrentPosition(limit_2_position);
    }
    if (digitalRead(limit3)){
      x_motor.setCurrentPosition(limit_3_position);
    }
    x_motor.setMaxSpeed(10000);
    Serial.println("done");

}


void Cover_up(Servo servo1, Servo servo2){

    servo1.write(100); 
    servo2.write(100); 
}

void Cover_down(Servo servo1, Servo servo2){

    servo1.write(30); 
    servo2.write(30); 

}

void MOVE(int Distance, int Speed){
  x_motor.setMaxSpeed(Speed);
  //ACN_servo1.write(110);
  //ACN_servo2.write(90);
  //Cover_up(Detritylation_servo1,Detritylation_servo2);
  //Cover_up(Oxidation_servo1,Oxidation_servo2);
  //Cover_up(Blow_servo1,Blow_servo2);
  //delay(500);

  if (Distance <= max_position){
  x_motor.moveTo(Distance);
  x_motor.runToPosition();
  x_motor.stop();
  }
}


void loop() {


 if(Serial.available()){

    command = Serial.readStringUntil(';');


   if (command == "x_init"){
        x_init();
        //x_check();
    }

  else if (command == "Waste-"){
        I2C(wGC_arduino, "Waste-");
    } 

  else if (command == "Waste+"){
        I2C(wGC_arduino, "Waste+");
    } 


  else if(command == "4"){//블로우

    
    MOVE(12900,10000);
    
    digitalWrite(4,HIGH);
    //Blow_servo1.write(10);
    //Blow_servo2.write(10);
    MOVE(14100,500);
    //Blow_servo1.write(80);
    //Blow_servo2.write(80);
    
    MOVE(12900,500);
    //Blow_servo1.write(10);
    //Blow_servo2.write(10);
    
    digitalWrite(4,LOW);
    Serial.print("done");

  }

  else if(command == "Valve_open"){
    digitalWrite(4,HIGH);
    delay(3000);
    digitalWrite(4,LOW);
  }



  else if (command == "6"){//디트리틸레이션

    MOVE(15500,10000);

    //Detritylation_servo1.write(15); 
    //Detritylation_servo2.write(15);
    //I2C(bulk__solution_arduino, "Detritylation{1000}2000");
    Serial.print("done");
    
    

    
  }

  else if (command == "8"){//워시

    MOVE(10200,10000);

    //ACN_servo1.write(40); 
    //ACN_servo2.write(20);
    I2C(bulk__solution_arduino, "Wash{1000}5000");
    Serial.print("done");


}


  else if(command == "12"){//옥시데이션
    MOVE(18600,10000);
    //Oxidation_servo1.write(25); 
    //Oxidation_servo2.write(15);
    I2C(bulk__solution_arduino, "Oxidation{300}1000");
    Serial.print("done");
}


  else if (command.indexOf("aAT") == 0){
    command = command.substring(3);

    I2C(aAT_arduino, command);

}

  else if (command.indexOf("wGC") == 0){
    command = command.substring(3);

    I2C(wGC_arduino, command);

}



  else if (command =="Q"){
      Serial.println("done");
  } 
  
  else if(command[0]=='x'){
      MOVE(command.substring(1).toInt(),10000);
      Serial.print("done");

  }



  //이게 원래의 프린팅 함수!!!!!!!!!!!!!!!!!!
  else if (command == "P"){

    x_motor.setMaxSpeed(1000);
    x_motor.moveTo(600);
    x_motor.runToPosition();
    x_motor.setMaxSpeed(10000);
    Serial.print("done");
    
  }

  else if (command == "A_Flush"){
    x_motor.setMaxSpeed(10000);
    x_motor.moveTo(14000);
    x_motor.runToPosition();
    x_motor.setMaxSpeed(10000);
    Serial.print("done");
  }
  
  else if (command == "Act_Flush"){
    x_motor.setMaxSpeed(10000);
    x_motor.moveTo(13700);
    x_motor.runToPosition();
    x_motor.setMaxSpeed(10000);
    Serial.print("done");
  }

  else if (command == "T_Flush"){
    x_motor.setMaxSpeed(10000);
    x_motor.moveTo(14300);
    x_motor.runToPosition();
    x_motor.setMaxSpeed(10000);
    Serial.print("done");
  }

  else if (command == "Get_humidity"){
    u16 value=0;
    u8 data[6]={0};
    if(NO_ERROR!=sensor.read_meas_data_single_shot(HIGH_REP_WITH_STRCH,&temp,&hum)){
        SERIAL.print("humidity Error");
    }
    else{
      Serial.print(temp);
      Serial.print("C ");
      Serial.print(hum);
      Serial.print("%done");
    }
  }

  else if (command[0] == 't'){
    int dis = command.substring(1).toInt();
    analogWrite(7,200);
    analogWrite(6,dis);
    Serial.println(dis);
    Serial.println("t1t1t1");
    digitalWrite(12,LOW);
    digitalWrite(13,LOW);

    delay(1000);
    Serial.println("t2t2t2");
    digitalWrite(12,HIGH);
    digitalWrite(13,LOW);
  }


 
 }
}
