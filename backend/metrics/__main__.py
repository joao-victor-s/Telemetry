import shared.config as config
from metrics import listeners, routes
from sanic import Sanic
from sanic.log import logger
from sanic_cors import CORS

logger.setLevel(config.log.LOGLEVEL)

app = Sanic(name=config.metrics.APPLICATION_NAME, strict_slashes=False)
CORS(app)  # don't deploy this :p

app.blueprint(listeners.blueprint)
app.blueprint(routes.blueprint)

logger.info("Registered blueprints: %s", [str(bp) for bp in app.blueprints])

if __name__ == "__main__":
    app.run(
        host=config.metrics.APPLICATION_HOST,
        port=config.metrics.APPLICATION_PORT,
        workers=config.metrics.APPLICATION_WORKERS,
    )
