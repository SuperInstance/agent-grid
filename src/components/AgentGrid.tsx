import React from 'react';
import { AgentGridProps } from '../types';
import { AgentCard } from './AgentCard';

/**
 * AgentGrid Component
 *
 * Grid layout for displaying and managing multiple AI agents
 * Features:
 * - Responsive grid layout
 * - Agent status indicators
 * - Interactive agent cards
 * - Selection support
 * - Performance metrics display
 */
export const AgentGrid: React.FC<AgentGridProps> = ({
  agents,
  onAgentClick,
  onAgentSelect,
  selectedAgentId,
  columns = 'auto',
  spacing = 'medium',
  showStatus = true,
  showPerformance = true,
  selectable = false,
  theme = 'dark',
}) => {
  const spacingMap = {
    small: '12px',
    medium: '16px',
    large: '24px',
  };

  const gridStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns:
      columns === 'auto'
        ? 'repeat(auto-fill, minmax(280px, 1fr))'
        : `repeat(${columns}, 1fr)`,
    gap: spacingMap[spacing],
    padding: spacingMap[spacing],
  };

  if (agents.length === 0) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '400px',
          backgroundColor: theme === 'dark' ? '#1f2937' : '#f9fafb',
          borderRadius: '8px',
          border: `1px solid ${theme === 'dark' ? '#374151' : '#d1d5db'}`,
          color: theme === 'dark' ? '#9ca3af' : '#6b7280',
          fontSize: '16px',
        }}
      >
        No agents available
      </div>
    );
  }

  return (
    <div
      className={`agent-grid ${theme}`}
      style={gridStyle}
    >
      {agents.map((agent) => (
        <AgentCard
          key={agent.id}
          agent={agent}
          onClick={() => onAgentClick?.(agent)}
          onSelect={() => onAgentSelect?.(agent)}
          isSelected={selectedAgentId === agent.id}
          isSelectable={selectable}
          showStatus={showStatus}
          showPerformance={showPerformance}
          theme={theme}
        />
      ))}
    </div>
  );
};

export default AgentGrid;
