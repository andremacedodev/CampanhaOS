"""
Caso de uso: montar o extrato financeiro pra conciliação com o banco.

A ideia central: cada LINHA do extrato é um movimento real de dinheiro,
na data em que ele realmente aconteceu — não a data em que o lançamento
foi cadastrado no sistema. Por isso:
- Receita/doação: uma linha por lançamento, na data do lançamento (não
  têm controle de pagamento parcial, então "lançado" = "aconteceu").
- Despesa: uma linha POR PAGAMENTO registrado, na data daquele
  pagamento — uma despesa paga em 2 vezes gera 2 linhas, em datas
  diferentes, cada uma com o valor daquela parcela. Isso é o que faz o
  extrato bater com o banco de verdade.
- Despesa ainda não totalmente paga NÃO aparece nas linhas principais
  (dinheiro não saiu ainda) — aparece separada, na lista de pendências.
"""

from decimal import Decimal

from src.application.finance.dto import (
    FinanceStatementOutput,
    GetFinanceStatementInput,
    PendingExpenseOutput,
    StatementLineOutput,
)
from src.domain.finance.payment_repository import FinancePaymentRepository
from src.domain.finance.repository import FinanceRepository


class GetFinanceStatementUseCase:
    def __init__(self, finance_repository: FinanceRepository, payment_repository: FinancePaymentRepository) -> None:
        self._finance_repository = finance_repository
        self._payment_repository = payment_repository

    async def execute(self, input_data: GetFinanceStatementInput) -> FinanceStatementOutput:
        receitas_e_doacoes = await self._finance_repository.list_receitas_and_doacoes(
            input_data.tenant_id, input_data.occurred_after, input_data.occurred_before
        )
        payments = await self._payment_repository.list_in_range_with_transaction_info(
            input_data.tenant_id, input_data.occurred_after, input_data.occurred_before
        )
        pending = await self._finance_repository.list_pending_despesas(
            input_data.tenant_id, input_data.occurred_after, input_data.occurred_before
        )

        # Junta os dois tipos de movimento numa lista só, cada um com
        # (data, tipo, categoria, descrição, valor COM SINAL).
        raw_lines: list[tuple] = []
        for transaction in receitas_e_doacoes:
            raw_lines.append(
                (transaction.occurred_at, transaction.type, transaction.category, transaction.description, transaction.amount)
            )
        for item in payments:
            raw_lines.append(
                (item.payment.paid_at, "despesa", item.category, item.description, -item.payment.amount)
            )

        # Ordena por data — é isso que faz o saldo acumulado fazer
        # sentido (precisa processar os movimentos na ordem em que
        # aconteceram de verdade).
        raw_lines.sort(key=lambda line: line[0])

        lines: list[StatementLineOutput] = []
        running_balance = Decimal("0")
        for occurred_date, type_, category, description, signed_amount in raw_lines:
            running_balance += signed_amount
            lines.append(
                StatementLineOutput(
                    date=occurred_date,
                    type=type_,
                    category=category,
                    description=description,
                    amount=signed_amount,
                    running_balance=running_balance,
                )
            )

        pending_expenses = [
            PendingExpenseOutput(
                transaction_id=p.transaction.id,
                occurred_at=p.transaction.occurred_at,
                category=p.transaction.category,
                description=p.transaction.description,
                amount=p.transaction.amount,
                amount_paid=p.amount_paid,
                amount_remaining=p.transaction.amount - p.amount_paid,
            )
            for p in pending
        ]

        return FinanceStatementOutput(lines=lines, pending_expenses=pending_expenses)
