from asyncio import streams
import time
import numpy as np
import pyaudio
import anton.lights.config as config

class AudioProcess():
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.frames_per_buffer = int(config.MIC_RATE / config.FPS)
        self.overflows = 0
        self.prev_ovf_time = time.time()
        self.running = False
        
    def start_stream(self,callback):
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=config.MIC_RATE,
                                input=True,
                                frames_per_buffer=self.frames_per_buffer)
        self.running = True
        self.overflows = 0
        while self.running:
            try:
                y = np.fromstring(self.stream.read(self.frames_per_buffer, exception_on_overflow=False), dtype=np.int16)
                y = y.astype(np.float32)
                self.stream.read(self.stream.get_read_available(), exception_on_overflow=False)
                callback(y)
            except IOError:
                self.overflows += 1
                if time.time() > self.prev_ovf_time + 1:
                    self.prev_ovf_time = time.time()
                    print('Audio buffer has overflowed {} times'.format(self.overflows))
                    
    def kill_stream(self):
        self.running = False
    
    def stop_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        