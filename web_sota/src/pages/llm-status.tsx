import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  fetchSamplingStatus,
  fetchLlmHealth,
  type SamplingStatus,
  type LlmHealth,
} from "@/common/api";
import { Loader2, RefreshCw } from "lucide-react";

export function LlmStatus() {
  const [sampling, setSampling] = useState<SamplingStatus | null>(null);
  const [health, setHealth] = useState<LlmHealth | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setErr(null);
    try {
      const [s, h] = await Promise.all([fetchSamplingStatus(), fetchLlmHealth()]);
      setSampling(s);
      setHealth(h);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">LLM / sampling status</h2>
          <p className="text-slate-400">
            Environment used for MCP sampling handler and the Local chat proxy (
            <span className="font-mono">TAILSCALE_SAMPLING_*</span>).
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

      {err && <p className="text-sm text-red-400">{err}</p>}

      {loading && !sampling && <p className="text-slate-400">Loading…</p>}

      {sampling && (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Configuration</CardTitle>
            <CardDescription className="text-slate-400">No API keys are returned here.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 font-mono text-sm text-slate-300">
            <Row k="sampling_base_url" v={sampling.sampling_base_url} />
            <Row k="sampling_model" v={sampling.sampling_model} />
            <Row
              k="sampling_api_key_configured"
              v={sampling.sampling_api_key_configured ? "yes" : "no"}
            />
            <Row k="use_client_llm (TAILSCALE_SAMPLING_USE_CLIENT_LLM)" v={String(sampling.use_client_llm)} />
          </CardContent>
        </Card>
      )}

      {health && (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Probe</CardTitle>
            <CardDescription className="text-slate-400">
              Last tried: {health.endpoint_tried ?? "—"}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <span className="text-slate-500">reachable</span>
              <span className={health.reachable ? "text-emerald-400" : "text-amber-400"}>
                {health.reachable ? "yes" : "no"}
              </span>
            </div>
            {health.http_status != null && (
              <div className="text-slate-400">HTTP {health.http_status}</div>
            )}
            {health.models_sample && health.models_sample.length > 0 && (
              <div>
                <div className="mb-1 text-slate-500">Models (sample)</div>
                <ul className="list-inside list-disc text-slate-300">
                  {health.models_sample.map((m) => (
                    <li key={m} className="font-mono text-xs">
                      {m}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {health.detail && (
              <pre className="max-h-40 overflow-auto rounded border border-slate-800 bg-slate-950 p-2 text-xs text-slate-500">
                {health.detail}
              </pre>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex flex-wrap gap-2 border-b border-slate-800/80 py-1">
      <span className="text-slate-500">{k}</span>
      <span className="text-slate-200 break-all">{v}</span>
    </div>
  );
}
