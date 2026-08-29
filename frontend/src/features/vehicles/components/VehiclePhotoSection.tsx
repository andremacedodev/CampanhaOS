import { useRef, useState, type ChangeEvent } from "react";
import { Button } from "@/shared/components/ui/button";
import { formatFileSize, type Vehicle } from "@/features/vehicles/api/types";
import { getApiErrorMessage } from "@/shared/lib/api-client";
import {
  useDownloadVehiclePhoto,
  useRemoveVehiclePhoto,
  useUploadVehiclePhoto,
} from "@/features/vehicles/hooks/use-vehicles";

interface VehiclePhotoSectionProps {
  vehicle: Vehicle;
}

export function VehiclePhotoSection({ vehicle }: VehiclePhotoSectionProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const upload = useUploadVehiclePhoto(vehicle.id);
  const remove = useRemoveVehiclePhoto(vehicle.id);
  const download = useDownloadVehiclePhoto();

  async function handleFileSelected(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploadError(null);

    try {
      await upload.mutateAsync(file);
    } catch (error) {
      setUploadError(getApiErrorMessage(error));
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleDownload() {
    const newTab = window.open("", "_blank", "noopener,noreferrer");
    const result = await download.mutateAsync(vehicle.id);
    if (newTab) {
      newTab.location.href = result.download_url;
    } else {
      window.location.href = result.download_url;
    }
  }

  async function handleRemove() {
    if (!window.confirm("Remover a foto deste veículo?")) return;
    await remove.mutateAsync();
  }

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium">Foto do Veículo Adesivado</p>

      {vehicle.photo_filename ? (
        <div className="flex items-center justify-between rounded-md border border-border p-3">
          <div className="min-w-0">
            <p className="truncate text-sm">{vehicle.photo_filename}</p>
            {vehicle.photo_size_bytes !== null && (
              <p className="text-xs text-muted-foreground">
                {formatFileSize(vehicle.photo_size_bytes)}
              </p>
            )}
          </div>
          <div className="flex shrink-0 gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleDownload}
              disabled={download.isPending}
            >
              Ver
            </Button>
            <Button
              type="button"
              variant="destructive"
              size="sm"
              onClick={handleRemove}
              disabled={remove.isPending}
            >
              Remover
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".jpg,.jpeg,.png,image/jpeg,image/png"
            onChange={handleFileSelected}
            disabled={upload.isPending}
            className="block w-full text-sm text-muted-foreground file:mr-3 file:rounded-md file:border-0 file:bg-primary file:px-3 file:py-2 file:text-sm file:font-medium file:text-primary-foreground hover:file:opacity-90"
          />
          <p className="text-xs text-muted-foreground">
            JPEG ou PNG — até 10MB (opcional).
          </p>
          {upload.isPending && (
            <p className="text-xs text-muted-foreground">Enviando...</p>
          )}
          {uploadError && (
            <p className="text-xs text-destructive">{uploadError}</p>
          )}
        </div>
      )}
    </div>
  );
}
