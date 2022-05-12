from anton.lights.lightMode import LightMode, ModeCode
from anton.lights.rgb import RGBColor
from anton.lights.lightServer import register_mode

@register_mode
class Strobe(LightMode):
    def __init__(self):
        super().__init__(ModeCode.STROBE, config={'color':RGBColor()})
    
    def encode_config(self, config) -> bytes:
        return bytes(RGBColor(config['color']))
    
    def start(self):
        pass
        
    def stop(self):
        pass