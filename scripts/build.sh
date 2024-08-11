yarn --cwd grafana/telemetry-datasource run build
yarn --cwd grafana/telemetry-datasource run sign
yarn --cwd grafana/carview run build
yarn --cwd grafana/carview run sign

docker-compose \
    -p telemetry \
    -f compose/backend.yml \
    -f compose/backend.dev.yml \
    -f compose/grafana.yml \
    -f compose/grafana.dev.yml \
    --env-file ./.env \
    build
