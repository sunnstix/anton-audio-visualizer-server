/*
  UDPSendReceive.pde:
  This sketch receives UDP message strings, prints them to the serial port
  and sends an "acknowledge" string back to the sender
  A Processing sketch is included at the end of file that can be used to send
  and received messages for testing with a computer.
  created 21 Aug 2010
  by Michael Margolis
  This code is in the public domain.
  adapted from Ethernet library examples
*/


#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#include <NeoPixelBrightnessBus.h>
#include "Animator.h"
#include "Animations.h"

#ifndef STASSID
#define STASSID "DayCareWifi"
#define STAPSK  "YourMomsGay"
#endif

// local port to listen on
#define PORT 8080
// Set to the number of LEDs in your LED strip
#define NUM_LEDS 300
// Maximum number of packet bytes to hold in the buffer. Don't change this.
#define BUFFER_LEN 1024
// LED Pin
#define LED_PIN 7

// buffers for receiving and sending data
uint8_t packetBuffer[UDP_TX_PACKET_MAX_SIZE + 1]; //buffer to hold incoming packet

WiFiUDP Udp;

// LED strip
NeoPixelBrightnessBus<NeoGrbFeature, Neo800KbpsMethod> ledstrip(NUM_LEDS, LED_PIN);
int latestRead;

// Animation Manager
Animator animator; // NeoPixel animation management object
LightMode currMode;

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(STASSID, STAPSK);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(500);
  }
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());
  Serial.printf("UDP server on port %d\n", PORT);
  Udp.begin(PORT);


  ledstrip.Begin();
  currMode = LightMode::OffMode;
  animator.StartAnimation(new OffAnimation(&ledstrip));
}

void loop() {
  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();
  latestRead = 0;
  
  if (packetSize)
  {
    Serial.println("Recieved");
    // read the packet into packetBuffer
    latestRead = Udp.read(packetBuffer, BUFFER_LEN);
    // retrieve light mode from first byte of message
    LightMode packetMode = static_cast<LightMode>(packetBuffer[0]);
    
    // set current light mode if message is valid
    if (packetMode < LightMode::InvalidMode){
      switch (packetMode)
      {
      case LightMode::OffMode:
        animator.StartAnimation(new OffAnimation(&ledstrip));
        Serial.println("Off Mode");
        break;
      case LightMode::SolidMode:
        if (latestRead == 4)
          animator.StartAnimation(new SolidAnimation(&ledstrip, RgbColor(packetBuffer[1],packetBuffer[2],packetBuffer[3])));
        Serial.println("Solid Mode");
        break;
      case LightMode::RotateRainbowMode:
        animator.StartAnimation(new RotatingRainbowAnimation(&ledstrip));
        Serial.println("Rainbow Mode");
        break;
      case LightMode::RecieverConfig:
        if (latestRead == 4)
            animator.StartAnimation(new RecieverAnimation(&ledstrip, packetBuffer,latestRead));
        packetMode = LightMode::RecieverMode; // sets current mode to reciever mode
        latestRead = 0; // prevent animation of configuration bytes
        Serial.println("Reciever Mode");
        break;
      case LightMode::RecieverMode:
        break;
      case LightMode::StrobeMode:
        if (latestRead ==4)
          animator.StartAnimation(new StrobeAnimation(&ledstrip, RgbColor(packetBuffer[1],packetBuffer[2],packetBuffer[3])));
        Serial.println("Strobe Mode");
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
