import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  addFinanceAttachment,
  addFinancePayment,
  createFinanceTransaction,
  deleteFinanceTransaction,
  getFinanceAttachmentDownloadUrl,
  getFinanceTransaction,
  listFinanceAttachments,
  listFinancePayments,
  listFinanceTransactions,
  removeFinanceAttachment,
  removeFinancePayment,
  updateFinanceTransaction,
} from "@/features/finance/api/finance-api";
import type {
  FinancePaymentCreateRequest,
  FinanceTransactionCreateRequest,
  FinanceTransactionListParams,
  FinanceTransactionUpdateRequest,
} from "@/features/finance/api/types";

const FINANCE_QUERY_KEY = "finance";

export function useFinanceTransactions(params: FinanceTransactionListParams) {
  return useQuery({
    queryKey: [FINANCE_QUERY_KEY, params],
    queryFn: () => listFinanceTransactions(params),
  });
}

export function useFinanceTransaction(id: string | undefined) {
  return useQuery({
    queryKey: [FINANCE_QUERY_KEY, id],
    queryFn: () => getFinanceTransaction(id as string),
    enabled: Boolean(id),
  });
}

export function useCreateFinanceTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: FinanceTransactionCreateRequest) => createFinanceTransaction(data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [FINANCE_QUERY_KEY] });
    },
  });
}

export function useUpdateFinanceTransaction(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: FinanceTransactionUpdateRequest) => updateFinanceTransaction(id, data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [FINANCE_QUERY_KEY] });
    },
  });
}

export function useDeleteFinanceTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteFinanceTransaction(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [FINANCE_QUERY_KEY] });
    },
  });
}

const FINANCE_ATTACHMENTS_QUERY_KEY = "finance-attachments";

export function useFinanceAttachments(transactionId: string) {
  return useQuery({
    queryKey: [FINANCE_ATTACHMENTS_QUERY_KEY, transactionId],
    queryFn: () => listFinanceAttachments(transactionId),
  });
}

export function useAddFinanceAttachment(transactionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ category, file }: { category: string; file: File }) =>
      addFinanceAttachment(transactionId, category, file),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [FINANCE_ATTACHMENTS_QUERY_KEY, transactionId] });
    },
  });
}

export function useRemoveFinanceAttachment(transactionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (attachmentId: string) => removeFinanceAttachment(transactionId, attachmentId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [FINANCE_ATTACHMENTS_QUERY_KEY, transactionId] });
    },
  });
}

/**
 * Não é um useQuery normal de propósito — o link assinado expira em 15
 * minutos, então gerar um novo a cada clique em "baixar" (em vez de
 * cachear um link que pode já estar vencido) é o comportamento certo
 * aqui.
 */
export function useDownloadFinanceAttachment(transactionId: string) {
  return useMutation({
    mutationFn: (attachmentId: string) => getFinanceAttachmentDownloadUrl(transactionId, attachmentId),
  });
}

const FINANCE_PAYMENTS_QUERY_KEY = "finance-payments";

export function useFinancePayments(transactionId: string) {
  return useQuery({
    queryKey: [FINANCE_PAYMENTS_QUERY_KEY, transactionId],
    queryFn: () => listFinancePayments(transactionId),
  });
}

export function useAddFinancePayment(transactionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: FinancePaymentCreateRequest) => addFinancePayment(transactionId, data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [FINANCE_PAYMENTS_QUERY_KEY, transactionId] });
      // IMPORTANTE: também invalida o cache principal do lançamento —
      // amount_paid/amount_remaining/effective_payment_status vêm
      // JUNTO na consulta da transação, não só na de pagamentos.
      void queryClient.invalidateQueries({ queryKey: [FINANCE_QUERY_KEY] });
    },
  });
}

export function useRemoveFinancePayment(transactionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (paymentId: string) => removeFinancePayment(transactionId, paymentId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [FINANCE_PAYMENTS_QUERY_KEY, transactionId] });
      void queryClient.invalidateQueries({ queryKey: [FINANCE_QUERY_KEY] });
    },
  });
}
