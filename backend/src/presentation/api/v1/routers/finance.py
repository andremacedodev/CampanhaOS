"""
Router financeiro (Financeiro básico).

Mesma convenção dos routers anteriores: `current_user` sempre primeiro na
assinatura (ver comentário em v1/routers/voters.py).
"""

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from src.application.finance.add_attachment import AddFinanceAttachmentInput, AddFinanceAttachmentUseCase
from src.application.finance.add_payment import AddFinancePaymentUseCase
from src.application.finance.create_transaction import CreateFinanceTransactionUseCase
from src.application.finance.delete_transaction import DeleteFinanceTransactionUseCase
from src.application.finance.dto import (
    AddFinancePaymentInput,
    CreateFinanceTransactionInput,
    DeleteFinanceTransactionInput,
    GetFinanceTransactionInput,
    ListFinanceAttachmentsInput,
    ListFinancePaymentsInput,
    ListFinanceTransactionsInput,
    RemoveFinancePaymentInput,
    UpdateFinanceTransactionInput,
)
from src.application.finance.get_attachment_download_url import (
    GetFinanceAttachmentDownloadUrlInput,
    GetFinanceAttachmentDownloadUrlUseCase,
)
from src.application.finance.get_transaction import GetFinanceTransactionUseCase
from src.application.finance.list_attachments import ListFinanceAttachmentsUseCase
from src.application.finance.list_payments import ListFinancePaymentsUseCase
from src.application.finance.list_transactions import ListFinanceTransactionsUseCase
from src.application.finance.remove_attachment import RemoveFinanceAttachmentInput, RemoveFinanceAttachmentUseCase
from src.application.finance.remove_payment import RemoveFinancePaymentUseCase
from src.application.finance.update_transaction import UpdateFinanceTransactionUseCase
from src.presentation.api.dependencies import CurrentUser, DbSession
from src.presentation.api.finance_dependencies import (
    get_add_finance_attachment_use_case,
    get_add_finance_payment_use_case,
    get_create_finance_transaction_use_case,
    get_delete_finance_transaction_use_case,
    get_finance_attachment_download_url_use_case,
    get_get_finance_transaction_use_case,
    get_list_finance_attachments_use_case,
    get_list_finance_payments_use_case,
    get_list_finance_transactions_use_case,
    get_remove_finance_attachment_use_case,
    get_remove_finance_payment_use_case,
    get_update_finance_transaction_use_case,
)
from src.presentation.api.v1.schemas.finance import (
    AttachmentCategory,
    FinanceAttachmentDownloadResponse,
    FinanceAttachmentListResponse,
    FinanceAttachmentResponse,
    FinancePaymentCreateRequest,
    FinancePaymentListResponse,
    FinancePaymentResponse,
    FinanceTransactionCreateRequest,
    FinanceTransactionListResponse,
    FinanceTransactionResponse,
    FinanceTransactionUpdateRequest,
)

router = APIRouter(prefix="/finance", tags=["finance"])


@router.post("", response_model=FinanceTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    current_user: CurrentUser,
    request: FinanceTransactionCreateRequest,
    session: DbSession,
    use_case: Annotated[CreateFinanceTransactionUseCase, Depends(get_create_finance_transaction_use_case)],
) -> FinanceTransactionResponse:
    output = await use_case.execute(
        CreateFinanceTransactionInput(
            tenant_id=current_user.tenant_id,
            created_by_user_id=current_user.id,
            type=request.type,
            category=request.category,
            amount=request.amount,
            occurred_at=request.occurred_at,
            description=request.description,
        )
    )
    await session.commit()
    return FinanceTransactionResponse.model_validate(output)


@router.get("", response_model=FinanceTransactionListResponse)
async def list_transactions(
    current_user: CurrentUser,
    use_case: Annotated[ListFinanceTransactionsUseCase, Depends(get_list_finance_transactions_use_case)],
    type: str | None = Query(None),  # nome mais natural pro cliente da API do que "type_"
    category: str | None = Query(None),
    occurred_after: date | None = Query(None),
    occurred_before: date | None = Query(None),
    payment_status: str | None = Query(
        None, description="Filtra despesas por 'pago', 'parcial', 'pendente' ou 'atrasado'"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> FinanceTransactionListResponse:
    output = await use_case.execute(
        ListFinanceTransactionsInput(
            tenant_id=current_user.tenant_id,
            type=type,
            category=category,
            occurred_after=occurred_after,
            occurred_before=occurred_before,
            payment_status=payment_status,
            page=page,
            page_size=page_size,
        )
    )
    return FinanceTransactionListResponse.model_validate(output)


@router.get("/{transaction_id}", response_model=FinanceTransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetFinanceTransactionUseCase, Depends(get_get_finance_transaction_use_case)],
) -> FinanceTransactionResponse:
    output = await use_case.execute(
        GetFinanceTransactionInput(tenant_id=current_user.tenant_id, transaction_id=transaction_id)
    )
    return FinanceTransactionResponse.model_validate(output)


@router.patch("/{transaction_id}", response_model=FinanceTransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    current_user: CurrentUser,
    request: FinanceTransactionUpdateRequest,
    session: DbSession,
    use_case: Annotated[UpdateFinanceTransactionUseCase, Depends(get_update_finance_transaction_use_case)],
) -> FinanceTransactionResponse:
    output = await use_case.execute(
        UpdateFinanceTransactionInput(
            tenant_id=current_user.tenant_id,
            transaction_id=transaction_id,
            type=request.type,
            category=request.category,
            amount=request.amount,
            occurred_at=request.occurred_at,
            description=request.description,
        )
    )
    await session.commit()
    return FinanceTransactionResponse.model_validate(output)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    current_user: CurrentUser,
    session: DbSession,
    use_case: Annotated[DeleteFinanceTransactionUseCase, Depends(get_delete_finance_transaction_use_case)],
) -> None:
    await use_case.execute(
        DeleteFinanceTransactionInput(tenant_id=current_user.tenant_id, transaction_id=transaction_id)
    )
    await session.commit()


@router.post("/{transaction_id}/attachments", response_model=FinanceAttachmentResponse, status_code=status.HTTP_201_CREATED)
async def add_attachment(
    transaction_id: UUID,
    current_user: CurrentUser,
    session: DbSession,
    use_case: Annotated[AddFinanceAttachmentUseCase, Depends(get_add_finance_attachment_use_case)],
    category: AttachmentCategory = Query(...),
    file: UploadFile = File(...),
) -> FinanceAttachmentResponse:
    file_bytes = await file.read()
    output = await use_case.execute(
        AddFinanceAttachmentInput(
            tenant_id=current_user.tenant_id,
            transaction_id=transaction_id,
            uploaded_by_user_id=current_user.id,
            category=category,
            filename=file.filename or "arquivo",
            file_bytes=file_bytes,
        )
    )
    await session.commit()
    return FinanceAttachmentResponse.model_validate(output)


@router.get("/{transaction_id}/attachments", response_model=FinanceAttachmentListResponse)
async def list_attachments(
    transaction_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[ListFinanceAttachmentsUseCase, Depends(get_list_finance_attachments_use_case)],
) -> FinanceAttachmentListResponse:
    items = await use_case.execute(
        ListFinanceAttachmentsInput(tenant_id=current_user.tenant_id, transaction_id=transaction_id)
    )
    return FinanceAttachmentListResponse(items=[FinanceAttachmentResponse.model_validate(i) for i in items])


@router.delete("/{transaction_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_attachment(
    transaction_id: UUID,
    attachment_id: UUID,
    current_user: CurrentUser,
    session: DbSession,
    use_case: Annotated[RemoveFinanceAttachmentUseCase, Depends(get_remove_finance_attachment_use_case)],
) -> None:
    await use_case.execute(
        RemoveFinanceAttachmentInput(
            tenant_id=current_user.tenant_id, transaction_id=transaction_id, attachment_id=attachment_id
        )
    )
    await session.commit()


@router.get(
    "/{transaction_id}/attachments/{attachment_id}/download-url", response_model=FinanceAttachmentDownloadResponse
)
async def get_attachment_download_url(
    transaction_id: UUID,
    attachment_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[
        GetFinanceAttachmentDownloadUrlUseCase, Depends(get_finance_attachment_download_url_use_case)
    ],
) -> FinanceAttachmentDownloadResponse:
    output = await use_case.execute(
        GetFinanceAttachmentDownloadUrlInput(
            tenant_id=current_user.tenant_id, transaction_id=transaction_id, attachment_id=attachment_id
        )
    )
    return FinanceAttachmentDownloadResponse(download_url=output.download_url, filename=output.filename)


@router.post("/{transaction_id}/payments", response_model=FinancePaymentResponse, status_code=status.HTTP_201_CREATED)
async def add_payment(
    transaction_id: UUID,
    current_user: CurrentUser,
    request: FinancePaymentCreateRequest,
    session: DbSession,
    use_case: Annotated[AddFinancePaymentUseCase, Depends(get_add_finance_payment_use_case)],
) -> FinancePaymentResponse:
    output = await use_case.execute(
        AddFinancePaymentInput(
            tenant_id=current_user.tenant_id,
            transaction_id=transaction_id,
            created_by_user_id=current_user.id,
            amount=request.amount,
            paid_at=request.paid_at,
        )
    )
    await session.commit()
    return FinancePaymentResponse.model_validate(output)


@router.get("/{transaction_id}/payments", response_model=FinancePaymentListResponse)
async def list_payments(
    transaction_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[ListFinancePaymentsUseCase, Depends(get_list_finance_payments_use_case)],
) -> FinancePaymentListResponse:
    items = await use_case.execute(
        ListFinancePaymentsInput(tenant_id=current_user.tenant_id, transaction_id=transaction_id)
    )
    return FinancePaymentListResponse(items=[FinancePaymentResponse.model_validate(i) for i in items])


@router.delete("/{transaction_id}/payments/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_payment(
    transaction_id: UUID,
    payment_id: UUID,
    current_user: CurrentUser,
    session: DbSession,
    use_case: Annotated[RemoveFinancePaymentUseCase, Depends(get_remove_finance_payment_use_case)],
) -> None:
    await use_case.execute(
        RemoveFinancePaymentInput(
            tenant_id=current_user.tenant_id, transaction_id=transaction_id, payment_id=payment_id
        )
    )
    await session.commit()
