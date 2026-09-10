from datetime import date
from decimal import Decimal

from src.application.finance.dto import (
    FinanceAttachmentOutput,
    FinancePaymentOutput,
    FinanceSummaryOutput,
    FinanceTransactionOutput,
)
from src.domain.finance.entities import FinanceAttachment, FinancePayment, FinanceTransaction
from src.domain.finance.repository import FinanceSummary


def transaction_to_output(
    transaction: FinanceTransaction, attachment_count: int, amount_paid: Decimal
) -> FinanceTransactionOutput:
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
        effective_payment_status=transaction.compute_effective_status(amount_paid, date.today()),
        amount_paid=amount_paid,
        amount_remaining=transaction.amount - amount_paid,
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


def payment_to_output(payment: FinancePayment) -> FinancePaymentOutput:
    return FinancePaymentOutput(
        id=payment.id,
        transaction_id=payment.transaction_id,
        amount=payment.amount,
        paid_at=payment.paid_at,
        created_at=payment.created_at,
    )


def summary_to_output(summary: FinanceSummary) -> FinanceSummaryOutput:
    return FinanceSummaryOutput(
        total_receitas=summary.total_receitas,
        total_despesas=summary.total_despesas,
        total_doacoes=summary.total_doacoes,
        total_pago=summary.total_pago,
        total_a_pagar=summary.total_a_pagar,
        saldo_atual=summary.saldo_atual,
    )
