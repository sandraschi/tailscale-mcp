import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	AlertTriangle,
	CheckCircle,
	ExternalLink,
	Loader2,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:10821";

export function Settings() {
	const [apiKey, setApiKey] = useState("");
	const [tailnet, setTailnet] = useState("");
	const [saving, setSaving] = useState(false);
	const [saved, setSaved] = useState(false);
	const [testing, setTesting] = useState(false);
	const [testResult, setTestResult] = useState<{
		success: boolean;
		message: string;
	} | null>(null);
	const [error, setError] = useState("");
	const [status, setStatus] = useState<{
		api_key_set: boolean;
		tailnet_set: boolean;
	} | null>(null);

	const fetchStatus = useCallback(async () => {
		try {
			const r = await fetch(`${API_BASE}/api/v1/status`);
			const d = await r.json();
			setStatus({ api_key_set: d.api_key_set, tailnet_set: d.tailnet_set });
		} catch {
			setStatus(null);
		}
	}, []);

	useEffect(() => {
		fetchStatus();
	}, [fetchStatus]);

	const handleSave = async () => {
		const key = apiKey.trim();
		const net = tailnet.trim();
		if (!key || !net) {
			setError("Both API key and tailnet name are required.");
			return;
		}
		setError("");
		setSaving(true);
		setSaved(false);
		try {
			const r = await fetch(`${API_BASE}/api/v1/settings`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					tailscale_api_key: key,
					tailscale_tailnet: net,
				}),
			});
			if (!r.ok) {
				const d = await r.json().catch(() => ({}));
				throw new Error(
					(d as { detail?: string }).detail || `HTTP ${r.status}`,
				);
			}
			setSaved(true);
			fetchStatus();
		} catch (e) {
			setError(e instanceof Error ? e.message : "Failed to save settings.");
		} finally {
			setSaving(false);
		}
	};

	const handleTest = async () => {
		const key = apiKey.trim();
		const net = tailnet.trim();
		if (!key || !net) {
			setError("Both API key and tailnet name are required.");
			return;
		}
		setError("");
		setTestResult(null);
		setTesting(true);
		try {
			const r = await fetch(`${API_BASE}/api/v1/settings/test`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					tailscale_api_key: key,
					tailscale_tailnet: net,
				}),
			});
			const d = await r.json();
			setTestResult({
				success: d.success ?? false,
				message: d.message ?? "Unknown response",
			});
		} catch (e) {
			setTestResult({
				success: false,
				message: e instanceof Error ? e.message : "Test failed.",
			});
		} finally {
			setTesting(false);
		}
	};

	const configured = status?.api_key_set && status?.tailnet_set;

	return (
		<div className="space-y-6">
			<div>
				<h2 className="text-2xl font-bold tracking-tight text-white">
					Settings
				</h2>
				<p className="text-slate-400">
					Backend, MCP connection, and Tailscale credentials
				</p>
			</div>

			<div className="grid gap-6">
				<Card className="border-slate-800 bg-slate-950/50">
					<CardHeader>
						<CardTitle className="text-white">Tailscale Credentials</CardTitle>
						<CardDescription className="text-slate-400">
							API key and tailnet name required to call the Tailscale Admin API.
							Keys are created at{" "}
							<a
								href="https://login.tailscale.com/admin/settings/keys"
								target="_blank"
								rel="noreferrer"
								className="text-sky-400 hover:underline"
							>
								login.tailscale.com/admin/settings/keys
							</a>
							. Stored in the repo{" "}
							<code className="text-xs bg-slate-800 px-1 rounded">.env</code>{" "}
							file.
						</CardDescription>
					</CardHeader>
					<CardContent className="space-y-4">
						{status && (
							<div
								className={`flex items-center gap-2 text-sm rounded-md px-3 py-2 ${configured ? "bg-emerald-950/30 text-emerald-400 border border-emerald-800/50" : "bg-amber-950/30 text-amber-400 border border-amber-800/50"}`}
							>
								{configured ? (
									<CheckCircle className="h-4 w-4 shrink-0" />
								) : (
									<AlertTriangle className="h-4 w-4 shrink-0" />
								)}
								<span>
									{configured
										? "Credentials configured — Tailscale API is reachable."
										: "No credentials set — Tailscale MCP tools will not work."}
								</span>
							</div>
						)}

						<div className="grid gap-2">
							<Label className="text-slate-300" htmlFor="ts-api-key">
								Tailscale API Key
							</Label>
							<Input
								id="ts-api-key"
								type="password"
								className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400 font-mono"
								placeholder="tskey-api-..."
								value={apiKey}
								onChange={(e) => setApiKey(e.target.value)}
							/>
						</div>

						<div className="grid gap-2">
							<Label className="text-slate-300" htmlFor="ts-tailnet">
								Tailnet Name
							</Label>
							<Input
								id="ts-tailnet"
								className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
								placeholder="example.ts.net"
								value={tailnet}
								onChange={(e) => setTailnet(e.target.value)}
							/>
						</div>

						{error && <p className="text-sm text-red-400">{error}</p>}
						{saved && (
							<p className="text-sm text-emerald-400 flex items-center gap-1">
								<CheckCircle className="h-3 w-3" /> Credentials saved. A server
								restart may be needed for MCP tools.
							</p>
						)}
						{testResult && (
							<p
								className={`text-sm flex items-center gap-1 ${testResult.success ? "text-emerald-400" : "text-red-400"}`}
							>
								{testResult.success ? (
									<CheckCircle className="h-3 w-3" />
								) : (
									<AlertTriangle className="h-3 w-3" />
								)}
								{testResult.message}
							</p>
						)}

						<div className="flex gap-3">
							<Button
								className="bg-sky-600 hover:bg-sky-500 text-white"
								onClick={handleSave}
								disabled={saving || testing}
							>
								{saving ? (
									<>
										<Loader2 className="h-4 w-4 mr-2 animate-spin" />
										Saving...
									</>
								) : (
									"Save Credentials"
								)}
							</Button>
							<Button
								variant="outline"
								className="border-slate-700 text-slate-300 hover:bg-slate-800"
								onClick={handleTest}
								disabled={testing || saving}
							>
								{testing ? (
									<>
										<Loader2 className="h-4 w-4 mr-2 animate-spin" />
										Testing...
									</>
								) : (
									"Test Connection"
								)}
							</Button>
						</div>
					</CardContent>
				</Card>

				<Card className="border-slate-800 bg-slate-950/50">
					<CardHeader>
						<CardTitle className="text-white">Backend URL</CardTitle>
						<CardDescription className="text-slate-400">
							Base URL of the Tailscale webapp backend (FastAPI). Used for
							/health, /api/v1/tools, /api/v1/tools/call. Set VITE_API_URL or
							use default.
						</CardDescription>
					</CardHeader>
					<CardContent className="space-y-4">
						<div className="grid gap-2">
							<Label className="text-slate-300">API base URL</Label>
							<Input
								className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
								defaultValue={API_BASE}
								id="api-url"
							/>
						</div>
						<Button
							variant="outline"
							className="border-slate-800 text-slate-300 hover:bg-slate-800"
							onClick={() => {
								const url =
									(document.getElementById("api-url") as HTMLInputElement)
										?.value || API_BASE;
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
							MCP server is mounted at /mcp on the same backend. IDEs and CLI
							clients can connect to BASE_URL/mcp (FastMCP 3.1 HTTP transport).
						</CardDescription>
					</CardHeader>
					<CardContent>
						<p className="text-sm text-slate-400 font-mono">{API_BASE}/mcp</p>
					</CardContent>
				</Card>

				<Card className="border-slate-800 bg-slate-950/50">
					<CardHeader>
						<CardTitle className="text-white">
							Tailscale API (browser)
						</CardTitle>
						<CardDescription className="text-slate-400">
							The interactive API is Tailscale's official explorer — not a page
							inside this webapp. Use it to browse routes and payloads; this MCP
							calls the same Admin API.
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
							<p className="text-slate-500 mt-1">
								Official reference at tailscale.com/api (try requests, copy
								curl).
							</p>
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
							<p className="text-slate-500 mt-1">
								Keys power TAILSCALE_API_KEY for the backend.
							</p>
						</div>
						<div>
							<Button
								variant="outline"
								className="border-slate-800 text-slate-300 hover:bg-slate-800"
								onClick={() => {
									const base =
										(document.getElementById("api-url") as HTMLInputElement)
											?.value || API_BASE;
									window.open(`${base}/api/v1/status`, "_blank");
								}}
							>
								Open backend /api/v1/status
							</Button>
							<p className="text-slate-500 mt-2">
								Shows whether env credentials are set (no secrets), plus the
								same doc links as JSON.
							</p>
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
