# Tailscale Funnel - Fleet Public Hub

**Mirror copy** - canonical document:
`mcp-central-docs/operations/TailscaleFunnel.md`. Keep this file in sync when
the canonical changes; other repos link to the canonical, not here.

---

## What this is

Tailscale Funnel exposes local services on `goliath` to the public internet
on `https://goliath.tailfab45.ts.net` - no port forwarding, no domain, TLS
auto-provisioned. Used as a low-usage public site for a few buddies: docs,
reports, and experiments, all subpages under one hostname with a landing
page at the root.

## Route map (live config)

Source of truth: `tailscale serve status` on goliath.

| Mount | Local target | Service | Auth |
| --- | --- | --- | --- |
| `/` | 127.0.0.1:11157 | Funnel landing page | none (public directory) |
| `/multigpu/` | 127.0.0.1:11136 | Multi-GPU Cluster Recipes playbook | none (public docs) |
| `/intel/` | 127.0.0.1:11027 | Intel Reports Hub | Basic auth except `/intel/public` + `/intel/health` |
| `:11027` (port) | 127.0.0.1:11027 | Intel Reports Hub | tailnet-only |
| `:10443` (port) | 127.0.0.1:10900 | legacy route | tailnet-only |

## Auth model

- Main funnel addresses challenge with **HTTP Basic auth (401 +
  WWW-Authenticate)** - never a 302 redirect, which would break the
  browser auth dialog and lock out outside users with credentials.
- The **`/public` subtree is open**; anything for unauthenticated visitors
  (iPad chatbot webviews cannot answer Basic auth prompts) lives there.
- See the canonical doc for the full policy and rationale.

## CLI notes (current tailscale version)

- Funnel is **per-target**: `tailscale funnel --bg --set-path /x/ http://127.0.0.1:PORT`.
  There is no `tailscale funnel on`; re-run the funnel commands after any
  `tailscale serve` change (serve edits drop the funnel flag).
- Path-prefix-aware apps: use uvicorn `root_path` so the mount path is
  stripped before routing; avoid absolute redirects under a prefix.
- ACL: funnel is a node attribute granted to goliath
  (`nodeAttrs: [{"target": ["100.118.171.110"], "attr": ["funnel"]}]`).

## Adding a public subpage

See the canonical doc's checklist (port registration, start script, serve +
funnel commands, landing-page link, public verification). Idempotent helper:
`mcp-central-docs/scripts/setup-funnel-routes.ps1`.

## Allowed content

Docs/reports/demos: yes (with auth where sensible). Personal data (email,
secrets, DB/windows ops): **tailnet-only, never funneled**. Funnel proxies
to whatever listens locally; the service must be running (502 = down).
