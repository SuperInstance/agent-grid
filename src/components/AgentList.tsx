import React, { useMemo } from 'react';
import { AgentListProps } from '../types';
import { AgentCard } from './AgentCard';

/**
 * AgentList Component
 *
 * List view of agents with sorting and filtering
 */
export const AgentList: React.FC<AgentListProps> = ({
  agents,
  onAgentClick,
  sortBy = 'name',
  sortOrder = 'asc',
  filterBy,
  showAvatars = true,
  theme = 'dark',
}) => {
  const filteredAndSortedAgents = useMemo(() => {
    let result = [...agents];

    // Apply filters
    if (filterBy?.status && filterBy.status.length > 0) {
      result = result.filter((agent) =>
        filterBy.status!.includes(agent.status)
      );
    }

    if (filterBy?.type && filterBy.type.length > 0) {
      result = result.filter(
        (agent) => agent.type && filterBy.type!.includes(agent.type)
      );
    }

    // Apply sorting
    result.sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'status':
          comparison = a.status.localeCompare(b.status);
          break;
        case 'lastActive':
          if (!a.lastActive && !b.lastActive) comparison = 0;
          else if (!a.lastActive) comparison = 1;
          else if (!b.lastActive) comparison = -1;
          else
            comparison =
              a.lastActive.getTime() - b.lastActive.getTime();
          break;
      }

      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [agents, sortBy, sortOrder, filterBy]);

  if (filteredAndSortedAgents.length === 0) {
    return (
      <div
        style={{
          padding: '48px',
          textAlign: 'center',
          color: theme === 'dark' ? '#9ca3af' : '#6b7280',
        }}
      >
        No agents match the current filters
      </div>
    );
  }

  return (
    <div
      className={`agent-list ${theme}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
      }}
    >
      {filteredAndSortedAgents.map((agent) => (
        <div
          key={agent.id}
          onClick={() => onAgentClick?.(agent)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '12px',
            backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff',
            borderRadius: '6px',
            border: `1px solid ${theme === 'dark' ? '#374151' : '#d1d5db'}`,
            cursor: onAgentClick ? 'pointer' : 'default',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            if (onAgentClick) {
              e.currentTarget.style.backgroundColor = theme === 'dark' ? '#374151' : '#f3f4f6';
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = theme === 'dark' ? '#1f2937' : '#ffffff';
          }}
        >
          {showAvatars && (
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor:
                  agent.status === 'active'
                    ? '#10b981'
                    : agent.status === 'busy'
                    ? '#f59e0b'
                    : agent.status === 'error'
                    ? '#ef4444'
                    : agent.status === 'offline'
                    ? '#6b7280'
                    : '#9ca3af',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '14px',
                fontWeight: 'bold',
                color: '#fff',
                flexShrink: 0,
              }}
            >
              {agent.name
                .split(' ')
                .map((word) => word[0])
                .join('')
                .toUpperCase()
                .slice(0, 2)}
            </div>
          )}

          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '2px',
              }}
            >
              <span
                style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: theme === 'dark' ? '#fff' : '#000',
                }}
              >
                {agent.name}
              </span>
              {agent.type && (
                <span
                  style={{
                    fontSize: '11px',
                    backgroundColor: theme === 'dark' ? '#374151' : '#e5e7eb',
                    color: theme === 'dark' ? '#d1d5db' : '#4b5563',
                    padding: '2px 6px',
                    borderRadius: '3px',
                  }}
                >
                  {agent.type}
                </span>
              )}
            </div>

            {agent.description && (
              <div
                style={{
                  fontSize: '12px',
                  color: theme === 'dark' ? '#9ca3af' : '#6b7280',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {agent.description}
              </div>
            )}
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
              flexShrink: 0,
            }}
          >
            {agent.performance && (
              <div style={{ textAlign: 'right' }}>
                <div
                  style={{
                    fontSize: '11px',
                    color: theme === 'dark' ? '#9ca3af' : '#6b7280',
                  }}
                >
                  Success Rate
                </div>
                <div
                  style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color:
                      agent.performance.successRate >= 90
                        ? '#10b981'
                        : agent.performance.successRate >= 70
                        ? '#f59e0b'
                        : '#ef4444',
                  }}
                >
                  {agent.performance.successRate}%
                </div>
              </div>
            )}

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <div
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor:
                    agent.status === 'active'
                      ? '#10b981'
                      : agent.status === 'busy'
                      ? '#f59e0b'
                      : agent.status === 'error'
                      ? '#ef4444'
                      : agent.status === 'offline'
                      ? '#6b7280'
                      : '#9ca3af',
                  }}
              />
              <span
                style={{
                  fontSize: '12px',
                  color: theme === 'dark' ? '#d1d5db' : '#4b5563',
                  fontWeight: '500',
                  textTransform: 'capitalize',
                }}
              >
                {agent.status}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AgentList;
