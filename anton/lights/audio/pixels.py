import numpy as np
import anton.lights.config as config

class LightConfig:
    def __init__(self, repetitions: int, pixel_stretch: int, rotate: bool, mirrored: bool) -> None:
        self.repetitions = repetitions
        self.pixel_stretch = pixel_stretch
        self.rotate = rotate
        self.mirrored = mirrored

    def encode(self) -> bytes:
        return b''.join([val.to_bytes(1, 'big') for val in [self.repetitions, self.pixel_stretch,
                                                            (int(self.mirrored) << 7) + self.rotate]])

class Pixels():
    def __init__(self, packet_sender: callable, config_byte: bytes, mode_byte: bytes, lconfig: LightConfig):
        self.lightConfig = lconfig
        
        self._gamma = np.load(config.GAMMA_TABLE_PATH)
        """Gamma lookup table used for nonlinear brightness correction"""

        self.regions = config.N_PIXELS // (lconfig.pixel_stretch * lconfig.repetitions * (1+lconfig.mirrored))
        self._prev_pixels = np.tile(253, (3, self.regions))
        """Pixel values that were most recently displayed on the LED strip"""

        self.pixels = np.tile(1, (3, self.regions))
        """Pixel values for the LED strip"""

        self.packet_sender = packet_sender
        self.mode_byte = mode_byte
        self.config_byte = config_byte

    def configure(self):
        self.packet_sender(self.config_byte + self.lightConfig.encode())

    def update(self, colors: np.array):
        """Sends UDP packets to ESP8266 to update LED strip values

        The ESP8266 will receive and decode the packets to determine what values
        to display on the LED strip.
        """
        # Truncate values and cast to integer
        colors = np.clip(colors, 0, 255).astype(int)
        
        # Optionally apply gamma correction
        p = self._gamma[colors] if config.SOFTWARE_GAMMA_CORRECTION else np.copy(colors)
        
        # save old state
        self._prev_pixels = np.copy(self.pixels)
        
        MAX_PIXELS_PER_PACKET = 127
        # send new pixels without idx for rotate
        if self.lightConfig.rotate:
            # update internal state
            self.pixels = np.concatenate((p, self.pixels),axis=1)[:self.regions] # rotate new pixels in
            
            # send pixels
            n_packets = np.ma.size(p,1) // MAX_PIXELS_PER_PACKET + 1
            p_packets = np.array_split(p,n_packets)
            for pix_g in p_packets:  
                m = self.mode_byte
                for pix in pix_g:
                    m+= bytes(list(pix))
                if len(m):
                    self.packet_sender(m)
        else:
            if p.shape != self.pixels.shape:
                raise RuntimeError("Invalid Pixel Length on Update")
            
            # Pixel indices
            idx = range(self.pixels.shape[1])
            idx = [i for i in idx if not np.array_equal(
                p[:, i], self._prev_pixels[:, i])]
            n_packets = len(idx) // MAX_PIXELS_PER_PACKET + 1
            idx = np.array_split(idx, n_packets)
            
            # update internal state
            self.pixels = p
            
            # send pixels
            for packet_indices in idx:
                m = self.mode_byte
                for i in packet_indices:
                    m += bytes([i]+list(p[:,i]))
                if len(m):
                    self.packet_sender(m)

# Execute this file to run a LED strand test
# If everything is working, you should see a red, green, and blue pixel scroll
# across the LED strip continously
if __name__ == '__main__':
    import time
    from anton.lights.modes import Lights, send_arduinos
    #Turn all pixels off
    pixels = Pixels(send_arduinos,Lights.MODES['audio'].mode_byte, Lights.MODES['audio'].update_byte, LightConfig(2,2,False,True))
    pix = np.copy(pixels.pixels)
    pix *= 0
    pix[0, 0] = 255  # Set 1st pixel red
    pix[1, 1] = 255  # Set 2nd pixel green
    pix[2, 2] = 255  # Set 3rd pixel blue
    time.sleep(2)
    import random
    print('Starting LED strand test')
    while True:
        pix = np.roll(pix, 1, axis=1)
        pixels.update(pix)
        time.sleep(0.1)
        #send_arduinos(bytes.fromhex('00'))
