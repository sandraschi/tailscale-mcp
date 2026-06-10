import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	AlertTriangle,
	Bug,
	CheckCircle,
	Download,
	Info,
	RotateCw,
	Search,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:10821";

const LEVEL_COLORS: Record<string, string> = {
	ERROR: "text-red-400",
	WARNING: "text-amber-400",
	WARN: "text-amber-400",
	INFO: "text-sky-400",
	DEBUG: "text-slate-500",
};

const LEVEL_ICONS: Record<string, React.FC<{ className?: string }>> = {
	ERROR: AlertTriangle,
	WARNING: AlertTriangle,
	WARN: AlertTriangle,
	INFO: Info,
	DEBUG: Bug,
};

interface LogEntry {
	timestamp?: string;
	level?: string;
	event?: string;
	logger?: string;
	[key: string]: unknown;
}

type Tab = "tail" | "search" | "export";

export function Logs() {
	const [tab, setTab] = useState<Tab>("tail");
	const [entries, setEntries] = useState<LogEntry[]>([]);
	const [filterLevel, setFilterLevel] = useState("");
	const [filterSearch, setFilterSearch] = useState("");
	const [filterLogger, setFilterLogger] = useState("");
	const [exportFormat, setExportFormat] = useState<"jsonl" | "text">("jsonl");
	const [loading, setLoading] = useState(false);
	const [status, setStatus] = useState<{
		total_lines: number;
		total_bytes: number;
		files: { name: string; size_bytes: number }[];
		rotation: { max_bytes: number; backup_count: number };
	} | null>(null);
	const tailRef = useRef<HTMLDivElement>(null);
	const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

	const fetchTail = useCallback(async () => {
		try {
			const r = await fetch(`${API_BASE}/api/v1/logs/search`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					lines: 200,
					min_level: filterLevel || null,
					search: filterSearch || null,
					logger_name: filterLogger || null,
					tail: true,
					offset: 0,
				}),
			});
			if (!r.ok) return;
			const d = await r.json();
			setEntries(d.lines ?? []);
		} catch {
			/* backend not reachable */
		}
	}, [filterLevel, filterSearch, filterLogger]);

	const fetchAll = useCallback(async () => {
		setLoading(true);
		try {
			const [statusR] = await Promise.all([
				fetch(`${API_BASE}/api/v1/logs/status`),
			]);
			if (statusR.ok) setStatus(await statusR.json());
		} catch {
			/* ignore */
		}
		setLoading(false);
	}, []);

	useEffect(() => {
		fetchAll();
	}, [fetchAll]);

	useEffect(() => {
		if (tab === "tail") {
			fetchTail();
			pollRef.current = setInterval(fetchTail, 3000);
		}
		return () => {
			if (pollRef.current) clearInterval(pollRef.current);
		};
	}, [tab, fetchTail]);

	useEffect(() => {
		if (tailRef.current) {
			tailRef.current.scrollTop = tailRef.current.scrollHeight;
		}
	}, [entries]);

	const handleSearch = async () => {
		setLoading(true);
		try {
			const r = await fetch(`${API_BASE}/api/v1/logs/search`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					lines: 500,
					min_level: filterLevel || null,
					search: filterSearch || null,
					logger_name: filterLogger || null,
					tail: false,
					offset: 0,
				}),
			});
			if (r.ok) {
				const d = await r.json();
				setEntries(d.lines ?? []);
			}
		} catch {
			/* ignore */
		}
		setLoading(false);
	};

	const handleExport = async () => {
		const params = new URLSearchParams({ format: exportFormat });
		if (filterLevel) params.set("min_level", filterLevel);
		if (filterSearch) params.set("search", filterSearch);
		if (filterLogger) params.set("logger_name", filterLogger);

		try {
			const r = await fetch(
				`${API_BASE}/api/v1/logs/export?${params.toString()}`,
			);
			if (!r.ok) return;
			const d = await r.json();
			const blob = new Blob([d.text], {
				type: exportFormat === "jsonl" ? "application/x-ndjson" : "text/plain",
			});
			const url = URL.createObjectURL(blob);
			const a = document.createElement("a");
			a.href = url;
			a.download = `tailscale-logs.${exportFormat === "jsonl" ? "jsonl" : "txt"}`;
			a.click();
			URL.revokeObjectURL(url);
		} catch {
			/* ignore */
		}
	};

	const tabs: { id: Tab; label: string }[] = [
		{ id: "tail", label: "Live Tail" },
		{ id: "search", label: "Search" },
		{ id: "export", label: "Export" },
	];

	return (
		<div className="space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h2 className="text-2xl font-bold tracking-tight text-white">Logs</h2>
					<p className="text-slate-400">
						JSONL log files with rotation (10 MB each, 5 backups)
					</p>
				</div>
			</div>

			<div className="flex gap-1 border-b border-slate-800">
				{tabs.map((t) => (
					<button
						key={t.id}
						type="button"
						onClick={() => setTab(t.id)}
						className={`px-4 py-2 text-sm font-medium rounded-t-md transition-colors ${
							tab === t.id
								? "bg-slate-800 text-white border border-slate-700 border-b-transparent"
								: "text-slate-500 hover:text-slate-300"
						}`}
					>
						{t.label}
					</button>
				))}
			</div>

			{/* Filter bar */}
			<div className="flex flex-wrap gap-3 items-end">
				<div className="grid gap-1.5">
					<Label className="text-xs text-slate-400">Level</Label>
					<select
						value={filterLevel}
						onChange={(e) => setFilterLevel(e.target.value)}
						className="bg-slate-900 border border-slate-800 text-slate-100 rounded-md px-3 py-1.5 text-sm"
					>
						<option value="">All</option>
						<option value="ERROR">Error</option>
						<option value="WARNING">Warning</option>
						<option value="INFO">Info</option>
						<option value="DEBUG">Debug</option>
					</select>
				</div>
				<div className="grid gap-1.5 flex-1 min-w-[200px]">
					<Label className="text-xs text-slate-400">Search text</Label>
					<Input
						value={filterSearch}
						onChange={(e) => setFilterSearch(e.target.value)}
						placeholder="Filter by event, logger, or any field..."
						className="bg-slate-900 border-slate-800 text-slate-100"
					/>
				</div>
				<div className="grid gap-1.5 flex-1 min-w-[160px]">
					<Label className="text-xs text-slate-400">Logger</Label>
					<Input
						value={filterLogger}
						onChange={(e) => setFilterLogger(e.target.value)}
						placeholder="e.g. tailscalemcp.server"
						className="bg-slate-900 border-slate-800 text-slate-100"
					/>
				</div>
				{tab === "tail" && (
					<Button
						variant="outline"
						size="sm"
						className="border-slate-700 text-slate-300"
						onClick={fetchTail}
					>
						<RotateCw className="h-3.5 w-3.5 mr-1" /> Refresh
					</Button>
				)}
				{tab === "search" && (
					<Button
						size="sm"
						className="bg-sky-600 text-white"
						onClick={handleSearch}
						disabled={loading}
					>
						<Search className="h-3.5 w-3.5 mr-1" /> Search
					</Button>
				)}
				{tab === "export" && (
					<div className="flex gap-2 items-end">
						<div className="grid gap-1.5">
							<Label className="text-xs text-slate-400">Format</Label>
							<select
								value={exportFormat}
								onChange={(e) =>
									setExportFormat(e.target.value as "jsonl" | "text")
								}
								className="bg-slate-900 border border-slate-800 text-slate-100 rounded-md px-3 py-1.5 text-sm"
							>
								<option value="jsonl">JSONL</option>
								<option value="text">Plain text</option>
							</select>
						</div>
						<Button
							size="sm"
							className="bg-sky-600 text-white"
							onClick={handleExport}
						>
							<Download className="h-3.5 w-3.5 mr-1" /> Download
						</Button>
					</div>
				)}
			</div>

			<div className="grid gap-6 md:grid-cols-4">
				<Card className="md:col-span-3 border-slate-800 bg-slate-950/50">
					<CardHeader className="py-3">
						<CardTitle className="text-white text-sm">
							{tab === "tail" ? "Live Tail (poll every 3s)" : "Log Entries"}
						</CardTitle>
					</CardHeader>
					<CardContent className="p-0">
						<div
							ref={tailRef}
							className="h-[500px] overflow-y-auto font-mono text-xs p-3 space-y-0.5 bg-slate-900/50 rounded-b-md"
						>
							{entries.length === 0 && (
								<p className="text-slate-500 p-2">
									{tab === "tail"
										? "Waiting for log entries..."
										: "No results."}
								</p>
							)}
							{entries.map((e, i) => {
								const level = (e.level ?? "INFO").toUpperCase();
								const color = LEVEL_COLORS[level] ?? "text-slate-300";
								const Icon = LEVEL_ICONS[level] ?? Info;
								const ts = (e.timestamp ?? "").slice(0, 19).replace("T", " ");
								return (
									<div
										key={`${ts}-${i}`}
										className={`flex items-start gap-2 py-0.5 ${color} hover:bg-slate-800/30 rounded px-1`}
									>
										<Icon className="h-3 w-3 mt-0.5 shrink-0" />
										<span className="shrink-0 text-slate-500">{ts}</span>
										<span className="shrink-0 font-semibold w-14">{level}</span>
										<span
											className="shrink-0 text-slate-600 w-40 truncate"
											title={e.logger}
										>
											{e.logger ?? ""}
										</span>
										<span className="flex-1 truncate">
											{e.event ?? JSON.stringify(e)}
										</span>
									</div>
								);
							})}
						</div>
					</CardContent>
				</Card>

				<Card className="border-slate-800 bg-slate-950/50">
					<CardHeader className="py-3">
						<CardTitle className="text-white text-sm">Log Status</CardTitle>
					</CardHeader>
					<CardContent className="space-y-3 text-xs">
						{status ? (
							<>
								<div>
									<p className="text-slate-500">Total lines</p>
									<p className="text-white font-mono">
										{status.total_lines.toLocaleString()}
									</p>
								</div>
								<div>
									<p className="text-slate-500">Total size</p>
									<p className="text-white font-mono">
										{(status.total_bytes / 1024 / 1024).toFixed(1)} MB
									</p>
								</div>
								<div>
									<p className="text-slate-500">Rotation</p>
									<p className="text-white font-mono">
										{(status.rotation.max_bytes / 1024 / 1024).toFixed(0)} MB ×{" "}
										{status.rotation.backup_count} backups
									</p>
								</div>
								<div>
									<p className="text-slate-500 mb-1">Files</p>
									{status.files.map((f) => (
										<p
											key={f.name}
											className="text-slate-400 font-mono truncate"
										>
											{f.name} ({(f.size_bytes / 1024).toFixed(0)} KB)
										</p>
									))}
								</div>
							</>
						) : (
							<p className="text-slate-500">Loading...</p>
						)}
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
