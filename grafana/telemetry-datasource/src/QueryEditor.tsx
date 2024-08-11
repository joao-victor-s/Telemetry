import React from "react";
import { InlineFormLabel, Input, Select, Spinner } from "@grafana/ui";
import { QueryEditorProps } from "@grafana/data";
import { css } from "emotion";

import TelemetryDataSource from "./TelemetryDataSource";
import { TelemetryDataSourceOptions, TelemetryQuery } from "./types";

type Props = QueryEditorProps<
  TelemetryDataSource,
  TelemetryQuery,
  TelemetryDataSourceOptions
>;

const spinnerCss = css`
  margin: 0px 3px;
  padding: 0px 3px;
`;

// TODO: handle errors
const QueryEditor: React.FC<Props> = (props: Props) => {
  const [availableMetrics, setAvailableMetrics] = React.useState<string[]>(
    Array.from(props.datasource.availableMetrics) || []
  );
  const [availableViews, setAvailableViews] = React.useState<string[]>(
    Array.from(props.datasource.availableViews) || []
  );

  React.useEffect(() => {
    const listener = () => {
      setAvailableMetrics(Array.from(props.datasource.availableMetrics));
      setAvailableViews(Array.from(props.datasource.availableViews));
    };

    props.datasource.addNewMetricListener(listener);
    props.datasource.addReadyListener(listener);

    return () => {
      props.datasource.removeNewMetricListener(listener);
      props.datasource.removeReadyListener(listener);
    };
  }, []);

  const selectOptions =
    props.query.type === "Metric" ? availableMetrics : availableViews;

  return (
    <>
      <div className="gf-form-inline">
        <InlineFormLabel
          className="query-keyword"
          tooltip={"The desired query mode"}
        >
          Mode
        </InlineFormLabel>
        <Select
          width={50}
          className={"gf-form--grow"}
          value={props.query.type || "Metric"}
          onChange={(opt) => {
            if (opt.value === "Metric") {
              props.onChange({
                ...props.query,
                type: "Metric",
                namespace: "",
                fieldsQuery: "",
              });
            } else {
              props.onChange({
                ...props.query,
                type: "View",
                namespace: "",
                // TODO: figure out what to do with query parameters
                parameters: {},
              });
            }
          }}
          disabled={!props.datasource.ready}
          placeholder={props.datasource.ready ? "Query mode" : "Loading..."}
          options={[
            {
              label: "Metric",
              value: "Metric",
            },
            {
              label: "View",
              value: "View",
            },
          ]}
        />
        {!props.datasource.ready && (
          <div>
            <Spinner className={spinnerCss} />
          </div>
        )}
      </div>
      <div className="gf-form-inline">
        <InlineFormLabel
          className="query-keyword"
          tooltip={'The query configuration"'}
        >
          Query
        </InlineFormLabel>
        <Select
          width={50}
          className={"gf-form--grow"}
          value={props.query.namespace}
          onChange={(opt) => {
            props.onChange({ ...props.query, namespace: opt.value! });
          }}
          disabled={!props.datasource.ready}
          placeholder={props.datasource.ready ? `Select...` : "Loading..."}
          options={selectOptions.map((opt) => {
            return {
              label: opt,
              value: opt,
            };
          })}
        />
        {props.query.type === "Metric" && (
          <Input
            width={50}
            className={"gf-form--grow"}
            value={props.query.fieldsQuery}
            onChange={(elem) => {
              if (props.query.type === "Metric") {
                props.onChange({
                  ...props.query,
                  fieldsQuery: elem.currentTarget.value,
                });
              }
            }}
          />
        )}
      </div>
    </>
  );
};

export default QueryEditor;
