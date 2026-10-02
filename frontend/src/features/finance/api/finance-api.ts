import { apiClient } from "@/shared/lib/api-client";
import type {
  FinanceAttachment,
  FinanceAttachmentDownloadResponse,
  FinanceAttachmentListResponse,
  FinancePayment,
  FinancePaymentCreateRequest,
  FinancePaymentListResponse,
  FinanceTransaction,
  FinanceTransactionCreateRequest,
  FinanceTransactionListParams,
  FinanceTransactionListResponse,
  FinanceTransactionUpdateRequest,
} from "@/features/finance/api/types";

export async function listFinanceTransactions(
  params: FinanceTransactionListParams,
): Promise<FinanceTransactionListResponse> {
  const response = await apiClient.get<FinanceTransactionListResponse>("/finance", { params });
  return response.data;
}

export async function getFinanceTransaction(id: string): Promise<FinanceTransaction> {
  const response = await apiClient.get<FinanceTransaction>(`/finance/${id}`);
  return response.data;
}

export async function createFinanceTransaction(data: FinanceTransactionCreateRequest): Promise<FinanceTransaction> {
  const response = await apiClient.post<FinanceTransaction>("/finance", data);
  return response.data;
}

export async function updateFinanceTransaction(
  id: string,
  data: FinanceTransactionUpdateRequest,
): Promise<FinanceTransaction> {
  const response = await apiClient.patch<FinanceTransaction>(`/finance/${id}`, data);
  return response.data;
}

export async function deleteFinanceTransaction(id: string): Promise<void> {
  await apiClient.delete(`/finance/${id}`);
}

export async function addFinanceAttachment(
  transactionId: string,
  category: string,
  file: File,
): Promise<FinanceAttachment> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiClient.post<FinanceAttachment>(
    `/finance/${transactionId}/attachments`,
    formData,
    { params: { category }, headers: { "Content-Type": "multipart/form-data" } },
  );
  return response.data;
}

export async function listFinanceAttachments(transactionId: string): Promise<FinanceAttachmentListResponse> {
  const response = await apiClient.get<FinanceAttachmentListResponse>(`/finance/${transactionId}/attachments`);
  return response.data;
}

export async function removeFinanceAttachment(transactionId: string, attachmentId: string): Promise<void> {
  await apiClient.delete(`/finance/${transactionId}/attachments/${attachmentId}`);
}

export async function getFinanceAttachmentDownloadUrl(
  transactionId: string,
  attachmentId: string,
): Promise<FinanceAttachmentDownloadResponse> {
  const response = await apiClient.get<FinanceAttachmentDownloadResponse>(
    `/finance/${transactionId}/attachments/${attachmentId}/download-url`,
  );
  return response.data;
}

export async function addFinancePayment(
  transactionId: string,
  data: FinancePaymentCreateRequest,
): Promise<FinancePayment> {
  const response = await apiClient.post<FinancePayment>(`/finance/${transactionId}/payments`, data);
  return response.data;
}

export async function listFinancePayments(transactionId: string): Promise<FinancePaymentListResponse> {
  const response = await apiClient.get<FinancePaymentListResponse>(`/finance/${transactionId}/payments`);
  return response.data;
}

export async function removeFinancePayment(transactionId: string, paymentId: string): Promise<void> {
  await apiClient.delete(`/finance/${transactionId}/payments/${paymentId}`);
}

export async function downloadFinanceStatementExcel(params: {
  occurred_after?: string;
  occurred_before?: string;
}): Promise<void> {
  const response = await apiClient.get("/finance/statement/excel", {
    params,
    responseType: "blob",
  });

  // Fluxo padrão pra "forçar download" de um arquivo que já veio pronto
  // na resposta: cria uma URL temporária só pro navegador, simula um
  // clique num link invisível apontando pra ela, e descarta a URL
  // logo em seguida (ela só existe na memória do navegador, não é um
  // link de verdade pra lugar nenhum).
  const blob = new Blob([response.data], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "extrato_financeiro.xlsx";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
