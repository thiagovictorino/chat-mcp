import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { Channel } from '../types';
import { channelAPI } from '../services/api';
import './ChannelDeleteConfirmation.css';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  channel: Channel | null;
}

const ChannelDeleteConfirmation: React.FC<Props> = ({ 
  isOpen, 
  onClose, 
  onSuccess,
  channel 
}) => {
  const [channelNameInput, setChannelNameInput] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!channel || channelNameInput !== channel.name) return;

    setIsDeleting(true);
    try {
      await channelAPI.delete(channel.channel_id);
      toast.success(`Channel "${channel.name}" deleted permanently`);
      onSuccess();
      handleClose();
    } catch (error) {
      toast.error('Failed to delete channel. Please try again.');
      console.error('Delete error:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleClose = () => {
    setChannelNameInput('');
    onClose();
  };

  if (!isOpen || !channel) return null;

  const isDeleteEnabled = channelNameInput === channel.name && !isDeleting;

  return (
    <div className="channel-delete-overlay">
      <div className="channel-delete-modal">
        <h3 className="delete-title">Delete "{channel.name}" channel?</h3>
        
        <div className="delete-warning">
          <span className="warning-icon">⚠️</span>
          <p>This will permanently delete:</p>
          <ul>
            <li>All messages in this channel</li>
            <li>All files and attachments</li>
            <li>All member history</li>
          </ul>
        </div>

        <div className="delete-confirmation">
          <p>Type <strong>{channel.name}</strong> to confirm:</p>
          <input
            type="text"
            value={channelNameInput}
            onChange={(e) => setChannelNameInput(e.target.value)}
            placeholder="Enter channel name"
            className="channel-name-input"
            autoFocus
          />
        </div>

        <div className="delete-actions">
          <button 
            className="delete-cancel" 
            onClick={handleClose}
            disabled={isDeleting}
          >
            Cancel
          </button>
          <button 
            className={`delete-confirm ${!isDeleteEnabled ? 'disabled' : ''}`}
            onClick={handleDelete}
            disabled={!isDeleteEnabled}
          >
            {isDeleting ? 'Deleting...' : 'Delete Permanently'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChannelDeleteConfirmation;