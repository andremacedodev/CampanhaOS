from src.application.vehicles.dto import VehicleOutput
from src.domain.vehicles.entities import StickeredVehicle


def vehicle_to_output(vehicle: StickeredVehicle) -> VehicleOutput:
    return VehicleOutput(
        id=vehicle.id,
        created_by_user_id=vehicle.created_by_user_id,
        plate=vehicle.plate,
        owner_name=vehicle.owner_name,
        voter_id=vehicle.voter_id,
        model=vehicle.model,
        city=vehicle.city,
        stickered_at=vehicle.stickered_at,
        created_at=vehicle.created_at,
        updated_at=vehicle.updated_at,
        photo_filename=vehicle.photo_filename,
        photo_content_type=vehicle.photo_content_type,
        photo_size_bytes=vehicle.photo_size_bytes,
    )
