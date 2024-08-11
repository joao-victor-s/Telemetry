import { DataSourcePlugin } from "@grafana/data";
import TelemetryDataSource from "./TelemetryDataSource";
import ConfigEditor from "./ConfigEditor";
import QueryEditor from "./QueryEditor";
// import VariableQueryEditor from "./views/VariableQueryEditor";
import { TelemetryQuery, TelemetryDataSourceOptions } from "./types";

export const plugin = new DataSourcePlugin<
  TelemetryDataSource,
  TelemetryQuery,
  TelemetryDataSourceOptions
>(TelemetryDataSource)
  .setConfigEditor(ConfigEditor)
  .setQueryEditor(QueryEditor);
// .setAnnotationQueryCtrl(AnnotationCtrl);
