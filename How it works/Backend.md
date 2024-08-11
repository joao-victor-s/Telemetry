Our metrics backend is responsible for ingesting, storing and serving metrics.

# Metrics
A metric is sequence of arbitrary JSON values that's indexed by time.

**Namespace:** A metric namespace is its unique identifier. Namespaces can be nested. Nested namespaces are indicated via a `.`. For example, `yolo.coneboxes` and `yolo.inference_time` are both namespaces that identify metrics belonging to `yolo`.

**Metric:**  A metric is essentialy a timeseries. All metrics are identified by their namespaces. All metric datapoints are indexed by their time in [Unix Milliseconds](https://en.wikipedia.org/wiki/Unix_time).

Let's suppose we want to store an integer timeseries. We could name this metric `testint` and suppose one of its datapoints were

```json
{
  "time": 1577836800000,
  "value": 1234
}
```

This means that the value `1234` was recorded at January 1st, 2020 (`1577836800000` milliseconds after the Unix Epoch).

# Services
The backend is divided into four main services:
- **Hook** (`backend/eventhook/`): receives metrics from the car and enqueues them into a ZeroMQ queue. This queue exists so that a momentaneous burst in requests does not overload the persister or redis.
- **Persister** (`backend/persister/`): consumes from Hook's queue, performs some validation and  then persists metrics onto redis.
- **Redis** (`backend/shared/`): [an in memory key-value store](https://redis.io) that acts as our primary database.
- **Metrics service** (`backend/metrics/`): provides an interface for accessing metrics via HTTP or Websockets. This interface is used by Grafana.

# Storage data model
The backend keeps track of information inside redis as follows:
- `all-metrics`: an unordered set that's used to keep track of all existing namespaces. Whenever a new metric is inserted, its namespace is added to `all-metrics`.
- `metric:<namespace>:index`: each metric is assigned its own sorted set to serve as an index. Whenever a new datapoint is inserted, it gets added to this set, with its time as the score. This assures all metrics are sorted and can be inserted/retreived in O(logn) time.
- `metric:<namespace>:value`: each metric datapoint is added to a hashtable, with its time as key. This way, we can add/remove datapoints in constant time.

To learn more specific details about the implementation of the datastore, check out its [implementation](https://gitlab.com/unicamperacing/Ia/driverless-2020/viz/-/blob/master/backend/shared/store/redis.py).

# Events
The metrics backend application uses a [redis pubsub](https://redis.io/topics/pubsub) for communication between services. Here are all the events that are produced/consumed by the application:
- `new-metric`: produced whenever a new metric is inserted. Its payload format is `[namespace, time, json_serialized_value]`.
- `value-update`: produced whenever a metric has a new datapoint inserted. Its payload format is `[namespace, time, json_serialized_value]`.

Pub/Sub events are used mainly to communicate to the Websocket API that it should inform subscribers of the existence of a new metric or datapoint.

# HTTP interface

The backend's metrics service exposes some HTTP endpoints that allow for querying and modification of metrics. This is used by the Grafana datasource plugin to retreive some of the information it needs.

## Getting the most recent value of a metric

`GET /metrics/<metric_namespace>/snapshot`

Response body:

```json
{
    "namespace": "<metric_namespace>",
    "snapshot": {
        "time": 123456,
        "fields": {
            ...
        }
    }
}
```

## Get all datapoints in a specific time window

`GET /metrics/<metric_namespace>/history/time`

Query parameters:

- `start`: time window start
- `length`: time window length

Response body:

```json
{
    "namespace": "<metric_namespace>",
    "history": [
        {
            "time": 1234,
            "fields": {
                ...
            }
        },
        {
            "time": 1235,
            "fields": {
                ...
            }
        },
        ...
    ]
}
```

## Updating a metric value

`PUT /metrics/<metric_namespace>`

Request body:

```json
{
    "time": "<time>",
    "fields": {
        ...
    }
}
```

# Websocket interface

The backend's metrics service exposes a Websocket API that's useful for receiving streaming updates without polling. This is used by the Grafana datasource plugin to retreive some of the information it needs.

To establish a connection, just connect a websocket to the route `/ws/<subscription_namespace>`. `subscription_namespace` is a unique identifier of your update feed. Clients that connect using the same subscription namespace are treated by the backend as the same client.

## Commands

`subscribe`: subscribes to updates to all `metric_namespace`
```json
{
    "type": "subscribe",

    "namespaces": [
        "<metric_namespace>"
    ]
}
```

`unsubscribe`: unsubscribes from updates to all `metric_namespace`
```json
{
    "type": "unsubscribe",

    "namespaces": [
        "<metric_namespace>"
    ]
}
```

`snapshot`: retreives the latest value of a all `metric_namespace`. If none is provided, retreives the latest value of all stored metrics
```json
{
    "type": "snapshot",

    "namespaces": [ // OPTIONAL
        "<metric_namespace>",
        ...
    ]
}
```
After issuing a `snapshot`, the client will receive the following payload
```json
{
    "type": "snapshot",

    "metrics": {
        "<metric_namespace>": {
            "time": "<time>",
            "fields": {
                ...
            }
        }
    }
}
```

`update`: adds or updates a `metric_namespace` datapoint
```json
{
    "type": "update",

    "namespace": "<metric_namespace>",
    "time": "<time>",
    "fields": {
        ...
    }
}
```

## Received payloads

`new-metric`: indicates a new metric (`metric_namespace`) is now available for querying
```json
{
    "type": "new-metric",

    "namespace": "<metric_namespace>",
    "snapshot": {
        "time": 1234,
        "fields": {
            ...
        }
    }
}
```

`update`: indicates `metric_namespace` had an update in one of its datapoints
```json
{
    "type": "update",

    "namespace": "<metric_namespace>",
    "snapshot": {
        "time": 1234,
        "fields": {
            ...
        }
    }
}
```

`error`: indicates an error while processing a request
```json
{
    "type": "error",

    "code": "<http_error_code>",
    "message": "<error_message>"
}
```
