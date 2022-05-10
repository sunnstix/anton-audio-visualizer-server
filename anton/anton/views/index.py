import anton
import flask
from xmlrpc.client import ServerProxy
from anton.lights.config import RPC_PORT

# Main Index Page
# ====================================================
@anton.app.route('/')
def show_index():
    with ServerProxy("http://localhost:"+str(RPC_PORT)+"/", allow_none=True) as proxy:
        context = {
            'light_modes': proxy.list_modes(),
        }
        print(context)
    return flask.render_template("index.html", **context)