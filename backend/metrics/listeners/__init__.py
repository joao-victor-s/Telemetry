from metrics.listeners.error import blueprint as error
from metrics.listeners.setup import blueprint as setup
from sanic import Blueprint

blueprint = Blueprint.group(error, setup)
