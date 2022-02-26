# Mega 2560 + ESP8266 Wifi Board
## General
This library runs the code to manage recieving requests from a local server and
controlling the lights accordingly. Connects to 2.4 GHz band of WiFi using WiFiESPAt
Library, communicating packets over Serial3 and controls lights using NeoPixelLib.

## Interface
The first byte of any message sent to the board must be indicative of what mode to 
set the lights to. The following details the specifics of packet encryptions for different 
modes.

### Off Mode
Singular Off Mode Indicator Byte

### Solid Mode
4 Byte Packet with Mode Indicator Byte followed by Byte for each Color Band (RGB)

### Rotate Rainbow Mode
Singular Rainbow Mode Indicator Byte

### Strobe Mode
4 Byte Packet with Mode Indicator Byte followed by Byte for each Color Band (RGB)

### Reciever Mode
#### Configuration
Initial 4 Byte Packet to Configure Reciever Mode must be sent. First byte is Mode Indicator,
second byte is indicator of the number of zones (repeating patterns), third byte is the number
of pixels that a singular color is represented by(pixel stretch), and fourth byte consists of 
2 boolean bits and 2 unused bits. The first boolean bit represents whether to enter rotate mode
and the second boolean bit represents whether to enter mirrored mode.

#### Updates
Pixels are updated (in non-rotational mode) by sending sequences of 4 bytes with first byte being
the pixel index and the following 3 bytes being the RGB value. All packets must be prepended with
the Reciever Mode indicator.

#### Rotate Reciever SubMode
While usually a pixel is represented by 4 bytes, with the first being the index followed by RGB
bytes but in rotate mode, indexes are not necessary so only 3 bytes are sent. In rotate mode, 
lights rotate within allocated segments,

#### Mirrored Reciever SubMode
Mirrors pixels to reduce neccessary bandwidth and buffer overflows on ESP. With multiple segments allocated,
mirrors pixels within segment.