import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
	Activity,
	Cpu,
	HardDrive,
	Network,
	Shield,
	Wifi,
	WifiOff,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:10821";

interface Device {
	id?: string;
	name?: string;
	online?: boolean;
	os?: string;
	addresses?: string[];
}

interface Status {
	tailscale_api_configured?: boolean;
	tailnet_set?: boolean;
	api_key_set?: boolean;
}

export function Dashboard() {
	const [devices, setDevices] = useState<Device[]>([]);
	const [status, setStatus] = useState<Status | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const fetchAll = useCallback(async () => {
		setLoading(true);
		setError(null);
		try {
			const [statusRes, toolRes] = await Promise.allSettled([
				fetch(`${API_BASE}/api/v1/status`),
				fetch(`${API_BASE}/api/v1/tools/call`, {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({
						name: "manage_tailnet_devices",
						arguments: { operation: "list" },
					}),
				}),
			]);

			if (statusRes.status === "fulfilled") {
				setStatus(await statusRes.value.json());
			}

			if (toolRes.status === "fulfilled" && toolRes.value.ok) {
				const data = await toolRes.value.json();
				const raw = data.data ?? data.result?.data ?? data;
				const list = raw?.devices ?? [];
				setDevices(Array.isArray(list) ? list : []);
			} else if (toolRes.status === "fulfilled") {
				const text = await toolRes.value.text().catch(() => "");
				setError(`API error (${toolRes.value.status}): ${text.slice(0, 200)}`);
			} else {
				setError(`Backend unreachable — is uvicorn running on ${API_BASE}?`);
			}
		} catch (e) {
			setError(e instanceof Error ? e.message : "Failed to load");
		} finally {
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		fetchAll();
	}, [fetchAll]);

	const onlineCount = devices.filter((d) => d.online).length;
	const offlineCount = devices.length - onlineCount;

	return (
		<div className="space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h2 className="text-2xl font-bold tracking-tight text-white">
						Tailscale Dashboard
					</h2>
					<p className="text-slate-400">Mesh network and security overview</p>
				</div>
				<button
					type="button"
					onClick={fetchAll}
					className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
					disabled={loading}
				>
					{loading ? "Loading..." : "Refresh"}
				</button>
			</div>

			<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
				<Card className="border-slate-800 bg-slate-950/50">
					<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle className="text-sm font-medium text-slate-200">
							Devices
						</CardTitle>
						<Network className="h-4 w-4 text-blue-500" />
					</CardHeader>
					<CardContent>
						<div className="text-2xl font-bold text-white">
							{loading ? "..." : devices.length}
						</div>
						<p className="text-xs text-slate-400">
							{loading
								? "Loading..."
								: `${onlineCount} online, ${offlineCount} offline`}
						</p>
					</CardContent>
				</Card>

				<Card className="border-slate-800 bg-slate-950/50">
					<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle className="text-sm font-medium text-slate-200">
							Tailnet Status
						</CardTitle>
						<Shield
							className={`h-4 w-4 ${status?.tailscale_api_configured ? "text-emerald-500" : "text-red-500"}`}
						/>
					</CardHeader>
					<CardContent>
						<div className="text-2xl font-bold text-white">
							{loading
								? "..."
								: status?.tailscale_api_configured
									? "Connected"
									: "Disconnected"}
						</div>
						<p className="text-xs text-slate-400">
							{status?.tailscale_api_configured
								? "API credentials OK"
								: "No API key set"}
						</p>
					</CardContent>
				</Card>

				<Card className="border-slate-800 bg-slate-950/50">
					<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle className="text-sm font-medium text-slate-200">
							Backend Port
						</CardTitle>
						<Activity className="h-4 w-4 text-purple-500" />
					</CardHeader>
					<CardContent>
						<div className="text-2xl font-bold text-white">10821</div>
						<p className="text-xs text-slate-400">FastAPI + MCP bridge</p>
					</CardContent>
				</Card>

				<Card className="border-slate-800 bg-slate-950/50">
					<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle className="text-sm font-medium text-slate-200">
							Online Ratio
						</CardTitle>
						<Cpu
							className={`h-4 w-4 ${onlineCount > 0 ? "text-emerald-500" : "text-slate-600"}`}
						/>
					</CardHeader>
					<CardContent>
						<div className="text-2xl font-bold text-white">
							{loading || devices.length === 0
								? "—"
								: `${Math.round((onlineCount / devices.length) * 100)}%`}
						</div>
						<p className="text-xs text-slate-400">
							{loading
								? "Loading..."
								: `${onlineCount}/${devices.length} devices reachable`}
						</p>
					</CardContent>
				</Card>
			</div>

			<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
				<Card className="col-span-4 border-slate-800 bg-slate-950/50">
					<CardHeader>
						<CardTitle className="text-white">Devices</CardTitle>
					</CardHeader>
					<CardContent>
						{error && <p className="text-sm text-red-400 mb-3">{error}</p>}
						<div className="space-y-2 max-h-[260px] overflow-y-auto">
							{loading ? (
								<p className="text-sm text-slate-500">Fetching devices...</p>
							) : devices.length === 0 ? (
								<p className="text-sm text-slate-500">
									{status?.tailscale_api_configured === false
										? "Set API key in Settings to enable device listing."
										: "No devices found."}
								</p>
							) : (
								devices.slice(0, 50).map((d, i) => (
									<div
										key={d.id ?? i}
										className="flex items-center gap-3 py-1.5 border-b border-slate-800/50 last:border-0"
									>
										{d.online ? (
											<Wifi className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
										) : (
											<WifiOff className="h-3.5 w-3.5 text-slate-600 shrink-0" />
										)}
										<span className="text-sm text-slate-200 truncate flex-1">
											{d.name ?? d.id ?? "unknown"}
										</span>
										<span className="text-xs text-slate-500">{d.os ?? ""}</span>
									</div>
								))
							)}
						</div>
					</CardContent>
				</Card>

				<Card className="col-span-3 border-slate-800 bg-slate-950/50">
					<CardHeader>
						<CardTitle className="text-white">API Status</CardTitle>
					</CardHeader>
					<CardContent>
						<div className="space-y-4">
							<div className="flex items-center">
								<HardDrive className="h-4 w-4 text-slate-400 mr-2" />
								<div className="ml-2 space-y-1">
									<p className="text-sm font-medium leading-none text-white">
										API Key
									</p>
									<p
										className={`text-xs ${status?.api_key_set ? "text-emerald-400" : "text-red-400"}`}
									>
										{status?.api_key_set ? "Configured" : "Missing"}
									</p>
								</div>
							</div>
							<div className="flex items-center">
								<Activity className="h-4 w-4 text-slate-400 mr-2" />
								<div className="ml-2 space-y-1">
									<p className="text-sm font-medium leading-none text-white">
										Tailnet
									</p>
									<p
										className={`text-xs ${status?.tailnet_set ? "text-emerald-400" : "text-slate-500"}`}
									>
										{status?.tailnet_set ? "Set" : "Not set"}
									</p>
								</div>
							</div>
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
