# Tailscale Troubleshooting

**Last Updated**: 2026-08-15
**Scope**: tailnet and Tailscale-Serve issues that surface through this repo's fleet usage.
**Fleet-level writeup**: [mcp-central-docs integrations/tailscale/TROUBLESHOOTING.md](https://github.com/sandraschi/mcp-central-docs/blob/master/integrations/tailscale/TROUBLESHOOTING.md)
**Upstream bug**: [tailscale/tailscale #19147](https://github.com/tailscale/tailscale/issues/19147) (open, OS-ios)

---

## 1. iOS devices cannot reach Tailscale Serve endpoints (ping and Taildrop still work)

**Incident**: 2026-08-15, tailnet `tailfab45.ts.net`. iPads connected to the tailnet could
ping goliath's tailnet IP and receive Taildrop files, but Safari could not load any
served endpoint (HTTPS on :11027, plain HTTP on :80, even a direct plain-HTTP listener
on the tailnet IP). Everything worked from the host itself and from the LAN IP.

### The trap

This symptom set *looks* like an iOS/Tailscale bug (there IS an open upstream issue,
#19147, with the same presentation) and like a MagicDNS problem, but the actual root
cause was the **tailnet ACL policy**: it had no `ip` grant at all.

- ACLs in the `grants` model only filter **TCP/UDP**. **ICMP ping always passes** and
  **Taildrop is an app capability**, not an IP grant.
- So: ping works, Taildrop works, every TCP connection is silently dropped
  **on the sending device** (Tailscale enforces the policy client-side from the
  netmap). The host never even sees the SYN.

### Diagnostic signature

| Check | Result when ACL is the culprit |
|---|---|
| ping `<tailnet-ip>` from remote device | works |
| Taildrop to/from remote device | works |
| Any TCP (HTTP/HTTPS/SMB) from remote device | fails, on *every* port |
| Same TCP from the host to its own tailnet IP | works (local delivery bypasses the policy) |
| Same TCP from the remote device to the host's **LAN IP** | works (no tailnet involved) |
| Server-side connection watch during a remote attempt | **no SYN ever arrives** |

The LAN-IP test is the highest-value discriminator: it proves the app and the browser
are fine and the failure lives inside the tailnet policy.

### How the policy was broken

The stored ACL was the admin-console default template with the allow-all rule
commented out:

```json
"grants": [
    //{"src": ["*"], "dst": ["*"], "ip": ["*"]},   // <-- commented out
    {
        "src": ["autogroup:member"],
        "dst": ["autogroup:member"],
        "app": { "tailscale.com/cap/drive": [ { "shares": ["*"], "access": "rw" } ] }
    }
]
```

A grant that carries only `app` capabilities grants **no IP connectivity**. The
tailnet effectively denied every TCP/UDP connection between members while
Taildrive (and Taildrop) still worked.

### Fix (Admin API)

Read the policy, then POST a policy that includes an explicit IP grant:

```powershell
# read
$r = Invoke-WebRequest -Uri "https://api.tailscale.com/api/v2/tailnet/$TAILNET/acl" `
    -Headers @{ Authorization = "Basic $auth" } -Method GET

# write (policy must include the ip grant)
$body = '{
  "nodeAttrs": [ { "target": ["autogroup:member"], "attr": ["drive:share","drive:access"] } ],
  "grants": [
    { "src": ["autogroup:member"], "dst": ["autogroup:member"], "ip": ["*"] },
    { "src": ["autogroup:member"], "dst": ["autogroup:member"],
      "app": { "tailscale.com/cap/drive": [ { "shares": ["*"], "access": "rw" } ] } }
  ],
  "ssh": [ { "action": "check", "src": ["autogroup:member"], "dst": ["autogroup:self"],
             "users": ["autogroup:nonroot","root"] } ]
}'
Invoke-WebRequest -Uri "https://api.tailscale.com/api/v2/tailnet/$TAILNET/acl" `
    -Headers @{ Authorization = "Basic $auth"; "Content-Type" = "application/hujson" } `
    -Method POST -Body ([Text.Encoding]::UTF8.GetBytes($body))
```

Notes:

- Do NOT surgically edit the stored HuJSON with string replacement. The template's
  arrays (`nodeAttrs`, `grants`, `ssh`) all close with the same `},` / `],` pattern
  and the parser rejects the result. POST a clean hand-written policy instead.
- Policy propagation to devices takes seconds; on iOS toggle the VPN off/on to force
  a netmap refresh if the first attempt still fails.
- `tailscale serve` HTTPS endpoints return 404 for requests made to the raw IP
  (serve routes by hostname) and iOS Safari cannot bypass the hostname-bound
  certificate for IP access. Use the `.ts.net` hostname for HTTPS, or plain HTTP
  against a listener that is not shadowed by a serve route.

### Prevention checklist

- [ ] ACL grants must include an explicit `ip` grant for member-to-member traffic
- [ ] After any ACL edit, test from a *remote* device (not the host): TCP to a served
      port, not just ping
- [ ] `tailscale serve status` shows the expected routes and `tailscale status`
      shows peers online via relay or direct

---

## 2. iOS confounders that look like the same bug

- **Certificate hostname binding**: iOS Safari cannot proceed past a certificate
  mismatch. `https://<tailnet-ip>:port` always fails; use the `.ts.net` hostname.
- **VPN extension suspension**: iOS tears down the Tailscale VPN extension when the
  app is backgrounded or the device locks. Test with the app foregrounded
  (iPadOS Split View works well).
- **Upstream #19147**: an open bug where iPhone/iPad fail on Serve HTTPS endpoints
  even with a healthy server side. If your tailnet ACL is correct and the hostname
  HTTPS URL still fails on iOS while the LAN IP works, this bug is the suspect;
  plain-HTTP direct listeners are the workaround.
