export interface Vehicle {
  id: string;
  created_by_user_id: string;
  plate: string;
  owner_name: string;
  voter_id: string | null;
  model: string | null;
  city: string | null;
  stickered_at: string;
  created_at: string;
  updated_at: string;
  photo_filename: string | null;
  photo_content_type: string | null;
  photo_size_bytes: number | null;
}

export interface VehicleListResponse {
  items: Vehicle[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface VehicleListParams {
  search?: string;
  page: number;
  page_size: number;
}

export interface VehicleCreateRequest {
  plate: string;
  owner_name: string;
  stickered_at: string;
  voter_id?: string | null;
  model?: string | null;
  city?: string | null;
}

export type VehicleUpdateRequest = Partial<VehicleCreateRequest>;

export interface VehiclePhotoDownloadResponse {
  download_url: string;
  filename: string;
}

export interface VehicleFormValues {
  plate: string;
  owner_name: string;
  stickered_at: string;
  voter_id: string;
  model: string;
  city: string;
}

/** Formata bytes em KB/MB legível — mesma lógica já usada no financeiro. */
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}