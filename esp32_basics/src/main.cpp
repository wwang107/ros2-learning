// Step 2: read a push button on a GPIO pin.
//
// Wiring (breadboard):
//   one leg of button -> GPIO4
//   opposite leg      -> GND
//   (no resistor needed: we enable the ESP32's internal pull-up)
//
// With INPUT_PULLUP the pin idles HIGH (3.3V via the internal ~45k resistor).
// Pressing the button connects it to GND, so it reads LOW. Logic is "inverted":
//   released = HIGH, pressed = LOW.
#include <Arduino.h>

#define BUTTON_PIN 4
#define LED_PIN 2  // on-board LED on most dev boards

constexpr uint32_t DEBOUNCE_MS = 30;

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  Serial.println("Button demo: press the button on GPIO4");
}

void loop() {
  static int stableState = HIGH;     // last debounced state (HIGH = released)
  static int lastRaw = HIGH;         // last raw reading
  static uint32_t lastChangeMs = 0;  // when the raw reading last changed
  static uint32_t pressCount = 0;

  int raw = digitalRead(BUTTON_PIN);

  // A mechanical button "bounces": it flickers HIGH/LOW for a few ms when
  // pressed. Only accept a new state once it has been steady for DEBOUNCE_MS.
  if (raw != lastRaw) {
    lastRaw = raw;
    lastChangeMs = millis();
  }

  if (millis() - lastChangeMs >= DEBOUNCE_MS && raw != stableState) {
    stableState = raw;
    if (stableState == LOW) {
      pressCount++;
      Serial.printf("pressed  (count=%lu)\n", (unsigned long)pressCount);
    } else {
      Serial.println("released");
    }
  }

  digitalWrite(LED_PIN, stableState == LOW ? HIGH : LOW);
}
