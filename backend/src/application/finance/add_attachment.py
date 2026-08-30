"""
Caso de uso: adicionar um documento (anexo) a um lançamento financeiro.

Um lançamento pode ter vários anexos agora (até MAX_ATTACHMENTS_PER_TRANSACTION)
— cada categoria (comprovante, contrato, orçamento, outro) pode se repetir,
não é um-por-categoria, é livre até o limite total.
"""

import uuid

from src.application.finance.dto import AddFinanceAttachmentInput, FinanceAttachmentOutput
from src.application.finance.exceptions import FinanceTransactionNotFoundError, UnsupportedFileTypeError
from src.application.finance.mapper import attachment_to_output
from src.application.shared.exceptions import ApplicationError
from src.application.shared.file_storage_port import FileStoragePort
from src.domain.finance.attachment_repository import FinanceAttachmentRepository
from src.domain.finance.entities import MAX_ATTACHMENT_SIZE_BYTES, MAX_ATTACHMENTS_PER_TRANSACTION, FinanceAttachment
from src.domain.finance.repository import FinanceRepository
from src.infrastructure.storage.file_signature import detect_content_type

_EXTENSION_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "application/pdf": ".pdf",
}


class AttachmentTooLargeError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(f"Arquivo muito grande — limite de {MAX_ATTACHMENT_SIZE_BYTES / 1024 / 1024:.0f}MB")


class TooManyAttachmentsError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(f"Limite de {MAX_ATTACHMENTS_PER_TRANSACTION} anexos por lançamento atingido")


class AddFinanceAttachmentUseCase:
    def __init__(
        self,
        finance_repository: FinanceRepository,
        attachment_repository: FinanceAttachmentRepository,
        file_storage: FileStoragePort,
    ) -> None:
        self._finance_repository = finance_repository
        self._attachment_repository = attachment_repository
        self._file_storage = file_storage

    async def execute(self, input_data: AddFinanceAttachmentInput) -> FinanceAttachmentOutput:
        transaction = await self._finance_repository.find_by_id(input_data.tenant_id, input_data.transaction_id)
        if transaction is None or transaction.is_deleted:
            raise FinanceTransactionNotFoundError

        # Checa o limite ANTES de validar tipo/tamanho ou subir qualquer
        # coisa — economiza trabalho se já estiver no limite.
        current_count = await self._attachment_repository.count_by_transaction(
            input_data.tenant_id, input_data.transaction_id
        )
        if current_count >= MAX_ATTACHMENTS_PER_TRANSACTION:
            raise TooManyAttachmentsError

        if len(input_data.file_bytes) > MAX_ATTACHMENT_SIZE_BYTES:
            raise AttachmentTooLargeError

        real_content_type = detect_content_type(input_data.file_bytes)
        if real_content_type is None:
            raise UnsupportedFileTypeError

        extension = _EXTENSION_BY_CONTENT_TYPE[real_content_type]
        storage_key = (
            f"finance-attachments/{input_data.tenant_id}/{input_data.transaction_id}/{uuid.uuid4()}{extension}"
        )

        await self._file_storage.upload(storage_key, input_data.file_bytes, real_content_type)

        attachment = FinanceAttachment.create(
            tenant_id=input_data.tenant_id,
            transaction_id=input_data.transaction_id,
            uploaded_by_user_id=input_data.uploaded_by_user_id,
            category=input_data.category,
            storage_key=storage_key,
            filename=input_data.filename,
            content_type=real_content_type,
            size_bytes=len(input_data.file_bytes),
        )
        await self._attachment_repository.save(attachment)

        return attachment_to_output(attachment)
