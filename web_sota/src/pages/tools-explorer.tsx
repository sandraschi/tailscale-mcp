import { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { listTools, callTool, type ToolInfo } from "@/common/api";
import { Loader2 } from "lucide-react";

export function ToolsExplorer() {
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState<string>("");
  const [argsJson, setArgsJson] = useState("{}");
  const [result, setResult] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(true);
  const [listError, setListError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setListLoading(true);
      setListError(null);
      try {
        const data = await listTools();
        if (!cancelled) {
          setTools(data.tools ?? []);
          if (data.tools?.length) setSelected(data.tools[0].name);
        }
      } catch (e) {
        if (!cancelled) setListError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setListLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const filtered = useMemo(() => {
    const q = filter.trim().toLowerCase();
    if (!q) return tools;
    return tools.filter(
      (t) =>
        t.name.toLowerCase().includes(q) || (t.description || "").toLowerCase().includes(q)
    );
  }, [tools, filter]);

  const selectedTool = tools.find((t) => t.name === selected);

  async function handleCall() {
    let parsed: Record<string, unknown>;
    try {
      parsed = JSON.parse(argsJson || "{}") as Record<string, unknown>;
    } catch {
      setResult("Invalid JSON in arguments.");
      return;
    }
    setLoading(true);
    setResult("");
    try {
      const out = await callTool(selected, parsed);
      setResult(JSON.stringify(out, null, 2));
    } catch (e) {
      setResult(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Tool explorer</h2>
        <p className="text-slate-400">
          List MCP tools from the backend and invoke <span className="font-mono">/api/v1/tools/call</span>.
        </p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Tools</CardTitle>
          <CardDescription className="text-slate-400">Search and select a tool name.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {listLoading && (
            <div className="flex items-center gap-2 text-slate-400">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading…
            </div>
          )}
          {listError && <p className="text-sm text-red-400">{listError}</p>}
          {!listLoading && !listError && (
            <>
              <div className="grid gap-2">
                <Label className="text-slate-300">Filter</Label>
                <Input
                  className="bg-slate-900 border-slate-800 text-slate-100"
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  placeholder="Filter by name or description"
                />
              </div>
              <div className="grid gap-2">
                <Label className="text-slate-300">Tool</Label>
                <select
                  className="rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100"
                  value={selected}
                  onChange={(e) => setSelected(e.target.value)}
                >
                  {filtered.map((t) => (
                    <option key={t.name} value={t.name}>
                      {t.name}
                    </option>
                  ))}
                </select>
              </div>
              {selectedTool && (
                <p className="text-sm text-slate-400">{selectedTool.description}</p>
              )}
              {selectedTool?.inputSchema != null && (
                <div>
                  <div className="mb-1 text-xs text-slate-500">inputSchema</div>
                  <pre className="max-h-40 overflow-auto rounded-md border border-slate-800 bg-slate-950 p-2 text-xs text-slate-400">
                    {JSON.stringify(selectedTool.inputSchema, null, 2)}
                  </pre>
                </div>
              )}
              <div className="grid gap-2">
                <Label className="text-slate-300">Arguments (JSON object)</Label>
                <textarea
                  className="min-h-[120px] rounded-md border border-slate-800 bg-slate-900 px-3 py-2 font-mono text-sm text-slate-100"
                  value={argsJson}
                  onChange={(e) => setArgsJson(e.target.value)}
                />
              </div>
              <Button
                type="button"
                className="bg-blue-600 hover:bg-blue-700"
                disabled={loading || !selected}
                onClick={() => void handleCall()}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Calling…
                  </>
                ) : (
                  "Call tool"
                )}
              </Button>
              {result && (
                <div>
                  <div className="mb-1 text-xs text-slate-500">Result</div>
                  <pre className="max-h-96 overflow-auto rounded-md border border-slate-800 bg-slate-950 p-3 text-xs text-slate-300">
                    {result}
                  </pre>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
