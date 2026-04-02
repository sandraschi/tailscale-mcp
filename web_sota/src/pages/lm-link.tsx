import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RefreshCw, Link2, ExternalLink } from "lucide-react";
import { useState, useEffect } from "react";
import { callTool } from "@/common/api";

export function LmLink() {
  const [info, setInfo] = useState<Record<string, unknown> | null>(null);
  const [readiness, setReadiness] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchLmLink() {
    setLoading(true);
    setError(null);
    try {
      const [infoRes, readinessRes] = await Promise.all([
        callTool("get_lm_link", { operation: "info" }),
        callTool("get_lm_link", { operation: "readiness" }),
      ]);
      setInfo((infoRes.data as Record<string, unknown>) ?? null);
      setReadiness((readinessRes.data as Record<string, unknown>) ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load LM Link info");
      setInfo(null);
      setReadiness(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchLmLink();
  }, []);

  const links = (info?.links as Record<string, string>) ?? {};
  const steps = (info?.steps as string[]) ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">LM Link</h2>
          <p className="text-slate-400">Tailscale + LM Studio – remote local LLMs (Feb 2026)</p>
        </div>
        <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800" onClick={fetchLmLink} disabled={loading}>
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
        <CardHeader className="flex flex-row items-center gap-2">
          <Link2 className="h-5 w-5 text-blue-400" />
          <CardTitle className="text-white">What is LM Link?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-slate-300 text-sm">
            LM Link lets you run LLMs on one machine (e.g. a GPU host) and use them from other devices over Tailscale—encrypted, no public internet. Built with Tailscale and LM Studio (Feb 2026).
          </p>
          {info?.description != null && info.description !== "" && (
            <pre className="text-xs text-slate-400 whitespace-pre-wrap rounded bg-slate-900/50 p-3">
              {String(info.description as string)}
            </pre>
          )}
          {steps.length > 0 && (
            <ol className="list-decimal list-inside space-y-2 text-sm text-slate-300">
              {steps.map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ol>
          )}
          <div className="flex flex-wrap gap-2">
            {Object.entries(links).map(([label, url]) => (
              <a
                key={label}
                href={url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 rounded bg-slate-800 px-3 py-1.5 text-sm text-blue-400 hover:bg-slate-700"
              >
                {label.replace(/_/g, " ")}
                <ExternalLink className="h-3 w-3" />
              </a>
            ))}
          </div>
        </CardContent>
      </Card>

      {readiness && (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-slate-200">Tailscale readiness</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm text-slate-300">{String(readiness.message ?? "")}</p>
            {readiness.tailscale_ok === true && (
              <p className="text-xs text-emerald-400">Tailscale is reporting; you can set up LM Link on your model host.</p>
            )}
            {readiness.error != null && readiness.error !== "" && (
              <p className="text-xs text-amber-400">{String(readiness.error)}</p>
            )}
            {readiness.status_summary != null && (
              <pre className="text-xs text-slate-400 overflow-auto max-h-32 rounded bg-slate-900/50 p-2">
                {JSON.stringify(readiness.status_summary as object, null, 2)}
              </pre>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
