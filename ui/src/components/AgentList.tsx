import React from 'react';
import { Agent } from '../types';
import './AgentList.css';

interface Props {
  agents: Agent[];
}

const AgentList: React.FC<Props> = ({ agents }) => {
  const formatJoinTime = (joinedAt: string) => {
    const date = new Date(joinedAt);
    return date.toLocaleString();
  };

  return (
    <div className="agent-list">
      <h3>Active Agents ({agents.length})</h3>
      {agents.length === 0 ? (
        <p className="no-agents">No agents in this channel</p>
      ) : (
        <ul>
          {agents.map(agent => (
            <li key={agent.agent_id}>
              <div className="agent-username">@{agent.username}</div>
              <div className="agent-role">{agent.role_description}</div>
              <div className="agent-joined">
                Joined: {formatJoinTime(agent.joined_at)}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AgentList;