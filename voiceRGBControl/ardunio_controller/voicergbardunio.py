 Define the pins connected to your RGB LED
 Ensure these are PWM pins (labeled with a ~ on most boards)
#define PIN_R 9
#define PIN_G 10
#define PIN_B 11

void setup() {
   Speed MUST match the Python script (115200)
  Serial.begin(115200); 
  
   Initialize pins as outputs
  pinMode(PIN_R, OUTPUT);
  pinMode(PIN_G, OUTPUT);
  pinMode(PIN_B, OUTPUT);

   Optional Flash the LED once to show it's ready
  updateLedColor(255, 0, 0); delay(200);
  updateLedColor(0, 255, 0); delay(200);
  updateLedColor(0, 0, 255); delay(200);
  updateLedColor(0, 0, 0);
}

void loop() {
   Check if Python has sent data
  if (Serial.available()  0) {
    
     parseInt looks for numbers and ignores the commas automatically
    int rVal = Serial.parseInt();
    int gVal = Serial.parseInt();
    int bVal = Serial.parseInt();

     Check for the newline 'n' to confirm the end of the command
    if (Serial.read() == 'n') {
      updateLedColor(rVal, gVal, bVal);
    }
  }
}

 Function to handle the hardware pins
void updateLedColor(int r, int g, int b) {
   Use analogWrite to set brightness via PWM (0-255)
  analogWrite(PIN_R, r);
  analogWrite(PIN_G, g);
  analogWrite(PIN_B, b);
}
