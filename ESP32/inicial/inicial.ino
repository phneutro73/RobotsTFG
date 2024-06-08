#include <Arduino.h>

const int pinIN1 = 26;
const int pinIN2 = 27;
const int pinENA = 25;

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
  ledcAttachPin(pinENA, 0);  // Asociar el pinENA al canal 0
  ledcAttachPin(pinENB, 1);  // Asociar el pinENB al canal 1
}

void loop() {
  // Rotación en sentido horario (CW) a baja velocidad
  digitalWrite(pinIN1, HIGH);
  digitalWrite(pinIN2, LOW);
  digitalWrite(pinIN3, HIGH);
  digitalWrite(pinIN4, LOW);
  ledcWrite(0, 96);  // PWM a mitad de velocidad (128 de 255)
  ledcWrite(1, 96);  // PWM a mitad de velocidad (128 de 255)
  delay(3000);  // Esperar 3 segundos

  // Rotación en sentido antihorario (CCW) a baja velocidad
  digitalWrite(pinIN1, LOW);
  digitalWrite(pinIN2, HIGH);
  digitalWrite(pinIN3, LOW);
  digitalWrite(pinIN4, HIGH);
  ledcWrite(0, 96);  // PWM a mitad de velocidad
  ledcWrite(1, 96);  // PWM a mitad de velocidad
  delay(3000);  // Esperar 3 segundos

}
