#include <Arduino.h>
#include <IRremote.hpp>

#define IR_REC_PIN 14
#define FEEDBACK_LED_PIN 13

void setup() {
  Serial.begin(9600);
  IrReceiver.begin(IR_REC_PIN, true);
  pinMode(FEEDBACK_LED_PIN, OUTPUT);
}

void loop() {
  Serial.print("HELLO FROM ESP32!");
  if (IrReceiver.decode()) {
    digitalWrite(FEEDBACK_LED_PIN, HIGH);
    IrReceiver.printIRResultShort(&Serial);
    IrReceiver.resume();
  } else {
    digitalWrite(FEEDBACK_LED_PIN, LOW);
  }
  delay(1000);
}