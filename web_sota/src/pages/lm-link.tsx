import {
  Cpu,
  ExternalLink,
  Link2,
  Monitor,
  Pencil,
  Power,
  PowerOff,
  RefreshCw,
  Star,
  Wifi,
  WifiOff,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { callTool } from "@/common/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

interface Peer {
  device_name?: string;
  name?: string;
  models?: string[];
  loaded_models?: string[];
  online?: boolean;
  preferred?: boolean;
}

interface LinkStatus {
  device_name?: string;
  enabled?: boolean;
  connected?: boolean;
  connection_state?: string;
  peers?: Peer[];
  peer_count?: number;
  preferred_device?: string;
}

function parseToolData(res: unknown): Record<string, unknown> {
  if (!res || typeof res !== "object") return {};
  const r = res as Record<string, unknown>;
  return (r.data as Record<string, unknown>) ?? r;
}

export function LmLink() {
  const [info, setInfo] = useState<Record<string, unknown> | null>(null);
  const [readiness, setReadiness] = useState<Record<string, unknown> | null>(
    null,
  );
  const [linkStatus, setLinkStatus] = useState<LinkStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionMsg, setActionMsg] = useState<string | null>(null);
  const [deviceName, setDeviceName] = useState("");
  const [showInfo, setShowInfo] = useState(false);

  const fetchStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await callTool("get_lm_link", { operation: "status" });
      const d = parseToolData(res);
      setLinkStatus(d as unknown as LinkStatus);
      if (d.device_name) setDeviceName(d.device_name as string);
    } catch (e) {
      setLinkStatus(null);
      setError(e instanceof Error ? e.message : "Failed to get LM Link status");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchInfo = useCallback(async () => {
    try {
      const [infoRes, readinessRes] = await Promise.all([
        callTool("get_lm_link", { operation: "info" }),
        callTool("get_lm_link", { operation: "readiness" }),
      ]);
      setInfo(parseToolData(infoRes));
      setReadiness(parseToolData(readinessRes));
    } catch {
      // non-critical
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    fetchInfo();
  }, [fetchStatus, fetchInfo]);

  async function doAction(
    operation: string,
    extra: Record<string, unknown> = {},
  ) {
    setActionMsg(null);
    try {
      const res = await callTool("get_lm_link", { operation, ...extra });
      const d = parseToolData(res);
      setActionMsg((d.message as string) ?? (d.ok ? "Done" : "Failed"));
      await fetchStatus();
    } catch (e) {
      setActionMsg(e instanceof Error ? e.message : "Action failed");
    }
  }

  const lmsAvailable =
    (readiness?.lms_installed as boolean) ?? linkStatus != null;
  const isEnabled = linkStatus?.enabled ?? linkStatus?.connected ?? false;
  const peers = linkStatus?.peers ?? [];
  const peerModels = (p: Peer) => p.models ?? p.loaded_models ?? [];

  const links = (info?.links as Record<string, string>) ?? {};

  return (
    <div className="space-y-6" data-testid="lm-link-page">
      {/* header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            LM Link
          </h2>
          <p className="text-slate-400">
            Tailscale + LM Studio — remote local LLMs (Feb 2026)
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            className="border-slate-800 bg-slate-900/50 hover:bg-slate-800"
            onClick={fetchStatus}
            disabled={loading}
            data-testid="lm-link-refresh"
          >
            <RefreshCw
              className={`mr-1 h-4 w-4 ${loading ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="text-slate-400 hover:text-white"
            onClick={() => setShowInfo(!showInfo)}
          >
            {showInfo ? "Hide info" : "What is LM Link?"}
          </Button>
        </div>
      </div>

      {actionMsg != null && actionMsg !== "" && (
        <Card className="border-blue-800 bg-blue-950/30">
          <CardContent className="py-3 text-blue-200 text-sm">
            {actionMsg}
          </CardContent>
        </Card>
      )}

      {error != null && error !== "" && (
        <Card className="border-amber-800 bg-amber-950/30">
          <CardContent className="py-3 text-amber-200 text-sm">
            {error}
          </CardContent>
        </Card>
      )}

      {/* status card */}
      <Card
        className="border-slate-800 bg-slate-950/50"
        data-testid="lm-link-status"
      >
        <CardHeader className="flex flex-row items-center gap-2 pb-3">
          {isEnabled ? (
            <Wifi className="h-5 w-5 text-emerald-400" />
          ) : (
            <WifiOff className="h-5 w-5 text-red-400" />
          )}
          <CardTitle className="text-white">Link Status</CardTitle>
          <Badge
            variant={isEnabled ? "default" : "destructive"}
            className="ml-auto"
            data-testid="lm-link-state-badge"
          >
            {isEnabled ? "Connected" : "Inactive"}
          </Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          {linkStatus != null ? (
            <>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-500">This device</span>
                  <p className="text-white font-medium">
                    {linkStatus.device_name ?? "unknown"}
                  </p>
                </div>
                <div>
                  <span className="text-slate-500">Peers</span>
                  <p className="text-white font-medium">
                    {linkStatus.peer_count ?? peers.length}
                  </p>
                </div>
              </div>

              {/* controls */}
              <div className="flex flex-wrap gap-2">
                {!isEnabled ? (
                  <Button
                    size="sm"
                    className="bg-emerald-600 hover:bg-emerald-700"
                    onClick={() => doAction("enable")}
                    data-testid="lm-link-enable"
                  >
                    <Power className="mr-1 h-4 w-4" />
                    Enable
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => doAction("disable")}
                    data-testid="lm-link-disable"
                  >
                    <PowerOff className="mr-1 h-4 w-4" />
                    Disable
                  </Button>
                )}
                <div className="flex items-center gap-1">
                  <Input
                    value={deviceName}
                    onChange={(e) => setDeviceName(e.target.value)}
                    placeholder="Device name"
                    className="h-8 w-40 bg-slate-900 border-slate-700 text-white text-xs"
                    data-testid="lm-link-device-name"
                  />
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-8 border-slate-700 text-xs"
                    onClick={() =>
                      doAction("set_device_name", { name: deviceName })
                    }
                    data-testid="lm-link-set-name"
                  >
                    <Pencil className="mr-1 h-3 w-3" />
                    Rename
                  </Button>
                </div>
              </div>

              {/* peers */}
              {peers.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                    Peers
                  </h4>
                  <div className="space-y-2" data-testid="lm-link-peers">
                    {peers.map((peer, i) => {
                      const models = peerModels(peer);
                      const name =
                        peer.device_name ?? peer.name ?? `Peer ${i + 1}`;
                      const isPref = peer.preferred;
                      return (
                        <div
                          key={name}
                          className="flex items-start gap-3 rounded border border-slate-800 bg-slate-900/50 p-3"
                          data-testid={`lm-link-peer-${i}`}
                        >
                          <Monitor className="mt-0.5 h-4 w-4 text-slate-400 shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-white truncate">
                                {name}
                              </span>
                              {isPref && (
                                <Badge
                                  variant="outline"
                                  className="text-amber-400 border-amber-800 text-xs"
                                >
                                  <Star className="mr-1 h-3 w-3" />
                                  Preferred
                                </Badge>
                              )}
                              {!isPref && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="h-6 text-xs text-slate-400 hover:text-amber-300"
                                  onClick={() =>
                                    doAction("set_preferred_device", {
                                      device: name,
                                    })
                                  }
                                  data-testid={`lm-link-prefer-${i}`}
                                >
                                  Make preferred
                                </Button>
                              )}
                            </div>
                            {models.length > 0 ? (
                              <div className="flex flex-wrap gap-1 mt-2">
                                {models.map((m) => (
                                  <Badge
                                    key={m}
                                    variant="secondary"
                                    className="text-xs bg-slate-800 text-slate-300"
                                  >
                                    <Cpu className="mr-1 h-3 w-3" />
                                    {m}
                                  </Badge>
                                ))}
                              </div>
                            ) : (
                              <p className="text-xs text-slate-500 mt-1">
                                No models loaded
                              </p>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {peers.length === 0 && isEnabled && (
                <p className="text-xs text-slate-500">
                  No peers connected. Add another device to your LM Link from LM
                  Studio.
                </p>
              )}
            </>
          ) : (
            !loading && (
              <div className="text-center py-6">
                <p className="text-slate-400 text-sm">
                  {lmsAvailable
                    ? "LM Link is not active. Enable it to see peers and models."
                    : "LM Studio CLI (lms) not found. Install LM Studio to use LM Link."}
                </p>
              </div>
            )
          )}

          {loading && !linkStatus && (
            <div className="text-center py-6">
              <RefreshCw className="mx-auto h-5 w-5 animate-spin text-slate-500" />
              <p className="text-slate-500 text-sm mt-2">Checking LM Link...</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* info card (collapsed) */}
      {showInfo && (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center gap-2 pb-3">
            <Link2 className="h-5 w-5 text-blue-400" />
            <CardTitle className="text-white">What is LM Link?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-slate-300 text-sm">
              LM Link lets you run LLMs on one machine (e.g. a GPU host) and use
              them from other devices over Tailscale — encrypted, no public
              internet. Built with Tailscale and LM Studio (Feb 2026).
            </p>
            {info?.description != null && info.description !== "" && (
              <pre className="text-xs text-slate-400 whitespace-pre-wrap rounded bg-slate-900/50 p-3 max-h-48 overflow-auto">
                {String(info.description)}
              </pre>
            )}
            {Array.isArray(info?.steps) && info.steps.length > 0 && (
              <ol className="list-decimal list-inside space-y-2 text-sm text-slate-300">
                {(info.steps as string[]).map((step) => (
                  <li key={step}>{step}</li>
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
      )}

      {/* readiness card */}
      {readiness != null && (
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-200">
              Readiness Check
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p className="text-slate-300">{String(readiness.message ?? "")}</p>
            {readiness.tailscale_ok === true && (
              <p className="text-xs text-emerald-400">Tailscale connected ✓</p>
            )}
            {readiness.lms_installed === true && (
              <p className="text-xs text-emerald-400">lms CLI found ✓</p>
            )}
            {readiness.lms_installed === false && (
              <p className="text-xs text-amber-400">
                lms CLI not found — install LM Studio for LM Link
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
