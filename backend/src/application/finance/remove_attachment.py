from src.application.finance.dto import RemoveFinanceAttachmentInput
from src.application.finance.exceptions import FinanceAttachmentNotFoundError
from src.application.shared.file_storage_port import FileStoragePort
from src.domain.finance.attachment_repository import FinanceAttachmentRepository


class RemoveFinanceAttachmentUseCase:
    def __init__(self, attachment_repository: FinanceAttachmentRepository, file_storage: FileStoragePort) -> None:
        self._attachment_repository = attachment_repository
        self._file_storage = file_storage

    async def execute(self, input_data: RemoveFinanceAttachmentInput) -> None:
        attachment = await self._attachment_repository.find_by_id(input_data.tenant_id, input_data.attachment_id)
        if attachment is None or attachment.transaction_id != input_data.transaction_id:
            raise FinanceAttachmentNotFoundError

        storage_key = attachment.storage_key
        await self._attachment_repository.delete(input_data.tenant_id, input_data.attachment_id)

        # Apaga do R2 só DEPOIS de confirmar que a referência já saiu do
        # banco — mesma ordem de sempre.
        await self._file_storage.delete(storage_key)
