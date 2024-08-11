import { PanelOptionsEditorBuilder, PanelPlugin } from "@grafana/data";
import { CarViewConfig } from "./types";
import { CarViewPanel } from "./CarViewPanel";

export const plugin = new PanelPlugin<CarViewConfig>(CarViewPanel).setPanelOptions(
  (builder: PanelOptionsEditorBuilder<CarViewConfig>) => {
    return (
      builder
        .addSliderInput({
          path: "zoom",
          name: "Zoom",
          defaultValue: 50,
          settings: {
            min: 1,
            max: 100
          }
        })

        // supervisor
        .addBooleanSwitch({
          path: "showSupervisorAll",
          name: "Show metrics from supervisor",
          defaultValue: true
        })
        .addBooleanSwitch({
          path: "showSupervisorPose",
          name: "Show pose according to supervisor",
          defaultValue: true,
          showIf: (config) => config.showSupervisorAll
        })
        .addBooleanSwitch({
          path: "showSupervisorLocalCones",
          name: "Show local cones according to supervisor",
          defaultValue: true,
          showIf: (config) => config.showSupervisorAll
        })
        .addBooleanSwitch({
          path: "showSupervisorPathPoints",
          name: "Show planned path points",
          defaultValue: true,
          showIf: (config) => config.showSupervisorAll
        })

        // emulator
        .addBooleanSwitch({
          path: "showEmulatorAll",
          name: "Show metrics from emulator",
          defaultValue: true
        })
        .addBooleanSwitch({
          path: "showEmulatorPose",
          name: "Show pose according to supervisor",
          defaultValue: true,
          showIf: (config) => config.showEmulatorAll
        })
        .addBooleanSwitch({
          path: "showEmulatorLocalCones",
          name: "Show local cones according to supervisor",
          defaultValue: true,
          showIf: (config) => config.showEmulatorAll
        })
    );
  }
);
