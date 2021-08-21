#ifndef ROTATINGRAINBOW_H
#define ROTATINGRAINBOW_H

#include "Animator.h"

class RotatingRainbowAnimation : public Animation
{
public:
    RotatingRainbowAnimation(LedStrip& led) : Animation(led, 10) {} //update rotating rainbow every 10ms (should be adjusted for speed setting)
    RotatingRainbowAnimation(uint16_t duration) : Animation(duration) {}
    void update() override
    {
        for (uint16_t i = 0; i < ledstrip.PixelCount(); ++i)
        {
            RgbColor tarColor = HslColor(float((i * 4 + this->offset) % 360) / 360.0f, 1.0f, 0.5f);
            ledstrip.SetPixelColor(i, this->colorGamma.Correct(tarColor)); // I try to use gamma correction for color fades
        }
        this->offset = (this->offset + 4) % 360;
        ledstrip.Show();
    }

private:
    uint16_t offset = 0;
};


#endif