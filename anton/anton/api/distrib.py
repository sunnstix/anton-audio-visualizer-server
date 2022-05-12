import anton
from flask import make_response, jsonify, request
from xmlrpc.client import ServerProxy
from anton.lights.config import RPC_PORT

LIGHTAPP = "http://localhost:"+str(RPC_PORT)+"/"

@anton.app.route('/api/')
def api():
    return jsonify({'about':'REST API for managing Anton Audio Lights','url':request.path})

# Error Handlers
# =======================================================

@anton.app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'message': 'Bad Request', 'status_code': 400}), 400)

@anton.app.errorhandler(403)
def forbidden(error):
    return make_response(jsonify({'message': 'Forbidden', 'status_code': 403}), 403)

@anton.app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': 'Not Found', 'status_code': 404}), 404)

# Light Mode Requests
# =======================================================
@anton.app.route('/api/modes/', methods=['GET'])
def get_light_modes():
    with ServerProxy(LIGHTAPP, allow_none=True) as proxy:
        return jsonify(
            {
                'modes': proxy.list_modes(), 
                'current_mode': proxy.get_mode(),
                'current_config': proxy.get_config(),
                'url': request.path
            })

@anton.app.route('/api/modes/', methods=['POST'])
def set_light_mode():
    with ServerProxy(LIGHTAPP, allow_none=True) as proxy:
        proxy.set_mode(request.json['mode'])
    with ServerProxy(LIGHTAPP, allow_none=True) as proxy:
        return jsonify({'mode':proxy.get_current_mode(),'url':request.path})

@anton.app.route('/api/modes/<string:mode>/', methods=['GET','POST']) #debug route
def set_lights(mode):
    with ServerProxy(LIGHTAPP, allow_none=True) as proxy:
        proxy.set_mode(mode, **request.args)
        return jsonify({'mode':mode,'url':request.path})
