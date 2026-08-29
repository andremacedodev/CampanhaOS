import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { LoginPage } from "@/features/auth/pages/LoginPage";
import { useAuth } from "@/features/auth/context/AuthContext";

vi.mock("@/features/auth/context/AuthContext", () => ({
  useAuth: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);

function renderLoginPage() {
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<p>Dashboard</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("LoginPage", () => {
  it("renderiza os três campos do formulário", () => {
    mockedUseAuth.mockReturnValue({ user: null, isLoading: false, login: vi.fn(), logout: vi.fn() });

    renderLoginPage();

    expect(screen.getByLabelText("ID da campanha")).toBeInTheDocument();
    expect(screen.getByLabelText("E-mail")).toBeInTheDocument();
    expect(screen.getByLabelText("Senha")).toBeInTheDocument();
  });

  it("mostra a mensagem de erro retornada pela API quando o login falha", async () => {
    // Simula o formato real de erro que nosso backend retorna (ver
    // error_handlers.py: {"detail": "..."}), envolvido como um erro do
    // axios — é o mesmo formato que `getApiErrorMessage` (api-client.ts)
    // sabe interpretar.
    const apiError = {
      isAxiosError: true,
      response: { data: { detail: "E-mail ou senha inválidos" } },
    };
    const login = vi.fn().mockRejectedValue(apiError);
    mockedUseAuth.mockReturnValue({ user: null, isLoading: false, login, logout: vi.fn() });

    const user = userEvent.setup();
    renderLoginPage();

    await user.type(screen.getByLabelText("ID da campanha"), "tenant-123");
    await user.type(screen.getByLabelText("E-mail"), "deco@teste.dev");
    await user.type(screen.getByLabelText("Senha"), "senha_errada");
    await user.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByText("E-mail ou senha inválidos")).toBeInTheDocument();
  });

  it("navega para o dashboard após login bem-sucedido", async () => {
    const login = vi.fn().mockResolvedValue(undefined);
    mockedUseAuth.mockReturnValue({ user: null, isLoading: false, login, logout: vi.fn() });

    const user = userEvent.setup();
    renderLoginPage();

    await user.type(screen.getByLabelText("ID da campanha"), "tenant-123");
    await user.type(screen.getByLabelText("E-mail"), "deco@teste.dev");
    await user.type(screen.getByLabelText("Senha"), "senha_correta");
    await user.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByText("Dashboard")).toBeInTheDocument();
    expect(login).toHaveBeenCalledWith("tenant-123", "deco@teste.dev", "senha_correta");
  });

  it("já redireciona para o dashboard se o usuário já estiver autenticado", () => {
    mockedUseAuth.mockReturnValue({
      user: { id: "1", tenant_id: "t1", name: "Deco", email: "deco@teste.dev", role_names: [] },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    renderLoginPage();

    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });

  it("lembra o ID da campanha no localStorage após login bem-sucedido", async () => {
    const login = vi.fn().mockResolvedValue(undefined);
    mockedUseAuth.mockReturnValue({ user: null, isLoading: false, login, logout: vi.fn() });

    const user = userEvent.setup();
    renderLoginPage();

    await user.type(screen.getByLabelText("ID da campanha"), "tenant-999");
    await user.type(screen.getByLabelText("E-mail"), "deco@teste.dev");
    await user.type(screen.getByLabelText("Senha"), "senha_correta");
    await user.click(screen.getByRole("button", { name: "Entrar" }));

    await screen.findByText("Dashboard");
    expect(localStorage.getItem("campanhaos_last_tenant_id")).toBe("tenant-999");
  });

  it("preenche o campo ID da campanha automaticamente se já tiver um lembrado", () => {
    localStorage.setItem("campanhaos_last_tenant_id", "tenant-lembrado");
    mockedUseAuth.mockReturnValue({ user: null, isLoading: false, login: vi.fn(), logout: vi.fn() });

    renderLoginPage();

    expect(screen.getByLabelText("ID da campanha")).toHaveValue("tenant-lembrado");
    expect(screen.getByText("trocar campanha")).toBeInTheDocument();
  });

  it("esquece o ID lembrado ao clicar em 'trocar campanha'", async () => {
    localStorage.setItem("campanhaos_last_tenant_id", "tenant-lembrado");
    mockedUseAuth.mockReturnValue({ user: null, isLoading: false, login: vi.fn(), logout: vi.fn() });

    const user = userEvent.setup();
    renderLoginPage();

    await user.click(screen.getByText("trocar campanha"));

    expect(screen.getByLabelText("ID da campanha")).toHaveValue("");
    expect(localStorage.getItem("campanhaos_last_tenant_id")).toBeNull();
  });
});
