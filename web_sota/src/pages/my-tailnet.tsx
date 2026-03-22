import { useCallback, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import * as Tabs from "@radix-ui/react-tabs";
import { RefreshCw, Radar, Loader2 } from "lucide-react";
import { callTool } from "@/common/api";
import { MermaidBlock } from "@/components/tailnet/mermaid-block";
import { TailnetOrbit } from "@/components/tailnet/tailnet-orbit";
import type { TailnetDevice } from "@/types/tailnet";

function parseToolData(data: unknown): Record<string, unknown> | null {
  if (!data || typeof data !== "object") return null;
  return data as Record<string, unknown>;
}

function extractDevices(raw: Record<string, unknown> | null): TailnetDevice[] {
  if (!raw) return [];
  const devices = raw.devices;
  if (Array.isArray(devices)) return devices as TailnetDevice[];
  return [];
}

function extractMermaid(raw: Record<string, unknown> | null): string | null {
  if (!raw) return null;
  const status = raw.status;
  if (status && typeof status === "object") {
    const md = (status as Record<string, unknown>).mermaid_diagram;
    if (typeof md === "string" && md.trim()) return md;
  }
  const direct = raw.mermaid_diagram;
  if (typeof direct === "string" && direct.trim()) return direct;
  return null;
}

function buildFallbackMermaid(devices: TailnetDevice[]): string {
  const lines = [
    "flowchart TB",
    "  TN[Tailnet]",
  ];
  devices.slice(0, 48).forEach((d, i) => {
    const id = `D${i}`;
    const safe = (d.name ?? d.id ?? `node-${i}`).replace(/"/g, "'").slice(0, 40);
    const state = d.online ? "online" : "offline";
    lines.push(`  ${id}["${safe}<br/>${state}"]`);
    lines.push(`  TN --> ${id}`);
  });
  if (devices.length > 48) {
    lines.push(`  MORE["+${devices.length - 48} more devices"]`);
    lines.push("  TN --> MORE");
  }
  return lines.join("\n");
}

export function MyTailnet() {
  const [devices, setDevices] = useState<TailnetDevice[]>([]);
  const [mermaid, setMermaid] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [devRes, statusRes] = await Promise.all([
        callTool("tailscale_device", { operation: "list" }),
        callTool("tailscale_status", {
          component: "overview",
          detail_level: "basic",
          include_mermaid_diagram: true,
        }),
      ]);

      const devData = parseToolData(devRes.data ?? devDataFromContent(devRes));
      const list = extractDevices(devData);
      setDevices(list);

      const stData = parseToolData(statusRes.data ?? devDataFromContent(statusRes));
      let md = extractMermaid(stData);
      if (!md && list.length) {
        md = buildFallbackMermaid(list);
      }
      setMermaid(md ?? "");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setDevices([]);
      setMermaid("");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">My tailnet</h2>
          <p className="text-slate-400">
            Mermaid topology from the MCP server (or a simple fallback graph). Orbit view is a stylized
            3D CSS scene — not real geography.
          </p>
        </div>
        <Button
          type="button"
          variant="outline"
          className="border-slate-700 text-slate-300"
          disabled={loading}
          onClick={() => void load()}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
          <span className="ml-2">Refresh</span>
        </Button>
      </div>

      {error && (
        <Card className="border-amber-800 bg-amber-950/20">
          <CardContent className="py-3 text-sm text-amber-200">{error}</CardContent>
        </Card>
      )}

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader className="flex flex-row items-center gap-2">
          <Radar className="h-6 w-6 text-blue-400" />
          <div>
            <CardTitle className="text-white">Visualization</CardTitle>
            <CardDescription className="text-slate-400">
              Full Unity / WebGL twin remains on <span className="text-slate-300">Visualizer</span> when wired.
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          {loading && !devices.length && !mermaid ? (
            <div className="flex items-center gap-2 py-12 text-slate-500">
              <Loader2 className="h-5 w-5 animate-spin" /> Loading tailnet…
            </div>
          ) : (
            <Tabs.Root defaultValue="mermaid" className="w-full">
              <Tabs.List className="mb-4 flex gap-1 rounded-lg border border-slate-800 bg-slate-900/50 p-1">
                <Tabs.Trigger
                  value="mermaid"
                  className="rounded-md px-4 py-2 text-sm text-slate-400 data-[state=active]:bg-slate-800 data-[state=active]:text-white"
                >
                  Mermaid
                </Tabs.Trigger>
                <Tabs.Trigger
                  value="orbit"
                  className="rounded-md px-4 py-2 text-sm text-slate-400 data-[state=active]:bg-slate-800 data-[state=active]:text-white"
                >
                  Orbit (CSS 3D)
                </Tabs.Trigger>
              </Tabs.List>
              <Tabs.Content value="mermaid">
                <MermaidBlock chart={mermaid} />
              </Tabs.Content>
              <Tabs.Content value="orbit">
                <TailnetOrbit devices={devices.length ? devices : [{ name: "No devices", online: false }]} />
              </Tabs.Content>
            </Tabs.Root>
          )}
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-sm text-slate-300">Devices ({devices.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="max-h-48 space-y-1 overflow-y-auto text-sm text-slate-400">
            {devices.slice(0, 100).map((d) => (
              <li key={d.id ?? d.name} className="font-mono text-xs">
                <span className={d.online ? "text-emerald-400" : "text-slate-500"}>
                  {d.online ? "●" : "○"}
                </span>{" "}
                {d.name ?? d.id ?? "?"}
              </li>
            ))}
            {devices.length > 100 && (
              <li className="text-slate-500">… and {devices.length - 100} more</li>
            )}
            {!devices.length && !loading && <li className="text-slate-500">No devices returned.</li>}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}

/** Recover structured data when FastMCP puts JSON in text content */
function devDataFromContent(res: {
  data?: unknown;
  content?: Array<{ text?: string }>;
}): Record<string, unknown> | null {
  if (res.data && typeof res.data === "object") return res.data as Record<string, unknown>;
  const parts = res.content;
  if (!Array.isArray(parts)) return null;
  const text = parts.map((c) => c?.text).join("");
  if (!text.trim()) return null;
  try {
    return JSON.parse(text) as Record<string, unknown>;
  } catch {
    return null;
  }
}
