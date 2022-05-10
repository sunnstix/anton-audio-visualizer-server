from anton.lights.lightMode import LightMode
from anton.lights.lightServer import register_mode, init_light_mode

@register_mode
class Off(LightMode):
    def __init__(self):
        super().__init__(modeId = 0)
        
    @init_light_mode
    def start(self,**kwargs):
        return b''
        
    def stop(self):
        pass