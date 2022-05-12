from enum import IntEnum
import abc
from typing import Dict

class ModeCode(IntEnum):
    OFF = 0
    RAINBOW = 1
    SOLID = 2
    STROBE = 3
    RECIEVER = 4
    
LightOptions = Dict[str,str]
LightConfig = Dict[str,object]

class LightMode:
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, mc : ModeCode, config :LightConfig = dict()):
        self.modeByte = int(mc).to_bytes(1,'big')
        self.config = config
        self.options : LightOptions = dict()
        for (key,value) in config.items():
            self.options[key] = type(value).__name__
        
    def get_options(self) -> LightOptions:
        return self.options
    
    def get_config(self):
        return self.config
    
    def encode(self) -> bytes:
        return self.modeByte + self.encode_config(self.config)
    
    def start(self, options) -> bytes:
        self.config = options
        self.initialize()
    
    @abc.abstractmethod
    def encode_config(self, config) -> bytes:
        raise NotImplementedError
    
    @abc.abstractmethod
    def initialize(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def stop(self):
        raise NotImplementedError
