import socket
import anton.lights.config as config
from anton.lights.audio.visualizer import Visualizer

_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Helpers
# =======================================================

class RgbColor:
    def __init__(self, *args):
        if len(args) == 1:
            self.r, self.g, self.b = tuple(int(args[0].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        elif len(args) == 3:
            self.r, self.g, self.b = args
        
        if self.r is None or self.g is None or self.g is None:
            raise ValueError
        
    
    def to_hex(self):
        return '#%02x%02x%02x' % (self.r, self.g, self.b)
    
    def to_bytes(self):
        return self.r.to_bytes(1,'big') + self.g.to_bytes(1,'big') + self.b.to_bytes(1,'big')
    

# Light Modes
# =======================================================

class LightMode:
    def __init__(self, mode_byte : bytes, uses_color : bool = False, submodes : list = list()):
        self.mode_byte = mode_byte
        self.color_dep = uses_color
        self.submodes= submodes
        
    def uses_color(self):
        return self.color_dep
    
    def get_submodes(self):
        return self.submodes
    
    def start(self,**kwargs):
        raise NotImplementedError
    
    def stop(self):
        raise NotImplementedError
    
    def send_arduinos(packet : bytes):
        """Sends packets to light controllers."""
        for ip in config.ARDUINO_IPS:
            try:
                _sock.sendto(packet,(ip, config.UDP_PORT))
            except Exception:
                continue
        
    
class OffMode(LightMode):
    def __init__(self,mode_byte : bytes):
        super().__init__(mode_byte)
        
    def start(self,**kwargs):
        self.send_arduinos(self.mode_byte)
        
    def stop(self):
        return

class SolidColorMode(LightMode):
    def __init__(self,mode_byte : bytes):
        super().__init__(mode_byte, uses_color = True)
        
    def start(self, **kwargs):
        self.send_arduinos(self.mode_byte + RgbColor(kwargs['color']).to_bytes())
        
    def stop(self):
        return
    
class RainbowMode(LightMode):
    def __init__(self,mode_byte : bytes):
        super().__init__(mode_byte)
        
    def start(self, **kwargs):
        self.send_arduinos(self.mode_byte)
        
    def stop(self):
        return
    
class AudioMode(LightMode):
    def __init__(self,mode_byte : bytes):
        super().__init__(mode_byte, submodes=['scroll', 'spectrum', 'energy'])
        self.visualizer = Visualizer(self.send_arduinos,mode_byte)
        
    def start(self, **kwargs):
        self.visualizer.start(kwargs['submode'])
        
    def stop(self):
        self.visualizer.stop()
        
class StrobeMode(LightMode):
    def __init__(self,mode_byte : bytes):
        super().__init__(mode_byte, uses_color=True)
        
    def start(self, **kwargs):
        self.send_arduinos(self.mode_byte + RgbColor(kwargs['color']).to_bytes())
        
    def stop(self):
        return
        
        
class Lights():
    
    MODES = {
        'off': OffMode(b'\x00'),
        'solid-color': SolidColorMode(b'\x01'),
        'rainbow': RainbowMode(b'\x02'),
        'audio': AudioMode(b'\x03'),
        'strobe': StrobeMode(b'\x04')
    }
    
    @classmethod
    def list_modes(self):
        return {modekey:{'color': mode.uses_color(), 'submodes': mode.get_submodes()} for modekey, mode in Lights.MODES.items()}
    
    def __init__(self):
        self.mode = 'off'
        self.submode = 'scroll'
        self.color = RgbColor(0,0,0)
        Lights.MODES[self.mode].start()

    def get_current_mode(self):
        return self.mode
    
    def get_current_submode(self):
        return self.submode
    
    def get_current_color(self):
        return self.color.to_hex()
   
    def set_mode(self, mode : str, **kwargs):
        Lights.MODES[self.mode].stop()
        self.mode = mode
        self.submode = kwargs.get('submode',self.submode)
        self.color = self.color if not kwargs.get('color') else RgbColor(kwargs.get('color'))
        Lights.MODES[self.mode].start(**kwargs)
        
