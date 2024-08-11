from metrics.routes.healthcheck import blueprint as healthcheck
from metrics.routes.metrics import blueprint as metrics
from metrics.routes.streaming_ws import blueprint as streaming_ws
from metrics.routes.views import blueprint as views
from sanic import Blueprint

blueprint = Blueprint.group(healthcheck, metrics, streaming_ws, views)
