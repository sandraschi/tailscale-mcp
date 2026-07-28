import { Code2, Eye } from "lucide-react";
import { type ReactNode, useState } from "react";

type JsonViewProps = {
  data: unknown;
  title?: string;
  className?: string;
  render?: () => ReactNode;
};

export function JsonView({
  data,
  title,
  className = "",
  render,
}: JsonViewProps) {
  const [showJson, setShowJson] = useState(false);

  return (
    <div className={className}>
      <div className="flex items-center justify-between mb-2">
        {title && <span className="text-xs text-slate-500">{title}</span>}
        <button
          type="button"
          onClick={() => setShowJson(!showJson)}
          className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-300 transition-colors"
        >
          {showJson ? (
            <Eye className="h-3 w-3" />
          ) : (
            <Code2 className="h-3 w-3" />
          )}
          {showJson ? "Rendered" : "JSON"}
        </button>
      </div>
      {showJson || !render ? (
        <pre className="text-xs text-slate-300 overflow-auto max-h-96 rounded bg-slate-900/50 p-3 whitespace-pre-wrap">
          {JSON.stringify(data, null, 2)}
        </pre>
      ) : (
        render()
      )}
    </div>
  );
}
