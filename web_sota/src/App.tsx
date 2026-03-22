import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/app-layout';
import { Dashboard } from '@/pages/dashboard';
import { Stats } from '@/pages/stats';
import { Control } from '@/pages/control';
import { Nets } from '@/pages/nets';
import { Funnels } from '@/pages/funnels';
import { Services } from '@/pages/services';
import { LmLink } from '@/pages/lm-link';
import { Visualizer } from '@/pages/visualizer';
import { Chat } from '@/pages/chat';
import { Settings } from '@/pages/settings';
import { Help } from '@/pages/Help';
import { McpConnection } from '@/pages/mcp-connection';
import { Runbook } from '@/pages/runbook';
import { ToolsExplorer } from '@/pages/tools-explorer';
import { LlmStatus } from '@/pages/llm-status';
const MyTailnet = lazy(async () => {
  const m = await import('@/pages/my-tailnet');
  return { default: m.MyTailnet };
});
const PartnerTailnets = lazy(async () => {
  const m = await import('@/pages/partner-tailnets');
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
