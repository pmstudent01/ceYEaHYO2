# Vehicle Service CLI

A small, runnable Python command-line application that **consumes the Vehicle
Service API** through the already-generated Python SDK that ships with this
repository.

## What it is

- `vehicle_client.py` — a thin wrapper (`VehicleServiceApp`) around the
  generated SDK client. It builds the proper request models and exposes
  friendly methods: `list_vehicles`, `create_vehicle`, `get_vehicle`,
  `update_vehicle`, and `delete_vehicle`. SDK/transport errors are caught and
  returned as clean messages.
- `main.py` — an [`argparse`](https://docs.python.org/3/library/argparse.html)
  CLI with `list`, `create`, `get`, `update`, and `delete` subcommands. It
  prints responses as nicely formatted JSON.

## How it uses the generated SDK

The generated SDK lives in the repo at:

```
postman/sdks/Collections SDKs/Vehicle Service Collection/python
```

- Package name: `vehicle_service_collection_sdk`
- Main client class: `VehicleServiceCollectionSdk`
- Request model: `CreateAVehicleRequest`

Rather than requiring you to install the SDK, `main.py` inserts the SDK's
`src` directory onto `sys.path` at runtime (computed relative to the repo
root). This means the CLI works straight from a clone — you only need the
SDK's own runtime dependencies installed.

The **generated SDK files are never modified** by this app.

## Install dependencies

The SDK needs `requests` and `pydantic` at runtime:

```bash
pip install -r app/requirements.txt
```

## Environment variables

| Variable                    | Description                                     | Default                   |
| --------------------------- | ----------------------------------------------- | ------------------------- |
| `VEHICLE_SERVICE_BASE_URL`  | Base URL of the Vehicle Service API.            | `http://localhost:55290`  |
| `VEHICLE_SERVICE_API_KEY`   | API key sent via the SDK (optional).            | _(none)_                  |

You can also override the base URL / API key per invocation with the global
`--base-url` and `--api-key` flags.

The default base URL points at the **local Postman mock server** running at
`http://localhost:55290`.

## Usage

Show help:

```bash
python app/main.py --help
```

### List all vehicles

```bash
python app/main.py list
```

### Create a vehicle

```bash
python app/main.py create \
  --nickname "Daily Driver" \
  --vin 1HGBH41JXMN109186 \
  --make Honda \
  --model Civic \
  --year 2020 \
  --miles 42000
```

### Get a vehicle by id

```bash
python app/main.py get <vehicle-id>
```

### Update a vehicle

Only the fields you pass are sent:

```bash
python app/main.py update <vehicle-id> --miles 43000 --nickname "Weekend Car"
```

### Delete a vehicle

```bash
python app/main.py delete <vehicle-id>
```

### Point at a different server

```bash
# via flag
python app/main.py --base-url http://localhost:55290 list

# via environment variable
export VEHICLE_SERVICE_BASE_URL=http://localhost:55290
python app/main.py list
```

All examples above target the local mock server at `http://localhost:55290`.
