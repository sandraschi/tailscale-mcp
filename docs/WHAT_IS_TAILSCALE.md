# What is Tailscale?

**Tailscale** — mesh VPN on [WireGuard](https://www.wireguard.com/); devices join a **tailnet** (`*.tailnet-name.ts.net`).

**This MCP** uses the [**Admin API**](https://tailscale.com/api) (HTTPS), not the desktop client. You need **`TAILSCALE_API_KEY`** + **`TAILSCALE_TAILNET`** ([create a key](https://login.tailscale.com/admin/settings/keys)).

| Term | Meaning |
|------|--------|
| **Tailnet** | Your private network |
| **Admin API** | HTTP API for tailnet admin — what this server calls |
| **Client** | Per-device app; not required on the MCP host for most API calls |

More: [Tailscale KB](https://tailscale.com/kb/1150/what-is-tailscale) · [Trust credentials](https://tailscale.com/docs/reference/trust-credentials) (future)
