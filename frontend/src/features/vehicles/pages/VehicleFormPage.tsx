import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { getApiErrorMessage } from "@/shared/lib/api-client";
import { VehicleForm } from "@/features/vehicles/components/VehicleForm";
import { VehiclePhotoSection } from "@/features/vehicles/components/VehiclePhotoSection";
import { useCreateVehicle, useUpdateVehicle, useVehicle } from "@/features/vehicles/hooks/use-vehicles";
import type { VehicleFormValues } from "@/features/vehicles/api/types";

export function VehicleFormPage() {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const isEditMode = Boolean(id);

  const { data: existingVehicle, isLoading: isLoadingVehicle } = useVehicle(id);
  const createVehicle = useCreateVehicle();
  const updateVehicle = useUpdateVehicle(id ?? "");
  const [submitError, setSubmitError] = useState<string | null>(null);

  async function handleSubmit(values: VehicleFormValues) {
    setSubmitError(null);

    const payload = {
      plate: values.plate,
      owner_name: values.owner_name,
      stickered_at: values.stickered_at,
      voter_id: values.voter_id || null,
      model: values.model || null,
      city: values.city || null,
    };

    try {
      if (isEditMode) {
        await updateVehicle.mutateAsync(payload);
        navigate("/veiculos");
      } else {
        const created = await createVehicle.mutateAsync(payload);
        // Vai direto pra edição — é ali que aparece a seção de foto
        // (só faz sentido depois do veículo já existir).
        navigate(`/veiculos/${created.id}/editar`);
      }
    } catch (error) {
      setSubmitError(getApiErrorMessage(error));
    }
  }

  if (isEditMode && isLoadingVehicle) {
    return <p className="text-muted-foreground">Carregando veículo...</p>;
  }

  return (
    <div className="mx-auto max-w-lg">
      <Card>
        <CardHeader>
          <CardTitle>{isEditMode ? "Editar Veículo" : "Novo Veículo Adesivado"}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {submitError && (
            <p className="rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
              {submitError}
            </p>
          )}
          <VehicleForm
            initialVehicle={existingVehicle}
            onSubmit={handleSubmit}
            isSubmitting={createVehicle.isPending || updateVehicle.isPending}
            submitLabel={isEditMode ? "Salvar alterações" : "Cadastrar veículo"}
          />
          {isEditMode && existingVehicle && <VehiclePhotoSection vehicle={existingVehicle} />}
        </CardContent>
      </Card>
    </div>
  );
}
