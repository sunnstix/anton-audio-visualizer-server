from anton.lights.lightMode import LightMode, ModeCode
from anton.lights.rgb import RgbColor
from anton.lights.lightServer import register_mode, init_light_mode

@register_mode
class SolidColor(LightMode):
    def __init__(self):
        super().__init__(ModeCode.SOLID, uses_color = True)
    
    @init_light_mode   
    def start(self, **kwargs):
        return RgbColor(kwargs['color']).to_bytes()
        
    def stop(self):
        pass