import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RefreshCw, Activity, Cpu } from "lucide-react";
import { useState, useEffect } from "react";
import { callTool } from "@/common/api";

export function Stats() {
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchStats() {
    setLoading(true);
    setError(null);
    try {
      const [statusRes, metricsRes] = await Promise.all([
        callTool("monitor_tailnet", { operation: "status" }),
        callTool("monitor_tailnet", { operation: "metrics" }),
      ]);
      const sd = statusRes.data as Record<string, unknown> | undefined;
      const md = metricsRes.data as Record<string, unknown> | undefined;
      setStatus((sd?.status as Record<string, unknown>) ?? sd ?? null);
      setMetrics((md?.metrics as Record<string, unknown>) ?? md ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load stats");
      setStatus(null);
      setMetrics(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Stats</h2>
          <p className="text-slate-400">Network status and metrics from Tailscale</p>
        </div>
        <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800" onClick={fetchStats} disabled={loading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <Card className="border-amber-800 bg-amber-950/30">
          <CardContent className="py-3 text-amber-200 text-sm">
            {error}. Ensure backend is running (e.g. web_sota\\start.ps1).
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200 flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-xs text-slate-300 overflow-auto max-h-64 rounded bg-slate-900/50 p-3">
              {status ? JSON.stringify(status, null, 2) : "—"}
            </pre>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200 flex items-center gap-2">
              <Cpu className="h-4 w-4" />
              Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-xs text-slate-300 overflow-auto max-h-64 rounded bg-slate-900/50 p-3">
              {metrics ? JSON.stringify(metrics, null, 2) : "—"}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
