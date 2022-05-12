#ifndef ANIMRECIEVER_H
#define ANIMRECIEVER_H

#define UDPPORT 5001
#define UDP_BUFFER 512

#include "Animator.h"

using LedStrip = NeoPixelBrightnessBus<NeoGrbFeature, Neo800KbpsMethod>;

class RecieverAnimation : public Animation
{
public:
    RecieverAnimation(LedStrip* led,uint8_t reps, uint8_t stretch, bool mirror, bool rot) : Animation(led), 
        lightBuffer(packetBuffer), repetitions(reps), pixel_stretch(stretch), mirrored(mirror), rotate(rot) {
        this->zone_width = ledstrip->PixelCount() / (this->repetitions * (1 + this->mirrored) * this->pixel_stretch);
    }
    void start() override
    {
        // Clear lights
        solidColor(RgbColor(0, 0, 0));
        ledstrip->Show();
        Udp.begin(UDPPORT);
    }
    void update() override
    {
        // if there's data available, read a packet
        int packetSize = Udp.parsePacket();
        if (packetSize){
            // length of a designated repeating region
            int readSize = Udp.read(packetBuffer, UDP_BUFFER);
            const uint16_t seg_len = ledstrip->PixelCount() / this->repetitions;

            if (this->rotate)
            {
                if (this->mirrored) //rotate & mirrored
                {
                    for (int rep = 0; rep < this->repetitions; ++rep)
                    {
                        //determine bounds for repetition
                        const int left_bound = rep * seg_len;
                        const int right_bound = min((rep + 1) * seg_len, int(this->ledstrip->PixelCount()));
                        const int middle = left_bound + seg_len / 2; //integer truncated

                        //shift all pixels outward and replace central pixels
                        this->ledstrip->RotateLeft(this->pixel_stretch * uint16_t(readSize / 3), left_bound, middle-1);
                        this->ledstrip->RotateRight(this->pixel_stretch * uint16_t(readSize / 3), middle, right_bound-1);

                        //iterate through all sent pixels and update insides
                        for (int i = 0; i + 2 < readSize; i += 3)
                        {
                            RgbColor pixel = bytesToColor(lightBuffer + i);

                            //update new right pixels
                            this->SetPixelRange(pixel, middle + (i/3)*this->pixel_stretch, middle + ((i/3)+1) * this->pixel_stretch);

                            //update new left pixels
                            this->SetPixelRange(pixel, middle - ((i/3)+1) * this->pixel_stretch, middle - (i/3) * this->pixel_stretch);
                        }
                    }
                }
                else // rotate & not mirrored
                {
                    for (int rep = 0; rep < this->repetitions; ++rep)
                    {
                        //determine bounds for repetition
                        const int left_bound = rep * seg_len;
                        const int right_bound = min((rep + 1) * seg_len, int(this->ledstrip->PixelCount()));

                        //shift all pixels outward and replace leftmost pixels
                        this->ledstrip->RotateRight(this->pixel_stretch * uint16_t(readSize / 3), left_bound,  right_bound-1);

                        //iterate through all sent pixels and update insides
                        for (int i = 1; i + 2 < readSize; i += 3)
                        {
                            RgbColor pixel = bytesToColor(lightBuffer + i);
                            //update new left pixels
                            this->SetPixelRange(pixel, left_bound + (i/3) * this->pixel_stretch, left_bound + ((i/3)+1) * this->pixel_stretch);
                        }
                    }
                }
            }
            else
            { // not rotated
                for (int i = 0; i + 3 < readSize; i += 4)
                {
                    const uint8_t index = lightBuffer[i];

                    RgbColor pixel = bytesToColor(lightBuffer + i + 1);

                    if (index >= this->zone_width)
                        continue; // out of bounds

                    if (this->mirrored)
                    {
                        for (int rep = 0; rep < this->repetitions; ++rep)
                        {
                            const int left_bound = rep * seg_len + index * this->pixel_stretch;
                            const int right_bound = (rep + 1) * seg_len - index * this->pixel_stretch;

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
            ledstrip->Show();
        }
    }
    void stop() override 
    {
        Udp.stop()
    }
private:
    WiFiUDP Udp;
    uint16_t zone_width;
    uint8_t lightBuffer[UDP_BUFFER];
    uint8_t repetitions;
    uint8_t pixel_stretch;
    bool mirrored;
    bool rotate;
};

#endif
