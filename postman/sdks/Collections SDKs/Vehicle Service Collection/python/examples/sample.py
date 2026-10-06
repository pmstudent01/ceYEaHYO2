from vehicle_service_collection_sdk import VehicleServiceCollectionSdk, Environment

sdk = VehicleServiceCollectionSdk(
    api_key="YOUR_API_KEY", base_url=Environment.DEFAULT.value, timeout=10
)

result = sdk.vehicle_service_collection_sdk.get_all_vehicles()

with open("output-file.ext", "w") as f:
    f.write(
        result
        if isinstance(result, str)
        else result.decode(errors="replace")
        if isinstance(result, (bytes, bytearray))
        else str(result)
    )
