#ifndef ANIMATIONS_H
#define ANIMATIONS_H

#include "Animations/Off.h"
#include "Animations/Reciever.h"
#include "Animations/Strobe.h"
#include "Animations/Solid.h"
#include "Animations/RotatingRainbow.h"

// Light Modes (appended to start of packet)
enum class LightMode : uint8_t
{
    OffMode,
    SolidMode,
    RotateRainbowMode,
    RecieverConfig,
    RecieverMode,
    StrobeMode,
    BrightnessConfig,
    InvalidMode
};
#endif