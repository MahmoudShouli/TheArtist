// DC Motor A3 pins
#define ENA3 10  
#define IN1A3 8  
#define IN2A3 9  

// DC Motor A4 pins
#define ENA4 11  
#define IN1A4 6 
#define IN2A4 7


// Stepper Motor Roll pins
#define rollStep 48
#define rollDir 50
#define rollEn 46
#define motorDir LOW


// A3 Feeder IR pins
#define A3_F_IR 2

// A4 Feeder IR pins
#define A4_F_IR 3

// A3 Roll IR pins
#define A3_R_IR 4

// A4 Roll IR pins
#define A4_R_IR 5

void setup() {

  Serial.begin(9600); 
  
  // DC Motor A3 config
  pinMode(ENA3, OUTPUT);
  pinMode(IN1A3, OUTPUT);
  pinMode(IN2A3, OUTPUT);

  // DC Motor A4 config
  pinMode(ENA4, OUTPUT);
  pinMode(IN1A4, OUTPUT);
  pinMode(IN2A4, OUTPUT);

  // Stepper Motor Roll config
  pinMode(rollStep, OUTPUT);
  pinMode(rollDir, OUTPUT);
  pinMode(rollEn, OUTPUT);

  // IRs' congig
  pinMode(A3_F_IR, INPUT);
  pinMode(A4_F_IR, INPUT);
  pinMode(A3_R_IR, INPUT);
  pinMode(A4_R_IR, INPUT);


  // Initialize motor direction and enable the motor driver
  digitalWrite(rollDir, motorDir);
  digitalWrite(rollEn, HIGH); // disable the stepper motor driver (active LOW)
  

}

void loop() {
  // Check the IR roll sensors
  bool a3Detected = digitalRead(A3_R_IR);
  bool a4Detected = digitalRead(A4_R_IR);
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read the command

    if(digitalRead(A3_F_IR) == HIGH || digitalRead(A4_F_IR) == HIGH) {
        Serial.println("There's no paper!");
        delay(500);
    } else {

        if (command == "A3") {
            // DC Motor A3: Forward at max speed
            analogWrite(ENA3, 255); 
            digitalWrite(IN1A3, HIGH);
            digitalWrite(IN2A3, LOW);
            delay(12000); // Run for 12 seconds
            analogWrite(ENA3, 0); // Stop motor
            digitalWrite(rollEn, LOW); // enable the stepper motor driver (active LOW)
            
            if ( a3Detected == LOW) { // Assuming HIGH means white paper detected
              digitalWrite(rollEn, HIGH); // Disable the motor driver (active LOW)
              Serial.println("motor stops");
              return; // Exit the loop and stop further motor steps
            }

        } 
        else if (command == "A4") {
            // DC Motor A4: Forward at 100% speed
            analogWrite(ENA4, 255); 
            digitalWrite(IN1A4, HIGH);
            digitalWrite(IN2A4, LOW);
            delay(8000); // Run for 8 seconds
            analogWrite(ENA4, 0); // Stop motor
            digitalWrite(rollEn, LOW); // enable the stepper motor driver (active LOW)

            if ( a4Detected == LOW) { // Assuming HIGH means white paper detected
              digitalWrite(rollEn, HIGH); // Disable the motor driver (active LOW)
              Serial.println("motor stops");
              return; // Exit the loop and stop further motor steps
            }
        }

        // Get the current time
        unsigned long currentTime = micros();

        // Non-blocking stepper control
        if (currentTime - previousStepTime >= stepInterval) {
          previousStepTime = currentTime;

          // Generate a step pulse
          digitalWrite(rollStep, HIGH);
          delayMicroseconds(10); // Short pulse to ensure the driver detects the step
          digitalWrite(rollStep, LOW);
        }        

    }
    
  }
}
