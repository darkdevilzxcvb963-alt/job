import React, { useState, useEffect, useRef } from 'react';
import { X, Bell, MessageCircle, CheckCircle, Clock, Circle, Send, ArrowLeft, Search, UserPlus } from 'lucide-react';
import { getConversations, getThread, sendMessage, listUsers } from '../services/api';
import { useMessaging } from '../contexts/MessagingContext';
import { useAuth } from '../contexts/AuthContext';
import './MessageSidebar.css';

const MessageSidebar = () => {
  const { user } = useAuth();
  const { isSidebarOpen, activeThread, openChat, closeSidebar, setActiveThread, notifications, unreadCount, refreshStatus } = useMessaging();
  const [conversations, setConversations] = useState([]);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearch, setShowSearch] = useState(false);
  const [showToast, setShowToast] = useState(null);
  const [justSent, setJustSent] = useState(false);
  const messagesEndRef = useRef(null);
  const prevUnreadCount = useRef(unreadCount);

  useEffect(() => {
    if (isSidebarOpen) {
      fetchConversations();
    }
  }, [isSidebarOpen]);

  useEffect(() => {
    if (activeThread) {
      fetchThread(activeThread.userId);
      const interval = setInterval(() => fetchThread(activeThread.userId), 5000);
      return () => clearInterval(interval);
    }
  }, [activeThread]);

  // Mobile style notification toast
  useEffect(() => {
    if (unreadCount > prevUnreadCount.current) {
      const lastNotif = notifications[0];
      if (lastNotif) {
        setShowToast(lastNotif.message);
        setTimeout(() => setShowToast(null), 4000);
      }
    }
    prevUnreadCount.current = unreadCount;
  }, [unreadCount, notifications]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchConversations = async () => {
    try {
      const res = await getConversations();
      setConversations(res.data || []);
    } catch (err) {
      console.error('Failed to fetch conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchThread = async (userId) => {
    try {
      const res = await getThread(userId);
      setMessages(res.data);
    } catch (err) {
      console.error('Failed to fetch thread:', err);
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }
    try {
      const res = await listUsers({ search: query });
      setSearchResults(res.data.items || []);
    } catch (err) {
      console.error('Search failed:', err);
    }
  };

  const handleBack = () => {
    setActiveThread(null);
    setMessages([]);
    setShowSearch(false);
    fetchConversations();
    refreshStatus();
  };

  const handleSend = async () => {
    if (!newMessage.trim() || !activeThread) return;
    setSending(true);
    try {
      await sendMessage({
        receiver_id: activeThread.userId,
        content: newMessage.trim()
      });
      setNewMessage('');
      setJustSent(true);
      setTimeout(() => setJustSent(false), 2000);
      fetchThread(activeThread.userId);
    } catch (err) {
      console.error('Failed to send message:', err);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isSidebarOpen) return null;

  return (
    <div className={`message-sidebar-overlay ${isSidebarOpen ? 'open' : ''}`} onClick={closeSidebar}>
      
      {/* Mobile-style Toast Notification */}
      {showToast && (
        <div className="ms-mobile-toast">
          <div className="toast-icon">💬</div>
          <div className="toast-content">
            <strong>New Message</strong>
            <span>{showToast}</span>
          </div>
        </div>
      )}

      <div className="message-sidebar" onClick={(e) => e.stopPropagation()}>
        <div className="ms-header">
          <div className="ms-title">
            {activeThread ? (
              <button className="ms-back-btn" onClick={handleBack}>
                <ArrowLeft size={18} />
              </button>
            ) : (
              <MessageCircle size={20} className="ms-icon-primary" />
            )}
            <span>{activeThread ? activeThread.userName : 'Messaging'}</span>
          </div>
          <div className="ms-header-actions">
            {!activeThread && !showSearch && user?.role === 'recruiter' && (
              <button className="ms-search-btn" onClick={() => setShowSearch(true)}>
                <Search size={18} />
              </button>
            )}
            <button className="ms-close-btn" onClick={closeSidebar}>
              <X size={22} />
            </button>
          </div>
        </div>

        <div className="ms-content">
          {showSearch && !activeThread && user?.role === 'recruiter' ? (
            <div className="ms-search-view">
              <div className="search-bar-container">
                <Search size={16} className="search-icon" />
                <input 
                  type="text" 
                  autoFocus
                  placeholder="Search candidates or recruiters..." 
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                />
                <button onClick={() => setShowSearch(false)}><X size={16} /></button>
              </div>
              <div className="search-results">
                {searchResults.length === 0 && searchQuery.length > 1 ? (
                  <p className="ms-empty">No users found</p>
                ) : (
                  searchResults.map(u => (
                    <div key={u.id} className="ms-item compact" onClick={() => { openChat(u.id, u.full_name); setShowSearch(false); }}>
                      <div className="ms-avatar">{u.full_name.charAt(0)}</div>
                      <div className="ms-item-info">
                        <span className="ms-item-name">{u.full_name}</span>
                        <span className="ms-item-sub">{u.role}</span>
                      </div>
                      <UserPlus size={16} className="add-icon" />
                    </div>
                  ))
                )}
              </div>
            </div>
          ) : activeThread ? (
            <div className="ms-thread-view">
              <div className="ms-messages-list">
                {messages.length === 0 ? (
                  <p className="ms-empty">No messages yet. Say hi!</p>
                ) : (
                  messages.map((msg, idx) => (
                    <div key={msg.id || idx} className={`ms-bubble ${msg.sender_id === activeThread.userId ? 'received' : 'sent'}`}>
                      <div className="bubble-text">{msg.content}</div>
                      <div className="bubble-time">{new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>
              <div className="ms-input-area">
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type a message..."
                  rows={1}
                />
                <button 
                  onClick={handleSend} 
                  disabled={!newMessage.trim() || sending || justSent}
                  className={sending ? 'sending' : justSent ? 'sent' : ''}
                >
                  {sending ? (
                    <Clock size={18} className="animate-spin" />
                  ) : justSent ? (
                    <CheckCircle size={18} />
                  ) : (
                    <Send size={18} />
                  )}
                </button>
              </div>
            </div>
          ) : (
            <div className="ms-list-view">
              <section className="ms-section">
                <div className="ms-section-header"><Bell size={16} /><span>Notifications</span></div>
                {notifications.slice(0, 3).map(n => (
                  <div key={n.id} className={`ms-item ${!n.is_read ? 'unread' : ''}`}>
                    <div className="ms-item-dot"></div>
                    <div className="ms-item-text">{n.message}</div>
                  </div>
                ))}
              </section>

              <section className="ms-section">
                <div className="ms-section-header"><Clock size={16} /><span>Recent Conversations</span></div>
                {conversations.length === 0 ? <p className="ms-empty">No chats yet. Start one!</p> : 
                  conversations.map(c => (
                    <div key={c.other_user_id} className={`ms-item ${c.unread_count > 0 ? 'unread' : ''}`} onClick={() => openChat(c.other_user_id, c.other_user_name)}>
                      <div className="ms-avatar">{c.other_user_name.charAt(0)}</div>
                      <div className="ms-item-info">
                        <div className="name-unread">
                          <span className="ms-item-name">{c.other_user_name}</span>
                          {c.unread_count > 0 && <span className="unread-dot-badge"></span>}
                        </div>
                        <span className="ms-item-text preview">{c.last_message}</span>
                      </div>
                    </div>
                  ))
                }
              </section>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageSidebar;
