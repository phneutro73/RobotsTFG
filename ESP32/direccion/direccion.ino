#include <Arduino.h>

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

  // Iniciar comunicación serial
  Serial.begin(115200);

  // Configurar el canal PWM, frecuencia y resolución
  ledcSetup(0, 1000, 8);  // Canal 0, frecuencia 1kHz, 8 bits de resolución
  ledcSetup(1, 1000, 8);  // Canal 1, frecuencia 1kHz, 8 bits de resolución
  ledcAttachPin(pinENA, 0);  // Asociar pinENA al canal 0
  ledcAttachPin(pinENB, 1);  // Asociar pinENB al canal 1
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();  // Leer el comando del monitor serial

    switch (cmd) {
      case 'A':  // Motor A - solamente
        digitalWrite(pinIN3, HIGH);
        digitalWrite(pinIN4, LOW);
        ledcWrite(1, 128);  // Velocidad media
        Serial.println('A');
        delay(200);
        break;

      case 'D':  // Motor B - solamente
        digitalWrite(pinIN1, HIGH);
        digitalWrite(pinIN2, LOW);
        ledcWrite(0, 128);  // Velocidad media
        Serial.println('D');
        delay(200);
        break;

      case 'S':  // Ambos motores - adelante
        digitalWrite(pinIN1, HIGH);
        digitalWrite(pinIN2, LOW);
        digitalWrite(pinIN3, HIGH);
        digitalWrite(pinIN4, LOW);
        ledcWrite(0, 128);  // Máxima velocidad
        ledcWrite(1, 128);  // Máxima velocidad
        Serial.println('S');
        delay(200);
        break;

      case 'Z':  // Ambos motores - atrás
        digitalWrite(pinIN1, LOW);
        digitalWrite(pinIN2, HIGH);
        digitalWrite(pinIN3, LOW);
        digitalWrite(pinIN4, HIGH);
        ledcWrite(0, 128);  // Máxima velocidad
        ledcWrite(1, 128);  // Máxima velocidad
        Serial.println('Z');
        delay(200);
        break;

      default:
        // Detener todos los motores si se recibe un comando no reconocido
        ledcWrite(0, 0);
        ledcWrite(1, 0);
        break;
    }
  }
}
