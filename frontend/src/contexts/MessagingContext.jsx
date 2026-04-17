import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { getMyNotifications, getUnreadCount } from '../services/api';
import { useAuth } from './AuthContext';

const MessagingContext = createContext(null);

export const useMessaging = () => {
  const context = useContext(MessagingContext);
  if (!context) throw new Error('useMessaging must be used within MessagingProvider');
  return context;
};

export const MessagingProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeThread, setActiveThread] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [latestEvent, setLatestEvent] = useState(null);
  const socketRef = useRef(null);

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
    if (!isAuthenticated) return;
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

  // WebSocket Connection Management
  useEffect(() => {
    if (isAuthenticated && user?.id) {
      const token = localStorage.getItem('access_token');
      let apiBase = import.meta.env.VITE_API_URL || window.location.origin;
      let wsBase = apiBase.replace(/^http/, 'ws').replace(/\/api\/v1\/?$/, '');
      const wsUrl = `${wsBase}/ws/${user.id}?token=${token}`;
      
      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        console.log('Connected to Messaging WebSocket');
        fetchStatus(); // Sync initial state
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Real-time event received:', data.type);
        setLatestEvent(data); // Expose to components

        if (data.type === 'new_message') {
          setUnreadCount(prev => prev + 1);
        } else if (data.type === 'new_notification') {
          setNotifications(prev => [data.notification, ...prev]);
          setUnreadCount(prev => prev + 1);
        }
      };

      socket.onclose = () => {
        console.log('Messaging WebSocket disconnected');
      };

      socket.onerror = (err) => {
        console.error('WebSocket Error:', err);
      };

      return () => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.close();
        }
      };
    }
  }, [isAuthenticated, user?.id]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchStatus();
      const interval = setInterval(fetchStatus, 30000); // 30s polling
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  const value = {
    isSidebarOpen,
    activeThread,
    unreadCount,
    notifications,
    latestEvent,
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
