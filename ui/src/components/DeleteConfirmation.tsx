import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import './DeleteConfirmation.css';

interface DeleteConfirmationProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  itemName?: string;
  itemCount?: number;
  isBulk?: boolean;
}

const DeleteConfirmation: React.FC<DeleteConfirmationProps> = ({
  isOpen,
  onClose,
  onConfirm,
  itemName,
  itemCount,
  isBulk = false
}) => {
  const [countdown, setCountdown] = useState<number | null>(null);

  useEffect(() => {
    if (isOpen && !isBulk) {
      setCountdown(5);
    }
  }, [isOpen, isBulk]);

  useEffect(() => {
    if (countdown && countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(countdown - 1);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleConfirm = () => {
    onConfirm();
    
    if (!isBulk) {
      const toastId = toast.success(
        <div className="undo-toast">
          <span>✓ {itemName} deleted</span>
          <button
            className="undo-button"
            onClick={() => {
              toast.dismiss(toastId);
              // Handle undo logic here
            }}
          >
            Undo ({countdown}s)
          </button>
        </div>,
        {
          duration: 5000,
          id: 'delete-undo',
        }
      );
    }
    
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="delete-confirmation-overlay">
      <div className="delete-confirmation-modal">
        <h3 className="delete-title">
          {isBulk ? `Delete ${itemCount} items?` : `Delete ${itemName}?`}
        </h3>
        <p className="delete-message">
          {isBulk 
            ? "This action cannot be undone. All selected items will be permanently removed."
            : "This action can be undone for 5 seconds"
          }
        </p>
        <div className="delete-actions">
          <button className="delete-cancel" onClick={onClose}>
            Cancel
          </button>
          <button className="delete-confirm" onClick={handleConfirm}>
            {isBulk ? "I understand, delete all" : "Delete"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmation;