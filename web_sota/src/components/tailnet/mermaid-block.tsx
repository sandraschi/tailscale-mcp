import { useEffect, useId, useRef } from "react";
import mermaid from "mermaid";

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
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el || !chart.trim()) return;
    ensureMermaid();
    el.innerHTML = "";
    const node = document.createElement("div");
    node.className = "mermaid";
    node.id = `mm-${uid}`;
    node.textContent = chart;
    el.appendChild(node);
    void mermaid.run({ nodes: [node] }).catch((e) => {
      console.error("mermaid run failed", e);
      el.innerHTML = `<pre class="text-xs text-red-400 whitespace-pre-wrap p-2">${String(e)}</pre>`;
    });
  }, [chart, uid]);

  if (!chart.trim()) {
    return (
      <p className="text-sm text-slate-500">No diagram text (empty response from server).</p>
    );
  }

  return (
    <div
      ref={ref}
      className={`min-h-[240px] overflow-auto rounded-lg border border-slate-800 bg-slate-950/90 p-4 text-slate-200 ${className}`}
    />
  );
}
