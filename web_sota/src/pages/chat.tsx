import { useCallback, useEffect, useRef, useState } from "react";
import { Bot, Download, Eraser, Loader2, MessageSquare, Send, User } from "lucide-react";
import { chatComplete, type ChatMessage } from "@/common/api";

const HISTORY_KEY = "tailscale-chat-history";
const PERSONALITY_KEY = "tailscale-chat-personality";
const MAX_HISTORY = 100;

const PERSONALITIES: Record<string, string> = {
  "Network Engineer": "You are a Tailscale network engineer. Focus on subnet routes, ACLs, DNS configuration, and device connectivity. Provide concise technical guidance.",
  "Security Analyst": "You are a security analyst specializing in Tailscale mesh VPN security. Prioritize access controls, ACL hardening, authentication methods, and network segmentation.",
  "Quick Summarizer": "Keep responses to 2-3 sentences. Focus on key facts.",
  "Custom": "Custom prompt \u2014 editable below.",
};

const EXAMPLE_PROMPTS = [
  { group: "Devices", prompts: ["List all connected devices", "Show device details for [name]", "Find devices with expired keys"] },
  { group: "Network", prompts: ["Show subnet routes", "Check ACL configuration", "Verify DNS settings"] },
  { group: "Security", prompts: ["Audit ACL rules", "Check authentication methods", "Review exit node configuration"] },
];

export function Chat() {
  const [personality, setPersonality] = useState(() => localStorage.getItem(PERSONALITY_KEY) || "Network Engineer");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [model, setModel] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => { localStorage.setItem(HISTORY_KEY, JSON.stringify(messages)); }, [messages]);
  useEffect(() => { localStorage.setItem(PERSONALITY_KEY, personality); }, [personality]);
  useEffect(() => { scrollRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;
    const userMsg: ChatMessage = { role: "user", content: text };
    const next = [...messages, userMsg];
    setMessages(next);
    setInput("");
    setError(null);
    setLoading(true);
    try {
      const conv = next.filter((m) => m.role === "user" || m.role === "assistant");
      const out = await chatComplete(conv, { model: model.trim() || undefined });
      setMessages([...next, { role: "assistant", content: out.content }]);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
      setMessages([...next, { role: "assistant", content: `[error] ${msg}` }]);
    } finally {
      setLoading(false);
    }
  }, [input, messages, loading, model]);

  useEffect(() => {
    if (messages.length === 0 && !loading) {
      setMessages([{ role: "assistant", content: "Local chat uses POST /api/v1/chat \u2192 your OpenAI-compatible endpoint (default Ollama at TAILSCALE_SAMPLING_BASE_URL). This is separate from MCP sampling in the IDE." }]);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const exportChat = () => {
    const text = messages.map((m) => `[${m.role.toUpperCase()}] ${m.content}`).join("\n\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = "tailscale-chat.txt"; a.click();
    URL.revokeObjectURL(url);
  };

  const clearChat = () => { setMessages([]); };

  return (
    <div data-testid="chat-page" className="flex h-[calc(100vh-8rem)] flex-col space-y-4">
      <div data-testid="chat-controls" className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Local chat</h2>
          <p className="text-slate-400">HTTP proxy to Ollama / LM Studio (OpenAI-compatible). Optional model override below.</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 bg-slate-800 px-2 py-1 rounded">skill:tailscale-expert</span>
          <select data-testid="personality-select" className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200" value={personality} onChange={(e) => setPersonality(e.target.value)}>
            {Object.keys(PERSONALITIES).map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
          <button data-testid="chat-export" onClick={exportChat} disabled={messages.length === 0} className="p-1.5 rounded hover:bg-slate-800 text-slate-400 disabled:opacity-30" title="Export"><Download className="h-4 w-4" /></button>
          <button data-testid="chat-clear" onClick={clearChat} disabled={messages.length === 0} className="p-1.5 rounded hover:bg-slate-800 text-slate-400 disabled:opacity-30" title="Clear"><Eraser className="h-4 w-4" /></button>
        </div>
      </div>

      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="flex w-full max-w-xs flex-col gap-1">
          <label className="text-xs text-slate-500">Model override (optional)</label>
          <input className="w-full bg-slate-900 border border-slate-800 rounded px-2 py-1 text-sm text-slate-100 font-mono" value={model} onChange={(e) => setModel(e.target.value)} placeholder="e.g. llama3.2" />
        </div>
      </div>

      {error && <p className="text-sm text-amber-400">{error}</p>}

      <div className="flex-1 overflow-y-auto space-y-4">
        {messages.map((m, i) => (
          <div key={i} className="flex gap-3">
            <div className={`h-8 w-8 shrink-0 flex items-center justify-center rounded-full border ${m.role === "user" ? "border-slate-700 bg-slate-800" : "border-blue-800 bg-blue-950/30"}`}>
              {m.role === "user" ? <User className="h-4 w-4 text-slate-400" /> : <Bot className="h-4 w-4 text-blue-400" />}
            </div>
            <div className="min-w-0 flex-1">
              <div className="mb-1 text-xs font-medium text-slate-500">{m.role === "user" ? "You" : "Assistant"}</div>
              <div className="whitespace-pre-wrap rounded-md border border-slate-800 bg-slate-900/50 p-3 text-sm text-slate-300">{m.content}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 pl-11 text-sm text-slate-500">
            <Loader2 className="h-4 w-4 animate-spin" /> Thinking\u2026
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      <div data-testid="example-prompts" className="flex flex-wrap gap-2">
        {EXAMPLE_PROMPTS.map((group) => (
          <div key={group.group} className="flex flex-wrap items-center gap-1">
            <span className="text-xs text-slate-500 mr-1">{group.group}:</span>
            {group.prompts.map((p) => (
              <button key={p} onClick={() => setInput(p)} className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded">{p}</button>
            ))}
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input data-testid="chat-input" className="flex-1 resize-none rounded-md border border-slate-800 bg-slate-950 px-4 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="Message\u2026" value={input}
          onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }} />
        <button data-testid="chat-send" onClick={() => send()} disabled={loading} className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-md">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </button>
      </div>

      <p className="text-xs text-slate-500">
        <MessageSquare className="mr-1 inline h-3 w-3" />
        Tool calls from the IDE still use <span className="font-mono">/mcp</span>; this page is LLM chat only.
      </p>
    </div>
  );
}
