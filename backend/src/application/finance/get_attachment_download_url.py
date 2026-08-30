from src.application.finance.dto import GetFinanceAttachmentDownloadUrlInput, GetFinanceAttachmentDownloadUrlOutput
from src.application.finance.exceptions import FinanceAttachmentNotFoundError
from src.application.shared.file_storage_port import FileStoragePort
from src.domain.finance.attachment_repository import FinanceAttachmentRepository


class GetFinanceAttachmentDownloadUrlUseCase:
    def __init__(self, attachment_repository: FinanceAttachmentRepository, file_storage: FileStoragePort) -> None:
        self._attachment_repository = attachment_repository
        self._file_storage = file_storage

    async def execute(
        self, input_data: GetFinanceAttachmentDownloadUrlInput
    ) -> GetFinanceAttachmentDownloadUrlOutput:
        attachment = await self._attachment_repository.find_by_id(input_data.tenant_id, input_data.attachment_id)
        if attachment is None or attachment.transaction_id != input_data.transaction_id:
            raise FinanceAttachmentNotFoundError

        download_url = await self._file_storage.generate_download_url(attachment.storage_key)
        return GetFinanceAttachmentDownloadUrlOutput(download_url=download_url, filename=attachment.filename)
