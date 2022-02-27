import time
import threading

import anton.lights.config as config
from anton.lights.audio.audioprocess import AudioProcess
import anton.lights.audio.dsp as dsp
from anton.lights.audio.audio_modes import ScrollMode, SpectrumMode, EnergyMode

# Visualizer
# =======================================================
class Visualizer():
    
    def __init__(self, packet_sender : callable, config_byte: bytes, mode_byte: bytes):
        self._time_prev = time.time() * 1000.0
        self._fps = dsp.ExpFilter(val=config.FPS, alpha_decay=0.2, alpha_rise=0.2)
        self.audio_process = AudioProcess()
        self.prev_fps_update = time.time()
        self.thread = None
        
        self.config_byte = config_byte
        self.mode_byte = mode_byte
        self.packet_sender = packet_sender
        
    def start(self,visualization_type):
        self.set_effect(visualization_type)
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        
    def run(self):
        self.visualization_effect.start()
        self.audio_process.start_stream(self.visualization_effect.audio_update)
        
    def stop(self):
        if self.thread is not None:
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

    def set_effect(self,effect):
        if effect == 'scroll':
            self.visualization_effect = ScrollMode(self.packet_sender, self.config_byte, self.mode_byte)
        elif effect == 'energy':
            self.visualization_effect = EnergyMode(self.packet_sender, self.config_byte, self.mode_byte, 4)
        elif effect == 'spectrum':
            self.visualization_effect = SpectrumMode(self.packet_sender, self.config_byte, self.mode_byte)
        else:
            raise ValueError
        
    # if config.DISPLAY_FPS:
    #     fps = self.__frames_per_second()
    #     if time.time() - 0.5 > self.prev_fps_update:
    #         self.prev_fps_update = time.time()
    #         print('FPS {:.0f} / {:.0f}'.format(fps, config.FPS))
            

if __name__ == '__main__':
    from anton.lights.modes import send_arduinos, Lights
    visualizer = Visualizer(send_arduinos,Lights.MODES['audio'].mode_byte, Lights.MODES['audio'].update_byte)
    visualizer.start('scroll')
    print('Starting Audio Visualization')
    time.sleep(900)
    print('Stopping thread')
    visualizer.stop()