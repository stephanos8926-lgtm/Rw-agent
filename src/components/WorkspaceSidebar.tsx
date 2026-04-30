import React, { useState } from 'react';

export const WorkspaceSidebar = ({ workspaces, currentWorkspace, onSelect }) => {
  return (
    <div className="w-64 bg-gray-900 text-white p-4 h-full">
      <h2 className="text-xl font-bold mb-4">Workspaces</h2>
      <ul>
        {workspaces.map((ws) => (
          <li 
            key={ws.id} 
            className={`p-2 cursor-pointer ${ws.id === currentWorkspace ? 'bg-gray-700' : ''}`}
            onClick={() => onSelect(ws.id)}
          >
            {ws.name}
          </li>
        ))}
      </ul>
    </div>
  );
};
