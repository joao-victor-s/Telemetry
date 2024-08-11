import asyncio
import json
import logging

import zmq
import zmq.asyncio
from aioredis import create_redis_pool

import shared.config as config
from shared.store.redis import RedisMetricStore

logging.basicConfig(level=config.event.LOGLEVEL)


def validate_metric(metric):
    if not isinstance(metric, dict):
        raise ValueError("metric must be dict")
    if not isinstance(metric.get("namespace", None), str):
        raise ValueError("namespace attribute must be string")
    if not isinstance(metric.get("time", None), int):
        raise ValueError("time attribute must be integer")
    if not isinstance(metric.get("fields", None), dict):
        raise ValueError("fields attribute must be dict")


# TODO: multiprocesing if needed
async def main():
    zmq_ctx = zmq.asyncio.Context()
    zmq_consumer = zmq_ctx.socket(zmq.ROUTER)  # pylint: disable=no-member
    zmq_consumer.bind(f"tcp://*:{config.event.PERSISTER_PORT}")

    redis = await create_redis_pool(**config.redis.CONNECTION_OPTIONS)
    metric_store = RedisMetricStore(redis)

    logging.info("Persister receiving packets from ZeroMQ")

    while True:
        _ = await zmq_consumer.recv()  # used in ROUTER socket, zmq source
        serialized_metric = await zmq_consumer.recv()
        try:
            metric = json.loads(serialized_metric)
            validate_metric(metric)
        except json.JSONDecodeError:
            logging.warning("Could not deserialize metric as JSON. Discarding.")
            logging.warning("Received: %s", serialized_metric)
            continue
        except ValueError as err:
            logging.warning(
                "Wrong JSON structure for metric. %s. Discarding.", repr(err)
            )
            continue

        try:
            await metric_store.update_metric(
                metric["namespace"], metric["time"], metric["fields"]
            )
        except Exception as err:  # pylint: disable=broad-except
            logging.error("Could not update metric. %s", repr(err))


if __name__ == "__main__":
    asyncio.run(main())
