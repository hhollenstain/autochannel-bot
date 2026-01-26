import os
import logging
import coloredlogs
from flask import request
from flask_debugtoolbar import DebugToolbarExtension
from waitress import serve
from autochannel.ui.lib import utils
from autochannel.ui import create_app

LOG = logging.getLogger(__name__)

def main():
    args = utils.parse_arguments()
    logging.basicConfig(level=logging.INFO)
    coloredlogs.install(level=0,
                        fmt="[%(asctime)s][%(levelname)s] [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                        isatty=True)

    app = create_app()

    @app.after_request
    def after_request(response):
        LOG.info(f'{request.remote_addr} {request.method} {request.scheme} {request.full_path} {response.status}')
        return response

    if args.debug:
        l_level = logging.DEBUG
        app.debug = True
        toolbar = DebugToolbarExtension()
        toolbar.init_app(app)
    else:
        l_level = logging.INFO

    logging.getLogger(__package__).setLevel(l_level)
    logging.getLogger('websockets.protocol').setLevel(l_level)
    logging.getLogger('urllib3').setLevel(l_level)
   

    if 'http://' in app.config['OAUTH2_REDIRECT_URI']:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

    if args.debug:
        app.run(threaded=True)
    else:
        serve(app, listen='0.0.0.0:5000')

if __name__ == "__main__":
    main()