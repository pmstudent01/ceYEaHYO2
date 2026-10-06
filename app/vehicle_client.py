"""Thin wrapper around the generated Vehicle Service Collection Python SDK.

This module exposes a single :class:`VehicleServiceApp` class that constructs
the generated SDK client and provides small, friendly helper methods for each
Vehicle Service API operation. It does NOT modify the generated SDK in any way.

The SDK package name is ``vehicle_service_collection_sdk``. For this module to
import it, the SDK ``src`` directory must be present on ``sys.path``. The CLI in
``app/main.py`` takes care of inserting that path at runtime, so importing this
module from the CLI works without installing the SDK. If you import this module
directly, make sure the SDK ``src`` directory is importable first.
"""

from __future__ import annotations

import os
from typing import Any

from vehicle_service_collection_sdk import VehicleServiceCollectionSdk
from vehicle_service_collection_sdk.models import CreateAVehicleRequest

# The SDK raises RequestError on transport/HTTP failures. Import it defensively
# so this wrapper keeps working even if the SDK's internal layout changes.
try:  # pragma: no cover - import path is stable but guarded for safety
    from vehicle_service_collection_sdk.net.transport.request_error import RequestError
except Exception:  # pragma: no cover
    RequestError = Exception  # type: ignore[assignment,misc]


# Default base URL points at the local Postman mock server.
DEFAULT_BASE_URL = "http://localhost:55290"


class VehicleServiceError(Exception):
    """Raised when a Vehicle Service API call fails."""


class VehicleServiceApp:
    """A friendly facade over the generated Vehicle Service SDK client.

    :param base_url: Base URL of the Vehicle Service API. Defaults to the
        ``VEHICLE_SERVICE_BASE_URL`` environment variable, falling back to the
        local mock server at ``http://localhost:55290``.
    :param api_key: Optional API key. Defaults to the ``VEHICLE_SERVICE_API_KEY``
        environment variable.
    :param timeout: Optional request timeout in seconds.
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 timeout: float | None = None):
        self.base_url = (
            base_url
            or os.environ.get("VEHICLE_SERVICE_BASE_URL")
            or DEFAULT_BASE_URL
        )
        self.api_key = api_key or os.environ.get("VEHICLE_SERVICE_API_KEY")

        kwargs: dict[str, Any] = {"base_url": self.base_url}
        if self.api_key:
            kwargs["api_key"] = self.api_key
        if timeout is not None:
            kwargs["timeout"] = timeout

        self._client = VehicleServiceCollectionSdk(**kwargs)
        # The service object holds the actual endpoint methods.
        self._service = self._client.vehicle_service_collection_sdk

    # -- internal helper -------------------------------------------------
    @staticmethod
    def _call(fn, *args, **kwargs):
        """Invoke an SDK method, converting SDK errors into clean messages."""
        try:
            return fn(*args, **kwargs)
        except RequestError as exc:  # type: ignore[misc]
            raise VehicleServiceError(f"Vehicle Service request failed: {exc}") from exc
        except Exception as exc:  # noqa: BLE001 - surface a clean message
            raise VehicleServiceError(f"Unexpected error calling Vehicle Service: {exc}") from exc

    # -- public API ------------------------------------------------------
    def list_vehicles(self):
        """Return all vehicles (GET /vehicles)."""
        return self._call(self._service.get_all_vehicles)

    def create_vehicle(self, nick_name=None, vin=None, make=None, model=None,
                       year=None, miles=None):
        """Create a vehicle (POST /vehicles)."""
        request_body = CreateAVehicleRequest(
            nick_name=nick_name,
            vin=vin,
            make=make,
            model=model,
            year=year,
            miles=miles,
        )
        return self._call(self._service.create_a_vehicle, request_body)

    def get_vehicle(self, id: str):
        """Retrieve a single vehicle by id (GET /vehicles/{id})."""
        return self._call(self._service.retrieve_a_vehicle, id)

    def update_vehicle(self, id: str, **fields):
        """Update a vehicle by id (PATCH /vehicles/{id}).

        Only the provided fields are sent. Accepts the same field names as
        :meth:`create_vehicle`: ``nick_name``, ``vin``, ``make``, ``model``,
        ``year``, ``miles``.
        """
        allowed = {"nick_name", "vin", "make", "model", "year", "miles"}
        payload = {k: v for k, v in fields.items() if k in allowed and v is not None}
        request_body = CreateAVehicleRequest(**payload)
        # The SDK signature is update_a_collection(request_body, id_)
        return self._call(self._service.update_a_collection, request_body, id)

    def delete_vehicle(self, id: str):
        """Delete a vehicle by id (DELETE /vehicles/{id})."""
        return self._call(self._service.delete_a_vehicle, id)
