#define ENA3 10  // Motor A speed control
#define IN1A3 8  // Motor A direction 1
#define IN2A3 9  // Motor A direction 2

#define ENA4 11  // Motor B speed control
#define IN1A4 6 // Motor B direction 1
#define IN2A4 7 // Motor B direction 2

void setup() {
  Serial.begin(9600); // Initialize serial communication

  // Set motor control pins as outputs
  pinMode(ENA3, OUTPUT);
  pinMode(IN1A3, OUTPUT);
  pinMode(IN2A3, OUTPUT);

  pinMode(ENA4, OUTPUT);
  pinMode(IN1A4, OUTPUT);
  pinMode(IN2A4, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read the command

    if (command == "A3") {
      // Motor A: Forward at 75% speed
      analogWrite(ENA3, 191); // 75% of 255
      digitalWrite(IN1A3, HIGH);
      digitalWrite(IN2A3, LOW);
      delay(2000); // Run for 2 seconds
      analogWrite(ENA3, 0); // Stop motor
    } 
    else if (command == "A4") {
      // Motor B: Backward at 50% speed
      analogWrite(ENA4, 128); // 50% of 255
      digitalWrite(IN1A4, LOW);
      digitalWrite(IN2A4, HIGH);
      delay(2000); // Run for 2 seconds
      analogWrite(ENA4, 0); // Stop motor
    }
  }
}
