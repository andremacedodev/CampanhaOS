import { Fragment, useState } from "react";
import { Link } from "react-router-dom";
import { ChevronDown, ChevronRight } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Select } from "@/shared/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { useDeleteFinanceTransaction, useFinanceTransactions } from "@/features/finance/hooks/use-finance";
import {
  PAYMENT_STATUS_DISPLAY,
  TRANSACTION_TYPE_OPTIONS,
  formatCurrencyFromString,
} from "@/features/finance/api/types";

const PAGE_SIZE = 20;

/**
 * `occurred_at` é uma data SEM hora (ex: "2026-08-18") — passar essa
 * string direto pro construtor `new Date(...)` faz o JavaScript
 * interpretar como meia-noite em UTC, e `.toLocaleDateString()` depois
 * mostra isso no fuso LOCAL do navegador. Como o Brasil fica atrás do
 * UTC, meia-noite UTC de um dia vira noite do dia ANTERIOR aqui — a
 * data "volta" um dia na tela, mesmo estando correta no banco.
 *
 * Construir a data com ano/mês/dia separados (em vez de string ISO)
 * evita isso — esse construtor usa hora LOCAL diretamente, sem passar
 * por UTC no meio do caminho.
 */
function formatDate(iso: string): string {
  const [year, month, day] = iso.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("pt-BR");
}

export function FinanceTransactionsListPage() {
  const [typeFilter, setTypeFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data, isLoading, isError } = useFinanceTransactions({
    type: typeFilter || undefined,
    payment_status: statusFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });
  const deleteTransaction = useDeleteFinanceTransaction();

  async function handleDelete(id: string, category: string) {
    if (window.confirm(`Excluir o lançamento "${category}"? Esta ação não pode ser desfeita.`)) {
      await deleteTransaction.mutateAsync(id);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Financeiro</h1>
        <Button asChild>
          <Link to="/financeiro/novo">Novo Lançamento</Link>
        </Button>
      </div>

      {/*
        Aviso de compliance (ADR-010, documento fonte da verdade): este
        módulo é controle INTERNO — não substitui a prestação de contas
        oficial ao TSE, que é feita via Conta+JE.
      */}
      <p className="rounded-md border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-700 dark:text-amber-400">
        Este módulo é controle financeiro interno da campanha. A prestação de contas oficial ao TSE continua
        sendo feita separadamente, pelo sistema Conta+JE.
      </p>

      {data && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Despesas Lançadas</CardTitle>
            </CardHeader>
            <CardContent className="text-xl font-semibold text-destructive">
              {formatCurrencyFromString(data.summary.total_despesas)}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Pago</CardTitle>
            </CardHeader>
            <CardContent className="text-xl font-semibold text-emerald-600">
              {formatCurrencyFromString(data.summary.total_pago)}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total a Pagar</CardTitle>
            </CardHeader>
            <CardContent className="text-xl font-semibold text-amber-600">
              {formatCurrencyFromString(data.summary.total_a_pagar)}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Saldo Atual</CardTitle>
            </CardHeader>
            <CardContent className="text-xl font-semibold">
              {formatCurrencyFromString(data.summary.saldo_atual)}
            </CardContent>
          </Card>
        </div>
      )}

      <div className="flex flex-col gap-3 sm:flex-row">
        <Select
          value={typeFilter}
          onChange={(e) => {
            const newType = e.target.value;
            setTypeFilter(newType);
            // Mesma proteção do caminho inverso: se um status estava
            // ativo e o tipo mudou pra algo diferente de despesa, o
            // status não faz mais sentido (só existe pra despesa).
            if (statusFilter && newType !== "despesa") {
              setStatusFilter("");
            }
            setPage(1);
          }}
          className="max-w-xs"
        >
          <option value="">Todos os tipos</option>
          {TRANSACTION_TYPE_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>

        <Select
          value={statusFilter}
          onChange={(e) => {
            const newStatus = e.target.value;
            setStatusFilter(newStatus);
            // Status só existe pra despesa — escolher um status
            // trava o tipo em "despesa" automaticamente, evitando a
            // combinação contraditória "tipo=receita + status=pago"
            // (que voltaria sempre vazia, sem essa proteção).
            if (newStatus) {
              setTypeFilter("despesa");
            }
            setPage(1);
          }}
          className="max-w-xs"
        >
          <option value="">Todos os status</option>
          <option value="pago">Pago</option>
          <option value="parcial">Parcial</option>
          <option value="pendente">Pendente</option>
          <option value="atrasado">Atrasado</option>
        </Select>
      </div>
      {statusFilter && (
        <p className="text-xs text-muted-foreground">
          Esse filtro só se aplica a despesas — o tipo foi ajustado automaticamente.
        </p>
      )}

      {isLoading && <p className="text-muted-foreground">Carregando...</p>}
      {isError && <p className="text-destructive">Não foi possível carregar os lançamentos.</p>}

      {data && (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-8"></TableHead>
                <TableHead>Data</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead className="text-right">Valor</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Anexos</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.items.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground">
                    Nenhum lançamento encontrado.
                  </TableCell>
                </TableRow>
              )}
              {data.items.map((transaction) => {
                const statusDisplay = transaction.effective_payment_status
                  ? PAYMENT_STATUS_DISPLAY[transaction.effective_payment_status]
                  : null;
                const isExpanded = expandedId === transaction.id;
                // Só vale a pena expandir se tiver algo a mais pra
                // mostrar — sem descrição e sem controle de pagamento
                // (receita/doação), a linha expandida ficaria vazia.
                const hasExtraInfo = Boolean(transaction.description) || transaction.type === "despesa";

                return (
                  <Fragment key={transaction.id}>
                    <TableRow
                      onClick={() => hasExtraInfo && setExpandedId(isExpanded ? null : transaction.id)}
                      className={hasExtraInfo ? "cursor-pointer hover:bg-accent/50" : undefined}
                    >
                      <TableCell>
                        {hasExtraInfo &&
                          (isExpanded ? (
                            <ChevronDown className="h-4 w-4 text-muted-foreground" />
                          ) : (
                            <ChevronRight className="h-4 w-4 text-muted-foreground" />
                          ))}
                      </TableCell>
                      <TableCell>{formatDate(transaction.occurred_at)}</TableCell>
                      <TableCell className="capitalize">{transaction.type}</TableCell>
                      <TableCell className="font-medium">{transaction.category}</TableCell>
                      <TableCell className="text-right">{formatCurrencyFromString(transaction.amount)}</TableCell>
                      <TableCell>
                        {statusDisplay ? (
                          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusDisplay.className}`}>
                            {statusDisplay.label}
                          </span>
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {transaction.attachment_count > 0 ? `📎 ${transaction.attachment_count}` : "—"}
                      </TableCell>
                      <TableCell className="space-x-2 text-right" onClick={(e) => e.stopPropagation()}>
                        <Button variant="outline" size="sm" asChild>
                          <Link to={`/financeiro/${transaction.id}/editar`}>Editar</Link>
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDelete(transaction.id, transaction.category)}
                          disabled={deleteTransaction.isPending}
                        >
                          Excluir
                        </Button>
                      </TableCell>
                    </TableRow>
                    {isExpanded && (
                      <TableRow>
                        <TableCell colSpan={8} className="bg-muted/30 py-3">
                          <div className="space-y-2 pl-8 text-sm">
                            {transaction.description && (
                              <p>
                                <span className="font-medium text-muted-foreground">Descrição: </span>
                                {transaction.description}
                              </p>
                            )}
                            {transaction.type === "despesa" && (
                              <p className="flex flex-wrap gap-x-4 text-muted-foreground">
                                <span>
                                  Pago: <span className="font-medium text-emerald-600">{formatCurrencyFromString(transaction.amount_paid)}</span>
                                </span>
                                <span>
                                  {transaction.amount_remaining?.startsWith("-") ? "Pago a mais" : "Falta pagar"}:{" "}
                                  <span className="font-medium">
                                    {formatCurrencyFromString(
                                      transaction.amount_remaining?.startsWith("-")
                                        ? transaction.amount_remaining.slice(1)
                                        : transaction.amount_remaining,
                                    )}
                                  </span>
                                </span>
                              </p>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    )}
                  </Fragment>
                );
              })}
            </TableBody>
          </Table>

          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              Página {data.page} de {Math.max(data.total_pages, 1)} — {data.total} lançamento(s)
            </span>
            <div className="space-x-2">
              <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.max(p - 1, 1))} disabled={page <= 1}>
                Anterior
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= data.total_pages}
              >
                Próxima
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
