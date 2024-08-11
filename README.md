# Introduction

This repository contains portions of the code for the Unicamp E-Racing telemetry system, showcasing the work done for demonstration purposes.

In the "How It Works" folder, you'll find detailed information about the architecture. Feel free to explore!

# Installing and running

To run the complete telemetry stack in _production_ mode, first install [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/). 


## Step 1: Check if SocketCAN is Already Installed

Before installing SocketCAN, it's recommended to verify if it's already available on your system. Open a terminal and execute the following command:

```bash
sudo modprobe can
```

*Note*: If the command returns an error message, SocketCAN is not installed. If it returns nothing, SocketCAN is already installed.

## Step 2: Install SocketCAN

If SocketCAN is not already installed, follow these steps:

1. Open a terminal window and install the `can-utils` package:

```bash
sudo apt-get install can-utils
```

2. After the package is installed, load the CAN module:

```bash
sudo modprobe can
```

## Step 3: Create a Simulator on Your Computer

1. Create a virtual CAN using the script "create_vcan.sh":

```bash
sh simulator/create_vcan.sh
```

2. Run the CAN message decoder:

```bash
python3 decode_can.py
```

3. In a separate terminal, launch the CAN message metric generator:

```bash
python3 pycan.py
```

## Step 4: Run the Front-end

1. In yet another terminal (yes, quite a few terminals), execute:

```bash
bash scripts/run-dev.sh
```

*Note*: Front-end may not be built yet.

2. Open your preferred browser and visit:

- [localhost:3000](http://localhost:3000)

## Step 5: Access and Explore Grafana

1. Log in using the following credentials:

   - **User:** admin
   - **Password:** admin

2. Access our Data Source on the side bar:

   - _Configuration > Data Sources > Unicamp E-Racing_

   *Note:* Select it and run a test.

3. Select "Create" and then "Import", import the .json files from the dashboards and then access them.



_* Production mode doesn't allow frontend/backend debugging, hot code reloads and unsigned Grafana plugins. Refer to the [Development Setup](https://gitlab.com/unicamperacing/Ia/driverless-2020/viz/-/wikis/Development-Setup) if you want to run it in development mode._
