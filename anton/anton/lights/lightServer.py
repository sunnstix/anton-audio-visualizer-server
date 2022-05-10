from anton.lights.lightMode import LightMode
from anton.lights.registryServer import RegistryServer
from anton.lights.rgb import RgbColor
import anton.lights.config as config
from socket import socket

class LightServer:
    LIGHTMODES = dict()
    MODE = 'Off'
    CONFIG_BYTES = b''
    COLOR = RgbColor(0,0,0)
    
    class LightClient(RegistryServer.Client):
        def __init__(self, conn: socket, addr) -> None:
            super().__init__(conn, addr)
            mode : LightMode = LightServer.LIGHTMODES[LightServer.MODE]
            self.conn.sendall(mode.get_mode_byte()+LightServer.CONFIG_BYTES)
            
    REGISTRY = RegistryServer("",config.TCP_PORT, config.UDP_PORT, LightClient)

    @classmethod
    def list_modes(self):
        return {modekey:{'color':mode.uses_color()} for modekey, mode in LightServer.LIGHTMODES.items()}

    @classmethod
    def get_current_mode(self):
        return LightServer.MODE

    @classmethod
    def get_current_color(self):
        return LightServer.COLOR.to_hex()

    @classmethod
    def set_mode(self, mode : str, color:str):
        LightServer.LIGHTMODES[LightServer.MODE].stop()
        LightServer.MODE = mode
        LightServer.COLOR = LightServer.COLOR if not color else RgbColor(color)
        LightServer.LIGHTMODES[LightServer.MODE].start(color = color)
    
def register_mode(m: LightMode):
        modeName = m.__name__
        if modeName in LightServer.LIGHTMODES:
            raise Exception("Duplicate Mode:",modeName)
        LightServer.LIGHTMODES[modeName] = m()
        return m

def init_light_mode(f):
    def wrapper(*args,**kwargs):
        LightServer.CONFIG_BYTES = f(*args,**kwargs)
        mode : LightMode = args[0]
        LightServer.REGISTRY.broadcast(mode.get_mode_byte() + LightServer.CONFIG_BYTES) # intercept self
        return
    return wrapper
