import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import * as Tabs from "@radix-ui/react-tabs";
import { RefreshCw, Loader2, Users, Share2, Laptop } from "lucide-react";
import { callTool } from "@/common/api";
import { MermaidBlock } from "@/components/tailnet/mermaid-block";

function parseRecord(data: unknown): Record<string, unknown> | null {
  if (!data || typeof data !== "object") return null;
  return data as Record<string, unknown>;
}

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

function buildPartnerMermaid(summary: Record<string, unknown> | null): string {
  if (!summary) return "";
  const members = summary.members;
  const shared = summary.shared_tailnet_users;
  const mCount = Array.isArray(members) ? members.length : 0;
  const sCount = Array.isArray(shared) ? shared.length : 0;
  const lines = [
    "flowchart LR",
    `  TN[Your tailnet]`,
    `  M[Members<br/>${mCount}]`,
    `  S[Shared users<br/>${sCount}]`,
    "  TN --> M",
    "  TN --> S",
  ];
  if (Array.isArray(members)) {
    members.slice(0, 12).forEach((u, i) => {
      if (u && typeof u === "object") {
        const login = String((u as Record<string, unknown>).loginName ?? `m${i}`).slice(0, 32);
        const id = `M${i}`;
        lines.push(`  ${id}["${login.replace(/"/g, "'")}"]`);
        lines.push(`  M --> ${id}`);
      }
    });
  }
  if (Array.isArray(shared)) {
    shared.slice(0, 12).forEach((u, i) => {
      if (u && typeof u === "object") {
        const login = String((u as Record<string, unknown>).loginName ?? `s${i}`).slice(0, 32);
        const id = `S${i}`;
        lines.push(`  ${id}["${login.replace(/"/g, "'")}"]`);
        lines.push(`  S --> ${id}`);
      }
    });
  }
  return lines.join("\n");
}

export function PartnerTailnets() {
  const [summary, setSummary] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await callTool("tailscale_partner_tailnets", { operation: "summary" });
      const raw = parseRecord(res.data) ?? devDataFromContent(res);
      if (raw && raw.success === false) {
        setError(String(raw.error ?? "Unknown error"));
        setSummary(null);
        return;
      }
      setSummary(raw);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setSummary(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const mermaid = useMemo(() => buildPartnerMermaid(summary), [summary]);

  const users = summary?.users;
  const devicesByLogin = summary?.devices_by_login;
  const recs = summary?.recommendations;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Partner tailnets</h2>
          <p className="text-slate-400">
            Members vs tailnet-shared users (Admin API), plus devices grouped by node owner. Pending
            invites live in the console — not always in the API.
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

      {summary && summary.users_api_error != null && String(summary.users_api_error) !== "" ? (
        <Card className="border-amber-800 bg-amber-950/20">
          <CardContent className="py-3 text-sm text-amber-200">
            Users API: {String(summary.users_api_error)}
          </CardContent>
        </Card>
      ) : null}

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-slate-800 bg-slate-950/40">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-lg text-white">
              <Users className="h-5 w-5 text-emerald-400" />
              Members
            </CardTitle>
            <CardDescription className="text-slate-500">type=member</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold text-white">
              {String((summary?.counts as Record<string, unknown> | undefined)?.users_member ?? "—")}
            </p>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/40">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-lg text-white">
              <Share2 className="h-5 w-5 text-sky-400" />
              Shared into tailnet
            </CardTitle>
            <CardDescription className="text-slate-500">type=shared</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold text-white">
              {String((summary?.counts as Record<string, unknown> | undefined)?.users_shared ?? "—")}
            </p>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/40">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-lg text-white">
              <Laptop className="h-5 w-5 text-violet-400" />
              Devices
            </CardTitle>
            <CardDescription className="text-slate-500">All nodes</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold text-white">
              {String((summary?.counts as Record<string, unknown> | undefined)?.devices ?? "—")}
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs.Root defaultValue="diagram" className="w-full">
        <Tabs.List className="flex gap-2 border-b border-slate-800 pb-2">
          <Tabs.Trigger
            value="diagram"
            className="rounded-md px-3 py-1.5 text-sm text-slate-400 data-[state=active]:bg-slate-800 data-[state=active]:text-white"
          >
            Diagram
          </Tabs.Trigger>
          <Tabs.Trigger
            value="users"
            className="rounded-md px-3 py-1.5 text-sm text-slate-400 data-[state=active]:bg-slate-800 data-[state=active]:text-white"
          >
            Users (API)
          </Tabs.Trigger>
          <Tabs.Trigger
            value="devices"
            className="rounded-md px-3 py-1.5 text-sm text-slate-400 data-[state=active]:bg-slate-800 data-[state=active]:text-white"
          >
            Devices by login
          </Tabs.Trigger>
          <Tabs.Trigger
            value="recs"
            className="rounded-md px-3 py-1.5 text-sm text-slate-400 data-[state=active]:bg-slate-800 data-[state=active]:text-white"
          >
            Hints
          </Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="diagram" className="pt-4">
          <Card className="border-slate-800 bg-slate-950/40">
            <CardHeader>
              <CardTitle className="text-white">Mermaid overview</CardTitle>
              <CardDescription>
                High-level map — not a geographic map. For full topology see{" "}
                <Link to="/my-tailnet" className="text-blue-400 hover:text-blue-300">
                  My tailnet
                </Link>
                .
              </CardDescription>
            </CardHeader>
            <CardContent className="min-h-[280px] overflow-auto">
              {mermaid ? <MermaidBlock chart={mermaid} /> : (
                <p className="text-slate-500">Load data to render the diagram.</p>
              )}
            </CardContent>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="users" className="pt-4">
          <Card className="border-slate-800 bg-slate-950/40">
            <CardContent className="p-4">
              <pre className="max-h-[480px] overflow-auto rounded-lg bg-slate-900/80 p-3 text-xs text-slate-300">
                {Array.isArray(users) ? JSON.stringify(users, null, 2) : "—"}
              </pre>
            </CardContent>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="devices" className="pt-4">
          <Card className="border-slate-800 bg-slate-950/40">
            <CardContent className="p-4">
              <pre className="max-h-[480px] overflow-auto rounded-lg bg-slate-900/80 p-3 text-xs text-slate-300">
                {devicesByLogin && typeof devicesByLogin === "object"
                  ? JSON.stringify(devicesByLogin, null, 2)
                  : "—"}
              </pre>
            </CardContent>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="recs" className="pt-4">
          <Card className="border-slate-800 bg-slate-950/40">
            <CardContent className="p-4 text-sm text-slate-300">
              {Array.isArray(recs) && recs.length > 0 ? (
                <ul className="list-disc space-y-2 pl-5">
                  {recs.map((r, i) => (
                    <li key={i}>{String(r)}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-slate-500">No hints — data looks consistent.</p>
              )}
            </CardContent>
          </Card>
        </Tabs.Content>
      </Tabs.Root>
    </div>
  );
}
