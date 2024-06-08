#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>

#define MAX_MOTOR_SPEED 100

// Pines de control para el Motor A
const int pinIN1 = 2;
const int pinIN2 = 15;
const int pinENA = 4;

// Pines de control para el Motor B
const int pinIN3 = 13;
const int pinIN4 = 12;
const int pinENB = 14;

void setup() {
  // Configurar los pines como salidas
  pinMode(pinIN1, OUTPUT);
  pinMode(pinIN2, OUTPUT);
  pinMode(pinENA, OUTPUT);
  pinMode(pinIN3, OUTPUT);
  pinMode(pinIN4, OUTPUT);
  pinMode(pinENB, OUTPUT);

  // Configurar el canal PWM, frecuencia y resolución
  ledcSetup(0, 1000, 8);  // Canal 0, frecuencia 1kHz, 8 bits de resolución
  ledcSetup(1, 1000, 8);  // Canal 1, frecuencia 1kHz, 8 bits de resolución
  ledcAttachPin(pinENA, 0);  // Asociar pinENA al canal 0
  ledcAttachPin(pinENB, 1);  // Asociar pinENB al canal 1

  // Iniciar comunicación serial
  Serial.begin(115200);

  Serial.println("--- Slave ESPnow ---");

  Serial.println(WiFi.macAddress());
  
    // Iniciar WiFi en modo STA
  WiFi.mode(WIFI_STA);

  // Iniciar ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  } else {
    Serial.println("Success: Initialized ESP-NOW");
  }

  esp_now_register_recv_cb(OnDataRecv);
}

void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
  Serial.print("Datos recibidos: ");
  for (int i = 0; i < len; i++) {
    Serial.print((char)incomingData[i]);
  }
  Serial.println();
  char cmd = (char)incomingData[0];
  controlMotor(cmd);
}

void stopMotors(){
  ledcWrite(0, 0);
  ledcWrite(1, 0);
  digitalWrite(pinIN1, LOW);
  digitalWrite(pinIN2, LOW);
  digitalWrite(pinIN3, LOW);
  digitalWrite(pinIN4, LOW);
}

void backToInit(){
  delay(100);
  stopMotors();
}

void controlMotor(char cmd) {
  Serial.println(cmd);
  switch (cmd) {
      case 'A':  // Motor A - solamente
        digitalWrite(pinIN3, HIGH);
        digitalWrite(pinIN4, LOW);
        ledcWrite(1, MAX_MOTOR_SPEED); 
        backToInit();
        break;

      case 'D':  // Motor B - solamente
        digitalWrite(pinIN1, HIGH);
        digitalWrite(pinIN2, LOW);
        ledcWrite(0, MAX_MOTOR_SPEED);  
        backToInit();
        break;

      case 'S':  // Ambos motores - adelante
        digitalWrite(pinIN1, HIGH);
        digitalWrite(pinIN2, LOW);
        digitalWrite(pinIN3, HIGH);
        digitalWrite(pinIN4, LOW);
        ledcWrite(0, MAX_MOTOR_SPEED);  
        ledcWrite(1, MAX_MOTOR_SPEED);  
        backToInit();
        break;

      case 'Z':  // Ambos motores - atrás
        digitalWrite(pinIN1, LOW);
        digitalWrite(pinIN2, HIGH);
        digitalWrite(pinIN3, LOW);
        digitalWrite(pinIN4, HIGH);
        ledcWrite(0, MAX_MOTOR_SPEED);  // Máxima velocidad
        ledcWrite(1, MAX_MOTOR_SPEED);  // Máxima velocidad
        backToInit();
        break;

      default:
        // Detener todos los motores si se recibe un comando no reconocido
        backToInit();
        break;
    }
}

void loop() {
  // No se necesita hacer nada en el loop
}
