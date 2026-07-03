import { callTool } from "@/common/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FolderOpen, RefreshCw, Share2, Terminal } from "lucide-react";
import { useEffect, useState } from "react";

type Share = {
  name: string;
  path?: string;
  mounted?: boolean;
  mountPath?: string;
};

export function Taildrive() {
  const [shares, setShares] = useState<Share[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchShares() {
    setLoading(true);
    setError(null);
    try {
      const res = await callTool("manage_taildrop", { operation: "list_shares" });
      const data = res.data as Record<string, unknown> | undefined;
      setShares((data?.shares as Share[]) ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load shares");
      setShares([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchShares(); }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Taildrive</h2>
          <p className="text-slate-400">Share directories across your tailnet</p>
        </div>
        <Button variant="outline" onClick={fetchShares} disabled={loading}
          className="border-slate-800 bg-slate-900/50 hover:bg-slate-800">
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <Card className="border-amber-800 bg-amber-950/30">
          <CardContent className="py-3 text-amber-200 text-sm">{error}</CardContent>
        </Card>
      )}

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Share2 className="h-4 w-4" />
            Active Shares
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-slate-500 text-sm">Loading shares...</p>
          ) : shares.length === 0 ? (
            <p className="text-slate-400 text-sm">
              No shares configured. Share a directory with:
              <code className="block mt-2 text-xs bg-slate-900 rounded p-2">tailscale drive share &lt;name&gt; &lt;path&gt;</code>
            </p>
          ) : (
            <div className="space-y-2">
              {shares.map((s) => (
                <div key={s.name} className="flex items-center gap-3 py-2 border-b border-slate-800/50 last:border-0">
                  <FolderOpen className="h-4 w-4 text-blue-400 shrink-0" />
                  <span className="text-sm text-slate-200 font-medium">{s.name}</span>
                  <span className="text-xs text-slate-500">{s.path}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Terminal className="h-4 w-4" />
            Setup & Usage
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-slate-300 space-y-4">
          <div>
            <h4 className="text-slate-200 font-medium mb-1">1. Enable in ACLs</h4>
            <p className="text-slate-400 mb-2">Add node attributes to your tailnet policy file:</p>
            <pre className="text-xs bg-slate-900 rounded p-3 overflow-x-auto">{JSON.stringify({
  nodeAttrs: [
    { target: ["autogroup:member"], attr: ["drive:share", "drive:access"] }
  ]
}, null, 2)}</pre>
          </div>

          <div>
            <h4 className="text-slate-200 font-medium mb-1">2. Share a directory</h4>
            <pre className="text-xs bg-slate-900 rounded p-3">tailscale drive share repos D:\Dev\repos</pre>
            <p className="text-xs text-slate-500 mt-1">
              Share names: lowercase, a-z, underscore, parentheses, spaces.
            </p>
          </div>

          <div>
            <h4 className="text-slate-200 font-medium mb-1">3. Access from another machine</h4>
            <p className="text-slate-400 mb-2">
              Shares are available via WebDAV at <code className="text-amber-400">http://100.100.100.100:8080/</code>
            </p>
            <p className="text-slate-400 mb-2">Path format: <code className="text-amber-400">/tailnet/machine/share</code></p>
            <p className="text-slate-400">Example mount (Windows):</p>
            <pre className="text-xs bg-slate-900 rounded p-3 mt-1">
net use Z: http://100.100.100.100:8080/tailfab45.ts.net/goliath/repos /persistent:yes</pre>
          </div>

          <div>
            <h4 className="text-slate-200 font-medium mb-1">4. Control access with ACL grants</h4>
            <pre className="text-xs bg-slate-900 rounded p-3 overflow-x-auto">{JSON.stringify({
  grants: [{
    src: ["group:home"],
    dst: ["goliath"],
    app: { "tailscale.com/cap/drive": [{ shares: ["repos"], access: "ro" }] }
  }]
}, null, 2)}</pre>
          </div>

          <div>
            <h4 className="text-slate-200 font-medium mb-1">Commands</h4>
            <div className="space-y-1 text-xs font-mono">
              <div><span className="text-green-400">share</span> &lt;name&gt; &lt;path&gt; — Create/modify a share</div>
              <div><span className="text-green-400">list</span> — List current shares</div>
              <div><span className="text-green-400">rename</span> &lt;old&gt; &lt;new&gt; — Rename a share</div>
              <div><span className="text-green-400">unshare</span> &lt;name&gt; — Remove a share</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}