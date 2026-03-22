import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ExternalLink } from "lucide-react";

const DEFAULT_API_URL = "http://127.0.0.1:10821";

export function Settings() {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Settings</h2>
                <p className="text-slate-400">Backend and MCP connection</p>
            </div>

            <div className="grid gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Backend URL</CardTitle>
                        <CardDescription className="text-slate-400">
                            Base URL of the Tailscale webapp backend (FastAPI). Used for /health, /api/v1/tools, /api/v1/tools/call. Set VITE_API_URL or use default.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">API base URL</Label>
                            <Input
                                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                                defaultValue={DEFAULT_API_URL}
                                id="api-url"
                            />
                        </div>
                        <Button
                            variant="outline"
                            className="border-slate-800 text-slate-300 hover:bg-slate-800"
                            onClick={() => {
                                const url = (document.getElementById("api-url") as HTMLInputElement)?.value || DEFAULT_API_URL;
                                window.open(`${url}/health`, "_blank");
                            }}
                        >
                            Test health
                        </Button>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">MCP endpoint</CardTitle>
                        <CardDescription className="text-slate-400">
                            MCP server is mounted at /mcp on the same backend. IDEs and CLI clients can connect to BASE_URL/mcp (FastMCP 3.1 HTTP transport).
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-slate-400 font-mono">{DEFAULT_API_URL}/mcp</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Tailscale API (browser)</CardTitle>
                        <CardDescription className="text-slate-400">
                            The interactive API is Tailscale’s official explorer — not a page inside this webapp. Use it to browse routes and payloads; this MCP calls the same Admin API.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3 text-sm">
                        <div>
                            <a
                                href="https://tailscale.com/api"
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1 text-sky-400 hover:underline"
                            >
                                Interactive API docs <ExternalLink className="h-3 w-3" />
                            </a>
                            <p className="text-slate-500 mt-1">Official reference at tailscale.com/api (try requests, copy curl).</p>
                        </div>
                        <div>
                            <a
                                href="https://login.tailscale.com/admin/settings/keys"
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1 text-sky-400 hover:underline"
                            >
                                Create API keys <ExternalLink className="h-3 w-3" />
                            </a>
                            <p className="text-slate-500 mt-1">Keys power TAILSCALE_API_KEY for the backend.</p>
                        </div>
                        <div>
                            <Button
                                variant="outline"
                                className="border-slate-800 text-slate-300 hover:bg-slate-800"
                                onClick={() => {
                                    const base = (document.getElementById("api-url") as HTMLInputElement)?.value || DEFAULT_API_URL;
                                    window.open(`${base}/api/v1/status`, "_blank");
                                }}
                            >
                                Open backend /api/v1/status
                            </Button>
                            <p className="text-slate-500 mt-2">Shows whether env credentials are set (no secrets), plus the same doc links as JSON.</p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
