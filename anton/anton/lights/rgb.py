class RgbColor:
    def __init__(self, *args):
        if len(args) == 1:
            self.r, self.g, self.b = tuple(int(args[0].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        elif len(args) == 3:
            self.r, self.g, self.b = args
        elif len(args) == 0:
            self.r, self.g, self.b = 0,0,0
        
        if self.r is None or self.g is None or self.g is None:
            raise ValueError
        
    def to_hex(self):
        return '#%02x%02x%02x' % (self.r, self.g, self.b)
    
    def to_bytes(self):
        return self.r.to_bytes(1,'big') + self.g.to_bytes(1,'big') + self.b.to_bytes(1,'big')