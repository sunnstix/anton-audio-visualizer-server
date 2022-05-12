#ifndef ANIMATIONS_H
#define ANIMATIONS_H

#include "AnimOff.h"
#include "AnimReciever.h"
#include "AnimStrobe.h"
#include "AnimSolid.h"
#include "AnimRotatingRainbow.h"

// Light Modes (appended to start of packet)
enum class LightMode : uint8_t
{
    OffMode,
    RotateRainbowMode,
    SolidMode,
    StrobeMode,
    RecieverMode,
    BrightnessConfig,
    InvalidMode
};
#endif
