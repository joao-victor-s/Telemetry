import asyncio
import json

import websockets

# FIXME


async def run_ws(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            await websocket.send(input("> "))
            message = await websocket.recv()
            split = message.split(" ", 1)
            print("status:", split[0])
            if len(split) > 1:
                print("body:", json.loads(split[1]))


async def receiver(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            split = message.split(" ", 1)
            print("message type:", split[0])
            if len(split) > 1:
                print("body:", json.loads(split[1]))


subscription = input("Subscription: ")
task = run_ws(f"ws://localhost:8080/streaming/{subscription}")

asyncio.get_event_loop().run_until_complete(task)
