#include <WiFi.h>
#include <FirebaseESP32.h>
#include <DFRobotDFPlayerMini.h>
#include <SoftwareSerial.h>

// Firebase configuration and credentials
FirebaseData firebaseData;
FirebaseAuth auth;
FirebaseConfig config;

// Wi-Fi credentials
const char* ssid = "djjdjdjdj";         // Replace with your Wi-Fi network name
const char* password = "hhfhfhf"; // Replace with your Wi-Fi password

// Firebase project information
#define FIREBASE_HOST "Database URL" // replace with your database url
#define FIREBASE_AUTH "Database Secrete"        // replace with your firebase secret

// DFPlayer Mini configuration
SoftwareSerial mySerial(16, 17); // RX, TX
DFRobotDFPlayerMini myDFPlayer;

// Pin for alarm (buzzer or LED)
const int buzzerPin = 4;

void setup() {
  // Start serial communication
  Serial.begin(115200);

  // Initialize DFPlayer Mini first
  mySerial.begin(9600);
  Serial.println("Initializing DFPlayer Mini...");
  if (!myDFPlayer.begin(mySerial)) {
    Serial.println("Unable to initialize DFPlayer Mini. Check connections and SD card.");
    while (true);
  }
  Serial.println("DFPlayer Mini initialized.");
  myDFPlayer.volume(25);  // Set volume level
  myDFPlayer.play(1);     // Play track 1 for testing
  delay(3000);            // Allow the track to play for 3 seconds
  myDFPlayer.stop();      // Stop playback after testing

  // Initialize Wi-Fi
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to Wi-Fi...");
  }
  Serial.println("Connected to Wi-Fi!");

  // Firebase configuration
  config.database_url = FIREBASE_HOST;
  config.signer.tokens.legacy_token = FIREBASE_AUTH;

  // Initialize Firebase
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  Serial.println("Firebase initialized.");

  // Initialize buzzer/LED pin
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);  // Turn off buzzer initially
}

void loop() {
  // Check Firebase for detection status
  if (Firebase.ready()) {
    if (Firebase.getJSON(firebaseData, "/elephant_detection")) {
      String jsonStr = firebaseData.jsonString();
      Serial.println("Data from Firebase:");
      Serial.println(jsonStr);

      // Parse detection status
      if (jsonStr.indexOf("\"detected\":true") > 0) {
        Serial.println("Elephant detected! Playing deterrent sound...");
        myDFPlayer.loop(1);         // Loop track 1
        digitalWrite(buzzerPin, HIGH);  // Turn on buzzer/LED
        delay(5000);                // Allow sound to play for 5 seconds

        // Reset detection status
        if (Firebase.setBool(firebaseData, "/elephant_detection/detected", false)) {
          Serial.println("Successfully updated detection status to false");
        } else {
          Serial.println("Failed to update detection status");
        }
      } else {
        Serial.println("No elephant detected. Stopping sound...");
        myDFPlayer.stop();          // Stop sound
        digitalWrite(buzzerPin, LOW); // Turn off buzzer/LED
      }
    } else {
      Serial.println("Failed to get data from Firebase.");
    }
  }

  delay(1000);  // Poll Firebase every second
}