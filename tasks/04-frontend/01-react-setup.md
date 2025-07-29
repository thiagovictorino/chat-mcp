# Task: React UI Setup

## Description
Set up the React frontend application with TypeScript for monitoring agent conversations.

## Acceptance Criteria
- [ ] React app created with TypeScript
- [ ] Docker setup for UI container
- [ ] Basic project structure
- [ ] Environment configuration
- [ ] Auto-refresh capability configured

## Implementation Steps

1. Create UI directory structure:
```bash
ui/
├── Dockerfile
├── package.json
├── tsconfig.json
├── public/
│   └── index.html
└── src/
    ├── index.tsx
    ├── App.tsx
    ├── components/
    ├── services/
    └── types/
```

2. Create `ui/package.json`:
```json
{
  "name": "mac-p-ui",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.0.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "devDependencies": {
    "react-scripts": "5.0.1",
    "@types/node": "^20.0.0"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
```

3. Create `ui/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
```

4. Create `ui/Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "start"]
```

5. Create `ui/public/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#000000" />
  <meta name="description" content="Multi-Agent Communication Platform Monitor" />
  <title>MAC-P Monitor</title>
  <style>
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
        'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
        sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      background-color: #f5f5f5;
    }
    code {
      font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace;
    }
  </style>
</head>
<body>
  <noscript>You need to enable JavaScript to run this app.</noscript>
  <div id="root"></div>
</body>
</html>
```

6. Create `ui/src/index.tsx`:
```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

7. Create `ui/src/types/index.ts`:
```typescript
export interface Channel {
  channel_id: string;
  name: string;
  description?: string;
  agent_count: number;
  max_agents: number;
  created_at: string;
}

export interface Agent {
  agent_id: string;
  username: string;
  role_description: string;
  joined_at: string;
}

export interface Message {
  message_id: string;
  sender: {
    agent_id: string;
    username: string;
  };
  content: string;
  mentions: string[];
  timestamp: string;
  sequence_number: number;
  read_by: Array<{
    username: string;
    read_at: string;
  }>;
}
```

8. Create `ui/src/services/api.ts`:
```typescript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Channel APIs
export const channelAPI = {
  list: (limit = 20, offset = 0) => 
    api.get(`/channels?limit=${limit}&offset=${offset}`),
  create: (data: { name: string; description?: string; max_agents?: number }) =>
    api.post('/channels', data),
};

// Agent APIs
export const agentAPI = {
  list: (channelId: string) => 
    api.get(`/channels/${channelId}/agents`),
};

// Message APIs
export const messageAPI = {
  list: (channelId: string, limit = 50) =>
    api.get(`/channels/${channelId}/messages?limit=${limit}`),
};
```

## Dependencies
- Node.js 18+
- React 18+
- TypeScript 5+

## Estimated Time: 30 minutes