// Motor A pins
#define ENA3 10  
#define IN1A3 8  
#define IN2A3 9  

// Motor B pins
#define ENA4 11  
#define IN1A4 6 
#define IN2A4 7 

// IR
#define IROUT 2

void setup() {
  Serial.begin(9600); 

  
  pinMode(ENA3, OUTPUT);
  pinMode(IN1A3, OUTPUT);
  pinMode(IN2A3, OUTPUT);

  pinMode(ENA4, OUTPUT);
  pinMode(IN1A4, OUTPUT);
  pinMode(IN2A4, OUTPUT);

  pinMode(IROUT, INPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read the command

    if(digitalRead(IROUT) == HIGH) {
        Serial.println("There's no paper!");
        delay(500);
    } else {

        if (command == "A3") {
            // Motor A: Forward at 75% speed
            analogWrite(ENA3, 191); // 75% of 255
            digitalWrite(IN1A3, HIGH);
            digitalWrite(IN2A3, LOW);
            delay(2000); // Run for 2 seconds
            analogWrite(ENA3, 0); // Stop motor
        } 
        else if (command == "A4") {
            // Motor B: Backward at 75% speed
            analogWrite(ENA4, 191); // 75% of 255
            digitalWrite(IN1A4, LOW);
            digitalWrite(IN2A4, HIGH);
            delay(2000); // Run for 2 seconds
            analogWrite(ENA4, 0); // Stop motor
        }

    }
    
  }
}
