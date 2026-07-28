import { useCallback, useEffect, useState } from "react";
import {
  startHealthPoll,
  stopHealthPoll,
  useConnection,
} from "@/store/connection";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

const ZOOM_LEVELS = [0.8, 1.0, 1.25, 1.5, 2.0, 3.0];
// import { Toaster } from '@/components/ui/toaster';

interface AppLayoutProps {
  children: React.ReactNode;
}

function useZoom() {
  const [_zoomIndex, setZoomIndex] = useState(() => {
    try {
      const saved = localStorage.getItem("tauri-zoom");
      return saved ? ZOOM_LEVELS.indexOf(parseFloat(saved)) : 0;
    } catch {
      return 0;
    }
  });

  const applyZoom = useCallback(async (level: number) => {
    localStorage.setItem("tauri-zoom", String(level));
    // CSS zoom for both browser and Tauri (visual feedback)
    document.documentElement.style.zoom = String(level);
    // Tauri native zoom for crisp text
    try {
      const { getCurrentWindow } = await import("@tauri-apps/api/window");
      const win = getCurrentWindow() as {
        setZoom?: (l: number) => Promise<void>;
      };
      if (win.setZoom) await win.setZoom(level);
    } catch {
      /* dev browser -- CSS zoom handles it */
    }
  }, []);

  useEffect(() => {
    const handler = (e: WheelEvent) => {
      if (!e.ctrlKey) return;
      e.preventDefault();
      setZoomIndex((prev) => {
        const next =
          e.deltaY < 0
            ? Math.min(prev + 1, ZOOM_LEVELS.length - 1)
            : Math.max(prev - 1, 0);
        if (next !== prev) applyZoom(ZOOM_LEVELS[next]);
        return next;
      });
    };
    window.addEventListener("wheel", handler, { passive: false });
    // Apply persisted zoom on mount
    const saved = localStorage.getItem("tauri-zoom");
    if (saved) applyZoom(parseFloat(saved));
    return () => window.removeEventListener("wheel", handler);
  }, [applyZoom]);
}

export function AppLayout({ children }: AppLayoutProps) {
  const [collapsed, setCollapsed] = useState(false);
  useZoom();

  // Global health polling + Tauri event bridge
  useEffect(() => {
    startHealthPoll();
    let unlisten: (() => void) | undefined;
    (async () => {
      try {
        const { listen } = await import("@tauri-apps/api/event");
        unlisten = await listen<string>("backend-status", (event) => {
          if (event.payload === "ready") {
            useConnection.setState({ state: "connected", lastError: null });
          } else if (
            typeof event.payload === "string" &&
            event.payload.startsWith("error:")
          ) {
            useConnection.setState({
              state: "error",
              lastError: event.payload,
            });
          }
        });
      } catch {
        /* not in Tauri */
      }
    })();
    return () => {
      stopHealthPoll();
      if (unlisten) unlisten();
    };
  }, []);

  // Persist sidebar state
  useEffect(() => {
    const stored = localStorage.getItem("sidebar-collapsed");
    if (stored !== null) setCollapsed(stored === "true");
  }, []);

  const handleToggle = () => {
    const newState = !collapsed;
    setCollapsed(newState);
    localStorage.setItem("sidebar-collapsed", String(newState));
  };

  return (
    <div className="flex min-h-screen flex-col bg-slate-950 text-slate-50 font-sans selection:bg-emerald-500/30">
      <div className="flex flex-1 overflow-hidden">
        <Sidebar collapsed={collapsed} onToggle={handleToggle} />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-6 scroll-smooth">
            <div className="mx-auto max-w-7xl animate-in fade-in duration-500">
              {children}
            </div>
          </main>
        </div>
      </div>
      {/* <Toaster /> */}
    </div>
  );
}
