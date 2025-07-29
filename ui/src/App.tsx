import React, { useState, useEffect } from 'react';
import ChannelList from './components/ChannelList';
import ChatView from './components/ChatView';
import LogViewer from './components/LogViewer';
import Navigation from './components/Navigation';
import ToastProvider from './components/ToastProvider';
import { Channel } from './types';
import './App.css';
import './styles/design-system.css';

function App() {
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);
  const [showLogs, setShowLogs] = useState(false);
  const [currentSection, setCurrentSection] = useState('dashboard');
  const [refreshInterval] = useState(
    parseInt(process.env.REACT_APP_REFRESH_INTERVAL || '2000')
  );

  const handleNavigate = (section: string) => {
    setCurrentSection(section);
    if (section === 'scan') {
      // Handle scanner functionality
      console.log('Opening scanner...');
    }
  };

  return (
    <div className="app">
      <ToastProvider />
      
      <div className="app-header">
        <h1>Multi-Agent Communication Platform</h1>
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
      
      {showLogs && (
        <button 
          className="log-toggle floating"
          onClick={() => setShowLogs(false)}
        >
          Hide Logs
        </button>
      )}
    </div>
  );
}

export default App;