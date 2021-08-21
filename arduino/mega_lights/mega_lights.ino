
#include <NeoPixelBrightnessBus.h>
#include "Animator.h"
#include "Animations.h"

#include <WiFiEspAT.h>

// Emulate Serial1 on pins 6/7 if not present
#ifndef HAVE_HWSERIAL3
#include "SoftwareSerial.h"
SoftwareSerial Serial3(6, 7); // RX, TX
#endif

// local port to listen on
#define PORT 6969
// Set to the number of LEDs in your LED strip
#define NUM_LEDS 300
// Maximum number of packet bytes to hold in the buffer. Don't change this.
#define BUFFER_LEN 1024
// LED Pin
#define LED_PIN 7
// Num Animations
#define NUM_ANIMS 1

// Wifi Information (Never Going to reuse this password or ssid)
const char ssid[] = "7th Doug TH~2.4GHz"; // your network SSID (name)
const char pass[] = "#ZBJJJMS42";         // your network password
int status = WL_IDLE_STATUS;              // the Wifi radio's status

// UDP protocol for ESP8266
WiFiUDP Udp;
int latestRead;
uint8_t packetBuffer[BUFFER_LEN];

// LED strip
NeoPixelBrightnessBus<NeoGrbFeature, Neo800KbpsMethod> ledstrip(NUM_LEDS, LED_PIN);

// Animation Manager
Animator animator; // NeoPixel animation management object
LightMode currMode;

// raspi IP
IPAddress ip(10, 0, 0, 248);
// router gateway
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);

void setup()
{
  // initialize serial for debugging
  Serial.begin(115200);
  // initialize serial for ESP module
  Serial3.begin(115200);
  // initialize ESP module
  WiFi.init(&Serial3);

  // check for the presence of the shield:
  if (WiFi.status() == WL_NO_SHIELD)
  {
    Serial.println("WiFi shield not present");
    // don't continue:
    while (true)
      ;
  }

  // attempt to connect to WiFi network
  while (status != WL_CONNECTED)
  {
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

  ledstrip.Begin();
  currMode = LightMode::OffMode;
  animator.StartAnimation(new OffAnimation());
}

void loop()
{
  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();
  latestRead = 0;
  if (packetSize)
  {
    // read the packet into packetBuffer
    latestRead = Udp.read(packetBuffer, BUFFER_LEN);

    // retrieve light mode from first byte of message
    LightMode packetMode = static_cast<LightMode>(packetBuffer[0]);

    // set current light mode if message is valid
    if (packetMode < LightMode::InvalidMode){
      switch (packetMode)
      {
      case LightMode::OffMode:
        animator.StartAnimation(new OffAnimation());
        break;
      case LightMode::SolidMode:
        if (latestRead >=4)
          animator.StartAnimation(new SolidAnimation(RgbColor(packetBuffer[1],packetBuffer[2],packetBuffer[3])));
        break;
      case LightMode::RotateRainbowMode:
        animator.StartAnimation(new RotatingRainbowAnimation());
        break;
      case LightMode::RecieverConfig:
        animator.StartAnimation(new RecieverAnimation(packetBuffer,latestRead));
        packetMode = LightMode::RecieverMode; // sets current mode to reciever mode
        break;
      case LightMode::RecieverMode:
        break;
      case LightMode::StrobeMode:
        if (latestRead >=4)
          animator.StartAnimation(new StrobeAnimation(RgbColor(packetBuffer[1],packetBuffer[2],packetBuffer[3])));
        break;
      default:
        return; //don't update if message is invalid
      }

      //update current mode
      currMode = packetMode;
    }
  }

  animator.UpdateAnimation();
}

void printWifiStatus()
{
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