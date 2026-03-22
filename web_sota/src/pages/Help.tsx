import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ExternalLink } from "lucide-react";

export function Help() {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Help</h2>
                <p className="text-slate-400">
                    MCP tool <span className="font-mono text-slate-300">tailscale_help</span> mirrors these topics;
                    use <span className="font-mono">topic=&quot;sampling&quot;</span> for SEP-1577 and credentials.
                </p>
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white">Credentials and non-mock testing</CardTitle>
                    <CardDescription className="text-slate-400">
                        Put real values in a <span className="font-mono">.env</span> file at the repository root
                        (copy from <span className="font-mono">.env.example</span>). The Python server loads it via
                        python-dotenv; <span className="font-mono">.env</span> is gitignored—do not commit API keys.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-slate-300">
                    <p>
                        <strong className="text-slate-200">Required for Tailscale Admin API:</strong>{" "}
                        <span className="font-mono">TAILSCALE_API_KEY</span>,{" "}
                        <span className="font-mono">TAILSCALE_TAILNET</span>
                    </p>
                    <p className="text-slate-400">
                        After restarting the MCP server or webapp backend, tools call the live API (not mock data).
                    </p>
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white">SEP-1577 / sampling</CardTitle>
                    <CardDescription className="text-slate-400">
                        <span className="font-mono">tailscale_agentic_workflow</span> uses FastMCP sampling with tools.
                        Optional environment variables:
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <ul className="list-inside list-disc space-y-1 font-mono text-xs text-slate-400 sm:text-sm">
                        <li>TAILSCALE_SAMPLING_BASE_URL (default Ollama http://127.0.0.1:11434/v1)</li>
                        <li>TAILSCALE_SAMPLING_MODEL</li>
                        <li>TAILSCALE_SAMPLING_API_KEY (cloud APIs; often omit for local Ollama)</li>
                        <li>TAILSCALE_SAMPLING_USE_CLIENT_LLM=1 — MCP host performs sampling</li>
                    </ul>
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white">Webapp pages</CardTitle>
                    <CardDescription className="text-slate-400">
                        MCP &amp; API, Runbook, Tool explorer, LLM status, and Local chat are in the sidebar.
                    </CardDescription>
                </CardHeader>
                <CardContent className="text-sm text-slate-400">
                    Use <span className="font-mono text-slate-300">/mcp-connection</span>,{" "}
                    <span className="font-mono text-slate-300">/runbook</span>,{" "}
                    <span className="font-mono text-slate-300">/tools-explorer</span>,{" "}
                    <span className="font-mono text-slate-300">/llm-status</span>,{" "}
                    <span className="font-mono text-slate-300">/my-tailnet</span>,{" "}
                    <span className="font-mono text-slate-300">/partner-tailnets</span>,{" "}
                    <span className="font-mono text-slate-300">/chat</span>.
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white">Resources</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col gap-2 text-sm">
                    <a
                        className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300"
                        href="https://tailscale.com/api"
                        target="_blank"
                        rel="noreferrer"
                    >
                        Tailscale API reference
                        <ExternalLink className="h-4 w-4" />
                    </a>
                    <p className="text-slate-500">
                        MCP resource <span className="font-mono text-slate-400">resource://tailscale/skills</span> —
                        expert notes from <span className="font-mono">skills/TAILSCALE_EXPERT.md</span>
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}
