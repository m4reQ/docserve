import os

import flask
from models import Registry

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 2137

class App(flask.Flask):
    def __init__(self, registry: Registry, **kwargs) -> None:
        super().__init__(__name__, **kwargs)

        self.registry = registry

def _index():
    return flask.render_template('index.html')

def _search():
    registry: Registry = flask.current_app.registry # type: ignore
    return flask.render_template(
        'search_results.html',
        query_result=registry.query(flask.request.form['search_query'], limit=20))

def run(registry: Registry,
        host: str,
        port: int) -> None:
    _app = App(registry, template_folder=os.path.abspath('./templates'))
    _app.add_url_rule('/', '/', _index)
    _app.add_url_rule('/search', '/search', _search, methods=['POST'])

    _app.run(host, port)
