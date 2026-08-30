import { apiClient } from "@/shared/lib/api-client";
import type {
  FinanceAttachment,
  FinanceAttachmentDownloadResponse,
  FinanceAttachmentListResponse,
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
