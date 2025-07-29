import React, { useState, useEffect, useRef } from 'react';
import { Channel, Message, Agent } from '../types';
import { messageAPI, agentAPI } from '../services/api';
import RichMessageItem from './RichMessageItem';
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
  const messagesAreaRef = useRef<HTMLDivElement>(null);
  const previousMessageCount = useRef(0);
  const isNearBottom = useRef(true);

  const checkIfNearBottom = () => {
    if (!messagesAreaRef.current) return true;
    const { scrollTop, scrollHeight, clientHeight } = messagesAreaRef.current;
    // Consider "near bottom" if within 100px of the bottom
    return scrollHeight - scrollTop - clientHeight < 100;
  };

  const loadData = async () => {
    try {
      // Check scroll position before loading new data
      isNearBottom.current = checkIfNearBottom();
      
      const [messagesRes, agentsRes] = await Promise.all([
        messageAPI.list(channel.channel_id, 100),
        agentAPI.list(channel.channel_id)
      ]);
      
      const newMessages = messagesRes.data.messages || [];
      previousMessageCount.current = messages.length;
      setMessages(newMessages);
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
    // Only scroll if we have new messages AND user was near the bottom
    if (messages.length > previousMessageCount.current && isNearBottom.current) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Scroll to bottom on initial load or channel change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'auto' });
  }, [channel.channel_id]);

  return (
    <div className="chat-view">
      <div className="chat-header">
        <h2>{channel.name}</h2>
        <span className="channel-id">ID: {channel.channel_id}</span>
      </div>
      
      <div className="chat-content">
        <div className="messages-area" ref={messagesAreaRef} onScroll={() => {
          isNearBottom.current = checkIfNearBottom();
        }}>
          {loading && messages.length === 0 ? (
            <div className="loading">Loading messages...</div>
          ) : messages.length === 0 ? (
            <div className="no-messages">No messages yet</div>
          ) : (
            <>
              {messages.map(message => (
                <RichMessageItem key={message.message_id} message={message} />
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