docker-compose \
    -p telemetry \
    -f compose/backend.yml \
    -f compose/backend.dev.yml \
    -f compose/grafana.yml \
    -f compose/grafana.dev.yml \
    --env-file ./.env \
    up --remove-orphans
