import copy

class RGBColor:
    def __init__(self, *args):
        if len(args) == 0:
            self.r, self.g, self.b = 0,0,0
        if len(args) == 1:
            inp = args[0]
            if isinstance(inp,str):
                self.r, self.g, self.b = tuple(int(inp.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            elif isinstance(inp,dict):
                self.r, self.g, self.b = inp['r'],inp['g'],inp['b']
            elif isinstance(inp,RGBColor):
                self.r, self.g, self.b = inp.r, inp.g, inp.b
        elif len(args) == 3:
            self.r, self.g, self.b = args
        
        if self.r is None or self.g is None or self.g is None:
            raise ValueError
        
    def __str__(self) -> str:
        return '#%02x%02x%02x' % (self.r, self.g, self.b)
    
    def __bytes__(self) -> bytes:
        return self.r.to_bytes(1,'big') + self.g.to_bytes(1,'big') + self.b.to_bytes(1,'big')