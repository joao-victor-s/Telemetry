# check for python
python3.8 --version || exit 1

# check for yarn
yarn --version || exit 1

# create virtual environment
python3.8 -m venv venv
. venv/bin/activate

# install dependencies
python3.8 -m pip install -r requirements.txt

# install pre-commit
pre-commit install

# install grafana plugin dependencies
# plugin: datasource
cd grafana/telemetry-datasource
yarn install
cd ../../

# plugin: carview
cd grafana/carview
yarn install
cd ../../
