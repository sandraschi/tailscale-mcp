import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RefreshCw, Globe } from "lucide-react";
import { useState, useEffect } from "react";
import { callTool } from "@/common/api";

export function Funnels() {
  const [list, setList] = useState<unknown[]>([]);
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchFunnels() {
    setLoading(true);
    setError(null);
    try {
      const [listRes, statusRes] = await Promise.all([
        callTool("manage_funnel", { operation: "funnel_list" }),
        callTool("manage_funnel", { operation: "funnel_status" }),
      ]);
      const listData = listRes.data as Record<string, unknown>;
      const statusData = statusRes.data as Record<string, unknown>;
      const raw = listData?.funnels ?? listData?.services;
      setList(Array.isArray(raw) ? raw : []);
      setStatus(statusData ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load funnels");
      setList([]);
      setStatus(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchFunnels();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Funnels</h2>
          <p className="text-slate-400">Public HTTPS exposure for local services</p>
        </div>
        <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800" onClick={fetchFunnels} disabled={loading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <Card className="border-amber-800 bg-amber-950/30">
          <CardContent className="py-3 text-amber-200 text-sm">{error}</CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200 flex items-center gap-2">
              <Globe className="h-4 w-4" />
              Active Funnels ({list.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {list.length === 0 ? (
              <p className="text-slate-400 text-sm">No funnels listed. Enable via Tailscale CLI or ACL.</p>
            ) : (
              <pre className="text-xs text-slate-300 overflow-auto max-h-64 rounded bg-slate-900/50 p-3">
                {JSON.stringify(list, null, 2)}
              </pre>
            )}
          </CardContent>
        </Card>
        {status && (
          <Card className="border-slate-800 bg-slate-950/50">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-200">Funnel status</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-xs text-slate-300 overflow-auto max-h-48 rounded bg-slate-900/50 p-3">
                {JSON.stringify(status, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
