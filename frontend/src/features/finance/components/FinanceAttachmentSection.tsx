import { useRef, useState, type ChangeEvent } from "react";
import { Button } from "@/shared/components/ui/button";
import { Select } from "@/shared/components/ui/select";
import {
  ATTACHMENT_CATEGORY_OPTIONS,
  formatFileSize,
  MAX_ATTACHMENTS_PER_TRANSACTION,
  type FinanceAttachment,
  type FinanceTransaction,
} from "@/features/finance/api/types";
import { getApiErrorMessage } from "@/shared/lib/api-client";
import {
  useAddFinanceAttachment,
  useDownloadFinanceAttachment,
  useFinanceAttachments,
  useRemoveFinanceAttachment,
} from "@/features/finance/hooks/use-finance";

interface FinanceAttachmentSectionProps {
  transaction: FinanceTransaction;
}

function categoryLabel(value: string): string {
  return ATTACHMENT_CATEGORY_OPTIONS.find((opt) => opt.value === value)?.label ?? value;
}

export function FinanceAttachmentSection({ transaction }: FinanceAttachmentSectionProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [category, setCategory] = useState<string>(ATTACHMENT_CATEGORY_OPTIONS[0].value);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const { data, isLoading } = useFinanceAttachments(transaction.id);
  const add = useAddFinanceAttachment(transaction.id);
  const remove = useRemoveFinanceAttachment(transaction.id);
  const download = useDownloadFinanceAttachment(transaction.id);

  const attachments = data?.items ?? [];
  const atLimit = attachments.length >= MAX_ATTACHMENTS_PER_TRANSACTION;

  async function handleFileSelected(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploadError(null);

    try {
      await add.mutateAsync({ category, file });
    } catch (error) {
      setUploadError(getApiErrorMessage(error));
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleDownload(attachmentId: string) {
    // Abre a aba ANTES de esperar a URL — precisa ser síncrono, dentro
    // do próprio clique, senão navegadores de celular tratam como
    // pop-up bloqueado e não abrem nada.
    const newTab = window.open("", "_blank", "noopener,noreferrer");
    const result = await download.mutateAsync(attachmentId);
    if (newTab) {
      newTab.location.href = result.download_url;
    } else {
      window.location.href = result.download_url;
    }
  }

  async function handleRemove(attachmentId: string, filename: string) {
    if (!window.confirm(`Remover o anexo "${filename}"?`)) return;
    await remove.mutateAsync(attachmentId);
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">Documentos Anexados</p>
        <span className="text-xs text-muted-foreground">
          {attachments.length}/{MAX_ATTACHMENTS_PER_TRANSACTION}
        </span>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Carregando...</p>}

      {attachments.length > 0 && (
        <div className="space-y-2">
          {attachments.map((attachment) => (
            <AttachmentRow
              key={attachment.id}
              attachment={attachment}
              onDownload={() => handleDownload(attachment.id)}
              onRemove={() => handleRemove(attachment.id, attachment.filename)}
              isDownloading={download.isPending}
              isRemoving={remove.isPending}
            />
          ))}
        </div>
      )}

      {atLimit ? (
        <p className="rounded-md border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-700 dark:text-amber-400">
          Limite de {MAX_ATTACHMENTS_PER_TRANSACTION} documentos atingido — remove algum pra anexar outro.
        </p>
      ) : (
        <div className="space-y-2 rounded-md border border-dashed border-border p-3">
          <div className="flex flex-col gap-2 sm:flex-row">
            <Select value={category} onChange={(e) => setCategory(e.target.value)} className="sm:w-40">
              {ATTACHMENT_CATEGORY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </Select>
            <input
              ref={fileInputRef}
              type="file"
              accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf"
              onChange={handleFileSelected}
              disabled={add.isPending}
              className="block flex-1 text-sm text-muted-foreground file:mr-3 file:rounded-md file:border-0 file:bg-primary file:px-3 file:py-2 file:text-sm file:font-medium file:text-primary-foreground hover:file:opacity-90"
            />
          </div>
          <p className="text-xs text-muted-foreground">
            Escolhe a categoria (comprovante, contrato, orçamento) e o arquivo — JPEG, PNG ou PDF, até 10MB.
          </p>
          {add.isPending && <p className="text-xs text-muted-foreground">Enviando...</p>}
          {uploadError && <p className="text-xs text-destructive">{uploadError}</p>}
        </div>
      )}
    </div>
  );
}

interface AttachmentRowProps {
  attachment: FinanceAttachment;
  onDownload: () => void;
  onRemove: () => void;
  isDownloading: boolean;
  isRemoving: boolean;
}

function AttachmentRow({ attachment, onDownload, onRemove, isDownloading, isRemoving }: AttachmentRowProps) {
  return (
    <div className="flex items-center justify-between rounded-md border border-border p-3">
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-[11px] text-muted-foreground">
            {categoryLabel(attachment.category)}
          </span>
          <p className="truncate text-sm">{attachment.filename}</p>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">{formatFileSize(attachment.size_bytes)}</p>
      </div>
      <div className="flex shrink-0 gap-2">
        <Button type="button" variant="outline" size="sm" onClick={onDownload} disabled={isDownloading}>
          Ver
        </Button>
        <Button type="button" variant="destructive" size="sm" onClick={onRemove} disabled={isRemoving}>
          Remover
        </Button>
      </div>
    </div>
  );
}
