import React from "react";

import * as PIXI from "pixi.js";

import { PanelProps } from "@grafana/data";
import { CarMap, CarViewConfig } from "types";
import { css, cx } from "emotion";
import { stylesFactory, useTheme } from "@grafana/ui";

import useLazyRef from "useLazyRef";
import CarRenderer from "renderer";

interface Props extends PanelProps<CarViewConfig> {}

const getStyles = stylesFactory(() => {
  return {
    wrapper: css`
      position: relative;
    `,
    svg: css`
      position: absolute;
      top: 0;
      left: 0;
    `,
    textBox: css`
      position: absolute;
      bottom: 0;
      left: 0;
      padding: 10px;
    `
  };
});

function tryExtractCarMapFromData(data: unknown): CarMap | null {
  const maybeCarMap = data as CarMap;

  if (typeof maybeCarMap !== "object") {
    return null;
  }

  if (typeof maybeCarMap.supervisor !== "object") {
    return null;
  }
  if (typeof maybeCarMap.supervisor.pose === "undefined") {
    return null;
  }
  if (typeof maybeCarMap.supervisor.local_cones === "undefined") {
    return null;
  }
  if (typeof maybeCarMap.supervisor.path_points === "undefined") {
    return null;
  }

  if (typeof maybeCarMap.emulator !== "object") {
    return null;
  }
  if (typeof maybeCarMap.emulator.pose === "undefined") {
    return null;
  }
  if (typeof maybeCarMap.emulator.local_cones === "undefined") {
    return null;
  }

  return maybeCarMap;
}

export const CarViewPanel: React.FC<Props> = (props: Props) => {
  const { options, data, width, height } = props;
  const theme = useTheme();
  const styles = getStyles();

  const renderer = useLazyRef(() => {
    const bgColorInt = parseInt(theme.colors.bg1.replace("#", ""), 16);
    const pixiApp = new PIXI.Application({
      backgroundColor: bgColorInt,
      resolution: window.devicePixelRatio || 1
    });
    return new CarRenderer(
      options,
      pixiApp.screen.width,
      pixiApp.screen.height,
      pixiApp
    );
  });

  const containerDiv = React.useRef<HTMLDivElement | null>(null);
  const clientWidth = containerDiv.current?.clientWidth;
  const clientHeight = containerDiv.current?.clientHeight;
  const containerClassName = cx(
    styles.wrapper,
    css`
      width: ${width}px;
      height: ${height}px;
    `
  );
  React.useLayoutEffect(() => {
    const divWidth = containerDiv.current?.clientWidth as number;
    const divHeight = containerDiv.current?.clientHeight as number;
    renderer.resize(divWidth, divHeight);
  }, [renderer, clientWidth, clientHeight]);

  const map = tryExtractCarMapFromData(data.series[0].fields[1].values.get(0));
  if (map === null) {
    return (
      <div className={containerClassName}>
        <h1
          style={{
            color: theme.colors.textBlue
          }}
        >
          Car view metric type must implement "CarMap"
        </h1>
      </div>
    );
  }

  renderer.config = options;
  renderer.carMap = map;
  renderer.render();

  return (
    <div
      className={containerClassName}
      ref={(div: HTMLDivElement): void => {
        if (div) {
          containerDiv.current = div;
          div.appendChild(renderer.view);
        } else {
          containerDiv.current = null;
        }
      }}
    ></div>
  );
};
