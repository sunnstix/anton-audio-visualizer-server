import anton
from anton.lights.modes import Lights
import flask

# Main Index Page
# ====================================================


@anton.app.route('/')
def show_index():
    context = {
        'light_modes': Lights.MODES.keys(),
        'audio_modes': ['scroll','spectrum','energy']
    }
    return flask.render_template("index.html", **context)