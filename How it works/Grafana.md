# Overview

[Grafana](https://grafana.com/) is a metrics visualization and analysis tool that's widely used in the industry for application monitoring. It provides a couple of useful features:
- Dashboards, which allow metrics to be visualized as heatmaps, bar graphs, chart graphs, line plots and many other options;
- Alerts which can trigger specific actions such as calling APIs and making popup sounds;
- Storage, backend independency, which is useful for collecting data across multiple datasources and visualizing them in a single platform;
- Role-based access control, so that many users can access the platform at once while keeping sensitive metrics and systems safe;
- Plugins, which allow for customizations such as custom storage backends or visualization panels.

At E-Racing, Grafana is being used as the frontend interface for visualizing our metrics. We have developed some plugins to augment it according to our needs.

# Resources

Before we document our Grafana plugin stack, we list some useful resources that can help to understand about how plugins work in Grafana and how to develop them.

- **BEGINNER** [Build a streaming datasource plugin](https://grafana.com/docs/grafana/latest/developers/plugins/build-a-streaming-data-source-plugin/). This is a good begginer's tutorial.
- **INTERMEDIATE** [Github Datasource plugin](https://github.com/grafana/github-datasource/). This is useful for checking out some actual datasource plugin code.
- **INTERMEDIATE** [Go SDK documentation for backend plugins](https://pkg.go.dev/github.com/grafana/grafana-plugin-sdk-go).
- **ADVANCED** [Plugin signatures](https://grafana.com/docs/grafana/latest/plugins/plugin-signatures/). You'll need to read this before you develop a backend plugin.

# Telemetry Datasource

Telemetry Datasource is a datasource plugin that allows grafana to connect and query our custom metrics backend.

For now, it is very simple and connects directly to our backend through a Websocket in the frontend. In the future, we intend on using a [backend plugin](https://grafana.com/tutorials/build-a-data-source-backend-plugin/) to enable [Grafana Expressions](https://grafana.com/docs/grafana/latest/panels/expressions/).

# Changing configurations
To change any of [Grafana's stock configurations](https://grafana.com/docs/grafana/latest/administration/configuration/), edit the `compose/grafana.env` file by adding `GF_<UPPERCASE-CONFIG-KEY>=<CONFIG-VALUE>`.
