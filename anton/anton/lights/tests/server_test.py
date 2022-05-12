from xmlrpc.client import ServerProxy
from anton.lights.config import RPC_PORT
from anton.lights.rgb import RGBColor

if __name__ == "__main__":
    with ServerProxy("http://localhost:"+str(RPC_PORT)+"/", allow_none=True) as proxy:
        print(proxy.list_modes())
        print(proxy.get_mode())
        print(proxy.get_config())
        proxy.set_mode('SolidColor')
        # print(proxy.get_mode())
        # print(proxy.get_config())
        # proxy.set_config({'color':RGBColor('#00FFFF')})
        # print(proxy.get_mode())
        # print(proxy.get_config())