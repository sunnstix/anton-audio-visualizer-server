from anton.lights.lightMode import LightMode, ModeCode
from anton.lights.rgb import RgbColor
from anton.lights.lightServer import register_mode

@register_mode
class SolidColor(LightMode):
    def __init__(self):
        super().__init__(ModeCode.SOLID, config={'color':RgbColor()})
        
    def encode_config(self, config):
        return RgbColor(config['color']).to_bytes()
    
    def initialize(self):
        pass
        
    def stop(self):
        pass