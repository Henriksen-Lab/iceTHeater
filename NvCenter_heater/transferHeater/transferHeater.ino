//Written by Jeff Ahlers 6/21/2020
#include <PID_v1.h>
//#define relayPin B00001000
#define relayPin B00101000 //Pin 11 && 13
#define RTD A3


#include <Adafruit_MAX31865.h>
Adafruit_MAX31865 thermo = Adafruit_MAX31865(5, 6, 7, 8);

// The value of the Rref resistor. Use 430.0 for PT100 and 4300.0 for PT1000

#define RREF      430.0

// The 'nominal' 0-degrees-C resistance of the sensor
// 100.0 for PT100, 1000.0 for PT1000

#define RNOMINAL  100.0

//Define Variables we'll be connecting to
double Setpoint, Input, Output;

//Specify the links and initial tuning parameters
//No idea if the default Kp Ki Kd are correct
double aggKp=5, aggKi=0, aggKd=0;
double consKp=5, consKi=0, consKd=0;
const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;
PID myPID(&Input, &Output, &Setpoint, consKp, consKi, consKd, DIRECT);

unsigned long now = millis();
unsigned long then = millis();
bool heaterState = false;

unsigned long statusNow = millis();
unsigned long statusThen = millis();


unsigned long computeNow = millis();
unsigned long computeThen = millis();

enum serialState {
  idle,
  magic,
  tempCom,
  d1,
  d2,
  d3,
  d4,
  d5,
  finalizing
};

double unconfirmedSetpoint = 0;
serialState state = idle;
int i = 0;

void setup() {
  // Set pin 11 to output:
  DDRB = DDRB | relayPin;
  //Set pins 8-13 low
  PORTB = PORTB & B11000000;
  Setpoint = 0;
  Input = readRTD();
  myPID.SetOutputLimits(0, 100);
  //Turn the PID on
  myPID.SetMode(AUTOMATIC);
  Serial.begin(9600);
  thermo.begin(MAX31865_3WIRE);
}

void loop() {
  recvWithStartEndMarkers();
  computeNow = millis();
  if (computeNow >= computeThen + 200) {
    Input = readRTD();
    if(Input- Setpoint >= 0){
       myPID.SetTunings(consKp, consKi, consKd);
       //Serial.println("Down parameters"); 
    }

   else{ 
     myPID.SetTunings(aggKp, aggKi, aggKd);
     //Serial.println("Up parameters"); 
   }
    myPID.Compute();
    //Serial.print("Output is: ");
    //Serial.println(Output);
    computeThen = computeNow;
  }
  slowPWM(Output);
  SerialSend();
  
  //Display status message
  statusNow = millis();
  if (statusNow >= statusThen + 3000) {
    statusThen = statusNow;
    //Serial.print("The time is: ");
    //Serial.print(statusNow);
    //Serial.print(" The setpoint is: ");
    //Serial.print(Setpoint);
    //Serial.print(". The current temperature is: ");
    //Serial.println(readRTD());
  }
}
//Low frequency PWM for the solid state relay
void slowPWM(double setPer) {
  //In milliseconds
  double period = 1000 ;
  double onTime = period * setPer / 100;
 // Serial.print("Ontime: ");
  //CS 035.0E
  //Serial.println(onTime);
  now = millis();
  if (now >= then + onTime && heaterState) {
    //Turn heater off
    PORTB = PORTB & ~relayPin;
    heaterState = false;
  } else if (now >= then + period) {
    //Turn heater on
    PORTB = PORTB | relayPin;
    heaterState = true;
    then = now;
  }
}
//Read a temperature value. refResitance and the slope should be calibrated. Nominal: 100 Ohm refResist, 0.385 Ohm/C, 100 Ohm at 0 C
double readRTD() {
   uint16_t rtd = thermo.readRTD();

 // Serial.print("RTD value: "); Serial.println(rtd);
  float ratio = rtd;
  ratio /= 32768;
  //Serial.print("Ratio = "); Serial.println(ratio,8);
 // Serial.print("Resistance = "); Serial.println(RREF*ratio,8);
  double temperature = thermo.temperature(RNOMINAL, RREF);
 // Serial.print("Temperature = "); Serial.println(temperature);

  // Check and print any faults
  uint8_t fault = thermo.readFault();
  if (fault) {
    Serial.print("Fault 0x"); Serial.println(fault, HEX);
    if (fault & MAX31865_FAULT_HIGHTHRESH) {
      Serial.println("RTD High Threshold"); 
    }
    if (fault & MAX31865_FAULT_LOWTHRESH) {
      Serial.println("RTD Low Threshold"); 
    }
    if (fault & MAX31865_FAULT_REFINLOW) {
      Serial.println("REFIN- > 0.85 x Bias"); 
    }
    if (fault & MAX31865_FAULT_REFINHIGH) {
      Serial.println("REFIN- < 0.85 x Bias - FORCE- open"); 
    }
    if (fault & MAX31865_FAULT_RTDINLOW) {
      Serial.println("RTDIN- < 0.85 x Bias - FORCE- open"); 
    }
    if (fault & MAX31865_FAULT_OVUV) {
      Serial.println("Under/Over voltage"); 
    }
    thermo.clearFault();
  }
  //Serial.println();
  return temperature;
}


void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = 'k';
    char endMarker_1 = 'p';
    char endMarker_2 = 'i';
    char endMarker_3 = 'd';
    char endMarker_4 = 't';
    
    char rc;
    newData = false;
    
 
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();
        if (rc == startMarker && recvInProgress == false) {
            recvInProgress = true;
        }
        else if (rc == endMarker_1 && recvInProgress == true) {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
                aggKp = atof(receivedChars);
                consKp = atof(receivedChars);
            }
        else if(rc == endMarker_2 && recvInProgress == true) {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
                aggKi = atof(receivedChars);
                consKi = atof(receivedChars);
            }
        else if (rc == endMarker_3 && recvInProgress == true) {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
                aggKd = atof(receivedChars);
                consKd = atof(receivedChars);
            }
        else if (rc == endMarker_4&& recvInProgress == true) {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
                Setpoint = atof(receivedChars);
            }
        else if (recvInProgress == true) {
            receivedChars[ndx] = rc;
            ndx++;
            if (ndx >= numChars) {
              ndx = numChars - 1;
              }
            }
        else{
            recvInProgress = false;
        }
        }
        
    }



void SerialSend()
{
    Serial.print("<");
    Serial.print(Input);
    Serial.println(">");
    Serial.print("(");
    Serial.print(Setpoint);
    Serial.println(")");
    Serial.print("{");
    Serial.print(Output);
    Serial.println("}");
    Serial.print("$");
    Serial.print(aggKp);
    Serial.print(',');
    Serial.print(aggKi);
    Serial.print(',');
    Serial.print(aggKd);
    Serial.println("&");
}
