import { useState, type FormEvent } from "react";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import {
  PAYMENT_STATUS_DISPLAY,
  formatCurrencyFromString,
  type FinanceTransaction,
} from "@/features/finance/api/types";
import { getApiErrorMessage } from "@/shared/lib/api-client";
import {
  useAddFinancePayment,
  useFinancePayments,
  useRemoveFinancePayment,
} from "@/features/finance/hooks/use-finance";

interface FinancePaymentSectionProps {
  transaction: FinanceTransaction;
}

function todayAsDateInputValue(): string {
  return new Date().toISOString().split("T")[0];
}

/**
 * Mesma proteção contra o bug de fuso horário já documentado em
 * FinanceTransactionsListPage.tsx — construir a data com ano/mês/dia
 * separados evita passar por UTC no meio do caminho.
 */
function formatPaymentDate(iso: string): string {
  const [year, month, day] = iso.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("pt-BR");
}

/**
 * Só renderiza pra DESPESA — receita/doação não têm esse controle
 * nessa versão (decisão explícita de escopo). `FinanceTransactionFormPage`
 * já garante isso antes de renderizar este componente, mas confere de
 * novo aqui por segurança (defesa em profundidade — evita chamar as
 * APIs de pagamento por engano se algo mudar lá em cima no futuro).
 */
export function FinancePaymentSection({ transaction }: FinancePaymentSectionProps) {
  const [amount, setAmount] = useState("");
  const [paidAt, setPaidAt] = useState(todayAsDateInputValue());
  const [error, setError] = useState<string | null>(null);

  const { data } = useFinancePayments(transaction.id);
  const addPayment = useAddFinancePayment(transaction.id);
  const removePayment = useRemoveFinancePayment(transaction.id);

  if (transaction.type !== "despesa") {
    return null;
  }

  const payments = data?.items ?? [];
  const statusDisplay = transaction.effective_payment_status
    ? PAYMENT_STATUS_DISPLAY[transaction.effective_payment_status]
    : null;

  async function handleAddPayment(event: FormEvent) {
    event.preventDefault();
    setError(null);

    if (!/^\d+(\.\d{1,2})?$/.test(amount) || Number(amount) <= 0) {
      setError("Valor precisa ser um número positivo, com até 2 casas decimais (ex: 500.00).");
      return;
    }

    try {
      await addPayment.mutateAsync({ amount, paid_at: paidAt });
      setAmount("");
      setPaidAt(todayAsDateInputValue());
    } catch (err) {
      setError(getApiErrorMessage(err));
    }
  }

  async function handleRemove(paymentId: string) {
    if (!window.confirm("Remover este pagamento?")) return;
    await removePayment.mutateAsync(paymentId);
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">Controle de Pagamento</p>
        {statusDisplay && (
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusDisplay.className}`}>
            {statusDisplay.label}
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3 rounded-md border border-border p-3 text-sm">
        <div>
          <p className="text-xs text-muted-foreground">Valor Total</p>
          <p className="font-medium">{formatCurrencyFromString(transaction.amount)}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Já Pago</p>
          <p className="font-medium text-emerald-600">{formatCurrencyFromString(transaction.amount_paid)}</p>
        </div>
        <div className="col-span-2">
          {/* Proteção defensiva contra amount_remaining vindo undefined
              (mesmo padrão já usado nos gráficos do painel) — calcula
              uma vez só em vez de checar .startsWith duas vezes. */}
          {(() => {
            const isOverpaid = (transaction.amount_remaining ?? "").startsWith("-");
            const displayValue = isOverpaid
              ? transaction.amount_remaining?.slice(1)
              : transaction.amount_remaining;
            return (
              <>
                <p className="text-xs text-muted-foreground">{isOverpaid ? "Pago a Mais" : "Falta Pagar"}</p>
                <p className="font-medium">{formatCurrencyFromString(displayValue)}</p>
              </>
            );
          })()}
        </div>
      </div>

      {payments.length > 0 && (
        <div className="space-y-2">
          {payments.map((payment) => (
            <div key={payment.id} className="flex items-center justify-between rounded-md border border-border p-2">
              <div>
                <p className="text-sm font-medium">{formatCurrencyFromString(payment.amount)}</p>
                <p className="text-xs text-muted-foreground">{formatPaymentDate(payment.paid_at)}</p>
              </div>
              <Button
                type="button"
                variant="destructive"
                size="sm"
                onClick={() => handleRemove(payment.id)}
                disabled={removePayment.isPending}
              >
                Remover
              </Button>
            </div>
          ))}
        </div>
      )}

      <form onSubmit={handleAddPayment} className="space-y-2 rounded-md border border-dashed border-border p-3">
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <Label htmlFor="payment_amount">Valor Pago (R$)</Label>
            <Input
              id="payment_amount"
              type="text"
              inputMode="decimal"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="500.00"
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="payment_date">Data do Pagamento</Label>
            <Input id="payment_date" type="date" value={paidAt} onChange={(e) => setPaidAt(e.target.value)} />
          </div>
        </div>
        {error && <p className="text-xs text-destructive">{error}</p>}
        <Button type="submit" size="sm" disabled={addPayment.isPending} className="w-full">
          {addPayment.isPending ? "Registrando..." : "Registrar Pagamento"}
        </Button>
      </form>
    </div>
  );
}
