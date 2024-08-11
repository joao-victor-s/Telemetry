import json
import random
import socket
import time

UDP_IP = "localhost"
UDP_PORT = 9512

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    steer = (random.randint(0, 90) * 2) - 90
    now = int(time.time_ns() // 1000000)
    metric_steer = {
        "namespace": "driverless.path_planning.steer_target",
        "time": now,
        "fields": {"value": steer},
    }
    server.sendto(json.dumps(metric_steer).encode("utf-8"), (UDP_IP, UDP_PORT))

    speed = (random.randint(0, 100) * 2) - 100
    metric_speed = {
        "namespace": "driverless.path_planning.speed_target",
        "time": now,
        "fields": {"value": speed},
    }
    server.sendto(json.dumps(metric_speed).encode("utf-8"), (UDP_IP, UDP_PORT))

    time_exec = {
        "namespace": "driverless.path_planning.time_exec",
        "time": now,
        "fields": {"value": random.randint(0, 10)},
    }
    server.sendto(json.dumps(time_exec).encode("utf-8"), (UDP_IP, UDP_PORT))

    print(metric_speed, metric_steer, time_exec)
    time.sleep(2)
