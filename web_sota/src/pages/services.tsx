import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RefreshCw, Server, Globe } from "lucide-react";
import { useState, useEffect } from "react";
import { callTool } from "@/common/api";

interface ServiceEndpoint {
  device_id?: string;
  deviceId?: string;
  ip?: string;
  port?: number;
  protocol?: string;
}

interface ServiceRow {
  id: string;
  name: string;
  tailvip_ipv4?: string;
  tailvip_ipv6?: string;
  tailvipIPv4?: string;
  tailvipIPv6?: string;
  magicdns_name?: string;
  magicDNS?: string;
  tags?: string[];
  endpoints?: ServiceEndpoint[];
}

export function Services() {
  const [services, setServices] = useState<ServiceRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchServices() {
    setLoading(true);
    setError(null);
    try {
      const res = await callTool("tailscale_network", { operation: "services_list" });
      const data = res.data as { services?: ServiceRow[]; count?: number } | undefined;
      const list = Array.isArray(data?.services) ? data.services : [];
      setServices(list);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load services");
      setServices([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchServices();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Services</h2>
          <p className="text-slate-400">Tailscale Services (TailVIPs) – app-aware connectivity</p>
        </div>
        <Button
          variant="outline"
          className="border-slate-800 bg-slate-900/50 hover:bg-slate-800"
          onClick={fetchServices}
          disabled={loading}
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <Card className="border-amber-800 bg-amber-950/30">
          <CardContent className="py-3 text-amber-200 text-sm">
            {error}. Ensure backend is running and tailnet has Services (TailVIPs) enabled.
          </CardContent>
        </Card>
      )}

      {services.length === 0 && !loading && !error && (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardContent className="py-8 text-center text-slate-400">
            No services. Use tailscale_network with services_create, or check tailnet policy.
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {services.map((svc) => (
          <Card key={svc.id} className="border-slate-800 bg-slate-950/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200 flex items-center gap-2">
                <Server className="h-4 w-4 text-slate-500" />
                {svc.name || svc.id}
              </CardTitle>
              <Badge variant="outline" className="border-slate-600 text-slate-400 text-xs">
                {svc.id.slice(0, 8)}
              </Badge>
            </CardHeader>
            <CardContent className="space-y-3">
              {(svc.magicdns_name ?? svc.magicDNS) && (
                <div className="flex items-center gap-2 text-xs">
                  <Globe className="h-3 w-3 text-slate-500" />
                  <span className="text-slate-300 font-mono">{svc.magicdns_name ?? svc.magicDNS}</span>
                </div>
              )}
              {((svc.tailvip_ipv4 ?? svc.tailvipIPv4) || (svc.tailvip_ipv6 ?? svc.tailvipIPv6)) && (
                <div className="text-xs text-slate-400 space-y-1">
                  {(svc.tailvip_ipv4 ?? svc.tailvipIPv4) && <div>IPv4: {svc.tailvip_ipv4 ?? svc.tailvipIPv4}</div>}
                  {(svc.tailvip_ipv6 ?? svc.tailvipIPv6) && <div>IPv6: {svc.tailvip_ipv6 ?? svc.tailvipIPv6}</div>}
                </div>
              )}
              {svc.tags && svc.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {svc.tags.map((t) => (
                    <Badge key={t} variant="secondary" className="text-xs bg-slate-800 text-slate-300">
                      {t}
                    </Badge>
                  ))}
                </div>
              )}
              {svc.endpoints && svc.endpoints.length > 0 && (
                <div className="text-xs text-slate-500">
                  {svc.endpoints.length} endpoint(s):{" "}
                  {svc.endpoints.map((ep) => `${ep.port ?? "?"}/${ep.protocol ?? "tcp"}`).join(", ")}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
