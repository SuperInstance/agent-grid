# @luciddreamer/agent-grid

[![npm version](https://badge.fury.io/js/%40luciddreamer%2Fagent-grid.svg)](https://www.npmjs.com/package/@luciddreamer/agent-grid)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Grid layout component for visualizing and managing multiple AI agents with status indicators, performance metrics, and interactive selection.

## Features

- **Responsive Grid Layout** - Auto-fill grid adapts to screen size
- **Agent Status Indicators** - Visual status with animated indicators
- **Performance Metrics** - Tasks completed, response time, success rate
- **Interactive Cards** - Click and select functionality
- **List View** - Alternative list layout with sorting/filtering
- **Statistics Overview** - Agent collection summary stats
- **Theme Support** - Dark and light themes
- **TypeScript Support** - Full type definitions included

## Installation

```bash
npm install @luciddreamer/agent-grid
# or
yarn add @luciddreamer/agent-grid
# or
pnpm add @luciddreamer/agent-grid
```

## Quick Start

```tsx
import React, { useState } from 'react';
import { AgentGrid, AgentList, AgentStats } from '@luciddreamer/agent-grid';

function App() {
  const [selectedAgent, setSelectedAgent] = useState(null);

  const agents = [
    {
      id: '1',
      name: 'Research Agent',
      status: 'active',
      type: 'Research',
      description: 'Handles research and data gathering tasks',
      capabilities: ['web-search', 'data-analysis', 'summarization'],
      currentTask: 'Analyzing market trends',
      performance: {
        tasksCompleted: 245,
        avgResponseTime: 1200,
        successRate: 94,
      },
      lastActive: new Date(),
    },
    // ... more agents
  ];

  return (
    <div>
      {/* Statistics Overview */}
      <AgentStats agents={agents} showDetails={true} />

      {/* Grid View */}
      <AgentGrid
        agents={agents}
        onAgentClick={(agent) => console.log('Clicked:', agent)}
        onAgentSelect={(agent) => setSelectedAgent(agent)}
        selectedAgentId={selectedAgent?.id}
        selectable={true}
        showStatus={true}
        showPerformance={true}
        theme="dark"
      />

      {/* List View */}
      <AgentList
        agents={agents}
        onAgentClick={(agent) => console.log('Clicked:', agent)}
        sortBy="name"
        sortOrder="asc"
        showAvatars={true}
        theme="dark"
      />
    </div>
  );
}
```

## Components

### AgentGrid

Grid layout for displaying agents in card format.

**Props:**

- `agents: Agent[]` - Array of agent objects
- `onAgentClick?: (agent: Agent) => void` - Click handler
- `onAgentSelect?: (agent: Agent) => void` - Selection handler
- `selectedAgentId?: string` - ID of selected agent
- `columns?: number | 'auto'` - Grid columns (default: 'auto')
- `spacing?: 'small' | 'medium' | 'large'` - Card spacing (default: 'medium')
- `showStatus?: boolean` - Show status indicators (default: true)
- `showPerformance?: boolean` - Show performance metrics (default: true)
- `selectable?: boolean` - Enable selection mode (default: false)
- `theme?: 'light' | 'dark'` - Color theme (default: 'dark')

### AgentCard

Individual agent display card (used internally by AgentGrid).

**Props:**

- `agent: Agent` - Agent object
- `onClick?: () => void` - Click handler
- `onSelect?: () => void` - Selection handler
- `isSelected?: boolean` - Whether card is selected
- `isSelectable?: boolean` - Show selection checkbox
- `showStatus?: boolean` - Show status indicator
- `showPerformance?: boolean` - Show performance metrics
- `theme?: 'light' | 'dark'` - Color theme

### AgentList

List view of agents with sorting and filtering.

**Props:**

- `agents: Agent[]` - Array of agent objects
- `onAgentClick?: (agent: Agent) => void` - Click handler
- `sortBy?: 'name' | 'status' | 'lastActive'` - Sort field (default: 'name')
- `sortOrder?: 'asc' | 'desc'` - Sort order (default: 'asc')
- `filterBy?: { status?: string[]; type?: string[] }` - Filters
- `showAvatars?: boolean` - Show agent avatars (default: true)
- `theme?: 'light' | 'dark'` - Color theme

### AgentStats

Summary statistics for agent collection.

**Props:**

- `agents: Agent[]` - Array of agent objects
- `showDetails?: boolean` - Show detailed metrics (default: true)

## Type Definitions

```typescript
interface Agent {
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
```

## Customization

### Custom Card Rendering

```tsx
import { AgentCard } from '@luciddreamer/agent-grid';

<AgentCard
  agent={myAgent}
  onClick={() => console.log('Clicked')}
  showStatus={true}
  showPerformance={true}
  theme="dark"
/>
```

### Filtering and Sorting

```tsx
import { AgentList } from '@luciddreamer/agent-grid';

<AgentList
  agents={agents}
  sortBy="status"
  sortOrder="desc"
  filterBy={{
    status: ['active', 'busy'],
    type: ['Research', 'Analysis']
  }}
  onAgentClick={(agent) => handleAgentClick(agent)}
/>
```

### Custom Grid Layout

```tsx
import { AgentGrid } from '@luciddreamer/agent-grid';

<AgentGrid
  agents={agents}
  columns={3}
  spacing="large"
  selectable={true}
  onAgentSelect={(agent) => setSelectedAgent(agent)}
  selectedAgentId={selectedAgent?.id}
/>
```

## Styling

Components use inline styles and can be customized through props. The grid and cards respond to the `theme` prop:

```tsx
// Light theme
<AgentGrid agents={agents} theme="light" />

// Dark theme (default)
<AgentGrid agents={agents} theme="dark" />
```

## Examples

### Agent Management Dashboard

```tsx
function Dashboard() {
  const [agents, setAgents] = useState([]);
  const [view, setView] = useState<'grid' | 'list'>('grid');

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <h1>Agent Management</h1>
        <button onClick={() => setView(view === 'grid' ? 'list' : 'grid')}>
          Toggle View
        </button>
      </div>

      <AgentStats agents={agents} />

      {view === 'grid' ? (
        <AgentGrid agents={agents} selectable onAgentSelect={handleSelect} />
      ) : (
        <AgentList agents={agents} sortBy="status" />
      )}
    </div>
  );
}
```

### Real-time Agent Monitoring

```tsx
function AgentMonitor() {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/agents');

    ws.onmessage = (event) => {
      const updatedAgents = JSON.parse(event.data);
      setAgents(updatedAgents);
    };

    return () => ws.close();
  }, []);

  return (
    <AgentGrid
      agents={agents}
      showPerformance={true}
      onAgentClick={(agent) => showAgentDetails(agent)}
    />
  );
}
```

## Dependencies

- React >= 18.0.0
- React-DOM >= 18.0.0

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT © LucidDreamer

## Related Packages

- [@luciddreamer/monitoring-dashboard](https://www.npmjs.com/package/@luciddreamer/monitoring-dashboard) - System monitoring dashboard
- [@luciddreamer/memory-visualization](https://www.npmjs.com/package/@luciddreamer/memory-visualization) - Memory system visualization
- [@luciddreamer/cost-analysis](https://www.npmjs.com/package/@luciddreamer/cost-analysis) - Cost tracking components

## Support

For issues and questions, please visit our [GitHub repository](https://github.com/luciddreamer/agent-grid).
