import React, { ChangeEvent } from "react";
import { LegacyForms } from "@grafana/ui";
import { DataSourcePluginOptionsEditorProps } from "@grafana/data";
import { TelemetryDataSourceOptions } from "./types";

const { FormField } = LegacyForms;

type Props = DataSourcePluginOptionsEditorProps<TelemetryDataSourceOptions>;

const ConfigEditor: React.FC<Props> = (props: Props) => {
  React.useEffect(() => {
    const { onOptionsChange, options } = props;
    const jsonData = {
      url: options.jsonData.url || "localhost:8080",
      subscriptionId: options.jsonData.subscriptionId || "frontend",
    };
    onOptionsChange({ ...options, jsonData });
  }, []);

  function onHostChange(event: ChangeEvent<HTMLInputElement>) {
    const { onOptionsChange, options } = props;
    const jsonData = {
      ...options.jsonData,
      url: event.target.value,
    };
    onOptionsChange({ ...options, jsonData });
  }

  function onSubscriptionIdChange(event: ChangeEvent<HTMLInputElement>) {
    const { onOptionsChange, options } = props;
    const jsonData = {
      ...options.jsonData,
      subscriptionId: event.target.value,
    };
    onOptionsChange({ ...options, jsonData });
  }

  const { options } = props;
  const { jsonData } = options;

  return (
    <div className="gf-form-group">
      <div className="gf-form">
        <FormField
          label="Url"
          labelWidth={6}
          inputWidth={20}
          onChange={onHostChange}
          value={jsonData.url}
          placeholder="A host URL"
        />
        <FormField
          label="Sub ID"
          labelWidth={6}
          inputWidth={20}
          onChange={onSubscriptionIdChange}
          value={jsonData.subscriptionId}
          placeholder="The subscription ID"
        />
      </div>
    </div>
  );
};

export default ConfigEditor;
