import asyncio
import json
import os
import random
import string
import time

from sanic import Sanic
from sanic.request import Request
from sanic.response import json as json_response
from sanic.websocket import WebSocketConnection
from sanic_cors import CORS

from .arguments import parse_args

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates.json"), "r"
) as templates_file:
    templates = json.loads(templates_file.read())


def get_random_template(template: dict):
    if isinstance(template, dict):
        value = dict()
        for k, v in template.items():
            value[k] = get_random_template(v)
    elif isinstance(template, list):
        value = []
        for _ in range(random.randint(0, 20)):
            value.append(get_random_template(template[0]))
    elif isinstance(template, str):
        value = template
        if template == "<random>":
            s = string.ascii_lowercase + string.digits
            value = "".join(random.sample(s, random.randint(0, len(s))))
    elif isinstance(template, int):
        value = random.randint(-template, template)
    elif isinstance(template, float):
        value = random.random() * 2 * template - template

    return value


def create_snapshot(subscription: str):
    fields = {"value": random.randint(-100, 100)}

    if subscription in templates:
        fields = get_random_template(templates[subscription])

    return {"time": time.time_ns(), "fields": fields}


def get_app(update_frequency: int):
    app = Sanic("backend_emulator")
    CORS(app)

    latest_metrics = {namespace: create_snapshot(namespace) for namespace in templates}

    def get_latest(metric_namespace: str):
        if not metric_namespace in latest_metrics:
            latest_metrics[metric_namespace] = create_snapshot(metric_namespace)
        return latest_metrics[metric_namespace]

    @app.get("/metrics")
    def metrics(request: Request):
        return json_response({"metrics": latest_metrics})

    @app.get("/metrics/<metric_namespace>/snapshot")
    def get_snapshot(request: Request, metric_namespace: str):
        return json_response(
            {"namespace": metric_namespace, "snapshot": get_latest(metric_namespace)}
        )

    @app.websocket("/ws/<streaming_namespace>")
    async def ws(
        request: Request, websocket: WebSocketConnection, streaming_namespace: str
    ):
        subscriptions = set()

        async def _controller(websocket: WebSocketConnection, subscriptions: set):
            while True:
                message = await websocket.recv()
                cmd_args = json.loads(message)
                command_type = cmd_args.get("type", None)

                namespaces = cmd_args.get("namespaces", [])

                if command_type == "subscribe":
                    for namespace in namespaces:
                        subscriptions.add(namespace)
                        print("+++", namespace)
                elif command_type == "unsubscribe":
                    for namespace in namespaces:
                        subscriptions.remove(namespace)
                        print("---", namespace)

        async def _receiver(websocket: WebSocketConnection, subscriptions: set):
            while True:
                send_tasks = []
                for subscription in subscriptions:
                    metric = {
                        "namespace": subscription,
                        "snapshot": create_snapshot(subscription),
                    }
                    latest_metrics[subscription] = metric

                    msg = {"type": "update", **metric}
                    send_task = websocket.send(json.dumps(msg))
                    send_tasks.append(send_task)

                await asyncio.gather(*send_tasks)
                await asyncio.sleep(update_frequency)

        controller_task = asyncio.ensure_future(_controller(websocket, subscriptions))
        receiver_task = asyncio.ensure_future(_receiver(websocket, subscriptions))
        tasks = asyncio.gather(controller_task, receiver_task)
        await tasks

    return app


if __name__ == "__main__":
    args = parse_args()
    app = get_app(**args)
    app.run(
        "localhost", 8080,
    )
