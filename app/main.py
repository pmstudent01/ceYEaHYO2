"""Command-line interface for the Vehicle Service API.

This CLI consumes the generated Python SDK located at::

    postman/sdks/Collections SDKs/Vehicle Service Collection/python

It inserts the SDK's ``src`` directory onto ``sys.path`` at runtime so the app
works without installing the SDK as a package. It then delegates all API calls
to :class:`app.vehicle_client.VehicleServiceApp`.

Examples
--------
    python app/main.py list
    python app/main.py create --nickname "Daily" --vin 1HG... --make Honda \
        --model Civic --year 2020 --miles 42000
    python app/main.py get <id>
    python app/main.py update <id> --miles 43000
    python app/main.py delete <id>
"""

from __future__ import annotations

import argparse
import json
import os
import sys


def _add_sdk_to_path() -> None:
    """Insert the generated SDK's ``src`` directory onto ``sys.path``.

    The path is computed relative to this file so the CLI is runnable from any
    working directory. The folder names ``Collections SDKs`` and
    ``Vehicle Service Collection`` contain spaces, so we build the path with
    ``os.path.join`` to keep it robust across platforms.
    """
    app_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(app_dir)
    sdk_src = os.path.join(
        repo_root,
        "postman",
        "sdks",
        "Collections SDKs",
        "Vehicle Service Collection",
        "python",
        "src",
    )
    if sdk_src not in sys.path:
        sys.path.insert(0, sdk_src)


# Make the SDK importable before we import the wrapper module (which imports it).
_add_sdk_to_path()

# Allow running both as `python app/main.py` and `python -m app.main`.
try:
    from app.vehicle_client import VehicleServiceApp, VehicleServiceError
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from vehicle_client import VehicleServiceApp, VehicleServiceError  # type: ignore


def _print_result(result) -> None:
    """Pretty-print an API result as JSON when possible."""
    if result is None:
        print("(no content)")
        return
    try:
        if isinstance(result, (dict, list)):
            print(json.dumps(result, indent=2, default=str))
        elif isinstance(result, str):
            # Try to parse JSON strings so they print nicely.
            try:
                print(json.dumps(json.loads(result), indent=2))
            except (ValueError, TypeError):
                print(result)
        else:
            print(json.dumps(result, indent=2, default=str))
    except (TypeError, ValueError):
        print(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vehicle-service",
        description="CLI for the Vehicle Service API (uses the generated Python SDK).",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Base URL of the Vehicle Service API. Defaults to $VEHICLE_SERVICE_BASE_URL "
             "or http://localhost:55290 (the local mock server).",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key. Defaults to $VEHICLE_SERVICE_API_KEY.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # list
    sub.add_parser("list", help="List all vehicles (GET /vehicles).")

    # create
    create = sub.add_parser("create", help="Create a vehicle (POST /vehicles).")
    create.add_argument("--nickname", dest="nickname", help="Vehicle nickname.")
    create.add_argument("--vin", help="Vehicle identification number.")
    create.add_argument("--make", help="Vehicle make.")
    create.add_argument("--model", help="Vehicle model.")
    create.add_argument("--year", help="Vehicle year.")
    create.add_argument("--miles", type=int, help="Vehicle mileage (integer).")

    # get
    get = sub.add_parser("get", help="Retrieve a vehicle by id (GET /vehicles/{id}).")
    get.add_argument("id", help="Vehicle id.")

    # update
    update = sub.add_parser("update", help="Update a vehicle by id (PATCH /vehicles/{id}).")
    update.add_argument("id", help="Vehicle id.")
    update.add_argument("--nickname", dest="nickname", help="Vehicle nickname.")
    update.add_argument("--vin", help="Vehicle identification number.")
    update.add_argument("--make", help="Vehicle make.")
    update.add_argument("--model", help="Vehicle model.")
    update.add_argument("--year", help="Vehicle year.")
    update.add_argument("--miles", type=int, help="Vehicle mileage (integer).")

    # delete
    delete = sub.add_parser("delete", help="Delete a vehicle by id (DELETE /vehicles/{id}).")
    delete.add_argument("id", help="Vehicle id.")

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    app = VehicleServiceApp(base_url=args.base_url, api_key=args.api_key)

    try:
        if args.command == "list":
            _print_result(app.list_vehicles())
        elif args.command == "create":
            _print_result(
                app.create_vehicle(
                    nick_name=args.nickname,
                    vin=args.vin,
                    make=args.make,
                    model=args.model,
                    year=args.year,
                    miles=args.miles,
                )
            )
        elif args.command == "get":
            _print_result(app.get_vehicle(args.id))
        elif args.command == "update":
            _print_result(
                app.update_vehicle(
                    args.id,
                    nick_name=args.nickname,
                    vin=args.vin,
                    make=args.make,
                    model=args.model,
                    year=args.year,
                    miles=args.miles,
                )
            )
        elif args.command == "delete":
            _print_result(app.delete_vehicle(args.id))
        else:  # pragma: no cover - argparse enforces a valid command
            parser.print_help()
            return 2
    except VehicleServiceError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
