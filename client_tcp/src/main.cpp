#include <Arduino.h>
#include <Ethernet.h>
#include <SPI.h>

const int buttonWIND  = 27; // WIND/BLOWER
const int buttonMINUS = 26; // MINUS THERMAL
const int buttonPLUS = 25;  // PLUS THERMAL
const int buttonONOFF = 33; // ON/OFF REMOTE
const int ledPin = 2;       // LED ESP32
const int ledBox = 12;      // LED BOX UNIVERSAL REMOTE
const int buzzer = 14;      // BUZZER REMOTE BOX

//------------ SETUP PIN W5500 ------------
#define SPI_MISO 19
#define SPI_MOSI 23
#define SPI_SCK 18
#define SPI_CS 5

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED }; // DEFAULT MAC ADDRESS

// Network configuration
IPAddress ip(192, 168, 1, 177);
IPAddress myDns(192, 168, 1, 1);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

EthernetClient client;

// --------- FUNCTION PROCESS PROGRAM ------------- 

// Function to connect to server
void connectToServer() { 
  Serial.println("Menghubungkan ke server...");
  if (client.connect(IPAddress(192, 168, 1, 100), 8899)) { // IP ETHERNET W5500 
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
void blinkLed(){
  for (int i = 0; i < 10; i++) {
    digitalWrite(ledPin, HIGH);
    delay(100);
    digitalWrite(ledPin, HIGH);
    delay(100);  
  }
}

// Function to control the LED from the server (NOT USE IN THE MAIN LOOP)
void serverLed(){
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
      digitalWrite(ledPin, HIGH);
      delay(100);
    }
  }
}

// --------- SETUP PIN AND COMMUNICATION TESTING-------------

void setup() {
  // LED pin mode
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH);
  
  //Box Indicator
  pinMode(buzzer, OUTPUT);
  pinMode(ledBox, OUTPUT);

  Serial.begin(115200);  // Setting baud rate
  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI, SPI_CS); // Initialize SPI
  
  pinMode(SPI_CS, OUTPUT); // Setting CS pin
  digitalWrite(SPI_CS, HIGH); // Test CS

  Ethernet.init(SPI_CS);
  Ethernet.begin(mac, ip, myDns, gateway, subnet);
  delay(1000);

  Serial.print("Alamat IP saya: ");
  Serial.println(Ethernet.localIP());

  if (Ethernet.localIP() == IPAddress(0, 0, 0, 0)) { // Check for successful configuration
    Serial.println("Gagal mengkonfigurasi Ethernet");
    while (true); // Stop execution if Ethernet configuration fails
  }

  
  // Button pin mode
  // pinMode(buttonONOFF, OUTPUT);
  // pinMode(buttonPLUS, OUTPUT);
  // pinMode(buttonMINUS, OUTPUT);
  // pinMode(buttonWIND, OUTPUT);

  connectToServer(); // Connect to server during setup
}

// ----------- MAIN PROGRAM -----------------------

void loop() {
  if (client.connected()) {
    receivePeopleCount();   // Receive data from server
  } else {
    connectToServer();      // Reconnect to server if disconnected
  }
  delay(1000);               // Delay main loop program by 1 second
}