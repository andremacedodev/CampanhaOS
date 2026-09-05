"""adiciona payment_status em finance_transactions

Revision ID: 0023_add_payment_status
Revises: 0022_finance_multi_attach
Create Date: 2026-08-31

Default "pago" pro histórico existente — sem isso, todo lançamento já
cadastrado antes dessa funcionalidade existir apareceria como "pendente"
do nada, o que seria enganoso (a maioria já estava paga de verdade;
"atrasado" é calculado em cima disso, então também afetaria todos).
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0023_add_payment_status"
down_revision: str | None = "0022_finance_multi_attach"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "finance_transactions",
        sa.Column("payment_status", sa.String(20), nullable=False, server_default="pago"),
    )


def downgrade() -> None:
    op.drop_column("finance_transactions", "payment_status")
