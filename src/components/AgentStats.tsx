import React from 'react';
import { AgentStatsProps } from '../types';

/**
 * AgentStats Component
 *
 * Summary statistics for agent collection
 */
export const AgentStats: React.FC<AgentStatsProps> = ({
  agents,
  showDetails = true,
}) => {
  const stats = React.useMemo(() => {
    const totalAgents = agents.length;
    const activeAgents = agents.filter((a) => a.status === 'active').length;
    const busyAgents = agents.filter((a) => a.status === 'busy').length;
    const idleAgents = agents.filter((a) => a.status === 'idle').length;
    const errorAgents = agents.filter((a) => a.status === 'error').length;
    const offlineAgents = agents.filter((a) => a.status === 'offline').length;

    const totalTasksCompleted = agents.reduce(
      (sum, agent) => sum + (agent.performance?.tasksCompleted || 0),
      0
    );

    const avgResponseTime =
      agents.length > 0
        ? agents.reduce(
            (sum, agent) =>
              sum + (agent.performance?.avgResponseTime || 0),
            0
          ) / agents.length
        : 0;

    const avgSuccessRate =
      agents.length > 0
        ? agents.reduce(
            (sum, agent) => sum + (agent.performance?.successRate || 0),
            0
          ) / agents.length
        : 0;

    return {
      totalAgents,
      activeAgents,
      busyAgents,
      idleAgents,
      errorAgents,
      offlineAgents,
      totalTasksCompleted,
      avgResponseTime,
      avgSuccessRate,
    };
  }, [agents]);

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '12px',
        padding: '16px',
        backgroundColor: '#1f2937',
        borderRadius: '8px',
        border: '1px solid #374151',
      }}
    >
      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            fontSize: '24px',
            fontWeight: 'bold',
            color: '#fff',
            marginBottom: '4px',
          }}
        >
          {stats.totalAgents}
        </div>
        <div
          style={{
            fontSize: '12px',
            color: '#9ca3af',
          }}
        >
          Total Agents
        </div>
      </div>

      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            fontSize: '24px',
            fontWeight: 'bold',
            color: '#10b981',
            marginBottom: '4px',
          }}
        >
          {stats.activeAgents}
        </div>
        <div
          style={{
            fontSize: '12px',
            color: '#9ca3af',
          }}
        >
          Active
        </div>
      </div>

      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            fontSize: '24px',
            fontWeight: 'bold',
            color: '#f59e0b',
            marginBottom: '4px',
          }}
        >
          {stats.busyAgents}
        </div>
        <div
          style={{
            fontSize: '12px',
            color: '#9ca3af',
          }}
        >
          Busy
        </div>
      </div>

      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            fontSize: '24px',
            fontWeight: 'bold',
            color: '#ef4444',
            marginBottom: '4px',
          }}
        >
          {stats.errorAgents}
        </div>
        <div
          style={{
            fontSize: '12px',
            color: '#9ca3af',
          }}
        >
          Errors
        </div>
      </div>

      {showDetails && (
        <>
          <div style={{ textAlign: 'center' }}>
            <div
              style={{
                fontSize: '24px',
                fontWeight: 'bold',
                color: '#fff',
                marginBottom: '4px',
              }}
            >
              {stats.totalTasksCompleted}
            </div>
            <div
              style={{
                fontSize: '12px',
                color: '#9ca3af',
              }}
            >
              Tasks Completed
            </div>
          </div>

          <div style={{ textAlign: 'center' }}>
            <div
              style={{
                fontSize: '24px',
                fontWeight: 'bold',
                color: '#fff',
                marginBottom: '4px',
              }}
            >
              {stats.avgResponseTime.toFixed(0)}ms
            </div>
            <div
              style={{
                fontSize: '12px',
                color: '#9ca3af',
              }}
            >
              Avg Response
            </div>
          </div>

          <div style={{ textAlign: 'center' }}>
            <div
              style={{
                fontSize: '24px',
                fontWeight: 'bold',
                color:
                  stats.avgSuccessRate >= 90
                    ? '#10b981'
                    : stats.avgSuccessRate >= 70
                    ? '#f59e0b'
                    : '#ef4444',
                marginBottom: '4px',
              }}
            >
              {stats.avgSuccessRate.toFixed(1)}%
            </div>
            <div
              style={{
                fontSize: '12px',
                color: '#9ca3af',
              }}
            >
              Avg Success Rate
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AgentStats;
