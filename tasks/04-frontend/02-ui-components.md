# Task: Create UI Components

## Description
Build the main UI components for displaying channels, agents, messages, and read receipts with auto-refresh functionality.

## Acceptance Criteria
- [ ] Channel list component
- [ ] Agent list component
- [ ] Message display with @ mention highlighting
- [ ] Read receipt display
- [ ] Auto-refresh every 2 seconds
- [ ] Log viewer component

## Implementation Steps

1. Create `ui/src/App.tsx`:
```tsx
import React, { useState, useEffect } from 'react';
import ChannelList from './components/ChannelList';
import ChatView from './components/ChatView';
import LogViewer from './components/LogViewer';
import { Channel } from './types';
import './App.css';

function App() {
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);
  const [showLogs, setShowLogs] = useState(false);
  const [refreshInterval] = useState(
    parseInt(process.env.REACT_APP_REFRESH_INTERVAL || '2000')
  );

  return (
    <div className="app">
      <div className="app-header">
        <h1>Multi-Agent Communication Platform Monitor</h1>
        <button 
          className="log-toggle"
          onClick={() => setShowLogs(!showLogs)}
        >
          {showLogs ? 'Hide Logs' : 'Show Logs'}
        </button>
      </div>
      
      <div className="app-content">
        <div className="sidebar">
          <ChannelList 
            onSelectChannel={setSelectedChannel}
            selectedChannel={selectedChannel}
            refreshInterval={refreshInterval}
          />
        </div>
        
        <div className="main-content">
          {showLogs ? (
            <LogViewer refreshInterval={refreshInterval} />
          ) : selectedChannel ? (
            <ChatView 
              channel={selectedChannel} 
              refreshInterval={refreshInterval}
            />
          ) : (
            <div className="no-channel-selected">
              <p>Select a channel to view conversations</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
```

2. Create `ui/src/App.css`:
```css
.app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: #2c3e50;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.log-toggle {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.log-toggle:hover {
  background-color: #2980b9;
}

.app-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 300px;
  background-color: #ecf0f1;
  border-right: 1px solid #bdc3c7;
  overflow-y: auto;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.no-channel-selected {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #7f8c8d;
}
```

3. Create `ui/src/components/ChannelList.tsx`:
```tsx
import React, { useState, useEffect } from 'react';
import { Channel } from '../types';
import { channelAPI } from '../services/api';
import './ChannelList.css';

interface Props {
  onSelectChannel: (channel: Channel) => void;
  selectedChannel: Channel | null;
  refreshInterval: number;
}

const ChannelList: React.FC<Props> = ({ 
  onSelectChannel, 
  selectedChannel,
  refreshInterval 
}) => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadChannels = async () => {
    try {
      const response = await channelAPI.list();
      setChannels(response.data.channels);
      setError(null);
    } catch (err) {
      setError('Failed to load channels');
      console.error('Error loading channels:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadChannels();
    const interval = setInterval(loadChannels, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  if (loading && channels.length === 0) {
    return <div className="channel-list-loading">Loading channels...</div>;
  }

  if (error) {
    return <div className="channel-list-error">{error}</div>;
  }

  return (
    <div className="channel-list">
      <h2>Channels</h2>
      {channels.length === 0 ? (
        <p className="no-channels">No channels available</p>
      ) : (
        <ul>
          {channels.map(channel => (
            <li
              key={channel.channel_id}
              className={selectedChannel?.channel_id === channel.channel_id ? 'selected' : ''}
              onClick={() => onSelectChannel(channel)}
            >
              <div className="channel-name">{channel.name}</div>
              <div className="channel-info">
                {channel.agent_count}/{channel.max_agents} agents
              </div>
              {channel.description && (
                <div className="channel-description">{channel.description}</div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ChannelList;
```

4. Create `ui/src/components/ChannelList.css`:
```css
.channel-list {
  padding: 1rem;
}

.channel-list h2 {
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
  color: #2c3e50;
}

.channel-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.channel-list li {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.channel-list li:hover {
  background-color: #f8f9fa;
}

.channel-list li.selected {
  background-color: #3498db;
  color: white;
}

.channel-name {
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.channel-info {
  font-size: 0.85rem;
  opacity: 0.8;
}

.channel-description {
  font-size: 0.85rem;
  margin-top: 0.25rem;
  opacity: 0.7;
}

.no-channels {
  text-align: center;
  color: #7f8c8d;
}

.channel-list-loading,
.channel-list-error {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}
```

5. Create `ui/src/components/ChatView.tsx`:
```tsx
import React, { useState, useEffect, useRef } from 'react';
import { Channel, Message, Agent } from '../types';
import { messageAPI, agentAPI } from '../services/api';
import MessageItem from './MessageItem';
import AgentList from './AgentList';
import './ChatView.css';

interface Props {
  channel: Channel;
  refreshInterval: number;
}

const ChatView: React.FC<Props> = ({ channel, refreshInterval }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const loadData = async () => {
    try {
      const [messagesRes, agentsRes] = await Promise.all([
        messageAPI.list(channel.channel_id, 100),
        agentAPI.list(channel.channel_id)
      ]);
      
      setMessages(messagesRes.data.messages || []);
      setAgents(agentsRes.data.agents || []);
    } catch (err) {
      console.error('Error loading chat data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    loadData();
    const interval = setInterval(loadData, refreshInterval);
    return () => clearInterval(interval);
  }, [channel.channel_id, refreshInterval]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="chat-view">
      <div className="chat-header">
        <h2>{channel.name}</h2>
        <span className="channel-id">ID: {channel.channel_id}</span>
      </div>
      
      <div className="chat-content">
        <div className="messages-area">
          {loading && messages.length === 0 ? (
            <div className="loading">Loading messages...</div>
          ) : messages.length === 0 ? (
            <div className="no-messages">No messages yet</div>
          ) : (
            <>
              {messages.map(message => (
                <MessageItem key={message.message_id} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
        
        <div className="agents-sidebar">
          <AgentList agents={agents} />
        </div>
      </div>
    </div>
  );
};

export default ChatView;
```

6. Create `ui/src/components/MessageItem.tsx`:
```tsx
import React from 'react';
import { Message } from '../types';
import './MessageItem.css';

interface Props {
  message: Message;
}

const MessageItem: React.FC<Props> = ({ message }) => {
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  const highlightMentions = (content: string) => {
    return content.replace(/@(\w+)/g, '<span class="mention">@$1</span>');
  };

  return (
    <div className="message-item">
      <div className="message-header">
        <span className="sender">@{message.sender.username}</span>
        <span className="timestamp">{formatTimestamp(message.timestamp)}</span>
      </div>
      
      <div 
        className="message-content"
        dangerouslySetInnerHTML={{ __html: highlightMentions(message.content) }}
      />
      
      <div className="read-receipts">
        <span className="read-label">Read by:</span>
        {message.read_by.length === 0 ? (
          <span className="no-reads">No one yet</span>
        ) : (
          message.read_by.map((reader, index) => (
            <span key={index} className="reader">
              @{reader.username}
              <span className="read-time">
                ({new Date(reader.read_at).toLocaleTimeString()})
              </span>
            </span>
          ))
        )}
      </div>
    </div>
  );
};

export default MessageItem;
```

7. Create component CSS files and additional components as needed...

## Dependencies
- React setup completed
- API service configured

## Estimated Time: 1.5 hours