from asyncio import AbstractEventLoop

from aioredis import create_redis_pool
from metrics.websocket.subscriptions_manager import SubscriptionsManager
from sanic import Blueprint, Sanic
from shared.config import redis as redis_config
from shared.store.redis import RedisMetricStore

blueprint = Blueprint("setup")

_conn_pool = None


@blueprint.listener("before_server_start")
async def setup(app: Sanic, loop: AbstractEventLoop) -> None:
    _conn_pool = await create_redis_pool(**redis_config.CONNECTION_OPTIONS, loop=loop)
    app.ctx.metric_store = RedisMetricStore(_conn_pool)
    app.ctx.subscriptions_manager = SubscriptionsManager(
        _conn_pool, app.ctx.metric_store
    )
    app.add_task(app.ctx.subscriptions_manager.run(loop))


@blueprint.listener("after_server_stop")
async def teardown(app: Sanic, loop: AbstractEventLoop) -> None:
    if _conn_pool:
        _conn_pool.close()
