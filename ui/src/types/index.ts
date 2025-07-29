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