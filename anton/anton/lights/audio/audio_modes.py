import numpy as np
from scipy.ndimage.filters import gaussian_filter1d

import anton.lights.config as config
import anton.lights.audio.dsp as dsp

from anton.lights.audio.pixels import Pixels, LightConfig


class AudioMode(Pixels):
    melbank = dsp.MelBank()

    fft_window = np.hamming(
        int(config.MIC_RATE / config.FPS) * config.N_ROLLING_HISTORY)

    # Static Filtering Configurations
    gain = dsp.ExpFilter(np.tile(0.01, config.N_FFT_BINS),
                         alpha_decay=0.001, alpha_rise=0.99)

    # Audio Rectification Configurations
    fft_plot_filter = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                                    alpha_decay=0.5, alpha_rise=0.99)
    mel_gain = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                             alpha_decay=0.01, alpha_rise=0.99)
    mel_smoothing = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                                  alpha_decay=0.5, alpha_rise=0.99)
    volume = dsp.ExpFilter(config.MIN_VOLUME_THRESHOLD,
                           alpha_decay=0.02, alpha_rise=0.02)

    # Number of audio samples to read every time frame
    samples_per_frame = int(config.MIC_RATE / config.FPS)

    def __init__(self, packet_sender: callable, config_byte: bytes, mode_byte: bytes, l_config: LightConfig) -> None:
        super().__init__(packet_sender, config_byte, mode_byte, l_config)

        # Array containing the rolling audio sample window
        self.audio_roll = np.random.rand(
            config.N_ROLLING_HISTORY, AudioMode.samples_per_frame) / 1e16

        self.mel = None
        self.mode_byte = mode_byte
        self.config_byte = config_byte

        # Pixel Scaling Config Matrices
        self.r_filt = dsp.ExpFilter(np.tile(0.01, self.regions),
                                    alpha_decay=0.2, alpha_rise=0.99)
        self.g_filt = dsp.ExpFilter(np.tile(0.01, self.regions),
                                    alpha_decay=0.05, alpha_rise=0.3)
        self.b_filt = dsp.ExpFilter(np.tile(0.01, self.regions),
                                    alpha_decay=0.1, alpha_rise=0.5)
        self.common_mode = dsp.ExpFilter(np.tile(0.01, self.regions),
                                         alpha_decay=0.99, alpha_rise=0.01)
        self.p_filt = dsp.ExpFilter(np.tile(1, (3, self.regions)),
                                    alpha_decay=0.1, alpha_rise=0.99)

    def start(self):
        self.configure()

    def audio_update(self, audio_samples):
        # Normalize samples between 0 and 1
        audio = audio_samples / 2.0**15
        # Construct a rolling window of audio samples
        self.audio_roll[:-1] = self.audio_roll[1:]
        self.audio_roll[-1, :] = np.copy(audio)
        y_data = np.concatenate(self.audio_roll, axis=0).astype(np.float32)

        vol = np.max(np.abs(y_data))
        if vol < config.MIN_VOLUME_THRESHOLD:
            print('No audio input. Volume below threshold. Volume:', vol)
            self.update(
                np.tile(0, (3, 1 if self.lightConfig.rotate else self.regions)))
        else:
            # Transform audio input into the frequency domain
            N = len(y_data)
            N_zeros = 2**int(np.ceil(np.log2(N))) - N
            # Pad with zeros until the next power of two
            y_data *= AudioMode.fft_window
            y_padded = np.pad(y_data, (0, N_zeros), mode='constant')
            YS = np.abs(np.fft.rfft(y_padded)[:N // 2])
            # Construct a Mel filterbank from the FFT data
            _, mel_y = AudioMode.melbank.get_mels()
            self.mel = np.atleast_2d(YS).T * mel_y.T
            # Scale data to values more suitable for visualization
            self.mel = np.sum(self.mel, axis=0)
            self.mel = self.mel**2.0
            # Gain normalization
            self.mel_gain.update(
                np.max(gaussian_filter1d(self.mel, sigma=1.0)))
            self.mel /= self.mel_gain.value
            self.mel = self.mel_smoothing.update(self.mel)
            # Map filterbank output onto LED strip
            self.update(self.effect(self.mel))

    def effect(self, audio) -> np.array:
        raise NotImplementedError

class ScrollMode(AudioMode):
    def __init__(self, packet_sender: callable, config_byte: bytes, mode_byte: bytes, repetitions: int = 4, pixel_stretch: int = 1, mirrored: bool = True) -> None:
        super().__init__(packet_sender, config_byte, mode_byte,
                         LightConfig(repetitions, pixel_stretch, True, mirrored))
        # self.pixel_arr = np.tile(1.0, (3, self.regions))

    def effect(self, audio) -> np.array:
        audio = audio**2.0
        self.gain.update(audio)
        audio /= self.gain.value
        audio *= 255.0
        r = int(np.max(audio[:len(audio) // 3]))
        g = int(np.max(audio[len(audio) // 3: 2 * len(audio) // 3]))
        b = int(np.max(audio[2 * len(audio) // 3:]))
        # Scrolling effect window
        # self.pixel_arr[:, 1:] = self.pixel_arr[:, :-1]
        # self.pixel_arr = gaussian_filter1d(0.98 * self.pixel_arr, sigma=0.2)
        # # Create new color originating at the center
        # self.pixel_arr[0, 0] = r
        # self.pixel_arr[1, 0] = g
        # self.pixel_arr[2, 0] = b
        # Update the LED strip
        return np.array([[r],[g],[b]])

class EnergyMode(AudioMode):
    def __init__(self, packet_sender: callable, config_byte: bytes, mode_byte: bytes, repetitions: int = 1, pixel_stretch: int = 1) -> None:
        super().__init__(packet_sender, config_byte, mode_byte,
                         LightConfig(repetitions, pixel_stretch, False, True))
        self.pixel_arr = np.tile(1.0, (3, self.regions))

    def effect(self, audio) -> np.array:
        audio = np.copy(audio)
        self.gain.update(audio)
        audio /= self.gain.value
        # Scale by the width of the LED strip
        audio *= float((self.regions) - 1)
        # Map color channels according to energy in the different freq bands
        scale = 0.9
        r = int(np.mean(audio[:len(audio) // 3]**scale))
        g = int(np.mean(audio[len(audio) // 3: 2 * len(audio) // 3]**scale))
        b = int(np.mean(audio[2 * len(audio) // 3:]**scale))
        # Assign color to different frequency regions
        self.pixel_arr[0, :r] = 255.0
        self.pixel_arr[0, r:] = 0.0
        self.pixel_arr[1, :g] = 255.0
        self.pixel_arr[1, g:] = 0.0
        self.pixel_arr[2, :b] = 255.0
        self.pixel_arr[2, b:] = 0.0
        self.p_filt.update(self.pixel_arr)
        self.pixel_arr = np.round(self.p_filt.value)
        # Apply substantial blur to smooth the edges
        self.pixel_arr[0, :] = gaussian_filter1d(
            self.pixel_arr[0, :], sigma=4.0)
        self.pixel_arr[1, :] = gaussian_filter1d(
            self.pixel_arr[1, :], sigma=4.0)
        self.pixel_arr[2, :] = gaussian_filter1d(
            self.pixel_arr[2, :], sigma=4.0)
        # Set the new pixel value
        return self.pixel_arr

class SpectrumMode(AudioMode):
    def __init__(self, packet_sender: callable, config_byte: bytes, mode_byte: bytes, repetitions: int = 1, pixel_stretch: int = 1) -> None:
        super().__init__(packet_sender, config_byte, mode_byte,
                         LightConfig(repetitions, pixel_stretch, False, True))
        self._prev_spectrum = np.tile(0.01, self.regions)

    def effect(self, audio) -> np.array:
        audio = np.copy(interpolate(audio, self.regions))
        self.common_mode.update(audio)
        diff = audio - self._prev_spectrum
        self._prev_spectrum = np.copy(audio)
        # Color channel mappings
        r = self.r_filt.update(audio - self.common_mode.value)
        g = np.abs(diff)
        b = self.b_filt.update(np.copy(audio))
        print(r,g,b)
        return np.array([r, g, b]) * 255


# Helpers
# =======================================================

def memoize(function):
    """Provides a decorator for memoizing functions"""
    from functools import wraps
    memo = {}

    @wraps(function)
    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper


@memoize
def _normalized_linspace(size):
    return np.linspace(0, 1, size)


def interpolate(y, new_length):
    """Intelligently resizes the array by linearly interpolating the values

    Parameters
    ----------
    y : np.array
        Array that should be resized

    new_length : int
        The length of the new interpolated array

    Returns
    -------
    z : np.array
        New array with length of new_length that contains the interpolated
        values of y.
    """
    if len(y) == new_length:
        return y
    x_old = _normalized_linspace(len(y))
    x_new = _normalized_linspace(new_length)
    z = np.interp(x_new, x_old, y)
    return z
