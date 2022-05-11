from enum import Enum

class ModeCode(Enum):
    OFF = 0
    RAINBOW = 1
    SOLID = 2
    STROBE = 3
    RECIEVER = 4

class LightMode:
    def __init__(self, modeId : int, uses_color : bool = False):
        self.modeId = modeId
        self.color_dep = uses_color
        
    def uses_color(self):
        return self.color_dep
    
    def get_mode_byte(self) -> bytes:
        return self.modeId.to_bytes(1,'big')
    
    def start(self,**kwargs) -> bytes:
        raise NotImplementedError
    
    def stop(self):
        raise NotImplementedError
