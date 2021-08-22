#ifndef ANIMRECIEVER_H
#define ANIMRECIEVER_H

#include "Animator.h"

using LedStrip = NeoPixelBrightnessBus<NeoGrbFeature, Neo800KbpsMethod>;

class RecieverAnimation : public Animation
{
public:
    RecieverAnimation(LedStrip &led, uint8_t *packetBuffer, int &last_read) : Animation(led), lightBuffer(packetBuffer), readSize(last_read) {}
    void start() override
    {
        // Evaluate Configuration factors
        this->num_zones = packetBuffer[1];
        this->mirrored = bool((packetBuffer[2] & 8) >> 3);
        this->rotate = bool((packetBuffer[2] & 4) >> 2);
        this->pixel_stretch = packetBuffer[3];
        this->repetitions = ledstrip.PixelCount() / (num_zones * (1 + this->mirrored) * this->pixel_stretch);

        // Clear lights
        solidColor(RgbColor(0, 0, 0));
        ledstrip.Show();
    }
    void update() override
    {
        if (readSize) // if any packages have been recieved
        {
            // length of a designated repeating region
            const int seg_len = ledstrip.PixelCount() / this->repetitions;

            if (this->rotate)
            { // lights in rotate mode
                if (this->mirrored)
                {
                    for (int rep = 0; rep < this->repetitions; ++rep)
                    {
                        //determine bounds for repetition
                        const int left_bound = rep * seg_len;
                        const int right_bound = min((rep + 1) * seg_len, this->ledstrip.PixelCount());
                        const int middle = left_bound + seg_len / 2; //integer truncated

                        //shift all pixels outward and replace central pixels
                        this->ledstrip.RotateRight(this->pixel_stretch * readSize / 4 - 1, left_bound, middle);
                        this->ledstrip.RotateLeft(this->pixel_stretch * readSize / 4 - 1, middle, right_bound);

                        //iterate through all sent pixels and update insides
                        for (int i = 4; i + 3 < readSize; i += 4)
                        {
                            RgbColor pixel = bytesToColor(lightBuffer + i);

                            //update new right pixels
                            this->SetPixelRange(pixel, middle + i*this->pixel_stretch, middle + (i+1) * this->pixel_stretch);

                            //update new left pixels
                            this->SetPixelRange(pixel, middle - (i+1) * this->pixel_stretch, middle - i * this->pixel_stretch);
                        }
                    }
                }
                else
                {
                    for (int rep = 0; rep < this->repetitions; ++rep)
                    {
                        //determine bounds for repetition
                        const int left_bound = rep * seg_len;
                        const int right_bound = min((rep + 1) * seg_len, this->ledstrip.PixelCount());
                        const int middle = rep * seg_len + seg_len / 2 ;

                        //shift all pixels outward and replace central pixels
                        this->ledstrip.RotateRight(this->pixel_stretch * readSize / 4 - 1, left_bound,  right_bound);

                        //iterate through all sent pixels and update insides
                        for (int i = 4; i + 3 < readSize; i += 4)
                        {
                            RgbColor pixel = bytesToColor(lightBuffer + i);

                            //update new right pixels
                            this->SetPixelRange(pixel, middle + i*this->pixel_stretch, middle + (i+1) * this->pixel_stretch);

                            //update new left pixels
                            this->SetPixelRange(pixel, middle - (i+1) * this->pixel_stretch, middle - i * this->pixel_stretch);
                        }
                    }
                }
            }
            else
            {
                for (int i = 4; i + 3 < readSize; i += 4)
                {
                    //assumes 7 bit color values sent and rescale
                    RgbColor pixel = bytesToColor(lightBuffer + i);

                    const uint32_t index = ((lightBuffer[i + 2] & 7) << 8) + lightBuffer[i + 3];

                    if (index >= this->num_zones)
                        continue;

                    if (this->mirrored)
                    {
                        for (int rep = 0; rep < this->repetitions; ++rep)
                        {
                            const int left_bound = rep * seg_len + index * this->pixel_stretch;
                            const int right_bound = (rep + 1) * seg_len;

                            this->SetPixelRange(pixel, left_bound, left_bound + this->pixel_stretch);
                            this->SetPixelRange(pixel, right_bound - this->pixel_stretch, right_bound);
                        }
                    }
                    else
                    {
                        for (int rep = 0; rep < this->repetitions; ++rep)
                        {
                            const int left_bound = rep * seg_len + index * this->pixel_stretch;
                            this->SetPixelRange(pixel, left_bound, left_bound + this->pixel_stretch);
                        }
                    }
                }
            }
            ledstrip.Show();
        }
    }

private:
    uint8_t *lightBuffer;
    uint8_t num_zones;
    uint8_t repetitions;
    uint8_t pixel_stretch;
    bool mirrored;
    bool rotate;
    int &readSize;
};

#endif