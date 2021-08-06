import time
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
import anton.lights.config as config
from anton.lights.audio.audioprocess import AudioProcess
import anton.lights.audio.dsp as dsp
from anton.lights.audio.pixels import Pixels
import threading

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

# Visualizer
# =======================================================

melbank = dsp.MelBank()

class Visualizer(Pixels):
    
    fft_window = np.hamming(int(config.MIC_RATE / config.FPS) * config.N_ROLLING_HISTORY)
    
    # Number of audio samples to read every time frame
    samples_per_frame = int(config.MIC_RATE / config.FPS)
    

    def __init__(self, packet_sender, mode_byte):
        Pixels.__init__(self,packet_sender, mode_byte)
        self._time_prev = time.time() * 1000.0
        self._fps = dsp.ExpFilter(val=config.FPS, alpha_decay=0.2, alpha_rise=0.2)
        self.audio_process = AudioProcess()
        self.pixel_arr = np.tile(1.0, (3, config.N_PIXELS // 2))
        self._prev_spectrum = np.tile(0.01, config.N_PIXELS // 2)
        self.prev_fps_update = time.time()
        
        # Array containing the rolling audio sample window
        self.audio_roll = np.random.rand(config.N_ROLLING_HISTORY, Visualizer.samples_per_frame) / 1e16
        
        # Static Filtering Configurations
        self.r_filt = dsp.ExpFilter(np.tile(0.01, config.N_PIXELS // 2),
                        alpha_decay=0.2, alpha_rise=0.99)
        self.g_filt = dsp.ExpFilter(np.tile(0.01, config.N_PIXELS // 2),
                            alpha_decay=0.05, alpha_rise=0.3)
        self.b_filt = dsp.ExpFilter(np.tile(0.01, config.N_PIXELS // 2),
                            alpha_decay=0.1, alpha_rise=0.5)
        self.common_mode = dsp.ExpFilter(np.tile(0.01, config.N_PIXELS // 2),
                            alpha_decay=0.99, alpha_rise=0.01)
        self.p_filt = dsp.ExpFilter(np.tile(1, (3, config.N_PIXELS // 2)),
                            alpha_decay=0.1, alpha_rise=0.99)
        self.gain = dsp.ExpFilter(np.tile(0.01, config.N_FFT_BINS),
                                alpha_decay=0.001, alpha_rise=0.99)
        
        # Audio Rectification Configurations
        self.fft_plot_filter = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                            alpha_decay=0.5, alpha_rise=0.99)
        self.mel_gain = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                                alpha_decay=0.01, alpha_rise=0.99)
        self.mel_smoothing = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                                alpha_decay=0.5, alpha_rise=0.99)
        self.volume = dsp.ExpFilter(config.MIN_VOLUME_THRESHOLD,
                            alpha_decay=0.02, alpha_rise=0.02)
        self.mel = None
        self.thread = None
        
    def start(self,visualization_type):
        if config.USE_GUI:
            if visualization_type == "spectrum":
                GUI.spectrum_click(0)
            elif visualization_type == "energy":
                GUI.energy_click(0)
            elif visualization_type == "scroll":
                GUI.scroll_click(0)
            else:
                raise ValueError
            
            self.thread = gui.GuiThread(self.run,self.mel,self.pixels)
            GUI.add_thread(self.thread.progress)
            self.thread.start()
            
        else: 
            self.set_effect(visualization_type)
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
        
    def run(self):
        self.update()
        self.audio_process.start_stream(self.__audio_update)
        
    def stop(self):
        if self.thread is not None:
            if config.USE_GUI:
                if self.thread.isRunning():
                    self.audio_process.kill_stream()
                    self.thread.quit()
                    self.thread.wait()
                    self.audio_process.stop_stream()
            else:
                if self.thread.is_alive():
                    self.audio_process.kill_stream()
                    self.thread.join()
                    self.audio_process.stop_stream()
    
    def __frames_per_second(self):
        """Return the estimated frames per second

        Returns the current estimate for frames-per-second (FPS).
        FPS is estimated by measured the amount of time that has elapsed since
        this function was previously called. The FPS estimate is low-pass filtered
        to reduce noise.

        This function is intended to be called one time for every iteration of
        the program's main loop.

        Returns
        -------
        fps : float
            Estimated frames-per-second. This value is low-pass filtered
            to reduce noise.
        """
        time_now = time.time() * 1000.0
        dt = time_now - self._time_prev
        self._time_prev = time_now
        if dt == 0.0:
            return self._fps.value
        return self._fps.update(1000.0 / dt)
    
    def __scroll_effect(self,audio):
        """Effect that originates in the center and scrolls outwards"""
        audio = audio**2.0
        self.gain.update(audio)
        audio /= self.gain.value
        audio *= 255.0
        r = int(np.max(audio[:len(audio) // 3]))
        g = int(np.max(audio[len(audio) // 3: 2 * len(audio) // 3]))
        b = int(np.max(audio[2 * len(audio) // 3:]))
        # Scrolling effect window
        self.pixel_arr[:, 1:] = self.pixel_arr[:, :-1]
        self.pixel_arr *= 0.98
        self.pixel_arr = gaussian_filter1d(self.pixel_arr, sigma=0.2)
        # Create new color originating at the center
        self.pixel_arr[0, 0] = r
        self.pixel_arr[1, 0] = g
        self.pixel_arr[2, 0] = b
        # Update the LED strip
        return np.concatenate((self.pixel_arr[:, ::-1], self.pixel_arr), axis=1)

    def __energy_effect(self,audio):
        """Effect that expands from the center with increasing sound energy"""
        audio = np.copy(audio)
        self.gain.update(audio)
        audio /= self.gain.value
        # Scale by the width of the LED strip
        audio *= float((config.N_PIXELS // 2) - 1)
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
        self.pixel_arr[0, :] = gaussian_filter1d(self.pixel_arr[0, :], sigma=4.0)
        self.pixel_arr[1, :] = gaussian_filter1d(self.pixel_arr[1, :], sigma=4.0)
        self.pixel_arr[2, :] = gaussian_filter1d(self.pixel_arr[2, :], sigma=4.0)
        # Set the new pixel value
        return np.concatenate((self.pixel_arr[:, ::-1], self.pixel_arr), axis=1)
    
    def __spectrum_effect(self,audio):
        """Effect that maps the Mel filterbank frequencies onto the LED strip"""
        audio = np.copy(interpolate(audio, config.N_PIXELS // 2))
        self.common_mode.update(audio)
        diff = audio - self._prev_spectrum
        self._prev_spectrum = np.copy(audio)
        # Color channel mappings
        r = self.r_filt.update(audio - self.common_mode.value)
        g = np.abs(diff)
        b = self.b_filt.update(np.copy(audio))
        # Mirror the color channels for symmetric output
        r = np.concatenate((r[::-1], r))
        g = np.concatenate((g[::-1], g))
        b = np.concatenate((b[::-1], b))
        return np.array([r, g,b]) * 255
    
    @classmethod
    def set_effect(self,effect):
        if effect == 'scroll':
            self.visualization_effect = self.__scroll_effect
        elif effect == 'energy':
            self.visualization_effect = self.__energy_effect
        elif effect == 'spectrum':
            self.visualization_effect = self.__spectrum_effect
        else:
            raise ValueError

    def __audio_update(self,audio_samples):
        # Normalize samples between 0 and 1
        audio = audio_samples / 2.0**15
        # Construct a rolling window of audio samples
        self.audio_roll[:-1] = self.audio_roll[1:]
        self.audio_roll[-1, :] = np.copy(audio)
        y_data = np.concatenate(self.audio_roll, axis=0).astype(np.float32)
        
        vol = np.max(np.abs(y_data))
        if vol < config.MIN_VOLUME_THRESHOLD:
            print('No audio input. Volume below threshold. Volume:', vol)
            self.pixels = np.tile(0, (3, config.N_PIXELS))
            self.update()
        else:
            # Transform audio input into the frequency domain
            N = len(y_data)
            N_zeros = 2**int(np.ceil(np.log2(N))) - N
            # Pad with zeros until the next power of two
            y_data *= Visualizer.fft_window
            y_padded = np.pad(y_data, (0, N_zeros), mode='constant')
            YS = np.abs(np.fft.rfft(y_padded)[:N // 2])
            # Construct a Mel filterbank from the FFT data
            _, mel_y = melbank.get_mels()
            self.mel = np.atleast_2d(YS).T * mel_y.T
            # Scale data to values more suitable for visualization
            # mel = np.sum(mel, axis=0)
            self.mel = np.sum(self.mel, axis=0)
            self.mel = self.mel**2.0
            # Gain normalization
            self.mel_gain.update(np.max(gaussian_filter1d(self.mel, sigma=1.0)))
            self.mel /= self.mel_gain.value
            self.mel = self.mel_smoothing.update(self.mel)
            # Map filterbank output onto LED strip
            output = self.visualization_effect(self.mel)
            self.pixels = output
            self.update()
        #     if config.USE_GUI:
        #         # Plot filterbank output
        #         x = np.linspace(config.MIN_FREQUENCY, config.MAX_FREQUENCY, len(mel))
        #         mel_curve.setData(x=x, y=self.fft_plot_filter.update(mel))
        #         # Plot the color channels
        #         r_curve.setData(y=self.pixels[0])
        #         g_curve.setData(y=self.pixels[1])
        #         b_curve.setData(y=self.pixels[2])
                
        # if config.USE_GUI:
        #     app.processEvents()
        
        if config.DISPLAY_FPS:
            fps = self.__frames_per_second()
            if time.time() - 0.5 > self.prev_fps_update:
                self.prev_fps_update = time.time()
                print('FPS {:.0f} / {:.0f}'.format(fps, config.FPS))
                


# GUI
# =======================================================

if config.USE_GUI:
    import anton.lights.audio.gui as gui
    GUI = gui.VisGUI(Visualizer.set_effect,melbank)

if __name__ == '__main__':
    from anton.lights.modes import send_arduinos, Lights
    visualizer = Visualizer(send_arduinos,Lights.MODES['audio'])
    visualizer.start('scroll')
    print('Starting Audio Visualization')
    time.sleep(5)
    print('Stopping thread')
    visualizer.stop()