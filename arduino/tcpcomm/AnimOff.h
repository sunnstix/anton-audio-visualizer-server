#ifndef ANIMOFF_H
#define ANIMOFF_H

#include "AnimSolid.h"

class OffAnimation : public SolidAnimation
{
public:
    OffAnimation(LedStrip* led) : SolidAnimation(led, RgbColor(0, 0, 0)) {}
};

#endif
