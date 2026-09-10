/**
 * Espelha src/presentation/api/v1/schemas/finance.py do backend.
 *
 * IMPORTANTE: `amount` e os campos do resumo vêm como STRING, não
 * number — confirmado pelos testes reais do backend
 * (`assert transaction["amount"] == "1000.00"`, Módulo 6). O Pydantic
 * serializa `Decimal` como string no JSON pra preservar precisão exata
 * — é o mesmo motivo pelo qual usamos Decimal no backend em vez de
 * float (Bloco A do Módulo 6). O frontend NUNCA deve fazer conta com
 * esses valores como número JavaScript (que voltaria a ter o problema
 * de arredondamento que o backend evitou) — só exibe como texto.
 */

export const TRANSACTION_TYPE_OPTIONS = [
  { value: "receita", label: "Receita" },
  { value: "despesa", label: "Despesa" },
  { value: "doacao", label: "Doação" },
] as const;

export const ATTACHMENT_CATEGORY_OPTIONS = [
  { value: "comprovante", label: "Comprovante" },
  { value: "contrato", label: "Contrato" },
  { value: "orcamento", label: "Orçamento" },
  { value: "outro", label: "Outro" },
] as const;

export const MAX_ATTACHMENTS_PER_TRANSACTION = 10;

// Usa effective_payment_status (vem do backend já calculado, nunca
// escolhido manualmente) — pode ser null pra receita/doação (não têm
// controle de pagamento nessa versão).
export const PAYMENT_STATUS_DISPLAY: Record<string, { label: string; className: string }> = {
  pago: { label: "Pago", className: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300" },
  parcial: { label: "Parcial", className: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300" },
  pendente: { label: "Pendente", className: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300" },
  atrasado: { label: "Atrasado", className: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300" },
};

export interface FinanceTransaction {
  id: string;
  created_by_user_id: string;
  type: string;
  category: string;
  amount: string;
  description: string | null;
  occurred_at: string;
  created_at: string;
  updated_at: string;
  // null pra receita/doação — só despesa tem controle de pagamento.
  effective_payment_status: string | null;
  amount_paid: string;
  // String porque é Decimal do backend — pode vir NEGATIVA se pagou
  // mais que o lançado (permitido, sem bloqueio).
  amount_remaining: string;
  attachment_count: number;
}

export interface FinanceAttachment {
  id: string;
  transaction_id: string;
  category: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  uploaded_at: string;
}

export interface FinanceAttachmentListResponse {
  items: FinanceAttachment[];
}

export interface FinanceAttachmentDownloadResponse {
  download_url: string;
  filename: string;
}

export interface FinancePayment {
  id: string;
  transaction_id: string;
  amount: string;
  paid_at: string;
  created_at: string;
}

export interface FinancePaymentListResponse {
  items: FinancePayment[];
}

export interface FinancePaymentCreateRequest {
  amount: string;
  paid_at: string;
}

export interface FinanceSummary {
  total_receitas: string;
  total_despesas: string;
  total_doacoes: string;
  total_pago: string;
  total_a_pagar: string;
  saldo_atual: string;
}

export interface FinanceTransactionListResponse {
  items: FinanceTransaction[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  summary: FinanceSummary;
}

export interface FinanceTransactionFormValues {
  type: string;
  category: string;
  amount: string;
  occurred_at: string;
  description: string;
}

export interface FinanceTransactionCreateRequest {
  type: string;
  category: string;
  amount: string;
  occurred_at: string;
  description?: string | null;
}

export type FinanceTransactionUpdateRequest = Partial<FinanceTransactionCreateRequest>;

export interface FinanceTransactionListParams {
  type?: string;
  category?: string;
  occurred_after?: string;
  occurred_before?: string;
  page?: number;
  page_size?: number;
}

/** Formata um valor Decimal-como-string para exibição em R$, sem passar por número JS. */
export function formatCurrencyFromString(value: string | undefined | null): string {
  // Proteção defensiva — mesmo padrão já usado nos gráficos do painel:
  // evita quebrar a página inteira se esse campo vier undefined (ex:
  // descompasso temporário entre deploy do frontend e do backend).
  if (value === undefined || value === null) return "R$ —";
  const isNegative = value.startsWith("-");
  const unsigned = isNegative ? value.slice(1) : value;
  const [integerPart, decimalPart = "00"] = unsigned.split(".");
  const withThousands = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return `${isNegative ? "-" : ""}R$ ${withThousands},${decimalPart}`;
}

/** Formata bytes em KB/MB legível, pra exibição do tamanho do anexo. */
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}