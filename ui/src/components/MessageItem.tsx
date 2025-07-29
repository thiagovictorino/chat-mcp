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