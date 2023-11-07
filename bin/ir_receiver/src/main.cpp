#include <Arduino.h>
#include <IRremote.hpp>

#define IR_REC_PIN 14
#define FEEDBACK_LED_PIN 12

bool validate_data(unsigned int);

void setup() {
  Serial.begin(9600);
  IrReceiver.begin(IR_REC_PIN, true);
  pinMode(FEEDBACK_LED_PIN, OUTPUT);
}

void loop() {
  if (IrReceiver.decode()) {
    digitalWrite(FEEDBACK_LED_PIN, HIGH);

    unsigned int data = IrReceiver.decodedIRData.decodedRawData;

    if (validate_data(data)) {
      Serial.print(data, HEX);
    }

    // IrReceiver.printIRResultShort(&Serial);
    IrReceiver.resume();
  }
  delay(500);
  digitalWrite(FEEDBACK_LED_PIN, LOW);
}

bool validate_data(unsigned int data) {
  if (data != 0) {
    return true;
  } else {
    return false;
  }
}