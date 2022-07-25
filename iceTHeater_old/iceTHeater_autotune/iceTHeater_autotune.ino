//Written by Jeff Ahlers 6/21/2020
//Modified by Shilling Du 11/1/2020
#include <PID_v1.h>
#include <PID_AutoTune_v0.h>
#define RelayPin 6
//Define Variables we'll be connecting to
double Setpoint, GetPoint, Input, Output;

//Specify the links and initial tuning parameters
//No idea if the default Kp Ki Kd are correct

double aggKp = 1, aggKi = 0.1, aggKd = 10;
//double consKp = 50, consKi = 0.1, consKd = 1;

byte ATuneModeRemember=2;
double kpmodel=1.5, taup=100, theta[50];
double outputStart=5;
double aTuneStep=5000, aTuneNoise=1, aTuneStartValue=5;
unsigned int aTuneLookBack=20;

boolean tuning = false;
unsigned long  modelTime, serialTime;


PID myPID(&Input, &Output, &Setpoint, aggKp, aggKi, aggKd, DIRECT);
PID_ATune aTune(&Input, &Output);

//set to false to connect to the real world
boolean useSimulation = false;

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
  Setpoint = 0;
  GetPoint = 0;
  Input = GetPoint;
  myPID.SetOutputLimits(0, 100);
  
  if(useSimulation)
  {
    for(byte i=0;i<50;i++)
    {
      theta[i]=outputStart;
    }
  }
  //Setup the pid 
  myPID.SetMode(AUTOMATIC);

  if(tuning)
  {
    tuning=false;
    changeAutoTune();
    tuning=true;
  }
  
  serialTime = 0;
  Serial.begin(9600);
  digitalWrite(RelayPin, LOW);
}

void loop()
{
  computeNow = millis();
  
  if (computeNow >= computeThen + 3000)
  {
    Input = GetPoint;
    if(tuning)
    {
      byte val = (aTune.Runtime());
      if (val!=0)
      {
        tuning = false;
      }
      if(!tuning)
      { //we're done, set the tuning parameters
         aggKp = aTune.GetKp();
         aggKi = aTune.GetKi();
         aggKd = aTune.GetKd();
         myPID.SetTunings(aggKp,aggKi,aggKd);
         AutoTuneHelper(false);
      }
      if(useSimulation)
      {
       theta[30]=Output;
       DoModel();
      }
      else{digitalWrite(RelayPin, LOW);}
    }
    else{myPID.Compute();}
    /*
    if (Input - Setpoint >= 0)
    {
      //Down parameters
      //myPID.SetTunings(consKp, consKi, consKd);
      myPID.SetTunings(aggKp, aggKi, aggKd);
    }

    else
    {
      //Up parameters
      myPID.SetTunings(aggKp, aggKi, aggKd);
      
    }
    myPID.Compute();
    */
    computeThen = computeNow;  
  }
  manageSerial();
  slowPWM(Output);
  SerialSend();
  
  
  //Display status message
  /*
  statusNow = millis();
  if (statusNow >= statusThen + 5000)
  {
    
    statusThen = statusNow;
    Serial.print("The time is: ");
    Serial.print(statusNow);
    Serial.print(" The setpoint is: ");
    Serial.print(Setpoint);
    Serial.print(". The current temperature is: ");
    Serial.println(GetPoint);   
  }
  */ 
}

void changeAutoTune()
  {
   if(!tuning)
    {
     //Set the output to the desired starting frequency.
     Output = aTuneStartValue;
     aTune.SetNoiseBand(aTuneNoise);
     aTune.SetOutputStep(aTuneStep);
     aTune.SetLookbackSec((int)aTuneLookBack);
     AutoTuneHelper(true);
     tuning = true;
   }
    else
    { //cancel autotune
      aTune.Cancel();
      tuning = false;
      AutoTuneHelper(false);
    }
  }

void AutoTuneHelper(boolean start)
  {
    if(start)
      ATuneModeRemember = myPID.GetMode();
    else
      myPID.SetMode(ATuneModeRemember);
  }


void DoModel()
  {
    //cycle the dead time
    for(byte i=0;i<49;i++)
    {
      theta[i] = theta[i+1];
    }
    //compute the input
    Input = (kpmodel / taup) *(theta[0]-outputStart) + Input*(1-1/taup) + ((float)random(-10,10))/100;
  }

//Low frequency PWM for the solid state relay
void slowPWM(double setPer)
{
  
  double windowsize = 200;
  double onTime = windowsize * setPer / 100;
  now = millis();
  if (now >= then + windowsize-onTime && heaterState==false) {
    //Turn heater on
    digitalWrite(RelayPin, HIGH);
    heaterState = true;
  } else if (now >= then + windowsize && heaterState==true) {
    //Turn heater off
    digitalWrite(RelayPin, LOW);
    heaterState = false;
    then = now;  
  }
}




void SerialSend()
{
  if(tuning){
    Serial.println("tuning mode");
  } else {
    Serial.print("kp: ");Serial.print(myPID.GetKp());Serial.print(" ");
    Serial.print("ki: ");Serial.print(myPID.GetKi());Serial.print(" ");
    Serial.print("kd: ");Serial.print(myPID.GetKd());Serial.print(" ");
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
          /*
          Serial.print("Setpoint set to: ");
          Serial.println(Setpoint);
          */
          break;
        case tempGet:
          GetPoint = serialBufferReading;
          changeAutoTune();
          /*
          Serial.print("GetPoint set to: ");
          Serial.println(GetPoint);
          */
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
