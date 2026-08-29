from src.application.vehicles.dto import CreateVehicleInput, VehicleOutput
from src.application.vehicles.mapper import vehicle_to_output
from src.domain.vehicles.entities import StickeredVehicle
from src.domain.vehicles.repository import VehicleRepository
from src.domain.voters.repository import VoterRepository


class CreateVehicleUseCase:
    def __init__(self, vehicle_repository: VehicleRepository, voter_repository: VoterRepository) -> None:
        self._vehicle_repository = vehicle_repository
        self._voter_repository = voter_repository

    async def execute(self, input_data: CreateVehicleInput) -> VehicleOutput:
        # Se um eleitor foi vinculado, confirma que ele existe DESTE
        # tenant — mesma lógica de validação já usada em
        # CreateLeadershipUseCase pra leadership_id. Se o id for
        # inválido, o próprio VoterRepository.find_by_id() retorna None,
        # e aqui simplesmente tratamos como "não vinculado" em vez de
        # travar o cadastro do veículo por causa de um detalhe de vínculo.
        validated_voter_id = None
        if input_data.voter_id is not None:
            voter = await self._voter_repository.find_by_id(input_data.tenant_id, input_data.voter_id)
            if voter is not None and not voter.is_deleted:
                validated_voter_id = input_data.voter_id

        vehicle = StickeredVehicle.create(
            tenant_id=input_data.tenant_id,
            created_by_user_id=input_data.created_by_user_id,
            plate=input_data.plate,
            owner_name=input_data.owner_name,
            stickered_at=input_data.stickered_at,
            voter_id=validated_voter_id,
            model=input_data.model,
            city=input_data.city,
        )
        await self._vehicle_repository.save(vehicle)
        return vehicle_to_output(vehicle)
