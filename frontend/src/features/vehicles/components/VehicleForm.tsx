import { useState, type FormEvent } from "react";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { VoterPicker } from "@/features/vehicles/components/VoterPicker";
import type { Vehicle, VehicleFormValues } from "@/features/vehicles/api/types";

interface VehicleFormProps {
  initialVehicle?: Vehicle;
  initialVoterName?: string;
  onSubmit: (values: VehicleFormValues) => Promise<void>;
  isSubmitting: boolean;
  submitLabel: string;
}

function todayAsDateInputValue(): string {
  return new Date().toISOString().split("T")[0];
}

function vehicleToFormValues(vehicle: Vehicle | undefined): VehicleFormValues {
  return {
    plate: vehicle?.plate ?? "",
    owner_name: vehicle?.owner_name ?? "",
    stickered_at: vehicle?.stickered_at ?? todayAsDateInputValue(),
    voter_id: vehicle?.voter_id ?? "",
    model: vehicle?.model ?? "",
    city: vehicle?.city ?? "",
  };
}

export function VehicleForm({
  initialVehicle,
  initialVoterName,
  onSubmit,
  isSubmitting,
  submitLabel,
}: VehicleFormProps) {
  const [values, setValues] = useState<VehicleFormValues>(() => vehicleToFormValues(initialVehicle));
  const [selectedVoterName, setSelectedVoterName] = useState(initialVoterName ?? "");
  const [error, setError] = useState<string | null>(null);

  function updateField<K extends keyof VehicleFormValues>(field: K, value: VehicleFormValues[K]) {
    setValues((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    if (!values.plate.trim()) {
      setError("Placa é obrigatória.");
      return;
    }
    if (!values.owner_name.trim()) {
      setError("Nome do proprietário é obrigatório.");
      return;
    }

    await onSubmit(values);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="plate">Placa</Label>
        <Input
          id="plate"
          value={values.plate}
          onChange={(e) => updateField("plate", e.target.value.toUpperCase())}
          placeholder="ABC1234 ou ABC1D23"
          maxLength={8}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="owner_name">Nome do Proprietário</Label>
        <Input
          id="owner_name"
          value={values.owner_name}
          onChange={(e) => updateField("owner_name", e.target.value)}
        />
        <p className="text-xs text-muted-foreground">
          Não precisa ser um eleitor cadastrado — pode ser só o nome da pessoa.
        </p>
      </div>

      <VoterPicker
        selectedVoterId={values.voter_id}
        selectedVoterName={selectedVoterName}
        onSelect={(voterId, voterName) => {
          updateField("voter_id", voterId);
          setSelectedVoterName(voterName);
        }}
        onClear={() => {
          updateField("voter_id", "");
          setSelectedVoterName("");
        }}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="model">Modelo / Cor</Label>
          <Input
            id="model"
            value={values.model}
            onChange={(e) => updateField("model", e.target.value)}
            placeholder="Ex: Onix branco"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="city">Cidade</Label>
          <Input id="city" value={values.city} onChange={(e) => updateField("city", e.target.value)} />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="stickered_at">Data que foi Adesivado</Label>
        <Input
          id="stickered_at"
          type="date"
          value={values.stickered_at}
          onChange={(e) => updateField("stickered_at", e.target.value)}
        />
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}

      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? "Salvando..." : submitLabel}
      </Button>
    </form>
  );
}
