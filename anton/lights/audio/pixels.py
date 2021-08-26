import numpy as np
import anton.lights.config as config


class Pixels():
    def __init__(self, packet_sender: function, config_byte: bytes,
                 mode_byte: bytes, num_zones: int, pixel_stretch: int, rotate: bool, mirrored: bool):
        
        self._gamma = np.load(config.GAMMA_TABLE_PATH)
        """Gamma lookup table used for nonlinear brightness correction"""

        self._prev_pixels = np.tile(253, (3, config.N_PIXELS))
        """Pixel values that were most recently displayed on the LED strip"""

        self.pixels = np.tile(1, (3, config.N_PIXELS))
        """Pixel values for the LED strip"""

        self.packet_sender = packet_sender
        self.config_byte = config_byte
        self.mode_byte = mode_byte
        self.num_zones = num_zones
        self.pixel_stretch = pixel_stretch
        self.rotate = rotate
        self.mirrored = mirrored

    def update(self):
        """Sends UDP packets to ESP8266 to update LED strip values

        The ESP8266 will receive and decode the packets to determine what values
        to display on the LED strip. The communication protocol supports LED strips
        with a maximum of 256 LEDs.

        The packet encoding scheme is:
            |r|g|b|i|
        where
            r (0 to 255): Red value of LED
            g (0 to 255): Green value of LED
            b (0 to 255): Blue value of LED
            i (0 to 255): Index of LED to change (zero-based)
        """
        # Truncate values and cast to integer
        self.pixels = np.clip(self.pixels, 0, 255).astype(int)
        # Optionally apply gamma correction
        p = self._gamma[self.pixels] if config.SOFTWARE_GAMMA_CORRECTION else np.copy(
            self.pixels)
        MAX_PIXELS_PER_PACKET = 127
        # Pixel indices
        idx = range(self.pixels.shape[1])
        idx = [i for i in idx if not np.array_equal(
            p[:, i], self._prev_pixels[:, i])]
        n_packets = len(idx) // MAX_PIXELS_PER_PACKET + 1
        idx = np.array_split(idx, n_packets)

        for packet_indices in idx:
            m = self.mode_byte
            for i in packet_indices:
                m += bytes(list(p[:,i])+[i])
            if len(m):
                self.packet_sender(m)

        self._prev_pixels = np.copy(p)

    def set_pixels(self, pixel_arr):
        self.pixels = pixel_arr


# Execute this file to run a LED strand test
# If everything is working, you should see a red, green, and blue pixel scroll
# across the LED strip continously
if __name__ == '__main__':
    import time
    from anton.lights.modes import send_arduinos, Lights
    # Turn all pixels off
    pixels = Pixels(send_arduinos, Lights.MODES['audio'])
    pixels.pixels *= 0
    pixels.pixels[0, 0] = 255  # Set 1st pixel red
    pixels.pixels[1, 1] = 255  # Set 2nd pixel green
    pixels.pixels[2, 2] = 255  # Set 3rd pixel blue
    print('Starting LED strand test')
    while True:
        pixels.pixels = np.roll(pixels.pixels, 1, axis=1)
        pixels.update()
        time.sleep(0.1)
