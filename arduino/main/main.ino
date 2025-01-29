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

// A4 Feeder IR pin
#define A4_F_IR 2

// A4 Feeder IR pin
#define A4_R_IR 5

// A3 Feeder IR pin
#define A3_F_IR 3

// A3 Roll IR pin
#define A3_R_IR 4

// Stepper motor parameters
const unsigned long stepInterval = 500; // Time between steps (microseconds)
unsigned long previousStepTime = 0;

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void printOnLCD(String text, int col, int row, bool clear) {
  if (clear)
    lcd.clear();
  lcd.setCursor(col, row);
  lcd.print(text);
}

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

  // IR sensors config
  pinMode(A3_F_IR, INPUT);
  pinMode(A3_R_IR, INPUT);
  pinMode(A4_R_IR, INPUT);

  lcd.init();
  lcd.backlight();

  printOnLCD("Welcome to", 3, 0, true);
  printOnLCD("THE ARTIST", 3, 1, false);


  // Initialize motor direction and enable the motor driver
  digitalWrite(rollDir, motorDir);
  digitalWrite(rollEn, HIGH); // Disable the stepper motor driver (active LOW)
}

void loop() {

  if(Serial.available() > 0) {
  
    // Command to activate A3
    String command = Serial.readStringUntil('\n'); // Read the command
    command.trim(); // Remove any trailing newline characters

  
    if (command.startsWith("info:")) {
      
      int firstColon = command.indexOf(":");
      int secondColon = command.indexOf(":", firstColon + 1);

      if (firstColon != -1 && secondColon != -1) {  
        String size = command.substring(firstColon + 1, secondColon);
        String color = command.substring(secondColon + 1);

        printOnLCD("Size: " + size, 3, 0, true);
        printOnLCD("Color: " + color, 3, 1, false);

        Serial.println("info received"); 
      }
     
    }

    else if (command == "PB") {
      printOnLCD("Picking up pen...", 0, 0, true);
    }

    else if (command == "DRAWING") {
      printOnLCD("Drawing...", 0, 0, true);
    }

    else if (command == "RET") {
      printOnLCD("Drawing done!", 0, 0, true);
      printOnLCD("Returning pen...", 0, 1, false);
    }

    else if (command == "A3") {

      // Check if paper is present in the feeder
      while (digitalRead(A3_F_IR) == HIGH ) {
        printOnLCD("No paper!", 3, 0, true);
      }

      unsigned long startTime = millis(); // Record the start time
      bool stepperStarted = false; // Flag to indicate when the stepper motor starts

      // Start DC Motor A3: Forward at max speed
      analogWrite(ENA3, 255);
      digitalWrite(IN1A3, HIGH);
      digitalWrite(IN2A3, LOW);

      printOnLCD("Paper rolling...", 0, 0, true);

      // Handle DC motor runtime and stepper motor activation
      while (millis() - startTime < 20000) {
        unsigned long elapsedTime = millis() - startTime;

        // Start stepper motor at 7 seconds
        if (!stepperStarted && elapsedTime >= 7000) {
          Serial.println("Starting stepper motor...");
          digitalWrite(rollEn, LOW); // Enable stepper motor
          stepperStarted = true;
        }

        // Generate step pulses for the stepper motor if started
        if (stepperStarted) {
          unsigned long currentTime = micros();
          if (currentTime - previousStepTime >= stepInterval) {
            previousStepTime = currentTime;

            // Generate a step pulse
            digitalWrite(rollStep, HIGH);
            delayMicroseconds(10); // Short pulse to ensure the driver detects the step
            digitalWrite(rollStep, LOW);
          }
        }
      }

      // Stop the DC motor after 17 seconds
      Serial.println("Stopping DC motor...");
      analogWrite(ENA3, 0);
      digitalWrite(IN1A3, LOW);
      digitalWrite(IN2A3, LOW);

      // Independent loop for stepper motor
      if (stepperStarted) {
        Serial.println("Stepper motor continues independently...");
        while (true) {
          // Generate step pulses for the stepper motor
          unsigned long currentTime = micros();
          if (currentTime - previousStepTime >= stepInterval) {
            previousStepTime = currentTime;

            // Generate a step pulse
            digitalWrite(rollStep, HIGH);
            delayMicroseconds(10); // Short pulse to ensure the driver detects the step
            digitalWrite(rollStep, LOW);
          }

          // Stop stepper motor when paper is detected
          if (digitalRead(A3_R_IR) == LOW) {
            printOnLCD("Paper arrived!", 3, 0, true);
            digitalWrite(rollEn, HIGH); // Disable the motor driver
            break; // Exit the loop after stepper stops
          }
        }
      }

      
    }
    else if (command == "A4") {

      // Check if paper is present in the feeder
      while ( digitalRead(A4_F_IR) == HIGH ) {
        printOnLCD("No paper!", 3, 0, true);
      }

      unsigned long startTime = millis(); // Record the start time
      bool stepperStarted = false; // Flag to indicate when the stepper motor starts

      // Start DC Motor A4: Forward at max speed
      analogWrite(ENA4, 255);
      digitalWrite(IN1A4, HIGH);
      digitalWrite(IN2A4, LOW);

      printOnLCD("Paper rolling...", 0, 0, true);

      // Handle DC motor runtime and stepper motor activation
      while (millis() - startTime < 20000) {
        unsigned long elapsedTime = millis() - startTime;

        // Start stepper motor at 7 seconds
        if (!stepperStarted && elapsedTime >= 7000) {
          Serial.println("Starting stepper motor...");
          digitalWrite(rollEn, LOW); // Enable stepper motor
          stepperStarted = true;
        }

        // Generate step pulses for the stepper motor if started
        if (stepperStarted) {
          unsigned long currentTime = micros();
          if (currentTime - previousStepTime >= stepInterval) {
            previousStepTime = currentTime;

            // Generate a step pulse
            digitalWrite(rollStep, HIGH);
            delayMicroseconds(10); // Short pulse to ensure the driver detects the step
            digitalWrite(rollStep, LOW);
          }
        }
      }

      // Stop the DC motor after 17 seconds
      Serial.println("Stopping DC motor...");
      analogWrite(ENA4, 0);
      digitalWrite(IN1A4, LOW);
      digitalWrite(IN2A4, LOW);

      // Independent loop for stepper motor
      if (stepperStarted) {
        Serial.println("Stepper motor continues independently...");
        while (true) {
          // Generate step pulses for the stepper motor
          unsigned long currentTime = micros();
          if (currentTime - previousStepTime >= stepInterval) {
            previousStepTime = currentTime;

            // Generate a step pulse
            digitalWrite(rollStep, HIGH);
            delayMicroseconds(10); // Short pulse to ensure the driver detects the step
            digitalWrite(rollStep, LOW);
          }

          // Stop stepper motor when paper is detected
          if (digitalRead(A4_R_IR) == LOW) {
            printOnLCD("Paper arrived!", 3, 0, true);
            digitalWrite(rollEn, HIGH); // Disable the motor driver
            break; // Exit the loop after stepper stops
          }
        }
      }

     
    }

    else if (command == "DONE") {
      unsigned long startTime = millis(); // Record the start time
      unsigned long currentTime;
      const unsigned long runDuration = 8000; // 10 seconds
      const unsigned long stepInterval = 500; // Adjust this to control motor speed (microseconds)
      unsigned long previousStepTime = micros(); // Record time for step pulse generation
      
      printOnLCD("Enjoy :)", 0, 0, true);

      digitalWrite(rollEn, LOW); // Enable the stepper motor driver

      while (true) {
        currentTime = millis();

        // Generate step pulses for the stepper motor
        if ((micros() - previousStepTime) >= stepInterval) {
          previousStepTime = micros();
          digitalWrite(rollStep, HIGH);
          delayMicroseconds(10); // Short pulse for the stepper driver
          digitalWrite(rollStep, LOW);
        }

        // Stop the stepper motor after 10 seconds
        if (currentTime - startTime >= runDuration) {
          Serial.println("Stopping stepper motor...");
          digitalWrite(rollEn, HIGH); // Disable the stepper motor driver
          break;
        }
      }
  }


  }
}
