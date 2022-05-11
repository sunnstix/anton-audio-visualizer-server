from anton.lights.lightMode import LightMode, ModeCode
from anton.lights.lightServer import register_mode, init_light_mode

@register_mode
class Off(LightMode):
    def __init__(self):
        super().__init__(ModeCode.OFF)
        
    @init_light_mode
    def start(self,**kwargs):
        return b''
        
    def stop(self):
        pass