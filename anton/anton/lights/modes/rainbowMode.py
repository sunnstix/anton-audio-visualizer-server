from anton.lights.lightMode import LightMode, ModeCode
from anton.lights.lightServer import register_mode

@register_mode
class Rainbow(LightMode):
    def __init__(self):
        super().__init__(ModeCode.RAINBOW)
        
    def encode_config(self, config):
        return b''
    
    def initialize(self):
        pass
        
    def stop(self):
        pass