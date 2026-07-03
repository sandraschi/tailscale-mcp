# Tailscale Feature Reference: Funnel, Taildrop, Services, Peer Relays

A standing reference for the Tailscale platform features this MCP server wraps, and a few it doesn't yet. Written because it's easy to forget which feature does what — they sound similar but solve opposite problems.

**Last verified against Tailscale's own docs:** 2026-06-20.

---

## The one-line summary

| Feature | Direction | Status | What it's for |
|---|---|---|---|
| **Funnel** | Outward — your service → public internet | Beta | Share a local service with anyone, even non-Tailscale users |
| **Taildrop** | Inward — your device → your other devices | Alpha (opt-in) | Move files between your own tailnet devices, no third-party server |
| **Services** | N/A — naming layer | GA | Give a stable name to an internal endpoint instead of an IP |
| **Peer Relays** | N/A — connectivity layer | GA (Feb 2026) | Keep connections fast when NAT/firewalls block a direct path |

If you only remember one thing: **Funnel goes out to the world, Taildrop stays inside your tailnet.** They are not variations on the same feature — they're opposites.

---

## Funnel

**What it is.** Tailscale Funnel routes traffic from the public internet to a local service running on one of your tailnet devices. The person you share it with does **not** need Tailscale installed — they just open a URL. You get a real `*.ts.net` HTTPS endpoint with an automatically provisioned, browser-trusted certificate — no buying a domain, no Let's Encrypt setup, no port forwarding.

**Status:** beta, available on all plans (including free Personal). Requires Tailscale client v1.38.3+.

**When to actually use it:**
- Sharing a local dev server or demo with someone outside your tailnet (a client, a collaborator who doesn't run Tailscale)
- Testing a webhook receiver without waiting for a cloud deploy on every change — point GitHub/Stripe/whatever at a stable Funnel URL once
- Exposing a small static site, file, or directory for the duration of a conversation
- A throwaway file server (`tailscale funnel /path/to/dir`) — faster to set up than `python -m http.server` + ngrok

**When *not* to use it:**
- Fleet-internal traffic between your own devices — that's already flowing over the tailnet without Funnel; Funnel is specifically for the part of the world that *isn't* on your tailnet
- Anything that needs to stay private — Funnel makes a service genuinely public; treat the URL like you'd treat any other public endpoint (add auth if the service itself doesn't have any)
- Long-term production hosting — Funnel is explicitly built for ephemeral sharing, not a permanent ingress layer

**Prerequisites:**
1. Tailscale client v1.38.3 or later on the serving device
2. Funnel enabled in your tailnet's ACL policy (the `funnel` node attribute)
3. The local service already running on the port you want to expose

**MCP tool:** `manage_funnel`

| Operation | What it does |
|---|---|
| `funnel_enable` | Expose a port; returns the public URL |
| `funnel_disable` | Stop exposing a port (or all ports if none specified) |
| `funnel_status` | Current Funnel state for this device |
| `funnel_list` | All active Funnels |
| `funnel_certificate_info` | TLS cert details for a Funnel port |

```python
# Enable
manage_funnel(operation="funnel_enable", port=8080)

# Check what's live
manage_funnel(operation="funnel_list")

# Turn it off when done — Funnel is meant to be temporary
manage_funnel(operation="funnel_disable", port=8080)
```

**Funnel vs. device sharing:** if you want to give one specific person ongoing, ACL-governed access to a device (not just one service), use Tailscale's device-sharing/node-sharing feature instead — that's a different mechanism, outside what `manage_funnel` covers. Funnel is for "share this one thing, briefly, with anyone with the link."

---

## Taildrop

**What it is.** Taildrop sends files directly between devices on your own tailnet — peer-to-peer, end-to-end encrypted, no intermediate server. It's the opposite of Funnel: strictly internal, never touches the public internet.

**Status:** still **alpha**, not beta. This is worth remembering precisely because it's easy to assume a feature this commonly mentioned has graduated — it hasn't, as of this writing. You must explicitly opt your tailnet in via the admin console before Taildrop calls will work at all.

**When to use it:** moving a file from your phone to Goliath, from a coffeeshop laptop back to the home server, between any two of your own tailnet devices — including NAS targets (Synology etc. need a small one-time folder setup, documented in Tailscale's own KB).

**MCP tool:** `manage_taildrop`

| Operation | What it does |
|---|---|
| `send` | Send a file to a named device |
| `receive` | Pull pending incoming files |
| `list` | List in-flight/completed transfers |
| `cancel` | Cancel a transfer |
| `status` | Status of one transfer |
| `stats` | Aggregate transfer statistics |
| `cleanup` | Clear expired transfer records |

```python
manage_taildrop(
    operation="send",
    file_path="/path/to/file",
    recipient_device="goliath",
    expire_hours=24,
)
```

**If calls fail with something like "Taildrop not enabled":** that's the alpha opt-in gate — check the admin console setting before assuming the MCP server is broken.

---

## Tailscale Services

**What it is.** A newer addition: named, taggable endpoints for things running on your tailnet, so ACLs and DNS can reference "the printer" or "the home-lab API" by stable name instead of chasing IPs around as devices come and go. Useful once a tailnet has enough moving parts that IP-based policy gets unwieldy — which, with 140+ MCP servers and a robotics fleet, is a reasonable description of this setup.

**Status:** GA.

**MCP tool:** `manage_tailnet_network` (Services share this tool with DNS/MagicDNS/policy operations — it's a broader network-management portmanteau, not Services-only)

| Operation | What it does |
|---|---|
| `services_list` | List configured Services |
| `services_get` | Get one Service by ID |
| `services_create` | Define a new Service |
| `services_update` | Modify an existing Service |
| `services_delete` | Remove a Service |

---

## Peer Relays

**What it is.** A tailnet-native relay you run yourself on one of your own nodes, for the cases where two devices can't establish a direct WireGuard path (hard NAT, restrictive corporate/coffeeshop firewalls). Tailscale's managed DERP relay network is the default fallback when direct connection fails; Peer Relays let you run that fallback on your own infrastructure instead, with materially higher throughput and full observability — still no public ports exposed, the relay node just needs to be a normal authenticated tailnet member.

**Status:** GA since February 2026 (was beta before that). Requires Tailscale client v1.86+. Works on any OS for the relay role except iOS, Apple TV, and Android — client devices connecting through it can be anything.

**Why this is worth knowing for the Goliath/coffeeshop setup:** if Goliath goes to sleep and you're working from a coffeeshop laptop behind a restrictive NAT, a Peer Relay on an always-on node (the Plex mini-PC, say) is a more controllable fallback path than depending entirely on Tailscale's managed DERP servers — same idea as the WoL relay already living there, just for connectivity instead of wake.

**Not yet wrapped as a dedicated portmanteau operation in `tailscale-mcp`.** Configure via the Tailscale CLI or admin console for now (`tailscale set --relay-server-port=<port>` on the relay node, then advertise it). Worth a future tool addition if it ends up load-bearing for the fleet.

---

## Quick decision tree

```
Need to share something with someone OUTSIDE your tailnet?
  → Funnel

Need to move a file between two of YOUR OWN devices?
  → Taildrop (check it's opted in — still alpha)

Need a stable name for an internal endpoint instead of an IP?
  → Services

Two of your devices can't connect directly (NAT/firewall)?
  → Peer Relays (or just let DERP handle it automatically — only
    self-host a relay if you want the throughput/control)
```

---

## Sources

- [Tailscale Funnel docs](https://tailscale.com/docs/features/tailscale-funnel) — beta status confirmed 2026-01-20
- [Tailscale Funnel examples](https://tailscale.com/docs/reference/examples/funnel)
- [Funnel vs. sharing devices](https://tailscale.com/docs/reference/funnel-vs-sharing)
- [Taildrop docs](https://tailscale.com/kb/1106/taildrop) — alpha status confirmed 2026-01-05
- [Taildrop + NAS setup](https://tailscale.com/kb/1418/taildrop-nas)
- [Tailscale Peer Relays GA announcement](https://tailscale.com/blog/peer-relays-ga) — 2026-02-18
- [Tailscale March 2026 product update](https://tailscale.com/blog/march-26-product-update) — Services GA, Peer Relays GA, workload identity federation
