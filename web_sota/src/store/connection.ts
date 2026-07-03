import { create } from "zustand";

export type ConnectionState = "connecting" | "connected" | "offline" | "error";
type Store = {
  state: ConnectionState;
  lastError: string | null;
};

export const useConnection = create<Store>(() => ({
  state: "connecting",
  lastError: null,
}));

// Poll helpers — exported for the root component to start/stop
let _timer: ReturnType<typeof setTimeout> | null = null;
const _BACKOFF = [0, 1, 2, 4, 8, 16, 30];
let _attempt = 0;

async function _tick() {
  try {
    const r = await fetch("http://127.0.0.1:10821/health", {
      signal: AbortSignal.timeout(5000),
    });
    if (r.ok) {
      useConnection.setState({ state: "connected", lastError: null });
      _attempt = 0;
      _timer = setTimeout(_tick, 10000); // steady 10s poll while connected
      return;
    } else {
      useConnection.setState({ state: "offline", lastError: `HTTP ${r.status}` });
    }
  } catch (e) {
    useConnection.setState({
      state: "offline",
      lastError: e instanceof Error ? e.message : "Network error",
    });
  }
  _attempt = Math.min(_attempt + 1, _BACKOFF.length - 1);
  _timer = setTimeout(_tick, _BACKOFF[_attempt] * 1000);
}

export function startHealthPoll() { _tick(); }

export function stopHealthPoll() { if (_timer) clearTimeout(_timer); }