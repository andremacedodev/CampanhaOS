import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { useDeleteVehicle, useVehicles } from "@/features/vehicles/hooks/use-vehicles";
import type { Vehicle } from "@/features/vehicles/api/types";

const PAGE_SIZE = 20;

export function VehiclesListPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading, isError } = useVehicles({ search: search || undefined, page, page_size: PAGE_SIZE });
  const deleteVehicle = useDeleteVehicle();

  async function handleDelete(id: string, plate: string) {
    if (window.confirm(`Excluir o veículo de placa "${plate}"? Esta ação não pode ser desfeita.`)) {
      await deleteVehicle.mutateAsync(id);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-semibold">Veículos Adesivados</h1>
        <Button asChild>
          <Link to="/veiculos/novo">Novo Veículo</Link>
        </Button>
      </div>

      <Input
        placeholder="Buscar por placa, proprietário ou modelo..."
        value={search}
        onChange={(e) => {
          setSearch(e.target.value);
          setPage(1);
        }}
        className="max-w-sm"
      />

      {isLoading && <p className="text-muted-foreground">Carregando...</p>}
      {isError && <p className="text-destructive">Não foi possível carregar os veículos.</p>}

      {data && (
        <>
          {data.items.length === 0 && (
            <p className="py-8 text-center text-muted-foreground">Nenhum veículo encontrado.</p>
          )}

          {data.items.length > 0 && (
            <div className="hidden md:block">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Placa</TableHead>
                    <TableHead>Proprietário</TableHead>
                    <TableHead>Modelo</TableHead>
                    <TableHead>Cidade</TableHead>
                    <TableHead className="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.items.map((vehicle) => (
                    <TableRow key={vehicle.id}>
                      <TableCell className="font-mono font-medium">{vehicle.plate}</TableCell>
                      <TableCell>{vehicle.owner_name}</TableCell>
                      <TableCell>{vehicle.model ?? "—"}</TableCell>
                      <TableCell>{vehicle.city ?? "—"}</TableCell>
                      <TableCell className="space-x-2 text-right">
                        <Button variant="outline" size="sm" asChild>
                          <Link to={`/veiculos/${vehicle.id}/editar`}>Editar</Link>
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDelete(vehicle.id, vehicle.plate)}
                          disabled={deleteVehicle.isPending}
                        >
                          Excluir
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}

          <div className="space-y-3 md:hidden">
            {data.items.map((vehicle) => (
              <VehicleCard
                key={vehicle.id}
                vehicle={vehicle}
                onDelete={() => handleDelete(vehicle.id, vehicle.plate)}
                isDeleting={deleteVehicle.isPending}
              />
            ))}
          </div>

          <div className="flex flex-col gap-3 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
            <span>
              Página {data.page} de {Math.max(data.total_pages, 1)} — {data.total} veículo(s)
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
                disabled={page <= 1}
              >
                Anterior
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= data.total_pages}
              >
                Próxima
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

interface VehicleCardProps {
  vehicle: Vehicle;
  onDelete: () => void;
  isDeleting: boolean;
}

function VehicleCard({ vehicle, onDelete, isDeleting }: VehicleCardProps) {
  return (
    <div className="rounded-lg border border-border p-4">
      <p className="font-mono font-medium">{vehicle.plate}</p>
      <p className="mt-1 text-sm text-muted-foreground">{vehicle.owner_name}</p>
      {(vehicle.model || vehicle.city) && (
        <p className="mt-1 text-xs text-muted-foreground">
          {[vehicle.model, vehicle.city].filter(Boolean).join(" · ")}
        </p>
      )}
      <div className="mt-3 flex gap-2">
        <Button variant="outline" size="sm" asChild className="flex-1">
          <Link to={`/veiculos/${vehicle.id}/editar`}>Editar</Link>
        </Button>
        <Button variant="destructive" size="sm" onClick={onDelete} disabled={isDeleting} className="flex-1">
          Excluir
        </Button>
      </div>
    </div>
  );
}
