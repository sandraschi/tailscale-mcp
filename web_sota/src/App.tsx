import { AppLayout } from "@/components/layout/app-layout";
import { Help } from "@/pages/Help";
import { Chat } from "@/pages/chat";
import { Control } from "@/pages/control";
import { Dashboard } from "@/pages/dashboard";
import { Funnels } from "@/pages/funnels";
import { LlmStatus } from "@/pages/llm-status";
import { LmLink } from "@/pages/lm-link";
import { Logs } from "@/pages/logs";
import { McpConnection } from "@/pages/mcp-connection";
import { Nets } from "@/pages/nets";
import { Runbook } from "@/pages/runbook";
import { Services } from "@/pages/services";
import { Settings } from "@/pages/settings";
import { Stats } from "@/pages/stats";
import { ToolsExplorer } from "@/pages/tools-explorer";
import { Visualizer } from "@/pages/visualizer";
import { Suspense, lazy } from "react";
import {
	Navigate,
	Route,
	BrowserRouter as Router,
	Routes,
} from "react-router-dom";
const MyTailnet = lazy(async () => {
	const m = await import("@/pages/my-tailnet");
	return { default: m.MyTailnet };
});
const PartnerTailnets = lazy(async () => {
	const m = await import("@/pages/partner-tailnets");
	return { default: m.PartnerTailnets };
});

function App() {
	return (
		<Router>
			<AppLayout>
				<Suspense fallback={<div className="p-8 text-slate-400">Loading…</div>}>
					<Routes>
						<Route path="/" element={<Dashboard />} />
						<Route path="/stats" element={<Stats />} />
						<Route path="/devices" element={<Control />} />
						<Route path="/my-tailnet" element={<MyTailnet />} />
						<Route path="/partner-tailnets" element={<PartnerTailnets />} />
						<Route path="/nets" element={<Nets />} />
						<Route path="/funnels" element={<Funnels />} />
						<Route path="/services" element={<Services />} />
						<Route path="/lm-link" element={<LmLink />} />
						<Route path="/visualizer" element={<Visualizer />} />
						<Route path="/mcp-connection" element={<McpConnection />} />
						<Route path="/runbook" element={<Runbook />} />
						<Route path="/tools-explorer" element={<ToolsExplorer />} />
						<Route path="/llm-status" element={<LlmStatus />} />
						<Route path="/logs" element={<Logs />} />
						<Route path="/chat" element={<Chat />} />
						<Route path="/settings" element={<Settings />} />
						<Route path="/help" element={<Help />} />
						<Route path="*" element={<Navigate to="/" replace />} />
					</Routes>
				</Suspense>
			</AppLayout>
		</Router>
	);
}

export default App;
