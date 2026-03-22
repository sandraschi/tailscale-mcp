const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:10821";

export type ToolInfo = {
  name: string;
  description: string;
  inputSchema?: unknown;
};

export async function listTools(): Promise<{ tools: ToolInfo[] }> {
  const res = await fetch(`${API_BASE}/api/v1/tools`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function callTool(
  name: string,
  args: Record<string, unknown> = {}
): Promise<{ data?: unknown; content?: Array<{ text?: string }>; is_error?: boolean }> {
  const res = await fetch(`${API_BASE}/api/v1/tools/call`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, arguments: args }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const json = await res.json();
  return {
    data: json.data ?? json.result?.data,
    content: json.result?.content ?? json.content,
    is_error: json.is_error,
  };
}

export type SamplingStatus = {
  sampling_base_url: string;
  sampling_model: string;
  sampling_api_key_configured: boolean;
  use_client_llm: boolean;
};

export async function fetchSamplingStatus(): Promise<SamplingStatus> {
  const res = await fetch(`${API_BASE}/api/v1/sampling-status`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export type LlmHealth = {
  reachable: boolean;
  endpoint_tried: string | null;
  http_status: number | null;
  detail: string | null;
  models_sample: string[] | null;
};

export async function fetchLlmHealth(): Promise<LlmHealth> {
  const res = await fetch(`${API_BASE}/api/v1/llm-health`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export type ChatMessage = { role: "user" | "assistant" | "system"; content: string };

export async function chatComplete(
  messages: ChatMessage[],
  options?: { model?: string; temperature?: number; max_tokens?: number }
): Promise<{ content: string; model: string }> {
  const res = await fetch(`${API_BASE}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      messages,
      model: options?.model,
      temperature: options?.temperature ?? 0.7,
      max_tokens: options?.max_tokens ?? 1024,
    }),
  });
  if (!res.ok) {
    let detail = "";
    try {
      const j = await res.json();
      detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail ?? j);
    } catch {
      detail = await res.text();
    }
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export { API_BASE };
