import React from 'react';
import { AgentCardProps } from '../types';

/**
 * AgentCard Component
 *
 * Individual agent display card with status and metrics
 */
export const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  onClick,
  onSelect,
  isSelected = false,
  isSelectable = false,
  showStatus = true,
  showPerformance = true,
  theme = 'dark',
}) => {
  const getStatusColor = () => {
    switch (agent.status) {
      case 'active':
        return '#10b981';
      case 'busy':
        return '#f59e0b';
      case 'idle':
        return '#9ca3af';
      case 'error':
        return '#ef4444';
      case 'offline':
        return '#6b7280';
      default:
        return '#9ca3af';
    }
  };

  const getStatusLabel = () => {
    return agent.status.charAt(0).toUpperCase() + agent.status.slice(1);
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((word) => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div
      className={`agent-card ${isSelected ? 'selected' : ''} ${theme}`}
      onClick={onClick}
      style={{
        backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff',
        borderRadius: '8px',
        padding: '16px',
        border: isSelected
          ? '2px solid #3b82f6'
          : `1px solid ${theme === 'dark' ? '#374151' : '#d1d5db'}`,
        cursor: onClick || onSelect ? 'pointer' : 'default',
        transition: 'all 0.2s ease',
        position: 'relative',
      }}
      onMouseEnter={(e) => {
        if (onClick || onSelect) {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      {/* Selection checkbox */}
      {isSelectable && (
        <div
          style={{
            position: 'absolute',
            top: '12px',
            right: '12px',
          }}
          onClick={(e) => {
            e.stopPropagation();
            onSelect?.();
          }}
        >
          <div
            style={{
              width: '20px',
              height: '20px',
              borderRadius: '4px',
              border: `2px solid ${isSelected ? '#3b82f6' : '#6b7280'}`,
              backgroundColor: isSelected ? '#3b82f6' : 'transparent',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
            }}
          >
            {isSelected && (
              <span style={{ color: '#fff', fontSize: '14px' }}>✓</span>
            )}
          </div>
        </div>
      )}

      {/* Header with avatar and name */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '12px',
        }}
      >
        {/* Avatar */}
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '50%',
            backgroundColor: getStatusColor(),
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '16px',
            fontWeight: 'bold',
            color: '#fff',
          }}
        >
          {agent.avatar ? (
            <img
              src={agent.avatar}
              alt={agent.name}
              style={{
                width: '100%',
                height: '100%',
                borderRadius: '50%',
                objectFit: 'cover',
              }}
            />
          ) : (
            getInitials(agent.name)
          )}
        </div>

        {/* Name and status */}
        <div style={{ flex: 1 }}>
          <div
            style={{
              fontSize: '16px',
              fontWeight: '600',
              color: theme === 'dark' ? '#fff' : '#000',
              marginBottom: '4px',
            }}
          >
            {agent.name}
          </div>
          {showStatus && (
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
                  backgroundColor: getStatusColor(),
                  animation:
                    agent.status === 'active' || agent.status === 'busy'
                      ? 'pulse 2s infinite'
                      : 'none',
                }}
              />
              <span
                style={{
                  fontSize: '12px',
                  color: getStatusColor(),
                  fontWeight: '500',
                }}
              >
                {getStatusLabel()}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Type and description */}
      {agent.type && (
        <div
          style={{
            fontSize: '12px',
            color: theme === 'dark' ? '#9ca3af' : '#6b7280',
            marginBottom: '8px',
          }}
        >
          {agent.type}
        </div>
      )}

      {agent.description && (
        <div
          style={{
            fontSize: '13px',
            color: theme === 'dark' ? '#d1d5db' : '#4b5563',
            marginBottom: '12px',
            lineHeight: '1.4',
          }}
        >
          {agent.description.length > 80
            ? agent.description.substring(0, 80) + '...'
            : agent.description}
        </div>
      )}

      {/* Current task */}
      {agent.currentTask && (
        <div
          style={{
            fontSize: '12px',
            color: theme === 'dark' ? '#d1d5db' : '#4b5563',
            backgroundColor: theme === 'dark' ? '#374151' : '#f3f4f6',
            padding: '8px',
            borderRadius: '4px',
            marginBottom: '12px',
          }}
        >
          <div
            style={{
              fontSize: '11px',
              color: theme === 'dark' ? '#9ca3af' : '#6b7280',
              marginBottom: '2px',
            }}
          >
            Current Task:
          </div>
          {agent.currentTask.length > 60
            ? agent.currentTask.substring(0, 60) + '...'
            : agent.currentTask}
        </div>
      )}

      {/* Performance metrics */}
      {showPerformance && agent.performance && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '8px',
            paddingTop: '12px',
            borderTop: `1px solid ${theme === 'dark' ? '#374151' : '#d1d5db'}`,
          }}
        >
          <div>
            <div
              style={{
                fontSize: '11px',
                color: theme === 'dark' ? '#9ca3af' : '#6b7280',
                marginBottom: '2px',
              }}
            >
              Completed
            </div>
            <div
              style={{
                fontSize: '14px',
                fontWeight: '600',
                color: theme === 'dark' ? '#fff' : '#000',
              }}
            >
              {agent.performance.tasksCompleted}
            </div>
          </div>
          <div>
            <div
              style={{
                fontSize: '11px',
                color: theme === 'dark' ? '#9ca3af' : '#6b7280',
                marginBottom: '2px',
              }}
            >
              Avg Time
            </div>
            <div
              style={{
                fontSize: '14px',
                fontWeight: '600',
                color: theme === 'dark' ? '#fff' : '#000',
              }}
            >
              {agent.performance.avgResponseTime}ms
            </div>
          </div>
          <div>
            <div
              style={{
                fontSize: '11px',
                color: theme === 'dark' ? '#9ca3af' : '#6b7280',
                marginBottom: '2px',
              }}
            >
              Success
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
        </div>
      )}

      {/* Capabilities tags */}
      {agent.capabilities && agent.capabilities.length > 0 && (
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '4px',
            marginTop: '12px',
            paddingTop: '12px',
            borderTop: `1px solid ${theme === 'dark' ? '#374151' : '#d1d5db'}`,
          }}
        >
          {agent.capabilities.slice(0, 3).map((capability, index) => (
            <span
              key={index}
              style={{
                fontSize: '10px',
                backgroundColor: theme === 'dark' ? '#374151' : '#e5e7eb',
                color: theme === 'dark' ? '#d1d5db' : '#374151',
                padding: '2px 6px',
                borderRadius: '3px',
              }}
            >
              {capability}
            </span>
          ))}
          {agent.capabilities.length > 3 && (
            <span
              style={{
                fontSize: '10px',
                color: theme === 'dark' ? '#9ca3af' : '#6b7280',
              }}
            >
              +{agent.capabilities.length - 3} more
            </span>
          )}
        </div>
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default AgentCard;
