#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// RFID Setup
#define SS_PIN 10
#define RST_PIN 9
MFRC522 rfid(SS_PIN, RST_PIN);

// Servos
Servo servo1;
Servo servo2;
int servo1Pin = 2;
int servo2Pin = 5;

// LEDs, Buzzer, Relay
int greenLED = 7;
int redLED = 6;
int buzzer = 3;
int relayPin = 4;

// LCD
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Try 0x3F if needed

// Valid RFID card UID (edit to match your white card)
byte validCard[4] = {0x71, 0x4A, 0xA6, 0x08};  // Replace with your white card UID

// Invalid RFID card UID (blue tag - for testing)
byte invalidCard[4] = {0xCE, 0xA0, 0x56, 0xD3};  // Replace with your blue tag UID (example)

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();

  // Servo setup
  servo1.attach(servo1Pin);
  servo2.attach(servo2Pin);
  servo1.write(0);  // Closed
  servo2.write(0);  // Closed

  pinMode(greenLED, OUTPUT);
  pinMode(redLED, OUTPUT);
  pinMode(buzzer, OUTPUT);
  pinMode(relayPin, OUTPUT);

  // LCD setup
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("RFID Toll System");
  delay(2000);
  lcd.clear();
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;

  Serial.print("Card UID: ");
  for (byte i = 0; i < 4; i++) {
    if (rfid.uid.uidByte[i] < 0x10) Serial.print("0"); // Add leading zero
    Serial.print(rfid.uid.uidByte[i], HEX);
    Serial.print(" ");
  }
  Serial.println();

  // Check if card is valid or invalid
  if (isValidCard(rfid.uid.uidByte)) {
    openGate(); // White card detected
  } else if (isInvalidCard(rfid.uid.uidByte)) {
    denyAccess(); // Blue tag detected (or invalid)
  }

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();

  delay(1000); // Prevent multiple reads
}

bool isValidCard(byte *uid) {
  for (byte i = 0; i < 4; i++) {
    if (uid[i] != validCard[i]) return false;
  }
  return true;
}

bool isInvalidCard(byte *uid) {
  for (byte i = 0; i < 4; i++) {
    if (uid[i] != invalidCard[i]) return false;
  }
  return true;
}

void openGate() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Access Granted");

  digitalWrite(greenLED, HIGH);
  digitalWrite(redLED, LOW);
  digitalWrite(buzzer, LOW);
  digitalWrite(relayPin, HIGH);

  // Open both servos together
  servo1.write(90);
  servo2.write(90);
  delay(3000);  // Keep gate open for 3 seconds

  // Close both servos together
  servo1.write(0);
  servo2.write(0);

  digitalWrite(greenLED, LOW);
  digitalWrite(relayPin, LOW);
  lcd.clear();
}

void denyAccess() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Access Denied");

  digitalWrite(greenLED, LOW);
  digitalWrite(redLED, HIGH);
  digitalWrite(buzzer, HIGH);
  delay(2000);
  digitalWrite(redLED, LOW);
  digitalWrite(buzzer, LOW);
  lcd.clear();
}
