from src.application.vehicles.dto import UpdateVehicleInput, VehicleOutput
from src.application.vehicles.exceptions import VehicleNotFoundError
from src.application.vehicles.mapper import vehicle_to_output
from src.domain.vehicles.repository import VehicleRepository
from src.domain.voters.repository import VoterRepository


class UpdateVehicleUseCase:
    def __init__(self, vehicle_repository: VehicleRepository, voter_repository: VoterRepository) -> None:
        self._vehicle_repository = vehicle_repository
        self._voter_repository = voter_repository

    async def execute(self, input_data: UpdateVehicleInput) -> VehicleOutput:
        vehicle = await self._vehicle_repository.find_by_id(input_data.tenant_id, input_data.vehicle_id)
        if vehicle is None or vehicle.is_deleted:
            raise VehicleNotFoundError

        voter_id = input_data.voter_id
        if voter_id is not None:
            voter = await self._voter_repository.find_by_id(input_data.tenant_id, voter_id)
            if voter is None or voter.is_deleted:
                voter_id = None  # id inválido -> ignora, não trava a atualização

        vehicle.update_details(
            plate=input_data.plate,
            owner_name=input_data.owner_name,
            model=input_data.model,
            city=input_data.city,
            stickered_at=input_data.stickered_at,
            voter_id=voter_id,
        )
        await self._vehicle_repository.save(vehicle)
        return vehicle_to_output(vehicle)
