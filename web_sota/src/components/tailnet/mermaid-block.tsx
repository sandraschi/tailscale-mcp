import { ZoomIn, ZoomOut } from "lucide-react";
import mermaid from "mermaid";
import { useCallback, useEffect, useId, useRef, useState } from "react";

type Props = {
  chart: string;
  className?: string;
};

let mermaidReady = false;

function ensureMermaid() {
  if (mermaidReady) return;
  mermaid.initialize({
    startOnLoad: false,
    theme: "dark",
    securityLevel: "loose",
    themeVariables: {
      primaryColor: "#1e293b",
      primaryTextColor: "#e2e8f0",
      primaryBorderColor: "#334155",
      lineColor: "#64748b",
      secondaryColor: "#0f172a",
      tertiaryColor: "#1e293b",
    },
  });
  mermaidReady = true;
}

export function MermaidBlock({ chart, className = "" }: Props) {
  const uid = useId().replace(/:/g, "");
  const containerRef = useRef<HTMLDivElement>(null);
  const innerRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);

  useEffect(() => {
    const outer = containerRef.current;
    const inner = innerRef.current;
    if (!outer || !inner || !chart.trim()) return;
    ensureMermaid();
    inner.innerHTML = "";
    const node = document.createElement("div");
    node.className = "mermaid";
    node.id = `mm-${uid}`;
    node.textContent = chart;
    inner.appendChild(node);
    void mermaid
      .run({ nodes: [node] })
      .then(() => {
        const svg = inner.querySelector("svg");
        if (svg) {
          svg.style.maxWidth = "none";
          svg.style.height = "auto";
        }
      })
      .catch((e) => {
        console.error("mermaid run failed", e);
        inner.innerHTML = `<pre class="text-xs text-red-400 whitespace-pre-wrap p-2">${String(e)}</pre>`;
      });
  }, [chart, uid]);

  const zoomIn = useCallback(() => setScale((s) => Math.min(s + 0.25, 5)), []);
  const zoomOut = useCallback(
    () => setScale((s) => Math.max(s - 0.25, 0.25)),
    [],
  );

  const handleWheel = useCallback((e: React.WheelEvent) => {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault();
      setScale((s) => Math.max(0.25, Math.min(5, s - e.deltaY * 0.005)));
    }
  }, []);

  if (!chart.trim()) {
    return (
      <p className="text-sm text-slate-500">
        No diagram text (empty response from server).
      </p>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={zoomOut}
          className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
          title="Zoom out"
        >
          <ZoomOut className="h-4 w-4" />
        </button>
        <span className="text-xs text-slate-500 w-10 text-center">
          {Math.round(scale * 100)}%
        </span>
        <button
          type="button"
          onClick={zoomIn}
          className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
          title="Zoom in"
        >
          <ZoomIn className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={() => setScale(1)}
          className="text-xs text-slate-500 hover:text-slate-300 transition-colors ml-2"
        >
          Reset
        </button>
      </div>
      <div
        ref={containerRef}
        onWheel={handleWheel}
        className={`min-h-[240px] overflow-auto rounded-lg border border-slate-800 bg-slate-950/90 p-4 text-slate-200 ${className}`}
      >
        <div
          ref={innerRef}
          style={{ transform: `scale(${scale})`, transformOrigin: "top left" }}
        />
      </div>
    </div>
  );
}
