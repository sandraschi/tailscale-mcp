"use client";

import { APPS_CATALOG } from "@/common/apps-catalog";
import { useConnection } from "@/store/connection";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { ExternalLink, HelpCircle, LayoutGrid, RefreshCw } from "lucide-react";
import { Link } from "react-router-dom";

export function Topbar() {
  const { state, lastError } = useConnection();

  const statusColor =
    state === "connected" ? "text-emerald-500 border-emerald-500/20 bg-emerald-500/10" :
    state === "connecting" ? "text-amber-500 border-amber-500/20 bg-amber-500/10" :
    "text-red-500 border-red-500/20 bg-red-500/10";

  const statusLabel =
    state === "connected" ? "System Online" :
    state === "connecting" ? "Connecting..." :
    `Offline${lastError ? ` (${lastError.slice(0, 60)})` : ""}`;

  const restartBackend = async () => {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      await invoke("start_backend");
    } catch { /* not in Tauri */ }
  };

  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950/50 px-6 backdrop-blur-xl">
      <div className="flex items-center gap-4">
        <h1 className="text-sm font-medium text-slate-400">
          Navigation / <span className="text-slate-100">Control Center</span>
        </h1>
      </div>

      <div className="flex items-center gap-2">
        {/* Dynamic System Status */}
        <div className={`mr-4 flex items-center gap-2 rounded-full px-3 py-1 text-xs border ${statusColor}`}>
          <span className="relative flex h-2 w-2">
            {state === "connected" && (
              <>
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
              </>
            )}
            {state === "connecting" && (
              <RefreshCw className="h-3 w-3 animate-spin text-amber-400" />
            )}
            {state === "offline" && (
              <span className="relative inline-flex h-2 w-2 rounded-full bg-red-500" />
            )}
          </span>
          <span>{statusLabel}</span>
          {state !== "connected" && (
            <button onClick={restartBackend} className="ml-1 underline hover:text-white" title="Restart backend">
              Restart
            </button>
          )}
        </div>

        {/* Global Apps Navigation */}
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button className="flex items-center gap-2 rounded-md border border-slate-800 bg-slate-900/50 px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-slate-700">
              <LayoutGrid className="h-4 w-4" />
              Apps
            </button>
          </DropdownMenu.Trigger>

          <DropdownMenu.Portal>
            <DropdownMenu.Content
              className="z-50 min-w-[220px] animate-in fade-in zoom-in-95 data-[side=bottom]:slide-in-from-top-2 rounded-md border border-slate-800 bg-slate-950 p-1 shadow-xl"
              sideOffset={5}
              align="end"
            >
              <DropdownMenu.Label className="px-2 py-1.5 text-xs font-semibold text-slate-500">
                Switch Application
              </DropdownMenu.Label>

              <div className="h-px bg-slate-800 my-1" />

              {APPS_CATALOG.map((app) => (
                <DropdownMenu.Item key={app.id} asChild>
                  <a
                    href={app.url}
                    className="flex w-full select-none items-center rounded-sm px-2 py-1.5 text-sm text-slate-300 hover:bg-slate-800 hover:text-white focus:bg-slate-800 focus:text-white outline-none cursor-pointer"
                  >
                    <app.icon className="mr-2 h-4 w-4 text-slate-400" />
                    <span>{app.label}</span>
                    <ExternalLink className="ml-auto h-3 w-3 opacity-50" />
                  </a>
                </DropdownMenu.Item>
              ))}
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>

        <Link
          to="/help"
          className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-800 bg-slate-900/50 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
          title="Help — credentials, sampling, SEP-1577"
        >
          <HelpCircle className="h-4 w-4" />
        </Link>
      </div>
    </header>
  );
}
