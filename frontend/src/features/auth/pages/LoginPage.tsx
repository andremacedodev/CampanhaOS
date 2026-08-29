import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { useAuth } from "@/features/auth/context/AuthContext";
import { getApiErrorMessage } from "@/shared/lib/api-client";

// Só o ID da campanha (não é dado sensível tipo senha) — guardar no
// localStorage do navegador é seguro e resolve o incômodo de ter que
// copiar/colar o UUID toda vez que loga. Fica só neste navegador, nunca
// é enviado pra lugar nenhum sozinho.
const LAST_TENANT_ID_STORAGE_KEY = "campanhaos_last_tenant_id";

export function LoginPage() {
  const { user, isLoading, login } = useAuth();
  const navigate = useNavigate();

  const [tenantId, setTenantId] = useState(() => localStorage.getItem(LAST_TENANT_ID_STORAGE_KEY) ?? "");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Já autenticado (ex: sessão restaurada do sessionStorage) — não faz
  // sentido mostrar o formulário de login de novo.
  if (!isLoading && user) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(tenantId, email, password);
      // Login deu certo -> lembra esse ID pra próxima vez, evita ter
      // que copiar/colar de novo.
      localStorage.setItem(LAST_TENANT_ID_STORAGE_KEY, tenantId);
      navigate("/", { replace: true });
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleForgetTenant() {
    localStorage.removeItem(LAST_TENANT_ID_STORAGE_KEY);
    setTenantId("");
  }

  const hasRememberedTenant = Boolean(tenantId);

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 px-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>CampanhaOS</CardTitle>
          <CardDescription>Entre com os dados da sua campanha</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="tenantId">ID da campanha</Label>
                {hasRememberedTenant && (
                  <button
                    type="button"
                    onClick={handleForgetTenant}
                    className="text-xs text-muted-foreground underline"
                  >
                    trocar campanha
                  </button>
                )}
              </div>
              <Input
                id="tenantId"
                value={tenantId}
                onChange={(e) => setTenantId(e.target.value)}
                placeholder="UUID da campanha"
                required
              />
              {hasRememberedTenant && (
                <p className="text-xs text-muted-foreground">Lembrado do último acesso neste navegador.</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">E-mail</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? "Entrando..." : "Entrar"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
