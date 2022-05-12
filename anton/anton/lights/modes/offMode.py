from anton.lights.lightMode import LightMode, ModeCode
from anton.lights.lightServer import register_mode

@register_mode
class Off(LightMode):
    def __init__(self):
        super().__init__(ModeCode.OFF)
        
    def encode_config(self, config):
        return b''
    
    def start(self):
        pass
        
    def stop(self):
        pass