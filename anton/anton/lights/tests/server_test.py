from xmlrpc.client import ServerProxy
from anton.lights.config import RPC_PORT

if __name__ == "__main__":
    with ServerProxy("http://localhost:"+str(RPC_PORT)+"/", allow_none=True) as proxy:
        print(proxy.list_modes())
        print(proxy.get_current_mode())
        print(proxy.get_config())
        proxy.set_mode('SolidColor',{'color':'#FF00FF'})
        print(proxy.get_current_mode())
        print(proxy.get_config())