#include <Arduino.h>
#include <Ethernet.h>
#include <SPI.h>
#include <HTTPClient.h>

// Pin definitions
const int buttonWIND  = 27; // WIND/BLOWER
const int buttonMINUS = 26; // MINUS THERMAL
const int buttonPLUS = 25;  // PLUS THERMAL
const int buttonONOFF = 33; // ON/OFF REMOTE
const int ledPin = 2;       // LED ESP32
const int ledBox = 12;      // LED BOX UNIVERSAL REMOTE
const int buzzer = 14;      // BUZZER REMOTE BOX

// Ethernet setup
#define SPI_MISO 19
#define SPI_MOSI 23
#define SPI_SCK 18
#define SPI_CS 5

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 1, 177);
IPAddress myDns(192, 168, 1, 1);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

// Server URL
const char* serverUrl = "http://192.168.1.177:5005/send_temperature"; // Ganti dengan IP server Flask

EthernetClient client;

// Function to connect to server
void connectToServer() { 
  Serial.println("Menghubungkan ke server...");
  if (client.connect(IPAddress(192, 168, 1, 100), 8899)) { // IP server tujuan
    Serial.println("Terhubung ke server");
  } else {
    Serial.println("Gagal terhubung ke server");
    delay(500);
  }
}

// Function to receive the count of people
void receivePeopleCount() {
  if (client.connected() && client.available()) {
    String count = client.readStringUntil('\n');
    if (count.startsWith("--frame")) {
      return;
    } else {
      Serial.println("Detect People: " + count + " C");
      // Kirimkan konfirmasi ke server
      client.print("jon");
    }
  }
}

// Function to blink the LED on the ESP32
void blinkLed() {
  for (int i = 0; i < 10; i++) {
    digitalWrite(ledPin, HIGH);
    delay(100);
    digitalWrite(ledPin, LOW);
    delay(100);  
  }
}

// Function to control the LED from the server (NOT USED IN MAIN LOOP)
void serverLed() {
  if (client.connected()) {
    if (client.available()) {
      String message = client.readStringUntil('\n');
      Serial.println("Pesan dari server: " + message);
      if (message == "LED_ON") {
        blinkLed();      
      }
      client.println("LED_ON diterima");
    }
  } else {
    Serial.println("Terputus dari server");
    delay(1000);
    connectToServer();  
    for(int k = 0; k < 10; k++) {
      digitalWrite(ledPin, HIGH);
      delay(100);
      digitalWrite(ledPin, LOW);
      delay(100);
    }
  }
}

// Function to receive temperature data from Flask server
void receiveTemperature() {
  HTTPClient http;
  http.begin(serverUrl);
  int httpCode = http.GET();

  if (httpCode > 0) {
    String payload = http.getString();
    Serial.println("Temperature data: " + payload);
  } else {
    Serial.println("Gagal menerima data suhu");
  }
  
  http.end();
}

// Setup function
void setup() {
  // Initialize pin modes
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);
  pinMode(buzzer, OUTPUT);
  pinMode(ledBox, OUTPUT);

  // Initialize serial communication
  Serial.begin(115200);
  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI, SPI_CS);

  // Initialize Ethernet
  pinMode(SPI_CS, OUTPUT);
  digitalWrite(SPI_CS, HIGH);

  Ethernet.init(SPI_CS);
  Ethernet.begin(mac, ip, myDns, gateway, subnet);
  delay(1000);

  Serial.print("Alamat IP saya: ");
  Serial.println(Ethernet.localIP());

  if (Ethernet.localIP() == IPAddress(0, 0, 0, 0)) {
    Serial.println("Gagal mengkonfigurasi Ethernet");
    while (true);
  }

  connectToServer();
}

// Main loop function
void loop() {
  if (client.connected()) {
    receivePeopleCount();
  } else {
    connectToServer();
  }
  
  // Request temperature data from Flask server
  receiveTemperature();

  delay(10000); // Request temperature data every 10 seconds
}
