import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { RefreshCw, Wifi, Shield, Server, ExternalLink } from "lucide-react";
import { useState, useEffect } from "react";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:10821";

interface DeviceInfo {
    id?: string;
    device_id?: string;
    name?: string;
    online?: boolean;
    addresses?: string[];
    ip_addresses?: string[];
    os?: string;
}

type ApiStatus = {
    tailscale_api_configured?: boolean;
    docs?: { interactive_api?: string; create_api_key?: string };
};

function parseErrorDetail(data: unknown): { message: string; hint?: string } {
    if (!data || typeof data !== "object") {
        return { message: "Unknown error" };
    }
    const d = data as { detail?: unknown };
    const detail = d.detail;
    if (typeof detail === "string") {
        return { message: detail };
    }
    if (detail && typeof detail === "object") {
        const o = detail as { message?: string; hint?: string };
        return {
            message: o.message ?? JSON.stringify(detail),
            hint: o.hint,
        };
    }
    return { message: JSON.stringify(data) };
}

export function Control() {
    const [devices, setDevices] = useState<DeviceInfo[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [errorHint, setErrorHint] = useState<string | null>(null);
    const [apiStatus, setApiStatus] = useState<ApiStatus | null>(null);

    async function fetchStatus() {
        try {
            const res = await fetch(`${API_BASE}/api/v1/status`);
            if (res.ok) {
                setApiStatus((await res.json()) as ApiStatus);
            }
        } catch {
            setApiStatus(null);
        }
    }

    async function fetchDevices() {
        setLoading(true);
        setError(null);
        setErrorHint(null);
        try {
            const res = await fetch(`${API_BASE}/api/v1/tools/call`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: "tailscale_device",
                    arguments: { operation: "list" },
                }),
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                const { message, hint } = parseErrorDetail(data);
                setError(message || `HTTP ${res.status}`);
                setErrorHint(hint ?? null);
                setDevices([]);
                return;
            }
            const raw = data.data ?? data.result?.data ?? data;
            const content = data.result?.content ?? data.content ?? [];
            const text = Array.isArray(content)
                ? content.map((c: { text?: string }) => c?.text).join("")
                : "";
            let list: DeviceInfo[] = [];
            if (raw?.devices && Array.isArray(raw.devices)) {
                list = raw.devices;
            } else {
                try {
                    const parsed = text ? JSON.parse(text) : raw || {};
                    list = parsed.devices ?? (Array.isArray(parsed) ? parsed : []);
                } catch {
                    list = [];
                }
            }
            setDevices(Array.isArray(list) ? list : []);
        } catch (e) {
            setError(e instanceof Error ? e.message : "Failed to load devices");
            setDevices([]);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        void fetchStatus();
    }, []);

    useEffect(() => {
        void fetchDevices();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Devices</h2>
                    <p className="text-slate-400">Tailscale tailnet devices (via MCP tool <code className="text-slate-500">tailscale_device</code>)</p>
                </div>
                <Button
                    variant="outline"
                    className="border-slate-800 bg-slate-900/50 hover:bg-slate-800"
                    onClick={() => fetchDevices()}
                    disabled={loading}
                >
                    <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                    Refresh
                </Button>
            </div>

            {apiStatus && !apiStatus.tailscale_api_configured && (
                <Card className="border-amber-800 bg-amber-950/30">
                    <CardContent className="py-3 text-amber-200 text-sm space-y-2">
                        <p>
                            Backend env is missing <code className="text-amber-100">TAILSCALE_API_KEY</code> or{" "}
                            <code className="text-amber-100">TAILSCALE_TAILNET</code>. Put them in the repo root{" "}
                            <code className="text-amber-100">.env</code> and restart the uvicorn process
                            (e.g. <code className="text-amber-100">web_sota\start.ps1</code>).
                        </p>
                        {apiStatus.docs?.create_api_key && (
                            <a
                                href={apiStatus.docs.create_api_key}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1 text-amber-300 underline"
                            >
                                Open Tailscale Keys <ExternalLink className="h-3 w-3" />
                            </a>
                        )}
                    </CardContent>
                </Card>
            )}

            {error && (
                <Card className="border-amber-800 bg-amber-950/30">
                    <CardContent className="py-3 text-amber-200 text-sm space-y-2">
                        <p className="font-medium">{error}</p>
                        {errorHint && <p className="text-amber-100/90">{errorHint}</p>}
                        <p className="text-slate-400 text-xs">
                            Backend: <code className="text-slate-300">{API_BASE}</code> — ensure uvicorn is running and reachable from the browser (CORS allows 10820 and 5173).
                        </p>
                    </CardContent>
                </Card>
            )}

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {devices.length === 0 && !loading && !error && (
                    <Card className="col-span-full border-slate-800 bg-slate-950/50">
                        <CardContent className="py-8 text-center text-slate-400">
                            No devices returned. If the backend is up, check API keys and tailnet in{" "}
                            <a href="/settings" className="text-sky-400 underline">
                                Settings
                            </a>
                            .
                        </CardContent>
                    </Card>
                )}
                {devices.map((device) => {
                    const addrList = device.addresses?.length
                        ? device.addresses
                        : device.ip_addresses ?? [];
                    const key = device.id ?? device.device_id ?? device.name ?? Math.random();
                    return (
                        <Card key={key} className="border-slate-800 bg-slate-950/50">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium text-slate-200 flex items-center gap-2">
                                    <Server className="h-4 w-4 text-slate-500" />
                                    {device.name ?? device.id ?? "Unknown"}
                                </CardTitle>
                                <Badge
                                    variant="outline"
                                    className={
                                        device.online
                                            ? "border-emerald-500/50 text-emerald-400 bg-emerald-950/30"
                                            : "border-slate-600 text-slate-400 bg-slate-900/50"
                                    }
                                >
                                    {device.online ? "Online" : "Offline"}
                                </Badge>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-2 text-xs text-slate-400">
                                    {addrList.length ? (
                                        <div className="flex items-center gap-2">
                                            <Wifi className="h-3 w-3" />
                                            {addrList.slice(0, 2).join(", ")}
                                        </div>
                                    ) : null}
                                    {device.os && (
                                        <div className="flex items-center gap-2">
                                            <Shield className="h-3 w-3" />
                                            {device.os}
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>
        </div>
    );
}
