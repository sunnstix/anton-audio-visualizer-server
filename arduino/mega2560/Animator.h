#ifndef ANIMATOR_H
#define ANIMATOR_H

#include <NeoPixelBrightnessBus.h>

// Animation
// ========================================================================
class Animation
{
/* Virtual class for animation context */
public:
  using LedStrip = NeoPixelBrightnessBus<NeoGrbFeature, Neo800KbpsMethod>;

  Animation(LedStrip &led) : ledstrip(led), frequency(0) {}
  Animation(LedStrip &led, uint16_t freq) : ledstrip(led), frequency(freq) {}
  virtual ~Animation() = 0;
  virtual void start() {} //Initialization call
  virtual void update() {}
  virtual void stop() {} // Stop call
  uint16_t get_freq() { return this->frequency; }

protected:
  void SetPixelRange(RgbColor pixel, uint16_t left_bound, uint16_t right_bound)
  {
    /* Sets all of the pixels in a range to a certain color */
    for (; left_bound < right_bound && left_bound < ledstrip.PixelCount(); ++left_bound)
    {
      this->ledstrip.SetPixelColor(left_bound, pixel);
    }
  }

  void solidColor(RgbColor color)
  {
    /* Sets the entire ledstrip to a certain color*/
    for (uint16_t i = 0; i < ledstrip.PixelCount(); ++i)
    {
      ledstrip.SetPixelColor(i, colorGamma.Correct(color));
    }
  }

  RgbColor bytesToColor(uint8_t *bbuf)
  {
    /* Converts 21 bits in first 3 bytes of buffer to RgbColor Object*/
    const uint8_t red = *bbuf & 254; // doubles value recieved and ignores last bit
    const uint8_t green = ((*bbuf & 1) << 7) + ((*(bbuf + 1) & 252) >> 1);
    const uint8_t blue = ((*(bbuf + 1) & 3) << 6) + ((*(bbuf + 2) & 248) >> 2);
    return RgbColor(red, green, blue);
  }

  LedStrip &ledstrip;
  NeoGamma<NeoGammaTableMethod> colorGamma;

private:
  uint16_t frequency;
};
Animation::~Animation() {} // Force the Animation class to be abstract

// Animation Handler
// ========================================================================

class Animator
{
public:
  Animator() : anim(nullptr) {}
  Animator(Animation *new_anim) : anim(new_anim) {}
  ~Animator()
  {
    this->kill_anim();
  }
  void StartAnimation(Animation *new_anim)
  {
    this->kill_anim();
    new_anim->start();
    anim = new_anim;
    this->_isRunning = true;
  }
  void StopAnimation()
  {
    this->kill_anim();
  }
  void PauseAnimation()
  {
    this->_isRunning = false;
  }
  void ResumeAnimation()
  {
    this->_isRunning = true;
  }
  void UpdateAnimation()
  {
    if (!this->_isRunning)
      return;
    uint16_t freq = anim->get_freq();
    if (!freq)
      return anim->update();

    unsigned long curr_time = millis();
    if (uint16_t(curr_time - prev_time) > freq)
    {
      anim->update();
      prev_time = curr_time;
    }
  }

private:
  Animation *anim;
  bool _isRunning = false;
  unsigned long prev_time = millis();

  void kill_anim()
  {
    if (this->anim)
    {
      this->anim->stop();
      delete anim;
      this->_isRunning = false;
    }
  }
};

#endif