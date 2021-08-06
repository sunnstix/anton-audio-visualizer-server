import socket
import anton.lights.config as config
from anton.lights.audio.visualizer import Visualizer

_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Helpers
# =======================================================

def send_arduinos(packet : bytes):
    """Sends packets to light controllers."""
    for ip in config.ARDUINO_IPS:
        try:
            _sock.sendto(packet,(ip, config.UDP_PORT))
        except Exception:
            continue

class RgbColor:
    def __init__(self,red:int,green:int,blue:int):
        self.r = red
        self.g = green
        self.b = blue
        
    def __init__(self,flask_args:dict):
        self.r = flask_args.get('red', default=None, type=int)
        self.g = flask_args.get('green', default=None, type=int)
        self.b = flask_args.get('blue', default=None, type=int)
        if self.r is None or self.g is None or self.g is None:
            raise ValueError
    
    def to_bytes(self):
        return self.r.to_bytes(1,'big') + self.g.to_bytes(1,'big') + self.b.to_bytes(1,'big')
    

# Light Modes
# =======================================================

class Lights():
    
    MODES = {
        'off': b'\x00',
        'solid-color': b'\x01',
        'rotate-rainbow': b'\x02',
        'audio': b'\x03',
        'strobe': b'\x04'
    }
    
    
    
    def __init__(self):
        self.CURRENT_MODE = 'off'
        self.visualizer = Visualizer(send_arduinos,Lights.MODES['audio'])
        self.lights_off()

    def current_mode(self):
        return self.CURRENT_MODE

    def lights_off(self):
        self.kill_audio()
        self.CURRENT_MODE = 'off'
        send_arduinos(Lights.MODES['off'])

    def rotate_rainbow(self):
        self.kill_audio()
        self.CURRENT_MODE = 'rotate-rainbow'
        send_arduinos(Lights.MODES['rotate-rainbow'])
        
    def solid_color(self, color : RgbColor):
        self.kill_audio()
        self.CURRENT_MODE = 'solid-color'
        m = Lights.MODES['solid-color'] + color.to_bytes()
        send_arduinos(m)
        
    def audio_mode(self, audio_mode : str):
        self.kill_audio()
        self.CURRENT_MODE = 'audio'
        self.visualizer.start(audio_mode)
        
    def kill_audio(self):
        self.visualizer.stop()

    def strobe(self, color : RgbColor):
        self.kill_audio()
        self.CURRENT_MODE = 'strobe'
        m = Lights.MODES['strobe'] + color.to_bytes()
        send_arduinos(m)