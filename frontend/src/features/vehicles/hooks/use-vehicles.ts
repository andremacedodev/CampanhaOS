import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createVehicle,
  deleteVehicle,
  getVehicle,
  getVehiclePhotoDownloadUrl,
  listVehicles,
  removeVehiclePhoto,
  updateVehicle,
  uploadVehiclePhoto,
} from "@/features/vehicles/api/vehicles-api";
import type { VehicleCreateRequest, VehicleListParams, VehicleUpdateRequest } from "@/features/vehicles/api/types";

const VEHICLES_QUERY_KEY = "vehicles";

export function useVehicles(params: VehicleListParams) {
  return useQuery({
    queryKey: [VEHICLES_QUERY_KEY, params],
    queryFn: () => listVehicles(params),
  });
}

export function useVehicle(id: string | undefined) {
  return useQuery({
    queryKey: [VEHICLES_QUERY_KEY, id],
    queryFn: () => getVehicle(id as string),
    enabled: Boolean(id),
  });
}

export function useCreateVehicle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: VehicleCreateRequest) => createVehicle(data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [VEHICLES_QUERY_KEY] });
    },
  });
}

export function useUpdateVehicle(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: VehicleUpdateRequest) => updateVehicle(id, data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [VEHICLES_QUERY_KEY] });
    },
  });
}

export function useDeleteVehicle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteVehicle(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [VEHICLES_QUERY_KEY] });
    },
  });
}

export function useUploadVehiclePhoto(vehicleId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => uploadVehiclePhoto(vehicleId, file),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [VEHICLES_QUERY_KEY] });
    },
  });
}

export function useRemoveVehiclePhoto(vehicleId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => removeVehiclePhoto(vehicleId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [VEHICLES_QUERY_KEY] });
    },
  });
}

/** Não é useQuery de propósito — o link assinado expira em 15min, gera um novo a cada clique. */
export function useDownloadVehiclePhoto() {
  return useMutation({
    mutationFn: (vehicleId: string) => getVehiclePhotoDownloadUrl(vehicleId),
  });
}
