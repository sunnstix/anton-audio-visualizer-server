from anton.lights.lightMode import LightMode, LightConfig
from anton.lights.registryServer import RegistryServer
import anton.lights.config as config
from socket import socket
from typing import Dict

import traceback
def catchRPCError(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            raise e
    return wrapper

class LightServer:
    LIGHTMODES : Dict[str,LightMode] = dict()
    MODE = 'Off'
    
    class LightClient(RegistryServer.Client):
        def __init__(self, conn: socket, addr) -> None:
            super().__init__(conn, addr)
            self.conn.sendall(LightServer.__current_mode__().encode())
            
    REGISTRY = RegistryServer("",config.TCP_PORT, config.UDP_PORT, LightClient)
    
    @classmethod
    @catchRPCError
    def list_modes(self):
        return {modekey:mode.get_options() for modekey, mode in self.LIGHTMODES.items()}
    
    
    @classmethod
    @catchRPCError
    def get_mode(self):
        return self.MODE
    
    @classmethod
    @catchRPCError
    def set_mode(self, mode : str):
        self.__current_mode__().stop()
        self.MODE = mode
        self.__current_mode__().start()
        self.REGISTRY.broadcast(self.__current_mode__().encode())
    
    @classmethod
    @catchRPCError
    def get_config(self):
        return self.__current_mode__().get_config()
    
    @classmethod
    @catchRPCError    
    def set_config(self, config: LightConfig):
        self.__current_mode__().set_config(config)
        self.REGISTRY.broadcast(self.__current_mode__().encode())
        
    @classmethod
    def __current_mode__(self) -> LightMode:
        return self.LIGHTMODES[self.MODE]
            
    
def register_mode(m: LightMode):
    modeName = m.__name__
    if modeName in LightServer.LIGHTMODES:
        raise Exception("Duplicate Mode:",modeName)
    LightServer.LIGHTMODES[modeName] = m()
    return m
