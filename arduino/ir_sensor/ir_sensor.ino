// Define the pin connected to the IR sensor
#define IROUT 2 // Digital pin 2

void setup() {
  // Initialize the IR sensor pin as input
  pinMode(IROUT, INPUT);
  
  // Start the serial communication
  Serial.begin(9600);
  Serial.println("IR Sensor Test");
}

void loop() {
  // Continuously read the state of the IR sensor
  while (digitalRead(IROUT) == HIGH) {
    Serial.println("no paper");
    delay(500); // Small delay to avoid overwhelming the Serial Monitor
  }
  
  // Print when the sensor detects a LOW state
  Serial.println("white");
  delay(500); // Small delay for stability
}
