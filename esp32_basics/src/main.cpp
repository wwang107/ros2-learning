// Step 1: blink the on-board LED (GPIO2 on most dev boards) and print to serial.
#include <Arduino.h>

#define LED_PIN 2

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  Serial.println("ESP32 basics: hello");
}

void loop() {
  static uint32_t n = 0;
  digitalWrite(LED_PIN, HIGH);
  Serial.printf("blink %lu: LED on\n", (unsigned long)n);
  delay(500);
  digitalWrite(LED_PIN, LOW);
  Serial.printf("blink %lu: LED off\n", (unsigned long)n++);
  delay(500);
}
