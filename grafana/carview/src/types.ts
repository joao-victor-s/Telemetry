export interface RendererConfig {
  showSupervisorAll: boolean;
  showSupervisorPose: boolean;
  showSupervisorLocalCones: boolean;
  showSupervisorPathPoints: boolean;

  showEmulatorAll: boolean;
  showEmulatorPose: boolean;
  showEmulatorLocalCones: boolean;

  zoom: number;
}

export interface CarViewConfig extends RendererConfig {}

export interface Pose {
  x: number;
  y: number;
  yaw: number;
}

export type Point = [number, number];

export interface Cones {
  yellow: Point[];
  blue: Point[];
}

// FIXME: snake case because of backend return
export interface CarMap {
  supervisor: {
    pose: Pose | null;
    local_cones: Cones | null;
    path_points: Point[] | null;
    // globalCones: Cones;
  };
  emulator: {
    pose: Pose | null;
    local_cones: Cones | null;
    // fov: number;
    // globalCones: Cones;
  };
}
