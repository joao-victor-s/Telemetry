docker-compose \
    -p telemetry \
    -f compose/backend.yml \
    -f compose/grafana.yml \
    --env-file ./.env \
    up --remove-orphans
