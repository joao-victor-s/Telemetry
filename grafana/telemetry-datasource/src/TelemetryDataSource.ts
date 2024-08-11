import defaults from "lodash/defaults";

import { Observable, Subscriber, merge } from "rxjs";

import { getBackendSrv } from "@grafana/runtime";

import {
  CircularDataFrame,
  LoadingState,
  DataQueryRequest,
  DataQueryResponse,
  DataSourceApi,
  DataSourceInstanceSettings,
  FieldType,
  TimeRange,
} from "@grafana/data";

import { extractObjectValueFromQuery } from "fieldsquery";
import {
  TelemetryQuery,
  TelemetryDataSourceOptions,
  defaultMetricQuery,
  defaultViewQuery,
  TelemetryViewParameters,
} from "./types";

interface HistoryItem {
  time: number;
  fields: unknown;
}

interface HistoryResponse {
  namespace: string;
  history: HistoryItem[];
}

interface ViewResponse {
  meta: {
    reference_time: number;
  };
  values: unknown;
}

interface Snapshot {
  namespace: string;
  snapshot: HistoryItem;
}

interface SnapshotAllResponse {
  metrics: {
    [namespace: string]: HistoryItem;
  };
}

interface ViewDescriptorResponse {
  namespace: string;
  display_name: string;
  description: string;
}

interface ViewUpdate {
  namespace: string;
  meta: {
    reference_time: number;
  };
  values: unknown;
}

interface UpdateSubscriber {
  subscriber: Subscriber<unknown>;
  frame: CircularDataFrame;
  query: TelemetryQuery;
}

interface NewMetricListener {
  (metric: string): void;
}

interface ReadyListener {
  (): void;
}

export default class TelemetryDataSource extends DataSourceApi<
  TelemetryQuery,
  TelemetryDataSourceOptions
> {
  url: string;
  subscriptionId: string;

  private _newMetricListeners = new Set<NewMetricListener>();
  private _readyListeners = new Set<ReadyListener>();

  private _availableMetrics = new Set<string>();
  private _availableViews = new Set<string>();

  private _subscribedToMetrics = new Set<string>();
  private _subscribedToViews = new Set<string>();

  private _websocket: WebSocket;
  private _ready = false;
  private _pendingCommands: string[] = [];

  private _updateSubscribers: {
    [namespace: string]: UpdateSubscriber[];
  } = {};

  private _handlers: {
    [event: string]: (payload: unknown) => void | undefined;
  };

  constructor(
    instanceSettings: DataSourceInstanceSettings<TelemetryDataSourceOptions>
  ) {
    super(instanceSettings);

    this.url = instanceSettings.jsonData.url;
    this.subscriptionId = instanceSettings.jsonData.subscriptionId;

    this._websocket = new WebSocket(`ws://${this.url}/ws/${this.subscriptionId}`);
    this._websocket.addEventListener("message", this._listen.bind(this));
    this._websocket.addEventListener("open", this._open.bind(this));

    this._handlers = {
      "metric-update": this._listenMetricUpdate.bind(this),
      "new-metric": this._listenNewMetric.bind(this),
      "view-update": this._listenViewUpdate.bind(this),
    };
  }

  /** Binds a listener that's called whenever a new metric has been added do the datasource */
  addNewMetricListener(listener: NewMetricListener): NewMetricListener {
    this._newMetricListeners.add(listener);
    return listener;
  }

  /** Removes a bound new metric listener */
  removeNewMetricListener(listener: NewMetricListener): void {
    this._newMetricListeners.delete(listener);
  }

  /** Binds a listener that's called whenever the datasource gets ready */
  addReadyListener(listener: ReadyListener): ReadyListener {
    this._readyListeners.add(listener);
    return listener;
  }

  /** Removes a bound ready listener */
  removeReadyListener(listener: ReadyListener): void {
    this._readyListeners.delete(listener);
  }

  /** Whether the datasource is ready and fully loaded */
  get ready() {
    return this._ready;
  }

  /** Closes the socket connection */
  close(): void {
    this._websocket.close();
  }

  /** Either queues or sends a command to the socket based on its readiness */
  private _sendToSocket(command: string): void {
    if (this._ready) {
      this._websocket.send(command);
    } else {
      this._pendingCommands.push(command);
    }
  }

  /** Called whenever the socket is opened to kickstart the connection */
  private _open(): void {
    const p1 = this._requestAvailableMetrics().then((metrics: Snapshot[]) => {
      for (const metric of metrics) {
        this._availableMetrics.add(metric.namespace);
      }
    });

    const p2 = this._requestAvailableViews().then((views: string[]) => {
      for (const view of views) {
        this._availableViews.add(view);
      }
    });

    Promise.all([p1, p2]).then(() => {
      for (const command of this._pendingCommands) {
        this._websocket.send(command);
      }

      this._ready = true;

      for (const listener of this._readyListeners) {
        listener();
      }
    });
  }

  /** Listens to updates from a metric */
  private _listenMetricUpdate(payload: unknown) {
    const snapshot = payload as Snapshot;
    const subscribers = this._updateSubscribers[snapshot.namespace] || [];

    for (const subscriber of subscribers) {
      this._addItemToSubscriber(subscriber, snapshot.snapshot);
    }
  }

  /** Listens to updates from a view */
  private _listenViewUpdate(payload: unknown) {
    const update = payload as ViewUpdate;
    const subscribers = this._updateSubscribers[update.namespace] || [];

    const item: HistoryItem = {
      time: update.meta.reference_time,
      fields: update.values,
    };

    for (const subscriber of subscribers) {
      this._addItemToSubscriber(subscriber, item);
    }
  }

  /** Triggered whenever there's a new metric */
  private _listenNewMetric(payload: unknown) {
    const snapshot = payload as Snapshot;
    this._availableMetrics.add(snapshot.namespace);

    for (const listener of this._newMetricListeners) {
      listener(snapshot.namespace);
    }
  }

  /** Listen to any remote updates */
  private _listen(event: any): void {
    const payload = JSON.parse(event.data);

    const handler = this._handlers[payload.type];
    if (typeof handler !== "undefined") {
      handler(payload);
    }
  }

  /** Performs a healthcheck over the datasource */
  async testDatasource(): Promise<any> {
    const result = await getBackendSrv().get(`http://${this.url}/healthcheck`);

    if (!result.healthy) {
      return {
        status: "error",
        message: "Healthcheck failed.",
      };
    }

    return {
      status: "success",
      message: "Success",
    };
  }

  /** Subscribes to a metric update if it isn't already subscribed. */
  private _subscribeToMetricUpdate(metricNamespace: string): void {
    if (this._subscribedToMetrics.has(metricNamespace)) {
      return;
    }

    const command = {
      type: "metric_subscribe",
      namespaces: [metricNamespace],
    };
    this._sendToSocket(JSON.stringify(command));
  }

  /** Unsubscribes from a metric update. */
  private _unsubscribeFromMetricUpdate(metricNamespace: string): void {
    this._subscribedToMetrics.delete(metricNamespace);

    const command = {
      type: "metric_unsubscribe",
      namespaces: [metricNamespace],
    };
    this._sendToSocket(JSON.stringify(command));
  }

  /** Subscribes to a view update if it isn't already subscribed. */
  private _subscribeToViewUpdate(viewNamespace: string): void {
    if (this._subscribedToViews.has(viewNamespace)) {
      return;
    }

    const command = {
      type: "view_subscribe",
      // TODO: empty view parameters for now
      views: {
        [viewNamespace]: {},
      },
    };
    this._sendToSocket(JSON.stringify(command));
  }

  /** Unsubscribes from a view update. */
  private _unsubscribeFromViewUpdate(viewNamespace: string): void {
    this._subscribedToViews.delete(viewNamespace);

    const command = {
      type: "view_unsubscribe",
      namespaces: [viewNamespace],
    };
    this._sendToSocket(JSON.stringify(command));
  }

  /** Requests all available metrics to the backend REST API */
  private async _requestAvailableMetrics(): Promise<Snapshot[]> {
    const response: SnapshotAllResponse = await getBackendSrv().get(
      `http://${this.url}/metrics`
    );
    return Object.entries(response.metrics).map(([metricNamespace, snapshot]) => {
      return {
        namespace: metricNamespace,
        snapshot: snapshot,
      };
    });
  }

  /** Requests all available views to the backend REST API */
  private async _requestAvailableViews(): Promise<string[]> {
    const response: ViewDescriptorResponse[] = await getBackendSrv().get(
      `http://${this.url}/view`
    );
    return response.map((descriptorResponse) => {
      return descriptorResponse.namespace;
    });
  }

  private async _requestHistory(
    query: TelemetryQuery,
    range: TimeRange
  ): Promise<HistoryResponse> {
    if (query.type === "View") {
      throw new Error("Cannot request history for view.");
    }

    const start = range.from.valueOf();
    const end = range.to.valueOf();

    const response = await getBackendSrv().get(
      `http://${this.url}/metrics/${query.namespace}/history/time`,
      {
        start: start,
        length: end - start,
      }
    );

    return response;
  }

  private async _requestView(
    viewNamespace: string,
    viewParameters: TelemetryViewParameters
  ): Promise<ViewResponse> {
    const response = await getBackendSrv().get(
      `http://${this.url}/view/${viewNamespace}`,
      viewParameters
    );

    return response;
  }

  private _addItemToSubscriber(subscriber: UpdateSubscriber, item: HistoryItem) {
    const value =
      subscriber.query.type === "View"
        ? item.fields
        : extractObjectValueFromQuery(
            item.fields,
            subscriber.query.fieldsQuery,
            true
          );

    subscriber.frame.add({
      time: item.time,
      value: value,
    });

    subscriber.subscriber.next({
      data: [subscriber.frame],
      key: subscriber.query.refId,
      state: LoadingState.Streaming,
    });
  }

  /** The names of all the available metrics if ready. Returns empty set otherwise */
  get availableMetrics(): Set<string> {
    return this._availableMetrics;
  }

  /** The names of all the available views if ready. Returns empty set otherwise */
  get availableViews(): Set<string> {
    return this._availableViews;
  }

  private _queryTargetMetric(
    options: DataQueryRequest<TelemetryQuery>,
    target: TelemetryQuery
  ): Observable<DataQueryResponse> {
    if (target.type !== "Metric") {
      throw new Error("Called wrong query handler method");
    }

    const query = defaults(target, defaultMetricQuery);

    return new Observable((subscriber) => {
      const frame = new CircularDataFrame({
        append: "tail",
        capacity: 1000,
      });
      frame.refId = query.refId;
      frame.addField({ name: "time", type: FieldType.time });
      // TODO: value fieldtype may not be number
      frame.addField({ name: "value", type: FieldType.number });

      this._requestHistory(query, options.range).then((history) => {
        const metricSubscriber = {
          subscriber,
          query,
          frame,
        };

        if (!this._updateSubscribers[target.namespace]) {
          this._updateSubscribers[target.namespace] = [];
        }
        this._updateSubscribers[target.namespace].push(metricSubscriber);

        // backfill
        for (const item of history.history) {
          this._addItemToSubscriber(metricSubscriber, item);
        }

        this._subscribeToMetricUpdate(target.namespace);
      });

      return (() => {
        let that = this;
        return () => {
          that._unsubscribeFromMetricUpdate(target.namespace);
          if (!that._updateSubscribers[target.namespace]) {
            return;
          }

          const index = that._updateSubscribers[target.namespace].findIndex(
            (metricSubscriber) => metricSubscriber.query.refId === query.refId
          );
          that._updateSubscribers[target.namespace].splice(index, 1);
        };
      })();
    });
  }

  private _queryTargetView(
    options: DataQueryRequest<TelemetryQuery>,
    target: TelemetryQuery
  ): Observable<DataQueryResponse> {
    if (target.type !== "View") {
      throw new Error("Called wrong query handler method");
    }

    const query = defaults(target, defaultViewQuery);

    return new Observable((subscriber) => {
      const frame = new CircularDataFrame({
        append: "tail",
        capacity: 1,
      });
      frame.refId = query.refId;
      frame.addField({ name: "time", type: FieldType.time });
      frame.addField({ name: "value", type: FieldType.other });

      this._requestView(target.namespace, target.parameters).then(
        (response: ViewResponse) => {
          const viewSubscriber = {
            subscriber,
            query,
            frame,
          };

          if (!this._updateSubscribers[target.namespace]) {
            this._updateSubscribers[target.namespace] = [];
          }
          this._updateSubscribers[target.namespace].push(viewSubscriber);

          const item: HistoryItem = {
            time: response.meta.reference_time,
            fields: response.values,
          };
          this._addItemToSubscriber(viewSubscriber, item);

          this._subscribeToViewUpdate(target.namespace);
        }
      );
      return (() => {
        let that = this;
        return () => {
          that._unsubscribeFromViewUpdate(target.namespace);
          if (!that._updateSubscribers[target.namespace]) {
            return;
          }

          const index = that._updateSubscribers[target.namespace].findIndex(
            (metricSubscriber) => metricSubscriber.query.refId === query.refId
          );
          that._updateSubscribers[target.namespace].splice(index, 1);
        };
      })();
    });
  }

  query(options: DataQueryRequest<TelemetryQuery>): Observable<DataQueryResponse> {
    const targets = options.targets.filter((t) => typeof t.type !== "undefined");

    const observables = targets.map(
      (target): Observable<DataQueryResponse> => {
        console.log(target);
        if (target.type === "Metric") {
          return this._queryTargetMetric(options, target);
        } else {
          return this._queryTargetView(options, target);
        }
      }
    );

    return merge(...observables);
  }
}
