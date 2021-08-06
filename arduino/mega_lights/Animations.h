#ifndef ANIMATIONS_H
#define ANIMATIONS_H

#include <NeoPixelBus.h>
#include "Animator.h"

extern NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod> ledstrip;

// LED gamma correction
NeoGamma<NeoGammaTableMethod> colorGamma;

// Light Modes (appended to start of packet)
enum class LightMode : uint8_t
{
  OffMode,
  SolidMode,
  RotateRainbowMode,
  AudioMode,
  StrobeMode,
  InvalidMode
};

// helper func
void solidColor(RgbColor color);


class RotatingRainbowAnimation : public Animation
{
public:
  RotatingRainbowAnimation() : Animation(10) {}
  RotatingRainbowAnimation(uint16_t duration) : Animation(duration) {}
  void update() override
  {
    for (uint16_t i = 0; i < ledstrip.PixelCount(); ++i)
    {
      RgbColor tarColor = HslColor(float((i * 4 + this->offset) % 360) / 360.0f, 1.0f, 0.5f);
      ledstrip.SetPixelColor(i, colorGamma.Correct(tarColor)); // I try to use gamma correction for color fades
    }
    this->offset = (this->offset + 4) % 360;
    ledstrip.Show();
  }

private:
  uint16_t offset = 0;
};

class AudioRecieverAnimation : public Animation
{
public:
  AudioRecieverAnimation(uint8_t *packetBuffer, int &last_read) : Animation(), lightBuffer(packetBuffer), readSize(last_read) {}
  void start() override
  {
    solidColor(RgbColor(0, 0, 0));
    ledstrip.Show();
  }
  void update() override
  {
    if (readSize)
    {
      for (int i = 1; i + 3 < readSize; i += 4)
      {
        //assumes 7 bit color values sent and rescale
        const uint8_t red = (lightBuffer[i] & 254); // doubles value recieved and ignores last bit
        const uint8_t green = ((lightBuffer[i] & 1) << 7) + ((lightBuffer[i + 1] & 252) >> 1);
        const uint8_t blue = ((lightBuffer[i + 1] & 3) << 6) + ((lightBuffer[i + 2] & 248) >> 2);
        const uint32_t index = ((lightBuffer[i + 2] & 7) << 8) + lightBuffer[i + 3];

        RgbColor pixel = RgbColor(red, green, blue);
        for (int p = index * 5; p < 5 * index + 5 && p < ledstrip.PixelCount(); ++p)
          ledstrip.SetPixelColor(p, pixel);
      }
      ledstrip.Show();
    }
  }

private:
  uint8_t *lightBuffer;
  int &readSize;
};

class SolidAnimation : public Animation
{
public:
  SolidAnimation(RgbColor c) : Animation(), color(c) {}
  void start() override
  {
    solidColor(this->color);
    ledstrip.Show();
  }

private:
  RgbColor color;
};

class OffAnimation : public SolidAnimation
{
public:
  OffAnimation() : SolidAnimation(RgbColor(0, 0, 0)) {}
};

class StrobeAnimation : public Animation
{
public:
  StrobeAnimation(RgbColor c) : Animation(33), color(c) {} 
  void start() override {
    solidColor(color);
    ledstrip.Show();
  }
  void update() override {
    on_state = !on_state;
    if (on_state) {
      solidColor(color);
    }else{
      solidColor(RgbColor(0,0,0));
    }
    ledstrip.Show();
  }
private:
  RgbColor color;
  bool on_state = true;
};

void solidColor(RgbColor color)
{
  for (uint16_t i = 0; i < ledstrip.PixelCount(); ++i)
  {
    ledstrip.SetPixelColor(i, colorGamma.Correct(color));
  }
}

#endif