from src.application.vehicles.dto import DeleteVehicleInput
from src.application.vehicles.exceptions import VehicleNotFoundError
from src.domain.vehicles.repository import VehicleRepository


class DeleteVehicleUseCase:
    def __init__(self, vehicle_repository: VehicleRepository) -> None:
        self._vehicle_repository = vehicle_repository

    async def execute(self, input_data: DeleteVehicleInput) -> None:
        vehicle = await self._vehicle_repository.find_by_id(input_data.tenant_id, input_data.vehicle_id)
        if vehicle is None or vehicle.is_deleted:
            raise VehicleNotFoundError

        vehicle.soft_delete()
        await self._vehicle_repository.save(vehicle)
