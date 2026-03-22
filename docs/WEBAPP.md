# SOTA web dashboard (`Webapp`)

**Stack:** React, TypeScript, Vite, TanStack Query, Radix UI · **Ports:** Follow **WEBAPP_STANDARDS** (central docs) and this repo’s `web_sota\start.ps1` for the allocated frontend/backend pair.

## Purpose

Optional operator UI for Tailscale MCP: device lists, stats, MCP connection notes, **Help** (credentials and sampling env vars), **My tailnet** (topology/orbit), and **Partner tailnets** (members vs shared users, devices-by-login).

## Running locally

From the repo: use `web_sota\start.ps1` (clears ports, build, dev server). Configure API base URL as documented on the **MCP connection** and **Help** pages (e.g. `web_sota\.env` for local dev).

## Routes (high level)

| Path | Role |
|------|------|
| `/` | Dashboard / landing |
| `/devices` | Device list and detail |
| `/settings` | Settings and API references |
| `/help` | Credentials, `.env`, sampling variables |
| `/my-tailnet` | **Mermaid** topology + **Orbit (CSS 3D)** tabs |
| `/partner-tailnets` | **People & sharing**: members vs tailnet-shared users (`tailscale_partner_tailnets` `summary`), Mermaid overview, JSON tabs |
| `/visualizer` | Placeholder; links to **My tailnet** / **Partner tailnets** |
| `/stats`, `/control`, … | Other operator pages as implemented |

## My tailnet (`/my-tailnet`)

1. **Mermaid**  
   - Prefers diagram text from **`tailscale_status`** when called with **`include_mermaid_diagram: true`** (field `mermaid_diagram` in the tool result).  
   - If absent, builds a simple **flowchart** from **`tailscale_device`** `operation: "list"`.  
   - Rendered with the **`mermaid`** npm package. The route is **lazy-loaded** so the main bundle stays smaller.

2. **Orbit (CSS 3D)**  
   - Decorative rotating ring of device nodes (CSS 3D transforms). **Not** geographic positions.

## Backend contract

The UI expects the FastAPI/MCP bridge (or mock) to expose the same operations the tools use; failures should surface API **detail** strings to the user. CORS must allow the Vite dev origin when developing.

## Related

- [PRD.md](PRD.md) — product scope  
- [CHANGELOG](../CHANGELOG.md) — releases **[2.0.2]** (partner tailnets), **[2.0.1]** (My tailnet)  
- [CONTRIBUTING.md](../CONTRIBUTING.md) — Ruff, pre-commit, tests  
