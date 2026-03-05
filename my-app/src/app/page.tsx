"use client";

import { FormEvent, useEffect, useState } from "react";

import { useCopilotChat, useCopilotAction, CatchAllActionRenderProps } from "@copilotkit/react-core";
import { CopilotChat, CopilotKitCSSProperties, useCopilotChatSuggestions } from "@copilotkit/react-ui";
import { MCPEndpointConfig } from "@copilotkit/runtime";
import { DefaultToolRender } from "@/components/default-tool-render";

const themeColor = "#6366f1";

export default function Home() {
  return (
    <main style={{ "--copilot-kit-primary-color": themeColor } as CopilotKitCSSProperties}>
      <AppLayout />
    </main>
  );
}

function AppLayout() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isConfigured, setIsConfigured] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [databases, setDatabases] = useState<string[]>([]);
  const [selectedDatabase, setSelectedDatabase] = useState<string | null>(null);
  const [tables, setTables] = useState<string[]>([]);
  const [tablesLoading, setTablesLoading] = useState(false);
  const [tablesError, setTablesError] = useState<string | null>(null);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [rowsLoading, setRowsLoading] = useState(false);
  const [rowsError, setRowsError] = useState<string | null>(null);

  const [dbForm, setDbForm] = useState({
    host: "localhost",
    port: "5432",
    user: "postgres",
    password: "",
  });

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/api/db-config", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(dbForm),
      });

      const data = await response.json();

      if (!response.ok || !data.ok) {
        throw new Error(data.error || "Failed to configure database");
      }

      const dbResponse = await fetch("http://localhost:8000/api/databases");
      const dbData = await dbResponse.json();

      if (dbData.ok && Array.isArray(dbData.databases)) {
        setDatabases(dbData.databases);
      } else {
        setDatabases([]);
      }

      setIsConfigured(true);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
      setIsConfigured(false);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDatabase = async (db: string) => {
    setSelectedDatabase(db);
    setSelectedTable(null);
    setRows([]);
    setRowsError(null);
    setTables([]);
    setTablesError(null);
    setTablesLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/api/databases/${encodeURIComponent(db)}/tables`);
      const data = await response.json();

      if (!response.ok || !data.ok) {
        throw new Error(data.error || "Failed to load tables");
      }

      if (Array.isArray(data.tables)) {
        setTables(data.tables);
      } else {
        setTables([]);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error loading tables";
      setTablesError(message);
      setTables([]);
    } finally {
      setTablesLoading(false);
    }
  };

  const handleSelectTable = async (table: string) => {
    if (!selectedDatabase) return;

    setSelectedTable(table);
    setRows([]);
    setRowsError(null);
    setRowsLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8000/api/databases/${encodeURIComponent(
          selectedDatabase,
        )}/tables/${encodeURIComponent(table)}/rows?limit=50`,
      );
      const data = await response.json();

      // Backend returns ok: false and error: "nodata" when there is no data
      // so treat that as an empty result instead of an error.
      if (!data.ok && data.error === "nodata") {
        setRows([]);
        setRowsError(null);
        return;
      }

      if (!response.ok || !data.ok) {
        throw new Error(data.error || "Failed to load rows");
      }

      if (Array.isArray(data.rows)) {
        setRows(data.rows);
      } else {
        setRows([]);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error loading rows";
      setRowsError(message);
      setRows([]);
    } finally {
      setRowsLoading(false);
    }
  };

  if (!isConfigured) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-8 space-y-6">
          <div>
            <h1 className="text-xl font-semibold text-white mb-1">Connect to PostgreSQL</h1>
            <p className="text-sm text-slate-400">
              Enter your PostgreSQL connection details. We&apos;ll test the connection before continuing.
            </p>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Host</label>
                <input
                  className="w-full rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/70 focus:border-indigo-500/70"
                  value={dbForm.host}
                  onChange={(e) => setDbForm({ ...dbForm, host: e.target.value })}
                  placeholder="localhost"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">Port</label>
                  <input
                    className="w-full rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/70 focus:border-indigo-500/70"
                    value={dbForm.port}
                    onChange={(e) => setDbForm({ ...dbForm, port: e.target.value })}
                    placeholder="5432"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">User</label>
                  <input
                    className="w-full rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/70 focus:border-indigo-500/70"
                    value={dbForm.user}
                    onChange={(e) => setDbForm({ ...dbForm, user: e.target.value })}
                    placeholder="postgres"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
                <input
                  type="password"
                  className="w-full rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/70 focus:border-indigo-500/70"
                  value={dbForm.password}
                  onChange={(e) => setDbForm({ ...dbForm, password: e.target.value })}
                  placeholder="••••••••"
                />
              </div>
            </div>

            {error && (
              <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/40 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full inline-flex items-center justify-center rounded-lg bg-indigo-500 hover:bg-indigo-500/90 disabled:opacity-60 disabled:cursor-not-allowed px-4 py-2.5 text-sm font-medium text-white shadow-lg shadow-indigo-500/30 transition-colors"
            >
              {loading ? "Connecting..." : "Connect & Continue"}
            </button>
          </form>

          <p className="text-[11px] text-slate-500">
            These settings are used only locally by this app to connect to your PostgreSQL instance.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex">
      {/* Left database overview panel */}
      <aside className="w-80 border-r border-slate-800 bg-slate-900/60 backdrop-blur-md p-5 flex flex-col">
        <div className="mb-4">
          <h2 className="text-sm font-semibold text-white mb-1">Database Explorer</h2>
          <p className="text-xs text-slate-400">
            Connected to <span className="font-mono text-slate-200">{dbForm.host}:{dbForm.port}</span> as{" "}
            <span className="font-mono text-slate-200">{dbForm.user}</span>.
          </p>
        </div>

        <div className="flex-1 rounded-xl border border-slate-800 bg-slate-950/60 p-3 overflow-auto">
          <h3 className="text-xs font-semibold text-slate-300 mb-2">Databases</h3>
          {databases.length === 0 ? (
            <p className="text-xs text-slate-500">
              No databases found or failed to fetch. You can still use the SQL assistant from the chat.
            </p>
          ) : (
            <ul className="space-y-1 text-xs mb-3">
              {databases.map((db) => (
                <li
                  key={db}
                  onClick={() => handleSelectDatabase(db)}
                  className={`px-2 py-1 rounded-md border cursor-pointer transition ${
                    selectedDatabase === db
                      ? "bg-indigo-500/70 border-indigo-400 text-white"
                      : "bg-slate-800/70 text-slate-100 border-slate-700/60 hover:bg-slate-700/70"
                  }`}
                >
                  {db}
                </li>
              ))}
            </ul>
          )}

          {selectedDatabase && (
            <div className="mt-2 border-t border-slate-800 pt-2">
              <h4 className="text-[11px] font-semibold text-slate-300 mb-1">
                Tables in <span className="font-mono text-slate-100">{selectedDatabase}</span>
              </h4>

              {tablesLoading && <p className="text-[11px] text-slate-500">Loading tables…</p>}
              {tablesError && (
                <p className="text-[11px] text-red-400 bg-red-500/10 border border-red-500/40 rounded px-2 py-1">
                  {tablesError}
                </p>
              )}

              {!tablesLoading && !tablesError && tables.length === 0 && (
                <p className="text-[11px] text-slate-500">No public tables found.</p>
              )}

              {tables.length > 0 && (
                <ul className="space-y-1 text-[11px] max-h-40 overflow-auto mt-1">
                  {tables.map((table) => (
                    <li
                      key={table}
                      onClick={() => handleSelectTable(table)}
                      className={`px-2 py-1 rounded-md border cursor-pointer transition ${
                        selectedTable === table
                          ? "bg-slate-100 text-slate-900 border-slate-200"
                          : "bg-slate-900/70 text-slate-100 border-slate-700/60 hover:bg-slate-800/90"
                      }`}
                    >
                      {table}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </aside>

      {/* Main content area */}
      <section className="flex-1 relative p-8">
        <div className="max-w-2xl">
          <h1 className="text-2xl font-semibold mb-2">Postgres Assistant</h1>
          <p className="text-sm text-slate-400 mb-4">
            Your database connection is ready. Use the chat assistant in the bottom-right corner whenever you need help
            exploring schemas, writing queries, or understanding your data.
          </p>
        </div>

        {selectedDatabase && selectedTable && (
          <div className="mt-4">
            <div className="flex items-baseline justify-between mb-2">
              <div>
                <h2 className="text-sm font-semibold text-white">
                  {selectedDatabase}.{selectedTable}
                </h2>
                <p className="text-xs text-slate-400">
                  Showing up to 50 rows from this table for a quick preview.
                </p>
              </div>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-3 max-h-80 overflow-auto text-xs">
              {rowsLoading && <p className="text-slate-400">Loading rows…</p>}
              {rowsError && <p className="text-red-400">{rowsError}</p>}
              {!rowsLoading && !rowsError && rows.length === 0 && (
                <p className="text-slate-400">No rows found in this table.</p>
              )}
              {!rowsLoading && !rowsError && rows.length > 0 && (
                <table className="w-full border-collapse">
                  <thead>
                    <tr>
                      {Object.keys(rows[0]).map((col) => (
                        <th
                          key={col}
                          className="border-b border-slate-800 px-2 py-1 text-left font-medium text-slate-300 bg-slate-900/60"
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row, idx) => (
                      <tr key={idx} className="odd:bg-slate-900/40 even:bg-slate-900/10">
                        {Object.keys(rows[0]).map((col) => (
                          <td key={col} className="px-2 py-1 align-top text-slate-100">
                            {String(row[col] ?? "")}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}

        {/* Hidden Copilot chat bubble + button */}
        <YourMainContent />

        {isChatOpen && (
          <div className="fixed bottom-24 right-6 w-full max-w-md h-[480px] bg-slate-950 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
            <CopilotChat
              labels={{
                title: "SQL Assistant",
                initial:
                  "👋 Hi! I’m your PostgreSQL assistant. I can use tools like 'List Databases', 'List Tables', 'Table Schema', and 'Execute Query' to explore your database. What would you like to do?",
              }}
              className="h-full"
            />
          </div>
        )}

        <button
          type="button"
          onClick={() => setIsChatOpen((open) => !open)}
          className="fixed bottom-6 right-6 inline-flex items-center gap-2 rounded-full bg-indigo-500 hover:bg-indigo-500/90 px-4 py-2.5 text-sm font-medium text-white shadow-lg shadow-indigo-500/40"
        >
          <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-white/10 border border-white/20">
            💬
          </span>
          <span>{isChatOpen ? "Hide SQL Assistant" : "Open SQL Assistant"}</span>
        </button>
      </section>
    </div>
  );
}

function YourMainContent() {
  const { mcpServers, setMcpServers } = useCopilotChat();
  const [newMcpServer, setNewMcpServer] = useState("");

  useEffect(() => {
    setMcpServers([
      {
        endpoint: "http://localhost:8000/sse"  // Change this to your local MCP server
      }
    ]);
  }, []);

  const removeMcpServer = (url: string) => {
    setMcpServers(mcpServers.filter((server) => server.endpoint !== url));
  }

  const addMcpServer = (server: MCPEndpointConfig) => {
    setMcpServers([...mcpServers, server]);
  }

  useCopilotChatSuggestions({
    maxSuggestions: 3,
    instructions: "Give the user a short and concise suggestion based on the conversation and your available tools. Focus on PostgreSQL mine is connected to a PostgreSQL database. Suggest actions like 'List Databases', 'List Tables', 'Database Schema', 'Table Schema', 'Execute Query'.",
  })

  useCopilotAction({
    name: "*",
    render: ({ name, status, args, result }: CatchAllActionRenderProps<[]>) => (
      <DefaultToolRender status={status} name={name} args={args} result={result} />
    ),
  });
  return null;
}