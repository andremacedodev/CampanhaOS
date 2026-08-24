import { apiClient } from "@/shared/lib/api-client";
import type {
  Vehicle,
  VehicleCreateRequest,
  VehicleListParams,
  VehicleListResponse,
  VehiclePhotoDownloadResponse,
  VehicleUpdateRequest,
} from "@/features/vehicles/api/types";

export async function listVehicles(params: VehicleListParams): Promise<VehicleListResponse> {
  const response = await apiClient.get<VehicleListResponse>("/vehicles", { params });
  return response.data;
}

export async function getVehicle(id: string): Promise<Vehicle> {
  const response = await apiClient.get<Vehicle>(`/vehicles/${id}`);
  return response.data;
}

export async function createVehicle(data: VehicleCreateRequest): Promise<Vehicle> {
  const response = await apiClient.post<Vehicle>("/vehicles", data);
  return response.data;
}

export async function updateVehicle(id: string, data: VehicleUpdateRequest): Promise<Vehicle> {
  const response = await apiClient.patch<Vehicle>(`/vehicles/${id}`, data);
  return response.data;
}

export async function deleteVehicle(id: string): Promise<void> {
  await apiClient.delete(`/vehicles/${id}`);
}

export async function uploadVehiclePhoto(id: string, file: File): Promise<Vehicle> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiClient.post<Vehicle>(`/vehicles/${id}/photo`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function removeVehiclePhoto(id: string): Promise<void> {
  await apiClient.delete(`/vehicles/${id}/photo`);
}

export async function getVehiclePhotoDownloadUrl(id: string): Promise<VehiclePhotoDownloadResponse> {
  const response = await apiClient.get<VehiclePhotoDownloadResponse>(`/vehicles/${id}/photo/download-url`);
  return response.data;
}
