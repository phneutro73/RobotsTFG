#include <esp_now.h>
#include <WiFi.h>

//Right motor
int enableRightMotor=4; 
int rightMotorPin1=2;
int rightMotorPin2=15;
//Left motor
int enableLeftMotor=14;
int leftMotorPin1=13;
int leftMotorPin2=12;

#define MAX_MOTOR_SPEED 127

const int PWMFreq = 1000; /* 1 KHz */
const int PWMResolution = 8;
const int rightMotorPWMSpeedChannel = 4;
const int leftMotorPWMSpeedChannel = 5;

#define SIGNAL_TIMEOUT 1000  // This is signal timeout in milli seconds. We will reset the data if no signal
unsigned long lastRecvTime = 0;

// callback function that will be executed when data is received
void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) 
{
  if (len == 0)
  {
    return;
  }
  char cmd = (char)incomingData[0];
  
  controlMotor(cmd);
  lastRecvTime = millis();   
}

void setUpPinModes()
{
  pinMode(enableRightMotor,OUTPUT);
  pinMode(rightMotorPin1,OUTPUT);
  pinMode(rightMotorPin2,OUTPUT);
  
  pinMode(enableLeftMotor,OUTPUT);
  pinMode(leftMotorPin1,OUTPUT);
  pinMode(leftMotorPin2,OUTPUT);

  //Set up PWM for motor speed
  ledcSetup(rightMotorPWMSpeedChannel, PWMFreq, PWMResolution);
  ledcSetup(leftMotorPWMSpeedChannel, PWMFreq, PWMResolution);  
  ledcAttachPin(enableRightMotor, rightMotorPWMSpeedChannel);
  ledcAttachPin(enableLeftMotor, leftMotorPWMSpeedChannel); 
}

void stopMotors(){
  digitalWrite(rightMotorPin1, LOW);
  digitalWrite(rightMotorPin2, LOW);
  digitalWrite(leftMotorPin1, LOW);
  digitalWrite(leftMotorPin2, LOW);
  ledcWrite(enableRightMotor, 0);
  ledcWrite(enableLeftMotor, 0);
}

void controlMotor(char cmd) {
  Serial.println(cmd);
  switch (cmd) {
    case 'A':  // Motor A - solamente
        digitalWrite(rightMotorPin1, LOW);
        digitalWrite(rightMotorPin2, HIGH);
        digitalWrite(leftMotorPin1, LOW);
        digitalWrite(leftMotorPin2, LOW);
        ledcWrite(enableRightMotor, MAX_MOTOR_SPEED); 
        ledcWrite(enableLeftMotor, MAX_MOTOR_SPEED); 
        delay(100);
        stopMotors();

      case 'D':  // Motor B - solamente
        digitalWrite(rightMotorPin1, LOW);
        digitalWrite(rightMotorPin2, LOW);
        digitalWrite(leftMotorPin1, LOW);
        digitalWrite(leftMotorPin2, HIGH);
        ledcWrite(enableRightMotor, MAX_MOTOR_SPEED); 
        ledcWrite(enableLeftMotor, MAX_MOTOR_SPEED);
        delay(100);
        stopMotors();

      case 'S':  // Ambos motores - adelante
        
        digitalWrite(rightMotorPin1, LOW);
        digitalWrite(rightMotorPin2, HIGH);
        digitalWrite(leftMotorPin1, LOW);
        digitalWrite(leftMotorPin2, HIGH);
        ledcWrite(enableRightMotor, MAX_MOTOR_SPEED); 
        ledcWrite(enableLeftMotor, MAX_MOTOR_SPEED); 
        delay(100);
        stopMotors();

      case 'Z':  // Ambos motores - atrás
        digitalWrite(rightMotorPin1, HIGH);
        digitalWrite(rightMotorPin2, LOW);
        digitalWrite(leftMotorPin1, HIGH);
        digitalWrite(leftMotorPin2, LOW);
        ledcWrite(enableRightMotor, MAX_MOTOR_SPEED); 
        ledcWrite(enableLeftMotor, MAX_MOTOR_SPEED);
        delay(100);
        stopMotors();

      default:
        // Detener todos los motores si se recibe un comando no reconocido
        stopMotors();
  }
}

void setup() 
{
  setUpPinModes();
  
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK) 
  {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  esp_now_register_recv_cb(OnDataRecv);
}
 
void loop() 
{
  //Check Signal lost.
  unsigned long now = millis();
  if ( now - lastRecvTime > SIGNAL_TIMEOUT ) 
  {
    //stopMotors();
  }
}
