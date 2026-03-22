import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Send, MessageSquare, User, Loader2, Bot } from "lucide-react";
import { chatComplete, type ChatMessage } from "@/common/api";

export function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Local chat uses POST /api/v1/chat → your OpenAI-compatible endpoint (default Ollama at TAILSCALE_SAMPLING_BASE_URL). This is separate from MCP sampling in the IDE.",
    },
  ]);
  const [input, setInput] = useState("");
  const [model, setModel] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send() {
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
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Local chat</h2>
          <p className="text-slate-400">
            HTTP proxy to Ollama / LM Studio (OpenAI-compatible). Optional model override below.
          </p>
        </div>
        <div className="flex w-full max-w-xs flex-col gap-1">
          <Label className="text-xs text-slate-500">Model override (optional)</Label>
          <Input
            className="bg-slate-900 border-slate-800 font-mono text-sm text-slate-100"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            placeholder="e.g. llama3.2"
          />
        </div>
      </div>

      {error && <p className="text-sm text-amber-400">{error}</p>}

      <Card className="flex flex-1 flex-col overflow-hidden border-slate-800 bg-slate-950/50">
        <CardContent className="flex flex-1 flex-col overflow-hidden p-0">
          <div className="flex-1 space-y-4 overflow-y-auto p-4">
            {messages.map((m, i) => (
              <div key={i} className="flex gap-3">
                <div
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border ${
                    m.role === "user"
                      ? "border-slate-700 bg-slate-800"
                      : "border-blue-800 bg-blue-950/30"
                  }`}
                >
                  {m.role === "user" ? (
                    <User className="h-4 w-4 text-slate-400" />
                  ) : (
                    <Bot className="h-4 w-4 text-blue-400" />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="mb-1 text-xs font-medium text-slate-500">
                    {m.role === "user" ? "You" : "Assistant"}
                  </div>
                  <div className="whitespace-pre-wrap rounded-md border border-slate-800 bg-slate-900/50 p-3 text-sm text-slate-300">
                    {m.content}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex items-center gap-2 pl-11 text-sm text-slate-500">
                <Loader2 className="h-4 w-4 animate-spin" /> Thinking…
              </div>
            )}
          </div>
          <div className="border-t border-slate-800 bg-slate-900/30 p-4">
            <div className="flex gap-2">
              <input
                className="flex-1 resize-none rounded-md border border-slate-800 bg-slate-950 px-4 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="Message…"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    void send();
                  }
                }}
              />
              <Button
                type="button"
                size="icon"
                className="bg-blue-600 hover:bg-blue-700"
                disabled={loading}
                onClick={() => void send()}
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </Button>
            </div>
            <p className="mt-2 text-xs text-slate-500">
              <MessageSquare className="mr-1 inline h-3 w-3" />
              Tool calls from the IDE still use <span className="font-mono">/mcp</span>; this page is LLM chat only.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
