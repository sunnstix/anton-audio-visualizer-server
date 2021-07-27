

#include <NeoPixelBus.h>
#include <WiFiEsp.h>
#include <WiFiEspUdp.h>

// Emulate Serial1 on pins 6/7 if not present
#ifndef HAVE_HWSERIAL3
#include "SoftwareSerial.h"
SoftwareSerial Serial3(6, 7); // RX, TX
#endif

// local port to listen on
#define PORT 6969
// Set to the number of LEDs in your LED strip
#define NUM_LEDS 300
// Maximum number of packets to hold in the buffer. Don't change this.
#define BUFFER_LEN 1024
// LED Pin
#define LED_PIN 7

const char ssid[] = "7th Doug TH~2.4GHz";            // your network SSID (name)
const char pass[] = "#ZBJJJMS42";        // your network password
int status = WL_IDLE_STATUS;     // the Wifi radio's status

char packetBuffer[BUFFER_LEN];

WiFiEspUDP Udp;

// LED strip
NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod> ledstrip(NUM_LEDS, LED_PIN);

// raspi IP
IPAddress ip(10,0,0,248);
// router gateway
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);

void setup() {
  // initialize serial for debugging
  Serial.begin(115200);
  // initialize serial for ESP module
  Serial3.begin(115200);
  // initialize ESP module
  WiFi.init(&Serial3);

  // check for the presence of the shield:
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue:
    while (true);
  }

  // attempt to connect to WiFi network
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network
    WiFi.config(ip);
    status = WiFi.begin(ssid, pass);
  }
  
  Serial.println("Connected to wifi");
  printWifiStatus();

  Serial.println("\nStarting connection to server...");
  // if you get a connection, report back via serial:
  Udp.begin(PORT);
  
  Serial.print("Listening on port ");
  Serial.println(PORT);
}

void loop() {
  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();
  
  if (packetSize) {
    Serial.println("Received packet From ");
    IPAddress remoteIp = Udp.remoteIP();
    Serial.print(remoteIp);

    // read the packet into packetBuffer
    int len = Udp.read(packetBuffer, BUFFER_LEN);
    for(int i = 0; i+3 < len; i+=4) {
      //assumes 7 bit color values sent and rescales
      const uint8_t red = packetBuffer[i] && 14; // doubles value recieved and ignores last bit
      const uint8_t green = ((packetBuffer[i] && 1) << 3) + ((packetBuffer[i+1] && 12) >> 1);
      const uint8_t blue  = ((packetBuffer[i+1] && 3) << 2) + ((packetBuffer[i+2] && 8) >> 2);
      const uint32_t index = (packetBuffer[i+2] && 7) + packetBuffer[i+3];

      Serial.print("Index: ");
      Serial.print(index);
      Serial.print("\tRed: ");
      Serial.print(red);
      Serial.print("\tGreen: ");
      Serial.print(green);
      Serial.print("\tBlue: ");
      Serial.println(blue);

      RgbColor pixel(green, red, blue);
      ledstrip.SetPixelColor(index, pixel);
    } 
    ledstrip.Show();
  }
}


void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}