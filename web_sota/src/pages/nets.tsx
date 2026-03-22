import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RefreshCw, Network, Globe } from "lucide-react";
import { useState, useEffect } from "react";
import { callTool } from "@/common/api";

export function Nets() {
  const [dnsConfig, setDnsConfig] = useState<Record<string, unknown> | null>(null);
  const [topology, setTopology] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchNets() {
    setLoading(true);
    setError(null);
    try {
      const [dnsRes, topoRes] = await Promise.all([
        callTool("tailscale_network", { operation: "dns_config" }),
        callTool("tailscale_monitor", { operation: "topology" }),
      ]);
      const dns = dnsRes.data as Record<string, unknown> | undefined;
      const topo = topoRes.data as Record<string, unknown> | undefined;
      setDnsConfig((dns?.configuration as Record<string, unknown>) ?? dns ?? null);
      setTopology((topo?.topology as Record<string, unknown>) ?? topo ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load network");
      setDnsConfig(null);
      setTopology(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchNets();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Networks</h2>
          <p className="text-slate-400">DNS config and topology</p>
        </div>
        <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800" onClick={fetchNets} disabled={loading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <Card className="border-amber-800 bg-amber-950/30">
          <CardContent className="py-3 text-amber-200 text-sm">{error}</CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200 flex items-center gap-2">
              <Globe className="h-4 w-4" />
              DNS config
            </CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-xs text-slate-300 overflow-auto max-h-64 rounded bg-slate-900/50 p-3">
              {dnsConfig ? JSON.stringify(dnsConfig, null, 2) : "—"}
            </pre>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200 flex items-center gap-2">
              <Network className="h-4 w-4" />
              Topology
            </CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-xs text-slate-300 overflow-auto max-h-64 rounded bg-slate-900/50 p-3">
              {topology ? JSON.stringify(topology, null, 2) : "—"}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
