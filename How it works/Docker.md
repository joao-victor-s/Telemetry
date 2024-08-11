We use [Docker](https://docker.com) and [Docker Compose](https://docs.docker.com/compose/) to facilitate installation and setup, as our telemetry is split into a couple of microservices.

# Backend Docker build
The backend is build through its [Dockerfile](https://gitlab.com/unicamperacing/Ia/driverless-2020/viz/-/blob/master/backend/Dockerfile). It has one [build target](https://docs.docker.com/develop/develop-images/multistage-build/) for each service. Each target derives from the `shared` target, which installs common dependencies.

# Docker Compose
All docker-compose stuff is in the [`compose/`](https://gitlab.com/unicamperacing/Ia/driverless-2020/viz/-/tree/master/compose) folder.
- `backend.yml`: Contains all the information needed for building and deploying all backend containers.
- `backend.dev.yml`: Overrides `backend.yml` by mounting code volumes to container. Useful for hot code reloads without having to restart containers.
- `grafana.yml`: Contains all the information needed for downloading and deploying Grafana. It binds each plugin's repository to the expected folder inside the container. **NOTICE:** This is temporary and for development only. In the future, we'll build our own Grafana image which ships with pre-installed, signed plugins.
- `grafana.env`: Contains [Grafana's custom configurations](https://grafana.com/docs/grafana/latest/administration/configuration/).

All `sh run` scripts are basically aliases to different `docker-compose up` operations which combine permutations of these files.

Learn more about compose file specification [here](https://docs.docker.com/compose/compose-file/compose-file-v3/).
