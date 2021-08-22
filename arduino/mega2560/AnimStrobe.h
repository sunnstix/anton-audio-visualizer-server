#ifndef ANIMSTROBE_H
#define ANIMSTROBE_H

#include "Animator.h"

class StrobeAnimation : public Animation
{
public:
    StrobeAnimation(LedStrip& led, RgbColor c) : Animation(led, 33), color(c) {}
    void start() override
    {
        this->solidColor(color);
        ledstrip.Show();
    }
    void update() override
    {
        on_state = !on_state;
        this->solidColor(on_state ? color : RgbColor(0, 0, 0));
        ledstrip.Show();
    }

private:
    RgbColor color;
    bool on_state = true;
};


#endif