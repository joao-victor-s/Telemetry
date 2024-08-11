import { DataQuery, DataSourceJsonData } from "@grafana/data";

export type TelemetryQueryType = "View" | "Metric";

export type TelemetryViewParameters = {
  [p: string]: string | undefined;
};

export type TelemetryQuery = DataQuery &
  (
    | {
        type: "Metric";
        namespace: string;
        fieldsQuery: string;
      }
    | {
        type: "View";
        namespace: string;
        parameters: TelemetryViewParameters;
      }
  );

export const defaultMetricQuery: Partial<TelemetryQuery> = {
  type: "Metric",
  namespace: "",
  fieldsQuery: "",
};

export const defaultViewQuery: Partial<TelemetryQuery> = {
  type: "View",
  namespace: "",
};

export interface TelemetryDataSourceOptions extends DataSourceJsonData {
  url: string;
  subscriptionId: string;
}
