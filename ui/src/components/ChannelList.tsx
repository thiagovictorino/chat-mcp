import React, { useState, useEffect } from 'react';
import { Channel } from '../types';
import { channelAPI } from '../services/api';
import ChannelDeleteConfirmation from './ChannelDeleteConfirmation';
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
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    channel: Channel | null;
  }>({ isOpen: false, channel: null });

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
              <div className="channel-content">
                <div className="channel-name">{channel.name}</div>
                <div className="channel-info">
                  {channel.agent_count}/{channel.max_agents} agents
                </div>
                {channel.description && (
                  <div className="channel-description">{channel.description}</div>
                )}
              </div>
              <button
                className="channel-delete-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setDeleteModal({ isOpen: true, channel });
                }}
                title="Delete channel"
              >
                🗑️
              </button>
            </li>
          ))}
        </ul>
      )}
      
      <ChannelDeleteConfirmation
        isOpen={deleteModal.isOpen}
        onClose={() => setDeleteModal({ isOpen: false, channel: null })}
        onSuccess={() => {
          loadChannels();
          if (selectedChannel?.channel_id === deleteModal.channel?.channel_id) {
            onSelectChannel(channels[0] || null);
          }
        }}
        channel={deleteModal.channel}
      />
    </div>
  );
};

export default ChannelList;