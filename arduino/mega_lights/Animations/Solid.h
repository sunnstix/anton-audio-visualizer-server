#ifndef SOLID_H
#define SOLID_H

#include "Animator.h" 

using LedStrip = NeoPixelBrightnessBus<NeoGrbFeature, Neo800KbpsMethod>;

class SolidAnimation : public Animation
{
public:
    SolidAnimation(LedStrip& led, RgbColor& c) : Animation(led), color(c) {}
    void start() override
    {
        this->solidColor(this->color);
        ledstrip.Show();
    }

private:
    RgbColor color;
};


#endif