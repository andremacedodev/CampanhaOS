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

// Só 2 opções pra ESCOLHER — "atrasado" nunca é selecionado manualmente,
// é sempre calculado pelo backend (pendente + data já passada).
export const PAYMENT_STATUS_OPTIONS = [
  { value: "pago", label: "Pago" },
  { value: "pendente", label: "Pendente" },
] as const;

// Usa effective_payment_status (vem do backend já calculado) pra exibir
// — nunca payment_status puro, senão "atrasado" nunca apareceria.
export const PAYMENT_STATUS_DISPLAY: Record<string, { label: string; className: string }> = {
  pago: { label: "Pago", className: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300" },
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
  payment_status: string;
  effective_payment_status: string;
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

export interface FinanceSummary {
  total_receitas: string;
  total_despesas: string;
  total_doacoes: string;
  saldo: string;
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
  payment_status: string;
}

export interface FinanceTransactionCreateRequest {
  type: string;
  category: string;
  amount: string;
  occurred_at: string;
  description?: string | null;
  payment_status?: string;
}

export type FinanceTransactionUpdateRequest = Partial<FinanceTransactionCreateRequest>;

export interface FinanceTransactionListParams {
  type?: string;
  category?: string;
  occurred_after?: string;
  occurred_before?: string;
  payment_status?: string;
  page?: number;
  page_size?: number;
}

/** Formata um valor Decimal-como-string para exibição em R$, sem passar por número JS. */
export function formatCurrencyFromString(value: string): string {
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
