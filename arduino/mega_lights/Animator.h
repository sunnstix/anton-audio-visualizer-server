#ifndef ANIMATOR_H
#define ANIMATOR_H

// Animation
// ========================================================================
class Animation
{
  //virtual class for animation context
public:
  Animation() : frequency(0) {}
  Animation(uint16_t freq) : frequency(freq) {}
  virtual ~Animation() = 0;
  virtual void start() {}  //Initialization call
  virtual void update() {}
  virtual void stop() {}   // Stop call
  uint16_t get_freq() {return this->frequency;}
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
    if (uint16_t(curr_time - prev_time) > freq){
        anim->update();
        prev_time = curr_time;
    }
  }

private:
  Animation *anim;
  bool _isRunning = false;
  unsigned long prev_time = millis();

  void kill_anim() {
    if (this->anim) {
      this->anim->stop();
      delete anim;
      this->_isRunning = false;
    }
  }
};

#endif