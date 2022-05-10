from __future__ import print_function
import numpy as np
import anton.lights.config as config
import anton.lights.audio.melbank as melbank


class ExpFilter:
    """Simple exponential smoothing filter"""
    def __init__(self, val=0.0, alpha_decay=0.5, alpha_rise=0.5):
        """Small rise / decay factors = more smoothing"""
        assert 0.0 < alpha_decay < 1.0, 'Invalid decay smoothing factor'
        assert 0.0 < alpha_rise < 1.0, 'Invalid rise smoothing factor'
        self.alpha_decay = alpha_decay
        self.alpha_rise = alpha_rise
        self.value = val

    def update(self, value):
        if isinstance(self.value, (list, np.ndarray, tuple)):
            alpha = value - self.value
            alpha[alpha > 0.0] = self.alpha_rise
            alpha[alpha <= 0.0] = self.alpha_decay
        else:
            alpha = self.alpha_rise if value > self.value else self.alpha_decay
        self.value = alpha * value + (1.0 - alpha) * self.value
        return self.value


def rfft(data, window=None):
    window = 1.0 if window is None else window(len(data))
    ys = np.abs(np.fft.rfft(data * window))
    xs = np.fft.rfftfreq(len(data), 1.0 / config.MIC_RATE)
    return xs, ys


def fft(data, window=None):
    window = 1.0 if window is None else window(len(data))
    ys = np.fft.fft(data * window)
    xs = np.fft.fftfreq(len(data), 1.0 / config.MIC_RATE)
    return xs, ys

class MelBank:
    def __init__(self):
        self.samples = int(config.MIC_RATE * config.N_ROLLING_HISTORY / (2.0 * config.FPS))
        self.mel_y, (_, self.mel_x) = melbank.compute_melmat(num_mel_bands=config.N_FFT_BINS,
                                                freq_min=config.MIN_FREQUENCY,
                                                freq_max=config.MAX_FREQUENCY,
                                                num_fft_bands=self.samples,
                                                sample_rate=config.MIC_RATE)
        
    def get_samples(self):
        return self.samples
    
    def get_mels(self):
        return self.mel_x, self.mel_y
    
    def update(self):
        self.samples = int(config.MIC_RATE * config.N_ROLLING_HISTORY / (2.0 * config.FPS))
        self.mel_y, (_, self.mel_x) = melbank.compute_melmat(num_mel_bands=config.N_FFT_BINS,
                                                freq_min=config.MIN_FREQUENCY,
                                                freq_max=config.MAX_FREQUENCY,
                                                num_fft_bands=self.samples,
                                                sample_rate=config.MIC_RATE)