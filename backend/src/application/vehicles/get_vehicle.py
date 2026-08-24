from src.application.vehicles.dto import GetVehicleInput, VehicleOutput
from src.application.vehicles.exceptions import VehicleNotFoundError
from src.application.vehicles.mapper import vehicle_to_output
from src.domain.vehicles.repository import VehicleRepository


class GetVehicleUseCase:
    def __init__(self, vehicle_repository: VehicleRepository) -> None:
        self._vehicle_repository = vehicle_repository

    async def execute(self, input_data: GetVehicleInput) -> VehicleOutput:
        vehicle = await self._vehicle_repository.find_by_id(input_data.tenant_id, input_data.vehicle_id)
        if vehicle is None or vehicle.is_deleted:
            raise VehicleNotFoundError
        return vehicle_to_output(vehicle)
