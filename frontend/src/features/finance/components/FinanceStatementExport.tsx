import { useState } from "react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { useDownloadFinanceStatement } from "@/features/finance/hooks/use-finance";

/**
 * Pra conciliação com o extrato do banco — o Excel gerado usa a DATA
 * REAL de cada pagamento (não a data do lançamento), então uma despesa
 * paga em 2 vezes aparece como 2 linhas separadas, nas datas certas.
 * Ver backend: get_statement.py.
 */
export function FinanceStatementExport() {
  const [occurredAfter, setOccurredAfter] = useState("");
  const [occurredBefore, setOccurredBefore] = useState("");
  const download = useDownloadFinanceStatement();

  async function handleDownload() {
    await download.mutateAsync({
      occurred_after: occurredAfter || undefined,
      occurred_before: occurredBefore || undefined,
    });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Extrato Financeiro (Excel)</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="space-y-1">
          <Label htmlFor="statement_after">De</Label>
          <Input
            id="statement_after"
            type="date"
            value={occurredAfter}
            onChange={(e) => setOccurredAfter(e.target.value)}
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="statement_before">Até</Label>
          <Input
            id="statement_before"
            type="date"
            value={occurredBefore}
            onChange={(e) => setOccurredBefore(e.target.value)}
          />
        </div>
        <Button type="button" onClick={handleDownload} disabled={download.isPending}>
          {download.isPending ? "Gerando..." : "Baixar Extrato (Excel)"}
        </Button>
      </CardContent>
      <CardContent className="pt-0">
        <p className="text-xs text-muted-foreground">
          Deixa as duas datas em branco pra baixar o histórico inteiro. Cada linha do extrato é um movimento real de
          dinheiro (pagamento de despesa na data em que foi pago, não na data do lançamento) — é isso que facilita
          bater com o extrato do banco.
        </p>
      </CardContent>
    </Card>
  );
}
