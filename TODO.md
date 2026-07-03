# tailscale-mcp TODO

## Frontend pages — JSON switchable (Stats,Nets,Funnels,Runbook)
- [ ] Apply `JsonView` component (already in `components/ui/json-view.tsx`) to:
  - `pages/nets.tsx` — DNS config + topology
  - `pages/funnels.tsx` — funnel list + status
  - `pages/runbook.tsx` — automation results
  - `pages/stats.tsx` — DONE (reference impl)
- [ ] Add `import { JsonView } from "@/components/ui/json-view"` to each page
- [ ] Wrap each `<pre>JSON.stringify(...)</pre>` block with `<JsonView data={...} />`
- [ ] Add `render` prop for table/key-value views where useful

## Help page — tabs, organization, usage info
- [ ] Rewrite `pages/Help.tsx` with horizontal `<Tabs>` from @radix-ui/react-tabs
- [ ] Sections: Credentials, Tools, Sampling/Fleet Resources, Troubleshooting, FAQ
- [ ] Each tab: show tool descriptions, example calls, environment vars
- [ ] Pull content from server's `get_help` tool via `callTool("get_help", ...)`

## Logs page — verify 404 is fixed
- [ ] Verify `fetch` changed from `/api/logs` → `POST /api/v1/logs/search`
- [ ] Verify `handleExport` changed from `/api/logs/export` → `/api/v1/logs/export`
- [ ] Remove dead duplicate `pages/Logging.tsx` (capital L, not imported)
- [ ] Verify logs page renders correctly in NSIS build

## API audit — missing endpoints
- [ ] `/api/llm/providers` — DONE (added to server.py)
- [ ] Check `runbook.tsx` — verify it uses `callTool()` (not REST)
- [ ] Dead `Logging.tsx` — remove after verifying no imports

## Mermaid zoom
- [ ] Verified working in `components/tailnet/mermaid-block.tsx` (zoom buttons + Ctrl+wheel)

## Build pipeline hardening
- [ ] Verify `build.ps1` patches fastmcp + pydantic correctly before PyInstaller
- [ ] Run `just build-native` for full NSIS pipeline
- [ ] Verify `ruff check .` passes before release
