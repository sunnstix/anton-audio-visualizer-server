#ifndef OFF_H
#define OFF_H

#include "Solid.h"

class OffAnimation : public SolidAnimation
{
public:
    OffAnimation(LedStrip& led) : SolidAnimation(led, RgbColor(0, 0, 0)) {}
};

#endif