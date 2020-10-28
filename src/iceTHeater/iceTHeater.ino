//Written by Jeff Ahlers 6/21/2020
#include <PID_v1.h>
#define RelayPin 6
//Define Variables we'll be connecting to
double Setpoint, GetPoint, Input, Output;

//Specify the links and initial tuning parameters
//No idea if the default Kp Ki Kd are correct
double aggKp = 4, aggKi = .2, aggKd = 1; 
//double aggKp = .1, aggKi = .1, aggKd = 10;
double consKp = 1, consKi = .05, consKd = 0.25;
//double consKp = 50, consKi = .1, consKd = 1;

PID myPID(&Input, &Output, &Setpoint, consKp, consKi, consKd, DIRECT);

unsigned long now = millis();
unsigned long then = millis();

unsigned long statusNow = millis();
unsigned long statusThen = millis();

unsigned long computeNow = millis();
unsigned long computeThen = millis();
bool heaterState = false;

enum SerialState
{
  idle,
  magic,
  tempCom,
  d1,
  d2,
  d3,
  dp,
  d5,
  d6,
  finalizing
};

enum CommandState
{
  noCommand,
  tempSet,
  tempGet
};

double serialBufferReading = 0;
SerialState state = idle;
CommandState commandState = noCommand;
int i = 0;
void setup()
{
  pinMode(RelayPin, OUTPUT);
  Setpoint = 166;
  GetPoint = 165;
  Input = GetPoint;
  myPID.SetOutputLimits(0, 100);
  //Turn the PID on
  myPID.SetMode(AUTOMATIC);
  Serial.begin(9600);
  digitalWrite(RelayPin, LOW);
}

void loop()
{
  computeNow = millis();
  if (computeNow >= computeThen + 3000)
  {
    Input = GetPoint;
    if (Input - Setpoint >= 0)
    {
      //Down parameters
      myPID.SetTunings(consKp, consKi, consKd);
    }

    else
    {
      //Up parameters
      myPID.SetTunings(aggKp, aggKi, aggKd);
    }
    myPID.Compute();
    computeThen = computeNow;  
  }
  slowPWM(Output);
  manageSerial();

  //Display status message
  statusNow = millis();
  if (statusNow >= statusThen + 5000)
  {
    /*
    statusThen = statusNow;
    Serial.print("The time is: ");
    Serial.print(statusNow);
    Serial.print(" The setpoint is: ");
    Serial.print(Setpoint);
    Serial.print(". The current temperature is: ");
    Serial.println(GetPoint);   
    */ 
  }
}
//Low frequency PWM for the solid state relay
void slowPWM(double setPer)
{
  
  double windowsize = 1000;
  double onTime = windowsize * setPer / 100;
  now = millis();
  if (now >= then + onTime && heaterState) {
    //Turn heater off
    digitalWrite(RelayPin, LOW);
    heaterState = false;
  } else if (now >= then + windowsize) {
    //Turn heater on
    digitalWrite(RelayPin, HIGH);
    heaterState = true;
    then = now;  
  }
}
void manageSerial(){
  //Valid command format "CS ###.##E". Example: "CS 090.30E" for temperature setpoint of 90.30 C
  //Commands:
  // CS: Set temp
  // CG: Input temp
  if (Serial.available() > 0)
  {
    delay(100);
    switch (state)
    {
    case idle:
      //Look for magic number C
      if (Serial.read() == 67)
      {
        state = magic;
      }
      break;
    case magic:
      //Look for command type
      i = Serial.read();
      switch (i)
      {
      case 83:
        state = tempCom;
        commandState = tempSet;
        break;
      case 71:
        state = tempCom;
        commandState = tempGet;
        break;
      default:
        state = idle;
        commandState = noCommand;
        break;
      }
      break;

    //Look for space
    case tempCom:
      if (Serial.read() == 32)
      {
        state = d1;
      }
      else
      {
        state = idle;
        commandState = noCommand;
      }
      break;
    //Look for digits with validation
    case d1:
      i = Serial.read();
      serialBufferReading = 0;
      if (i >= 48 && i <= 57)
      {
        serialBufferReading += (i - 48) * 100;
        state = d2;
      }
      else
      {
        state = idle;
        commandState = noCommand;
        serialBufferReading = 0;
      }
      break;
    case d2:
      i = Serial.read();
      if (i >= 48 && i <= 57)
      {
        serialBufferReading += (i - 48) * 10;
        state = d3;
      }
      else
      {
        state = idle;
        commandState = noCommand;
        serialBufferReading = 0;
      }
      break;
    case d3:
      i = Serial.read();
      if (i >= 48 && i <= 57)
      {
        serialBufferReading += (i - 48);
        state = dp;
      }
      else
      {
        state = idle;
        commandState = noCommand;
        serialBufferReading = 0;
      }
      break;
    case dp:
      if (Serial.read() == 46)
      {
        state = d5;
      }
      else
      {
        state = idle;
        commandState = noCommand;
        serialBufferReading = 0;
      }
      break;
    case d5:
      i = Serial.read();
      if (i >= 48 && i <= 57)
      {
        serialBufferReading += (i - 48) * 0.1;
        state = d6;
      }
      else
      {
        state = idle;
        commandState = noCommand;
        serialBufferReading = 0;
      }
      break;
    case d6:
      i = Serial.read();
      if (i >= 48 && i <= 57)
      {
        serialBufferReading += (i - 48) * 0.01;
        state = finalizing;
      }
      else
      {
        state = idle;
        commandState = noCommand;
        serialBufferReading = 0;
      }
      break;
    //Look for exit code E
    case finalizing:
      if (Serial.read() == 69)
      {
        switch (commandState)
        {
        case tempSet:
          Setpoint = serialBufferReading;
          Serial.print("Setpoint set to: ");
          Serial.println(Setpoint);
          break;
        case tempGet:
          GetPoint = serialBufferReading;
          Serial.print("GetPoint set to: ");
          Serial.println(GetPoint);
          break;
        default:
          break;
        }
        serialBufferReading = 0;
        state = idle;
        commandState = noCommand;
      }
      else
      {
        serialBufferReading = 0;
        state = idle;
        commandState = noCommand;
      }
      break;
    }
  }
}
