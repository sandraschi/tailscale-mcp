import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { copyToClipboard } from "@/common/clipboard";

const SNIPPETS: { title: string; description: string; body: string }[] = [
  {
    title: "List devices (REST tool call)",
    description: "POST /api/v1/tools/call with manage_tailnet_devices",
    body: JSON.stringify(
      {
        name: "manage_tailnet_devices",
        arguments: { operation: "list", online_only: false },
      },
      null,
      2
    ),
  },
  {
    title: "Network status overview",
    description: "get_tailnet_status component overview",
    body: JSON.stringify(
      {
        name: "get_tailnet_status",
        arguments: {
          component: "overview",
          detail_level: "intermediate",
          include_health: true,
        },
      },
      null,
      2
    ),
  },
  {
    title: "Help — sampling topic",
    description: "Structured help for SEP-1577 and .env",
    body: JSON.stringify(
      {
        name: "get_help",
        arguments: { topic: "sampling", level: "intermediate" },
      },
      null,
      2
    ),
  },
  {
    title: "IDE: agentic workflow (MCP)",
    description:
      "Use from Cursor/Claude with sampling enabled. Not the same as REST-only call_tool.",
    body: `run_agentic_tailnet_workflow(
  workflow_prompt="Summarize offline devices and suggest checks.",
  available_tools=["manage_tailnet_devices", "get_tailnet_status"],
  max_iterations=5
)`,
  },
];

export function Runbook() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Runbook</h2>
        <p className="text-slate-400">
          <span className="text-slate-300">Runbook</span> is an ops term for a small cheat sheet: steps
          and copy-paste commands you reuse when something needs doing (here: calling the API
          without looking up JSON each time).
        </p>
        <p className="mt-2 text-slate-500 text-sm">
          Agentic / SEP-1577 flows still need a client with sampling (see Help)—not everything here
          maps 1:1 to REST.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-1">
        {SNIPPETS.map((s) => (
          <Card key={s.title} className="border-slate-800 bg-slate-950/50">
            <CardHeader>
              <CardTitle className="text-lg text-white">{s.title}</CardTitle>
              <CardDescription className="text-slate-400">{s.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="max-h-64 overflow-auto rounded-md border border-slate-800 bg-slate-950 p-3 text-xs text-slate-300 whitespace-pre-wrap">
                {s.body}
              </pre>
              <Button
                type="button"
                variant="outline"
                className="mt-3 border-slate-700 text-slate-300"
                onClick={() => void copyToClipboard(s.body)}
              >
                Copy
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
