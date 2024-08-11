import json
import time

import requests

host = "localhost"
port = 8080

start_time = time.time()

headers = {"content-type": "application/json"}

for i in range(10000):
    if i % 100 == 0:
        print("Checkpoint:", i)

    body = {"fields": {"int": i}, "time": i}
    response = requests.put(
        f"http://{host}:{port}/metrics/dummy.int/",
        headers=headers,
        data=json.dumps(body),
    )
    if response.status_code >= 300:
        print("Error: ", json.loads(response.content))
        break

end_time = time.time()

print("Elapsed:", end_time - start_time)
