import React, { createContext, useContext, useState, useEffect } from 'react';
import { getMyNotifications, getUnreadCount } from '../services/api';

const MessagingContext = createContext(null);

export const useMessaging = () => {
  const context = useContext(MessagingContext);
  if (!context) throw new Error('useMessaging must be used within MessagingProvider');
  return context;
};

export const MessagingProvider = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeThread, setActiveThread] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);

  const toggleSidebar = () => setIsSidebarOpen(prev => !prev);
  
  const openChat = (userId, userName) => {
    setActiveThread({ userId, userName });
    setIsSidebarOpen(true);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
    setActiveThread(null);
  };

  const fetchStatus = async () => {
    try {
      const [countRes, notifRes] = await Promise.all([
        getUnreadCount(),
        getMyNotifications()
      ]);
      setUnreadCount(countRes.data.unread_count);
      setNotifications(notifRes.data.notifications || []);
    } catch (err) {
      console.error('Failed to fetch messaging status:', err);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const value = {
    isSidebarOpen,
    activeThread,
    unreadCount,
    notifications,
    toggleSidebar,
    openChat,
    closeSidebar,
    setActiveThread,
    refreshStatus: fetchStatus
  };

  return (
    <MessagingContext.Provider value={value}>
      {children}
    </MessagingContext.Provider>
  );
};
