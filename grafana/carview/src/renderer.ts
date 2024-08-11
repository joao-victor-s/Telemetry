import * as PIXI from "pixi.js";
import { OutlineFilter } from "@pixi/filter-outline";
import { Viewport } from "pixi-viewport";
import assets from "./img";
import { CarMap, Point, RendererConfig } from "types";

const textures = {
  car: PIXI.Texture.from(assets.car.light),
  dots: {
    blue: PIXI.Texture.from(assets.dots.blue),
    yellow: PIXI.Texture.from(assets.dots.yellow),
    red: PIXI.Texture.from(assets.dots.red)
  }
};

const CAR_WIDTH = 1.4;
const CAR_HEIGHT = 2.62;
const CONE_DIAMETER = 0.228;

const filters = [new PIXI.filters.AlphaFilter(0.5), new OutlineFilter(2, 0)];

/** Renders a car local map on a PIXI scene. */
export class CarRenderer {
  static readonly ZOOM_DELTA = 1;

  private _app: PIXI.Application;

  private _carMap?: CarMap;

  private _config: RendererConfig;

  private _entities: {
    viewport: Viewport;
    supervisor: {
      local: {
        container: PIXI.Container;

        car: PIXI.Sprite;
        cones: {
          blue: PIXI.Container;
          yellow: PIXI.Container;
        };
        pathPoints: PIXI.Container;
      };
      // global: {
      //   container: PIXI.Container;

      //   cones: {
      //     blue: PIXI.Container;
      //     yellow: PIXI.Container;
      //   };
      // };
    };
    emulator: {
      local: {
        container: PIXI.Container;

        car: PIXI.Sprite;
        // fieldOfView: PIXI.Graphics;

        cones: {
          blue: PIXI.Container;
          yellow: PIXI.Container;
        };
      };
      // global: {
      //   container: PIXI.Container;

      //   cones: {
      //     blue: PIXI.Container;
      //     yellow: PIXI.Container;
      //   };
      // };
    };
  };

  constructor(
    config: RendererConfig,
    width: number,
    height: number,
    app: PIXI.Application
  ) {
    this._app = app;

    this._entities = {
      viewport: (() => {
        const v = new Viewport({
          interaction: app.renderer.plugins.interaction
        });
        v.rotation = Math.PI / 2;
        return v;
      })(),
      supervisor: {
        local: {
          container: new PIXI.Container(),

          car: (() => {
            const car = new PIXI.Sprite(textures.car);
            car.anchor.set(0.5);
            return car;
          })(),
          cones: {
            blue: new PIXI.Container(),
            yellow: new PIXI.Container()
          },
          pathPoints: new PIXI.Container()
        }
      },
      emulator: {
        local: {
          container: new PIXI.Container(),

          car: (() => {
            const car = new PIXI.Sprite(textures.car);
            car.filters = filters;
            car.anchor.set(0.5);
            return car;
          })(),
          cones: {
            blue: new PIXI.Container(),
            yellow: new PIXI.Container()
          }
        }
      }
    };

    // configure entity containers
    // this._entities.supervisor.local.container.pivot.set(0.5);
    this._entities.supervisor.local.container.addChild(
      this._entities.supervisor.local.car,
      this._entities.supervisor.local.cones.blue,
      this._entities.supervisor.local.cones.yellow,
      this._entities.supervisor.local.pathPoints
    );

    // this._entities.emulator.local.container.pivot.set(0.5);
    this._entities.emulator.local.container.addChild(
      this._entities.emulator.local.car,
      this._entities.emulator.local.cones.blue,
      this._entities.emulator.local.cones.yellow
    );

    // configure viewport
    this._entities.viewport.addChild(
      this._entities.supervisor.local.container,
      this._entities.emulator.local.container
    );
    // this._entities.viewport.pivot.set(0.5);
    // this._entities.viewport.follow(this._entities.supervisor.local.container);
    this._app.stage.addChild(
      (this._entities.viewport as unknown) as PIXI.DisplayObject
    );

    this._config = config;
    this._applyConfig();

    this.resize(width, height);
  }

  private _getPointSprites(
    cones: Point[],
    texture: PIXI.Texture,
    emulatorFilters: boolean
  ): PIXI.Sprite[] {
    return cones.map((cone) => {
      const child = new PIXI.Sprite(texture);
      child.anchor.set(0.5);
      child.scale.set(CONE_DIAMETER / texture.width, CONE_DIAMETER / texture.height);
      child.x = cone[0];
      child.y = -cone[1];
      if (emulatorFilters) {
        child.filters = filters;
      }
      return child;
    });
  }

  // TODO: inefficient
  private _updatePointsContainer(
    container: PIXI.Container,
    points: Point[],
    texture: PIXI.Texture,
    emulatorFilters: boolean
  ) {
    container.removeChildren();
    const sprites = this._getPointSprites(points, texture, emulatorFilters);
    if (sprites.length > 0) {
      container.addChild(...sprites);
    }
  }

  private _updateEntities(): void {
    if (!this._carMap) {
      return;
    }

    // TODO: figure out texture scaling problem
    this._entities.supervisor.local.car.scale.set(
      CAR_WIDTH / this._entities.supervisor.local.car.texture.width,
      CAR_HEIGHT / this._entities.supervisor.local.car.texture.height
    );

    // TODO: figure out texture scaling problem
    this._entities.emulator.local.car.scale.set(
      CAR_WIDTH / this._entities.emulator.local.car.texture.width,
      CAR_HEIGHT / this._entities.emulator.local.car.texture.height
    );

    // car
    if (this._carMap.supervisor.pose === null) {
      this._entities.supervisor.local.container.visible = false;
    } else {
      this._entities.supervisor.local.container.x = -this._carMap.supervisor.pose.y;
      this._entities.supervisor.local.container.y = -this._carMap.supervisor.pose.x;
      this._entities.supervisor.local.container.rotation = -this._carMap.supervisor
        .pose.yaw;

      if (this._carMap.supervisor.local_cones === null) {
        this._entities.supervisor.local.cones.yellow.visible = false;
        this._entities.supervisor.local.cones.blue.visible = false;
      } else {
        this._updatePointsContainer(
          this._entities.supervisor.local.cones.yellow,
          this._carMap.supervisor.local_cones.yellow,
          textures.dots.yellow,
          false
        );
        this._updatePointsContainer(
          this._entities.supervisor.local.cones.blue,
          this._carMap.supervisor.local_cones.blue,
          textures.dots.blue,
          false
        );
      }

      if (this._carMap.supervisor.path_points === null) {
        this._entities.supervisor.local.pathPoints.visible = false;
      } else {
        this._updatePointsContainer(
          this._entities.supervisor.local.pathPoints,
          this._carMap.supervisor.path_points,
          textures.dots.red,
          false
        );
      }
    }

    // emulator
    if (this._carMap.emulator.pose === null) {
      this._entities.emulator.local.container.visible = false;
    } else {
      this._entities.emulator.local.container.x = -this._carMap.emulator.pose.y;
      this._entities.emulator.local.container.y = -this._carMap.emulator.pose.x;
      this._entities.emulator.local.container.rotation = -this._carMap.emulator.pose
        .yaw;

      if (this._carMap.emulator.local_cones === null) {
        this._entities.emulator.local.cones.yellow.visible = false;
        this._entities.emulator.local.cones.blue.visible = false;
      } else {
        this._updatePointsContainer(
          this._entities.emulator.local.cones.yellow,
          this._carMap.emulator.local_cones.yellow,
          textures.dots.yellow,
          true
        );
        this._updatePointsContainer(
          this._entities.emulator.local.cones.blue,
          this._carMap.emulator.local_cones.blue,
          textures.dots.blue,
          true
        );
      }
    }
  }

  resize(width: number, height: number): void {
    this._app.renderer.resize(width, height);

    this._entities.viewport.resize(width, height);
    this._entities.viewport.x = width / 2;
    this._entities.viewport.y = height / 2;
  }

  get view(): HTMLCanvasElement {
    return this._app.view;
  }

  set carMap(carMap: CarMap) {
    this._carMap = carMap;
  }

  private _applyConfig(): void {
    this._entities.viewport.setZoom(this._config.zoom);

    this._entities.supervisor.local.container.visible = this._config.showSupervisorAll;
    this._entities.supervisor.local.cones.blue.visible = this._config.showSupervisorLocalCones;
    this._entities.supervisor.local.cones.yellow.visible = this._config.showSupervisorLocalCones;
    this._entities.supervisor.local.car.visible = this._config.showSupervisorPose;
    this._entities.supervisor.local.pathPoints.visible = this._config.showSupervisorPathPoints;

    this._entities.emulator.local.container.visible = this._config.showEmulatorAll;
    this._entities.emulator.local.cones.blue.visible = this._config.showEmulatorLocalCones;
    this._entities.emulator.local.cones.yellow.visible = this._config.showEmulatorLocalCones;
    this._entities.emulator.local.car.visible = this._config.showEmulatorPose;
  }

  set config(config: RendererConfig) {
    this._config = config;
  }

  render() {
    this._applyConfig();
    this._updateEntities();
  }
}

export default CarRenderer;
