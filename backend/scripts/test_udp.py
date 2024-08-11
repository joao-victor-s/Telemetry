import json
import socket

destination = ("localhost", 9512)

namespace = "test.test"
time = 123456789
fields = {"cones": 2469}

client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

metric = {"time": time, "namespace": namespace, "fields": fields}

client.sendto(json.dumps(metric).encode(), destination)
