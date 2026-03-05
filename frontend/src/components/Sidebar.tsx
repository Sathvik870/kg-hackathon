import { useState, useEffect } from 'react';
import { ChevronRight, ChevronDown, Database, Table, Folder } from 'lucide-react';
import { getStructure } from '../api';
import type { DbNode } from '../types';

const TreeNode = ({ node, onSelect }: { node: DbNode, onSelect: (n: DbNode) => void }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const Icon = node.type === 'database' ? Database : node.type === 'table' ? Table : Folder;
  const color = node.type === 'database' ? 'text-yellow-500' : 'text-blue-400';

  return (
    <div className="pl-3">
      <div 
        className="flex cursor-pointer items-center gap-1 py-1 text-sm text-gray-300 hover:bg-[#2a2d2e] hover:text-white"
        onClick={() => {
           setIsOpen(!isOpen);
           onSelect(node);
        }}
      >
        <span className="opacity-70">
            {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </span>
        <Icon size={14} className={color} />
        <span className="truncate">{node.name}</span>
      </div>
      {isOpen && node.children && (
        <div className="border-l border-[#444] ml-2">
          {node.children.map((child, i) => (
            <TreeNode key={i} node={child} onSelect={onSelect} />
          ))}
        </div>
      )}
    </div>
  );
};

export default function Sidebar({ onSelectTable }: { onSelectTable: (db: string, table: string) => void }) {
  const [structure, setStructure] = useState<DbNode[]>([]);

  useEffect(() => {
    getStructure().then(setStructure).catch(console.error);
  }, []);

  return (
    <div className="h-full w-64 flex-shrink-0 border-r border-[#333] bg-[#252526]">
      <div className="flex items-center justify-between px-4 py-2 text-xs font-bold uppercase tracking-wider text-gray-500">
        <span>Explorer</span>
      </div>
      <div className="overflow-y-auto p-2">
        {structure.map((node, i) => (
            <TreeNode 
                key={i} 
                node={node} 
                onSelect={(n) => {
                    // Logic to handle selection
                    // In a real app, clicking a DB would load its tables dynamically
                    if(n.type === 'table') {
                       // Assuming parent is DB for this demo
                       onSelectTable("postgres", n.name); 
                    }
                }} 
            />
        ))}
      </div>
    </div>
  );
}