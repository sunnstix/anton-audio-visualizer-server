from anton.lights.lightMode import LightMode
from anton.lights.registryServer import RegistryServer
import anton.lights.config as config
from socket import socket
from typing import Dict

from anton.lights.config import RPC_PORT
from xmlrpc.server import SimpleXMLRPCServer
import sys

class LightServer:
    LIGHTMODES : Dict[str,LightMode] = dict()
    MODE = 'Off'
    
    class LightClient(RegistryServer.Client):
        def __init__(self, conn: socket, addr) -> None:
            super().__init__(conn, addr)
            self.conn.sendall(LightServer.__current_mode__().encode())
            
    REGISTRY = RegistryServer("",config.TCP_PORT, config.UDP_PORT, LightClient)

    @classmethod
    def list_modes(self):
        return {modekey:mode.get_options() for modekey, mode in LightServer.LIGHTMODES.items()}

    @classmethod
    def get_current_mode(self):
        return LightServer.MODE

    @classmethod
    def get_config(self):
        return self.__current_mode__().get_config()

    @classmethod
    def set_mode(self, mode : str, options: dict):
        self.__current_mode__().stop()
        LightServer.MODE = mode
        self.__current_mode__().start(options)
        LightServer.REGISTRY.broadcast(self.__current_mode__().encode())
        
    @classmethod
    def __current_mode__(self) -> LightMode:
        return LightServer.LIGHTMODES[LightServer.MODE]
    
def register_mode(m: LightMode):
    modeName = m.__name__
    if modeName in LightServer.LIGHTMODES:
        raise Exception("Duplicate Mode:",modeName)
    LightServer.LIGHTMODES[modeName] = m()
    return m

def init_light_mode(f):
    def wrapper(mode: LightMode, options):
        LightServer.REGISTRY.broadcast(f(mode,options)) # intercept self
    return wrapper

def main():
    #Initialize
    import anton.lights.modes.offMode
    import anton.lights.modes.rainbowMode
    import anton.lights.modes.solidMode
    import anton.lights.modes.strobeMode
    
    # Create server
    with SimpleXMLRPCServer(('localhost', RPC_PORT), allow_none=True) as server:
        server.register_introspection_functions()

        # Register pow() function; this will use the value of
        # pow.__name__ as the name, which is just 'pow'.
        server.register_function(LightServer.get_config,'get_config')
        server.register_function(LightServer.get_current_mode,'get_current_mode')
        server.register_function(LightServer.list_modes,'list_modes')
        server.register_function(LightServer.set_mode,'set_mode')
    
        # Run the server's main loop
        print('Serving XML-RPC on localhost port', RPC_PORT)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)

if __name__ == "__main__":
    main()
