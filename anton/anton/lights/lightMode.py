class LightMode:
    MODEIDS = set()
    def __init__(self, modeId : int, uses_color : bool = False):
        if modeId in LightMode.MODEIDS:
            raise Exception("Duplicate Mode ID:",modeId)
        else:
            LightMode.MODEIDS.add(modeId)
        self.modeId = modeId
        self.color_dep = uses_color
        
    def uses_color(self):
        return self.color_dep
    
    def get_mode_byte(self) -> bytes:
        return str(self.modeId).encode('utf-8')
    
    def start(self,**kwargs) -> bytes:
        raise NotImplementedError
    
    def stop(self):
        raise NotImplementedError
