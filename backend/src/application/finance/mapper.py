from datetime import date

from src.application.finance.dto import FinanceAttachmentOutput, FinanceSummaryOutput, FinanceTransactionOutput
from src.domain.finance.entities import FinanceAttachment, FinanceTransaction
from src.domain.finance.repository import FinanceSummary


def transaction_to_output(transaction: FinanceTransaction, attachment_count: int) -> FinanceTransactionOutput:
    return FinanceTransactionOutput(
        id=transaction.id,
        created_by_user_id=transaction.created_by_user_id,
        type=transaction.type,
        category=transaction.category,
        amount=transaction.amount,
        description=transaction.description,
        occurred_at=transaction.occurred_at,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at,
        payment_status=transaction.payment_status,
        effective_payment_status=transaction.effective_payment_status(date.today()),
        attachment_count=attachment_count,
    )


def attachment_to_output(attachment: FinanceAttachment) -> FinanceAttachmentOutput:
    return FinanceAttachmentOutput(
        id=attachment.id,
        transaction_id=attachment.transaction_id,
        category=attachment.category,
        filename=attachment.filename,
        content_type=attachment.content_type,
        size_bytes=attachment.size_bytes,
        uploaded_at=attachment.uploaded_at,
    )


def summary_to_output(summary: FinanceSummary) -> FinanceSummaryOutput:
    return FinanceSummaryOutput(
        total_receitas=summary.total_receitas,
        total_despesas=summary.total_despesas,
        total_doacoes=summary.total_doacoes,
        saldo=summary.saldo,
    )
