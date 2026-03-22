import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { API_BASE } from "@/common/api";
import { copyToClipboard } from "@/common/clipboard";
import { ExternalLink } from "lucide-react";

const MCP_URL = `${API_BASE}/mcp`;
const HEALTH_URL = `${API_BASE}/health`;

export function McpConnection() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">MCP &amp; API</h2>
        <p className="text-slate-400">
          Backend base URL from <span className="font-mono">VITE_API_URL</span> (default{" "}
          <span className="font-mono">http://127.0.0.1:10821</span>). Override in{" "}
          <span className="font-mono">web_sota/.env</span> for local dev.
        </p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Endpoints</CardTitle>
          <CardDescription className="text-slate-400">Copy for MCP clients and REST tooling.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <EndpointRow label="API base" value={API_BASE} />
          <EndpointRow label="MCP (HTTP transport)" value={MCP_URL} />
          <EndpointRow label="Health" value={HEALTH_URL} />
          <EndpointRow
            label="List tools (REST)"
            value={`${API_BASE}/api/v1/tools`}
          />
          <EndpointRow
            label="Call tool (POST JSON)"
            value={`${API_BASE}/api/v1/tools/call`}
          />
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Cursor / IDE (stdio)</CardTitle>
          <CardDescription className="text-slate-400">
            For stdio, run the Python package; HTTP MCP uses the URL above.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-slate-400 font-mono break-all">
          <code className="text-slate-300">uv run python -m tailscalemcp.transport</code>
          <p className="mt-2 text-slate-500">
            See repo README for full <span className="font-mono">mcp.json</span> examples.
          </p>
        </CardContent>
      </Card>

      <a
        className="inline-flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300"
        href="https://tailscale.com/api"
        target="_blank"
        rel="noreferrer"
      >
        Tailscale Admin API reference
        <ExternalLink className="h-4 w-4" />
      </a>
    </div>
  );
}

function EndpointRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-800 bg-slate-900/40 p-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-1 flex flex-wrap items-center justify-between gap-2">
        <code className="text-sm text-slate-200 break-all">{value}</code>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="shrink-0 border-slate-700 text-slate-300"
          onClick={() => void copyToClipboard(value)}
        >
          Copy
        </Button>
      </div>
    </div>
  );
}
