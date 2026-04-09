import React, { createContext, useContext, useState, useCallback, useRef } from 'react';
import './NotifyContext.css';

const NotifyContext = createContext(null);

export const useNotify = () => {
  const ctx = useContext(NotifyContext);
  if (!ctx) throw new Error('useNotify must be used within NotifyProvider');
  return ctx;
};

let _toastId = 0;

export const NotifyProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);
  const [confirm, setConfirm] = useState(null); // { message, resolve }
  const [promptData, setPromptData] = useState(null); // { message, defaultValue, resolve }
  const [promptInput, setPromptInput] = useState('');
  const confirmResolveRef = useRef(null);
  const promptResolveRef = useRef(null);

  // Toast notifications
  const toast = useCallback((message, type = 'info', duration = 4000) => {
    const id = ++_toastId;
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, duration);
  }, []);

  const success = useCallback((msg) => toast(msg, 'success'), [toast]);
  const error   = useCallback((msg) => toast(msg, 'error', 5000), [toast]);
  const info    = useCallback((msg) => toast(msg, 'info'), [toast]);
  const warning = useCallback((msg) => toast(msg, 'warning'), [toast]);

  // Confirm dialog - returns a Promise<boolean>
  const showConfirm = useCallback((message) => {
    return new Promise((resolve) => {
      confirmResolveRef.current = resolve;
      setConfirm({ message });
    });
  }, []);

  const handleConfirm = (result) => {
    setConfirm(null);
    if (confirmResolveRef.current) {
      confirmResolveRef.current(result);
      confirmResolveRef.current = null;
    }
  };

  // Prompt dialog - returns a Promise<string | null>
  const showPrompt = useCallback((message, defaultValue = '') => {
    return new Promise((resolve) => {
      promptResolveRef.current = resolve;
      setPromptInput(defaultValue);
      setPromptData({ message });
    });
  }, []);

  const handlePrompt = (submit) => {
    setPromptData(null);
    if (promptResolveRef.current) {
      promptResolveRef.current(submit ? promptInput : null);
      promptResolveRef.current = null;
    }
  };

  const dismissToast = (id) => setToasts(prev => prev.filter(t => t.id !== id));

  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
  };

  return (
    <NotifyContext.Provider value={{ toast, success, error, info, warning, confirm: showConfirm, prompt: showPrompt }}>
      {children}

      {/* Toast Stack */}
      <div className="notify-toast-stack">
        {toasts.map(t => (
          <div key={t.id} className={`notify-toast notify-toast--${t.type}`}>
            <span className="notify-toast__icon">{icons[t.type]}</span>
            <span className="notify-toast__msg">{t.message}</span>
            <button className="notify-toast__close" onClick={() => dismissToast(t.id)}>✕</button>
          </div>
        ))}
      </div>

      {/* Confirm Dialog */}
      {confirm && (
        <div className="notify-overlay">
          <div className="notify-confirm">
            <div className="notify-confirm__icon">🤔</div>
            <p className="notify-confirm__msg">{confirm.message}</p>
            <div className="notify-confirm__actions">
              <button className="notify-confirm__btn notify-confirm__btn--cancel" onClick={() => handleConfirm(false)}>
                Cancel
              </button>
              <button className="notify-confirm__btn notify-confirm__btn--ok" onClick={() => handleConfirm(true)}>
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Prompt Dialog */}
      {promptData && (
        <div className="notify-overlay">
          <div className="notify-confirm notify-prompt">
            <p className="notify-confirm__msg notify-prompt__msg">{promptData.message}</p>
            <input 
              type="text" 
              className="notify-prompt__input"
              value={promptInput}
              onChange={(e) => setPromptInput(e.target.value)}
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') handlePrompt(true);
                if (e.key === 'Escape') handlePrompt(false);
              }}
            />
            <div className="notify-confirm__actions">
              <button 
                className="notify-confirm__btn notify-confirm__btn--cancel" 
                onClick={() => handlePrompt(false)}
              >
                Cancel
              </button>
              <button 
                className="notify-confirm__btn notify-confirm__btn--ok" 
                onClick={() => handlePrompt(true)}
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </NotifyContext.Provider>
  );
};
