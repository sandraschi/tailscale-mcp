import { ExternalLink } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";

export function Help() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Help</h2>
        <p className="text-slate-400">
          MCP tool <span className="font-mono text-slate-300">get_help</span>{" "}
          mirrors these topics; use{" "}
          <span className="font-mono">topic=&quot;sampling&quot;</span> for
          SEP-1577 and credentials. Click a section to expand it.
        </p>
      </div>

      <Accordion
        type="multiple"
        defaultValue={["features"]}
        className="rounded-lg border border-slate-800 bg-slate-950/50 px-4"
      >
        <AccordionItem value="credentials">
          <AccordionTrigger>Credentials and non-mock testing</AccordionTrigger>
          <AccordionContent className="space-y-3 text-sm text-slate-300">
            <p className="text-slate-400">
              Put real values in a <span className="font-mono">.env</span> file
              at the repository root (copy from{" "}
              <span className="font-mono">.env.example</span>). The Python
              server loads it via python-dotenv;{" "}
              <span className="font-mono">.env</span> is gitignored—do not
              commit API keys.
            </p>
            <p>
              <strong className="text-slate-200">
                Required for Tailscale Admin API:
              </strong>{" "}
              <span className="font-mono">TAILSCALE_API_KEY</span>,{" "}
              <span className="font-mono">TAILSCALE_TAILNET</span>
            </p>
            <p className="text-slate-400">
              After restarting the MCP server or webapp backend, tools call the
              live API (not mock data). Credentials are loaded once at process
              start — if a key was rotated after the process started, restart it
              rather than just re-saving <span className="font-mono">.env</span>
              .
            </p>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="sampling">
          <AccordionTrigger>SEP-1577 / sampling</AccordionTrigger>
          <AccordionContent className="text-sm text-slate-300">
            <p className="mb-2 text-slate-400">
              <span className="font-mono">run_agentic_tailnet_workflow</span>{" "}
              uses FastMCP sampling with tools. Optional environment variables:
            </p>
            <ul className="list-inside list-disc space-y-1 font-mono text-xs text-slate-400 sm:text-sm">
              <li>
                TAILSCALE_SAMPLING_BASE_URL (default Ollama
                http://127.0.0.1:11434/v1)
              </li>
              <li>TAILSCALE_SAMPLING_MODEL</li>
              <li>
                TAILSCALE_SAMPLING_API_KEY (cloud APIs; often omit for local
                Ollama)
              </li>
              <li>
                TAILSCALE_SAMPLING_USE_CLIENT_LLM=1 — MCP host performs sampling
              </li>
            </ul>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="features">
          <AccordionTrigger>
            Funnel, Taildrop, Services &amp; Peer Relays — what each one does
          </AccordionTrigger>
          <AccordionContent className="space-y-5 text-sm text-slate-300">
            <p className="text-slate-400">
              Four Tailscale features that are easy to mix up. Quick reference —
              full detail in the fleet docs linked below.
            </p>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <strong className="text-slate-200">Funnel</strong>
                <Badge
                  variant="outline"
                  className="border-amber-700 text-amber-400"
                >
                  beta
                </Badge>
              </div>
              <p className="text-slate-400">
                Expose a local service to the{" "}
                <strong className="text-slate-300">public internet</strong> over
                HTTPS — anyone with the link, no Tailscale required on their
                end. Auto TLS cert, no port forwarding. Use it for: sharing a
                dev server demo with a client, testing a webhook receiver,
                exposing a docs preview. It is <em>not</em> for fleet-internal
                traffic — that already flows over the tailnet without Funnel.
                Tool:{" "}
                <span className="font-mono text-slate-300">manage_funnel</span>{" "}
                (operations: funnel_enable, funnel_disable, funnel_status,
                funnel_list, funnel_certificate_info). Requires the{" "}
                <span className="font-mono">funnel</span> node attribute in your
                ACL policy.
              </p>
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <strong className="text-slate-200">Taildrop</strong>
                <Badge
                  variant="outline"
                  className="border-red-800 text-red-400"
                >
                  alpha — opt-in required
                </Badge>
              </div>
              <p className="text-slate-400">
                Send files{" "}
                <strong className="text-slate-300">
                  between your own devices
                </strong>{" "}
                on the tailnet, peer-to-peer and encrypted — no upload to a
                third-party server. Tailnet-internal only (the opposite of
                Funnel). Still alpha: opt your tailnet in via the admin console
                before tools will work. Tool:{" "}
                <span className="font-mono text-slate-300">
                  manage_taildrop
                </span>{" "}
                (send, receive, list, cancel, status, stats, cleanup).
              </p>
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <strong className="text-slate-200">Tailscale Services</strong>
                <Badge
                  variant="outline"
                  className="border-emerald-700 text-emerald-400"
                >
                  GA
                </Badge>
              </div>
              <p className="text-slate-400">
                Named, taggable application endpoints on the tailnet (think "the
                printer" or "the home-lab API" as a stable name, not just an
                IP). Newer addition to the platform — useful once a tailnet has
                enough devices that IP-based ACLs get unwieldy. Tool:{" "}
                <span className="font-mono text-slate-300">
                  manage_tailnet_network
                </span>{" "}
                (operations: services_list, services_get, services_create,
                services_update, services_delete).
              </p>
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <strong className="text-slate-200">Peer Relays</strong>
                <Badge
                  variant="outline"
                  className="border-emerald-700 text-emerald-400"
                >
                  GA (Feb 2026)
                </Badge>
              </div>
              <p className="text-slate-400">
                A tailnet-native, customer-deployed relay for when two devices
                can't establish a direct connection (hard NAT, restrictive
                firewalls). Higher throughput than Tailscale's managed DERP
                fallback, and it's just another tailnet node — no public IP or
                port exposure needed. Not yet wrapped as a dedicated portmanteau
                operation in this server; configure via the Tailscale CLI/admin
                console for now.
              </p>
            </div>
            <p className="text-xs text-slate-500 pt-1">
              One-line summary: <strong>Funnel</strong> = share outward to the
              public internet. <strong>Taildrop</strong> = move files inward
              between your own devices. <strong>Services</strong> = name your
              internal endpoints. <strong>Peer Relays</strong> = keep
              connections fast when NAT gets in the way.
            </p>
            <a
              className="inline-flex items-center gap-2 text-xs text-blue-400 hover:text-blue-300"
              href="https://github.com/sandraschi/tailscale-mcp/blob/main/docs/FEATURES.md"
              target="_blank"
              rel="noopener noreferrer"
            >
              Full reference — docs/FEATURES.md
              <ExternalLink className="h-3 w-3" />
            </a>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="pages">
          <AccordionTrigger>Webapp pages</AccordionTrigger>
          <AccordionContent className="text-sm text-slate-400">
            <p className="mb-2">
              MCP &amp; API, Runbook, Tool explorer, LLM status, and Local chat
              are in the sidebar.
            </p>
            Use{" "}
            <span className="font-mono text-slate-300">/mcp-connection</span>,{" "}
            <span className="font-mono text-slate-300">/runbook</span>,{" "}
            <span className="font-mono text-slate-300">/tools-explorer</span>,{" "}
            <span className="font-mono text-slate-300">/llm-status</span>,{" "}
            <span className="font-mono text-slate-300">/my-tailnet</span>,{" "}
            <span className="font-mono text-slate-300">/partner-tailnets</span>,{" "}
            <span className="font-mono text-slate-300">/chat</span>.
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="resources">
          <AccordionTrigger>Resources</AccordionTrigger>
          <AccordionContent className="flex flex-col gap-2 text-sm">
            <a
              className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300"
              href="https://tailscale.com/api"
              target="_blank"
              rel="noopener noreferrer"
            >
              Tailscale API reference
              <ExternalLink className="h-4 w-4" />
            </a>
            <p className="text-slate-500">
              MCP resource{" "}
              <span className="font-mono text-slate-400">
                resource://tailscale/skills
              </span>{" "}
              — expert notes from{" "}
              <span className="font-mono">skills/TAILSCALE_EXPERT.md</span>
            </p>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
