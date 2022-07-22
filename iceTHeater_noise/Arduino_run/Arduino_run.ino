//Written by Shilling Du 7/11/2022
#define RelayPin 6 //Define the output channel on arduino uno
double Output = 0; //Define Variables the python sent, the power level in percent, 0 means no power, 100 means full power

unsigned long now = millis();
unsigned long then = millis();
bool heaterState = false;
const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;

void setup()
{
   // initialize serial communication:
  Serial.begin(9600);
  Serial.setTimeout(1);
  // initialize the LED pin as an output:
  pinMode(RelayPin, OUTPUT);
}

void loop()
{
  //Receieve from python
  recvWithStartEndMarkers();
  slowPWM(Output);
  Serial.println(Output);
  newData = false;
}

//Low frequency PWM for the solid state relay
void slowPWM(double setPer)
{
  double windowsize = 3000;
  double onTime = windowsize * setPer / 100;
  now = millis();
  if(now < then + onTime && heaterState==false) {
    //Turn heater on
    digitalWrite(RelayPin, HIGH);
    heaterState = true;
  }  
  else if(now > then + onTime && heaterState==true && now< then + windowsize) {
    //Turn heater off
    digitalWrite(RelayPin, LOW);
    heaterState = false;
  }
  else if(now>= then + windowsize){
    then = now;
    //Turn heater off
    digitalWrite(RelayPin, LOW);
    heaterState = false; 
  } 
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
 
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
    Output = atof(receivedChars);
}
