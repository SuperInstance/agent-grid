/**
 * Agent grid types for visualization
 */

export interface Agent {
  id: string;
  name: string;
  status: 'active' | 'idle' | 'busy' | 'error' | 'offline';
  type?: string;
  description?: string;
  avatar?: string;
  capabilities?: string[];
  currentTask?: string;
  performance?: {
    tasksCompleted: number;
    avgResponseTime: number;
    successRate: number;
  };
  lastActive?: Date;
}

export interface AgentGridProps {
  agents: Agent[];
  onAgentClick?: (agent: Agent) => void;
  onAgentSelect?: (agent: Agent) => void;
  selectedAgentId?: string;
  columns?: number;
  spacing?: 'small' | 'medium' | 'large';
  showStatus?: boolean;
  showPerformance?: boolean;
  selectable?: boolean;
  theme?: 'light' | 'dark';
}

export interface AgentCardProps {
  agent: Agent;
  onClick?: () => void;
  onSelect?: () => void;
  isSelected?: boolean;
  isSelectable?: boolean;
  showStatus?: boolean;
  showPerformance?: boolean;
  theme?: 'light' | 'dark';
}

export interface AgentListProps {
  agents: Agent[];
  onAgentClick?: (agent: Agent) => void;
  sortBy?: 'name' | 'status' | 'lastActive';
  sortOrder?: 'asc' | 'desc';
  filterBy?: {
    status?: Agent['status'][];
    type?: string[];
  };
  showAvatars?: boolean;
  theme?: 'light' | 'dark';
}

export interface AgentStatsProps {
  agents: Agent[];
  showDetails?: boolean;
}
