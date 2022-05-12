from anton.lights.config import RPC_PORT
from xmlrpc.server import SimpleXMLRPCServer
import sys

from anton.lights.lightServer import LightServer

import anton.lights.modes.offMode
import anton.lights.modes.rainbowMode
import anton.lights.modes.solidMode
import anton.lights.modes.strobeMode

def main():
    # Create server
    with SimpleXMLRPCServer(('localhost', RPC_PORT), allow_none=True) as server:
        server.register_introspection_functions()

        # Register LightServer functions
        server.register_function(LightServer.list_modes,'list_modes')
        server.register_function(LightServer.get_mode,'get_mode')
        server.register_function(LightServer.set_mode,'set_mode')
        server.register_function(LightServer.get_config,'get_config')
        server.register_function(LightServer.set_config,'set_config')
    
        # Run the server's main loop
        print('Serving LightApp on localhost port', RPC_PORT)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)

if __name__ == "__main__":
    main()
