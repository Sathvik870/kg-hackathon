import { useState } from 'react';
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

import ConnectionForm from './components/ConnectionForm';
import Sidebar from './components/Sidebar';
import DataGrid from './components/DataGrid';
import { previewTable } from './api';

export default function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [tableData, setTableData] = useState<any[]>([]);
  const [currentView, setCurrentView] = useState("");

  const handleSelectTable = async (db: string, table: string) => {
    try {
      setCurrentView(`${db} > ${table}`);
      const data = await previewTable(db, table);
      setTableData(data);
    } catch (e) {
      console.error(e);
    }
  };

  if (!isConnected) {
    return <ConnectionForm onConnect={() => setIsConnected(true)} />;
  }

  return (
    <CopilotKit url="http://localhost:8000/copilotkit">
      <CopilotSidebar
        defaultOpen={true}
        labels={{
          title: "PG Copilot",
          initial: "Connected to PostgreSQL. \n\nWhich database would you like to query?",
        }}
        instructions="You are a SQL expert. The user has connected to a Postgres Server. Ask them which database to use, then use the available tools to list tables, get schemas, or run queries based on their request."
      >
        <div className="flex h-screen w-screen flex-col overflow-hidden bg-[#1e1e1e] text-gray-300">
          {/* Top Bar (VS Code style) */}
          <div className="flex h-10 items-center justify-between border-b border-[#333] bg-[#252526] px-4 text-xs">
            <span>PostgreSQL Explorer</span>
            <span>{currentView}</span>
          </div>

          <div className="flex h-[calc(100vh-40px)] w-full">
            {/* Left Sidebar */}
            <Sidebar onSelectTable={handleSelectTable} />

            {/* Main Content Area */}
            <div className="flex-1 overflow-hidden bg-[#1e1e1e]">
              <DataGrid data={tableData} />
            </div>
          </div>
        </div>
      </CopilotSidebar>
    </CopilotKit>
  );
}