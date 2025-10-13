import PropTypes from 'prop-types';
import { useEffect, useState } from 'react';

/**
 * FlashMessage Component - Display temporary alert/notification messages
 */
function FlashMessage({ message, type = 'info', duration = 5000, onClose }) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        if (onClose) onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  if (!isVisible || !message) return null;

  return (
    <div className={`flash-message ${type}`} role="alert">
      <div className="flex justify-between items-center">
        <span>{message}</span>
        {onClose && (
          <button
            onClick={() => {
              setIsVisible(false);
              onClose();
            }}
            className="ml-4 text-lg font-bold hover:opacity-70"
            aria-label="Close message"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}

FlashMessage.propTypes = {
  message: PropTypes.string.isRequired,
  type: PropTypes.oneOf(['success', 'error', 'info', 'warning']),
  duration: PropTypes.number,
  onClose: PropTypes.func,
};

/**
 * FlashMessages Container - Display multiple flash messages
 */
function FlashMessages({ messages = [], onDismiss }) {
  if (!messages || messages.length === 0) return null;

  return (
    <div className="max-w-2xl mx-auto my-5 px-4">
      {messages.map((msg, index) => (
        <FlashMessage
          key={msg.id || index}
          message={msg.message}
          type={msg.type || 'info'}
          duration={msg.duration}
          onClose={() => onDismiss && onDismiss(msg.id || index)}
        />
      ))}
    </div>
  );
}

FlashMessages.propTypes = {
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      message: PropTypes.string.isRequired,
      type: PropTypes.oneOf(['success', 'error', 'info', 'warning']),
      duration: PropTypes.number,
    })
  ),
  onDismiss: PropTypes.func,
};

export { FlashMessage, FlashMessages };
export default FlashMessages;
