import { useState } from "react";
import { useVoters } from "@/features/voters/hooks/use-voters";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";

interface VoterPickerProps {
  selectedVoterId: string;
  selectedVoterName: string;
  onSelect: (voterId: string, voterName: string) => void;
  onClear: () => void;
}

/**
 * Busca simples por nome, com lista de resultados — não é um componente
 * reutilizável sofisticado de propósito, é o suficiente pra esse caso de
 * uso específico (vincular opcionalmente um eleitor já cadastrado a um
 * veículo). Se um dia precisar disso em mais telas, vale extrair pra um
 * componente compartilhado de verdade.
 */
export function VoterPicker({ selectedVoterId, selectedVoterName, onSelect, onClear }: VoterPickerProps) {
  const [searchText, setSearchText] = useState("");
  const { data } = useVoters({ search: searchText || undefined, page: 1, page_size: 5 });

  if (selectedVoterId) {
    return (
      <div className="space-y-2">
        <Label>Eleitor Vinculado</Label>
        <div className="flex items-center justify-between rounded-md border border-border p-2 text-sm">
          <span>{selectedVoterName}</span>
          <button type="button" onClick={onClear} className="text-xs text-muted-foreground underline">
            remover vínculo
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <Label htmlFor="voter-search">Vincular a um Eleitor (opcional)</Label>
      <Input
        id="voter-search"
        placeholder="Buscar por nome..."
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
      />
      {searchText && data && data.items.length > 0 && (
        <div className="rounded-md border border-border">
          {data.items.map((voter) => (
            <button
              key={voter.id}
              type="button"
              onClick={() => {
                onSelect(voter.id, voter.name);
                setSearchText("");
              }}
              className="block w-full px-3 py-2 text-left text-sm hover:bg-accent"
            >
              {voter.name}
              {voter.phone && <span className="ml-2 text-xs text-muted-foreground">{voter.phone}</span>}
            </button>
          ))}
        </div>
      )}
      {searchText && data && data.items.length === 0 && (
        <p className="text-xs text-muted-foreground">Nenhum eleitor encontrado — pode deixar sem vínculo.</p>
      )}
    </div>
  );
}
