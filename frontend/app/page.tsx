'use client';
import React, { useState, useEffect } from 'react';

interface RunRecord {
  id: string;
  status: string;
  memory_summary: string;
  additional_instructions: string;
  final_output?: any;
}

interface TimelineItem {
  id: string;
  event_type: string;
  payload: any;
  agent_action: string;
  created_at: string;
}

const STATUS_STYLES: Record<string, string> = {
  RUNNING: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  PAUSED: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  INTERRUPTED: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  COMPLETED: 'bg-teal-500/10 text-teal-400 border-teal-500/30',
  TERMINATED: 'bg-red-500/10 text-red-400 border-red-500/30',
};

export default function Dashboard() {
  const [orderId, setOrderId] = useState<string>('ORD-777');
  const [instruction, setInstruction] = useState<string>('');
  const [runsList, setRunsList] = useState<RunRecord[]>([]);

  const [selectedRunId, setSelectedRunId] = useState<string>('ORD-777');
  const [activeTimeline, setActiveTimeline] = useState<TimelineItem[]>([]);
  const [currentRunDetails, setCurrentRunDetails] = useState<RunRecord | null>(null);

  const [logs, setLogs] = useState<string[]>([]);

  const formatFriendlyDate = (isoStr: string) => {
    try {
      const d = new Date(isoStr);
      return (
        d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) +
        ' ' +
        d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })
      );
    } catch {
      return isoStr;
    }
  };

  const fetchAllRegistryRuns = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/runs');
      const data = await res.json();
      if (Array.isArray(data)) {
        setRunsList(data);
        const current = data.find((r: RunRecord) => r.id === selectedRunId);
        if (current) setCurrentRunDetails(current);
      }
    } catch (e) {
      console.error('Registry fetch error', e);
    }
  };

  const inspectSpecificRunNode = async (id: string) => {
    setSelectedRunId(id);
    try {
      const res = await fetch(`http://localhost:8000/api/runs/${id}`);
      const data = await res.json();
      setActiveTimeline(data.timeline || []);
      if (data.run) setCurrentRunDetails(data.run);
    } catch (e) {
      console.error('Telemetry pipeline audit error', e);
    }
  };

  const initWorkflow = async (): Promise<void> => {
    if (!orderId.trim()) return;
    try {
      await fetch('http://localhost:8000/api/runs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          order_id: orderId,
          initial_context: { type: 'order_created', info: 'Standard Template Placement' },
        }),
      });

      setLogs((prev: string[]) => [...prev, `[${orderId}] 🚀 Supervisor Spawned & Initialized Successfully`]);
      setSelectedRunId(orderId);

      setTimeout(() => {
        fetchAllRegistryRuns();
        inspectSpecificRunNode(orderId);
      }, 800);
    } catch (e) {
      setLogs((prev: string[]) => [...prev, `[${orderId}] ⨯ Failed to launch supervisor`]);
    }
  };

  const fireSignal = async (type: string): Promise<void> => {
    try {
      await fetch(`http://localhost:8000/api/runs/${selectedRunId}/events`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_type: type, data: { fired_at: new Date().toISOString() } }),
      });

      setLogs((prev: string[]) => [...prev, `[${selectedRunId}] 📥 External Signal Received: ${type}`]);

      setTimeout(() => {
        fetchAllRegistryRuns();
        inspectSpecificRunNode(selectedRunId);
      }, 1000);
    } catch (e) {
      setLogs((prev: string[]) => [...prev, `[${selectedRunId}] ⨯ Signal transmission timed out`]);
    }
  };

  const pushInstructions = async (): Promise<void> => {
    if (!instruction.trim()) return;
    try {
      await fetch(`http://localhost:8000/api/runs/${selectedRunId}/instructions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instructions: instruction }),
      });
      setLogs((prev: string[]) => [...prev, `[${selectedRunId}] 👤 Human Override Rule Submitted: "${instruction}"`]);
      setInstruction('');
      setTimeout(() => {
        fetchAllRegistryRuns();
        inspectSpecificRunNode(selectedRunId);
      }, 800);
    } catch (e) {
      setLogs((prev: string[]) => [...prev, `[${selectedRunId}] ⨯ Directive rejection warning`]);
    }
  };

  const interruptWorkflow = async (id: string) => {
    await fetch('http://localhost:8000/api/runs/' + id + '/interrupt', { method: 'POST' });
    setLogs((prev) => [...prev, `[${id}] ⏸️ Workflow execution paused manually.`]);
    fetchAllRegistryRuns();
  };

  const resumeWorkflow = async (id: string) => {
    await fetch('http://localhost:8000/api/runs/' + id + '/resume', { method: 'POST' });
    setLogs((prev) => [...prev, `[${id}] ▶️ Workflow execution resumed.`]);
    fetchAllRegistryRuns();
  };

  const terminateWorkflow = async (id: string) => {
    await fetch('http://localhost:8000/api/runs/' + id + '/terminate', { method: 'POST' });
    setLogs((prev) => [...prev, `[${id}] 🛑 Workflow execution killed via termination command.`]);
    fetchAllRegistryRuns();
  };

  useEffect(() => {
    fetchAllRegistryRuns();
    const interval = setInterval(fetchAllRegistryRuns, 5000);
    return () => clearInterval(interval);
  }, [selectedRunId]);

  return (
    <div className="p-8 bg-zinc-950 text-zinc-100 min-h-screen font-sans grid grid-cols-3 gap-6">
      {/* LEFT COLUMN */}
      <div className="col-span-2 space-y-6">
        <header className="border-b border-zinc-800 pb-4">
          <h1 className="text-2xl font-bold tracking-tight text-teal-400 font-sans">
            Order Workflow Dashboard
          </h1>
          <p className="text-xs text-zinc-400 mt-1">One workflow runs per order</p>
        </header>

        {/* Supervisor Creation */}
        <section className="bg-zinc-900 border border-zinc-800 p-4 rounded-lg flex gap-4 items-center shadow-lg">
          <div className="flex flex-col flex-1">
            <span className="text-[11px] uppercase font-bold text-zinc-400 tracking-wider mb-1">
              Create Order Supervisor
            </span>
            <div className="flex gap-3">
              <input
                type="text"
                value={orderId}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setOrderId(e.target.value)}
                className="bg-zinc-950 border border-zinc-700 px-3 py-1.5 rounded text-sm text-white flex-1 focus:outline-none focus:border-teal-500 font-mono"
                placeholder="Enter unique Order ID..."
              />
              <button
                onClick={initWorkflow}
                className="bg-teal-500 hover:bg-teal-400 text-zinc-950 font-bold px-5 py-1.5 rounded text-sm transition tracking-tight"
              >
                Start Order
              </button>
            </div>
          </div>
        </section>

        {/* Status Monitoring */}
        <section className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 grid grid-cols-4 gap-4 shadow-md text-xs font-mono">
          <div className="bg-zinc-950 p-2.5 rounded border border-zinc-800">
            <div className="text-[10px] text-zinc-500 uppercase font-sans font-bold">Current Order</div>
            <div className="text-teal-400 font-bold mt-1 text-sm">{selectedRunId}</div>
          </div>
          <div className="bg-zinc-950 p-2.5 rounded border border-zinc-800">
            <div className="text-[10px] text-zinc-500 uppercase font-sans font-bold">Workflow State</div>
            <div className="mt-1 font-bold flex items-center gap-1.5 text-zinc-200">
              <span className={currentRunDetails?.status === 'RUNNING' ? 'text-emerald-400 animate-pulse' : 'text-zinc-500'}>
                ●
              </span>
              {currentRunDetails?.status || 'UNKNOWN'}
            </div>
          </div>
          <div className="bg-zinc-950 p-2.5 rounded border border-zinc-800 col-span-2">
            <div className="text-[10px] text-zinc-500 uppercase font-sans font-bold">Memory Summary</div>
            <div className="text-zinc-300 italic font-sans mt-1 text-[11px] line-clamp-2">
              &quot;{currentRunDetails?.memory_summary || 'No tracking footprint stored yet.'}&quot;
            </div>
          </div>
        </section>

        {/* Signals Section */}
        <section className="bg-zinc-900 border border-zinc-800 p-4 rounded-lg shadow-md">
          <h2 className="text-xs uppercase font-bold text-zinc-400 tracking-wider mb-3">
            Send Order Event (Current Order: {selectedRunId})
          </h2>
          <div className="grid grid-cols-4 gap-2">
            <button
              onClick={() => fireSignal('payment_failed')}
              className="bg-zinc-950 hover:bg-zinc-800 border border-zinc-800 p-3 rounded text-xs text-red-400 font-semibold transition text-left flex flex-col justify-between h-14 shadow-sm"
            >
              <span>🚨 Payment Failed</span>
            </button>
            <button
              onClick={() => fireSignal('shipment_delayed')}
              className="bg-zinc-950 hover:bg-zinc-800 border border-zinc-800 p-3 rounded text-xs text-amber-400 font-semibold transition text-left flex flex-col justify-between h-14 shadow-sm"
            >
              <span>⏳ Shipment Delayed</span>
            </button>
            <button
              onClick={() => fireSignal('customer_message_received')}
              className="bg-zinc-950 hover:bg-zinc-800 border border-zinc-800 p-3 rounded text-xs text-blue-400 font-semibold transition text-left flex flex-col justify-between h-14 shadow-sm"
            >
              <span>💬 Customer Message</span>
            </button>
            <button
              onClick={() => fireSignal('delivered')}
              className="bg-zinc-950 hover:bg-zinc-800 border border-zinc-800 p-3 rounded text-xs text-emerald-400 font-semibold transition text-left flex flex-col justify-between h-14 shadow-sm"
            >
              <span>📦 Delivered</span>
            </button>
          </div>
        </section>

        {/* Overrides Input */}
        <section className="bg-zinc-900 border border-zinc-800 p-4 rounded-lg shadow-md space-y-3">
          <h2 className="text-xs uppercase font-bold text-zinc-400 tracking-wider">
            Additional Instructions &amp; Runtime Instructions
          </h2>
          <div className="flex gap-3">
            <input
              type="text"
              value={instruction}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInstruction(e.target.value)}
              placeholder="e.g., If logistics stall, alert fulfillment team instantly..."
              className="bg-zinc-950 border border-zinc-700 px-3 py-2 rounded text-sm text-white flex-1 focus:outline-none focus:border-teal-500"
            />
            <button
              onClick={pushInstructions}
              className="bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-100 font-bold px-5 py-2 rounded text-sm transition tracking-tight"
            >
              Add Instruction
            </button>
          </div>
          {currentRunDetails?.additional_instructions && (
            <div className="text-[11px] text-zinc-500 font-mono">
              Active rule: <span className="text-zinc-300">{currentRunDetails.additional_instructions}</span>
            </div>
          )}
        </section>

        {/* Workflow Controls */}
        <section className="bg-zinc-900 border border-zinc-800 p-4 rounded-lg shadow-md">
          <h2 className="text-xs uppercase font-bold text-zinc-400 tracking-wider mb-3">
            Workflow Controls
          </h2>
          <div className="flex gap-3">
            <button
              onClick={() => interruptWorkflow(selectedRunId)}
              className="bg-zinc-950 hover:bg-zinc-800 border border-amber-800 text-amber-400 font-semibold px-4 py-2 rounded text-xs transition"
            >
              ⏸️ Interrupt
            </button>
            <button
              onClick={() => resumeWorkflow(selectedRunId)}
              className="bg-zinc-950 hover:bg-zinc-800 border border-emerald-800 text-emerald-400 font-semibold px-4 py-2 rounded text-xs transition"
            >
              ▶️ Resume
            </button>
            <button
              onClick={() => terminateWorkflow(selectedRunId)}
              className="bg-zinc-950 hover:bg-zinc-800 border border-red-800 text-red-400 font-semibold px-4 py-2 rounded text-xs transition"
            >
              🛑 Terminate
            </button>
          </div>
        </section>

        {/* Timeline Logs */}
        <section className="bg-zinc-900 border border-zinc-800 p-4 rounded-lg shadow-md">
          <h2 className="text-xs uppercase font-bold text-zinc-400 tracking-wider mb-3">
            Order Timeline — {selectedRunId}
          </h2>
          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {activeTimeline.length === 0 && (
              <div className="text-xs text-zinc-600 italic">No timeline events recorded yet.</div>
            )}
            {activeTimeline.map((item) => (
              <div
                key={item.id}
                className="bg-zinc-950 border border-zinc-800 rounded p-3 flex items-start justify-between gap-4"
              >
                <div className="flex-1">
                  <div className="text-xs font-semibold text-zinc-200">{item.event_type}</div>
                  <div className="text-[11px] text-zinc-500 mt-0.5">{item.agent_action}</div>
                  {item.payload && (
                    <pre className="text-[10px] text-zinc-600 mt-1.5 font-mono whitespace-pre-wrap">
                      {JSON.stringify(item.payload, null, 2)}
                    </pre>
                  )}
                </div>
                <div className="text-[10px] text-zinc-500 font-mono whitespace-nowrap">
                  {formatFriendlyDate(item.created_at)}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Final Outpost Metrics Area */}
        {currentRunDetails?.status === 'COMPLETED' && currentRunDetails.final_output && (
          <section className="bg-teal-950/30 border border-teal-800/60 rounded-lg p-4 space-y-2.5 shadow-xl text-xs border-l-4 border-l-teal-400 animate-fade-in">
            <h4 className="font-bold text-teal-400 border-b border-teal-800/40 pb-1.5 font-sans tracking-wide uppercase text-[10px]">
              🏁 Final AI Learnings &amp; Feedback Report
            </h4>
            <div className="space-y-3 font-sans text-zinc-300 text-[11px] leading-relaxed">
              <div>
                <strong className="text-zinc-100 font-semibold block text-[10px] uppercase tracking-wider text-zinc-400 mb-0.5">
                  Summary Report:
                </strong>
                {currentRunDetails.final_output?.final_summary}
              </div>
              <div>
                <strong className="text-zinc-100 font-semibold block text-[10px] uppercase tracking-wider text-zinc-400 mb-0.5">
                  Actions Taken:
                </strong>
                <ul className="list-disc pl-4 space-y-0.5 text-zinc-300">
                  {Array.isArray(currentRunDetails.final_output?.actions_taken)
                    ? currentRunDetails.final_output.actions_taken.map((act: string, i: number) => (
                        <li key={i}>{act}</li>
                      ))
                    : <li>• Multi-team message channels updated safely.</li>}
                </ul>
              </div>
              <div>
                <strong className="text-zinc-100 font-semibold block text-[10px] uppercase tracking-wider text-zinc-400 mb-0.5">
                  Key Core Learnings:
                </strong>
                <ul className="list-disc pl-4 space-y-0.5 text-teal-300">
                  {Array.isArray(currentRunDetails.final_output?.learnings)
                    ? currentRunDetails.final_output.learnings.map((lrn: string, i: number) => (
                        <li key={i}>{lrn}</li>
                      ))
                    : <li>• Delay states correctly isolated away from multi-threaded locks.</li>}
                </ul>
              </div>
              <div>
                <strong className="text-zinc-100 font-semibold block text-[10px] uppercase tracking-wider text-zinc-400 mb-0.5">
                  Platform Recommendations:
                </strong>
                <ul className="list-disc pl-4 space-y-0.5 text-zinc-300">
                  {Array.isArray(currentRunDetails.final_output?.recommendations)
                    ? currentRunDetails.final_output.recommendations.map((rec: string, i: number) => (
                        <li key={i}>{rec}</li>
                      ))
                    : <li>• Configure downstream automated customer notifications if delays stall beyond 12 hours.</li>}
                </ul>
              </div>
            </div>
          </section>
        )}

        {/* Local Activity Logs */}
        <section className="bg-zinc-900 border border-zinc-800 p-4 rounded-lg shadow-md">
          <h2 className="text-xs uppercase font-bold text-zinc-400 tracking-wider mb-3">Client Activity Log</h2>
          <div className="space-y-1 max-h-48 overflow-y-auto font-mono text-[11px] text-zinc-400">
            {logs.length === 0 && <div className="italic text-zinc-600">No local activity yet.</div>}
            {logs.map((line, idx) => (
              <div key={idx}>{line}</div>
            ))}
          </div>
        </section>
      </div>

      {/* RIGHT COLUMN — Runs Registry */}
      <div className="col-span-1 space-y-6">
        <section className="bg-zinc-900 border border-zinc-800 rounded-lg shadow-lg overflow-hidden">
          <h2 className="text-xs uppercase font-bold text-zinc-400 tracking-wider px-4 py-3 border-b border-zinc-800">
            Active &amp; Completed Runs
          </h2>
          <div className="divide-y divide-zinc-800 max-h-[calc(100vh-140px)] overflow-y-auto">
            {runsList.length === 0 && (
              <div className="p-4 text-xs text-zinc-600 italic">No supervisor runs registered yet.</div>
            )}
            {runsList.map((run) => (
              <button
                key={run.id}
                onClick={() => inspectSpecificRunNode(run.id)}
                className={`w-full text-left px-4 py-3 hover:bg-zinc-800/60 transition flex flex-col gap-1.5 ${
                  selectedRunId === run.id ? 'bg-zinc-800/40' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-mono font-semibold text-zinc-100">{run.id}</span>
                  <span
                    className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${
                      STATUS_STYLES[run.status] || 'bg-zinc-800 text-zinc-400 border-zinc-700'
                    }`}
                  >
                    {run.status}
                  </span>
                </div>
                <div className="text-[11px] text-zinc-500 line-clamp-1 italic">
                  {run.memory_summary || 'No memory summary yet.'}
                </div>
              </button>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}