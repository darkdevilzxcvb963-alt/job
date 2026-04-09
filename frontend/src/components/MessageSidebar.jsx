import React, { useState, useEffect, useRef } from 'react';
import { X, Bell, MessageCircle, CheckCircle, Clock, Circle, Send, ArrowLeft, Search, UserPlus } from 'lucide-react';
import { getConversations, getThread, sendMessage, listUsers } from '../services/api';
import { useMessaging } from '../contexts/MessagingContext';
import { useAuth } from '../contexts/AuthContext';
import { useNotify } from '../contexts/NotifyContext';
import './MessageSidebar.css';

const MessageSidebar = () => {
  const { user } = useAuth();
  const { error: notifyError } = useNotify();
  const { isSidebarOpen, activeThread, openChat, closeSidebar, setActiveThread, notifications, unreadCount, refreshStatus, latestEvent } = useMessaging();
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
  const [leftPanelTab, setLeftPanelTab] = useState('conversations'); // 'conversations' | 'notifications'
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

  // Real-time message listener
  useEffect(() => {
    if (activeThread && latestEvent) {
      if (latestEvent.type === 'new_message' && (
        latestEvent.message.sender_id === activeThread.userId || 
        latestEvent.message.sender_id === user.id
      )) {
        // Only append if it's for this conversation
        // check if message is already in list (to avoid duplicates if we just sent it)
        setMessages(prev => {
          if (prev.some(m => m.id === latestEvent.message.id)) return prev;
          return [...prev, latestEvent.message];
        });
      }
    }
  }, [latestEvent, activeThread, user?.id]);

  const handleSend = async () => {
    if (!newMessage.trim() || !activeThread) return;
    const msgText = newMessage.trim();
    setSending(true);
    setNewMessage(''); // Clear immediately for better UX
    
    try {
      const res = await sendMessage({
        receiver_id: activeThread.userId,
        content: msgText
      });
      
      // Manually add sent message if WS hasn't echoed it back yet
      setMessages(prev => {
        if (prev.some(m => m.id === res.data.id)) return prev;
        return [...prev, res.data];
      });
      
      setJustSent(true);
      setTimeout(() => setJustSent(false), 2000);
    } catch (err) {
      console.error('Failed to send message:', err);
      notifyError(err.response?.data?.detail || 'Failed to send message. Please try again.');
      setNewMessage(msgText); // Restore on failure
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
            <MessageCircle size={20} className="ms-icon-primary" />
            <span>Messages</span>
          </div>
          <div className="ms-header-actions">
            {!showSearch && user?.role === 'recruiter' && (
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
          {/* LEFT SIDE: CONVERSATIONS LIST */}
          <div className="ms-sidebar-left">
            {showSearch && user?.role === 'recruiter' ? (
              <div className="ms-search-view">
                <div className="search-bar-container">
                  <Search size={16} className="search-icon" />
                  <input 
                    type="text" 
                    autoFocus
                    placeholder="Search candidates..." 
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
            ) : (
              <div className="ms-list-view" style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}>
                <div className="ms-tabs-header" style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', marginBottom: '1rem' }}>
                  <button 
                    className={`ms-tab-btn ${leftPanelTab === 'conversations' ? 'active' : ''}`}
                    onClick={() => setLeftPanelTab('conversations')}
                    style={{ flex: 1, padding: '0.75rem', background: 'none', border: 'none', borderBottom: leftPanelTab === 'conversations' ? '2px solid #6366f1' : '2px solid transparent', color: leftPanelTab === 'conversations' ? '#6366f1' : 'var(--text-secondary)', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
                  >
                    <Clock size={16} /> Conversations
                  </button>
                  <button 
                    className={`ms-tab-btn ${leftPanelTab === 'notifications' ? 'active' : ''}`}
                    onClick={() => setLeftPanelTab('notifications')}
                    style={{ flex: 1, padding: '0.75rem', background: 'none', border: 'none', borderBottom: leftPanelTab === 'notifications' ? '2px solid #6366f1' : '2px solid transparent', color: leftPanelTab === 'notifications' ? '#6366f1' : 'var(--text-secondary)', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
                  >
                    <Bell size={16} /> Notifications
                  </button>
                </div>

                {leftPanelTab === 'notifications' && (
                  <section className="ms-section" style={{ flex: 1, overflowY: 'auto', paddingRight: '0.5rem' }}>
                    {notifications.length === 0 ? <p className="ms-empty">No new notifications.</p> :
                      notifications.map(n => (
                        <div key={n.id} className={`ms-item ${!n.is_read ? 'unread' : ''}`} style={{ marginBottom: '0.75rem' }}>
                          <div className="ms-item-dot"></div>
                          <div className="ms-item-text">{n.message}</div>
                        </div>
                      ))
                    }
                  </section>
                )}

                {leftPanelTab === 'conversations' && (
                  <section className="ms-section" style={{ flex: 1, overflowHidden: 'hidden', display: 'flex', flexDirection: 'column' }}>
                    <div className="conversations-scroll-area">
                      {conversations.length === 0 ? <p className="ms-empty">No chats yet. Start one!</p> : 
                        conversations.map(c => (
                          <div key={c.other_user_id} className={`ms-item ${activeThread?.userId === c.other_user_id ? 'active-chat' : ''} ${c.unread_count > 0 ? 'unread' : ''}`} onClick={() => openChat(c.other_user_id, c.other_user_name)}>
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
                    </div>
                  </section>
                )}
              </div>
            )}

          </div>

          {/* RIGHT SIDE: THREAD VIEW OR EMPTY STATE */}
          <div className="ms-sidebar-right">
            {activeThread ? (
              <div className="ms-thread-view">
                <div className="ms-thread-header">
                  <div className="ms-thread-user-info">
                    <div className="ms-avatar">{activeThread.userName.charAt(0)}</div>
                    <strong>{activeThread.userName}</strong>
                  </div>
                </div>
                <div className="ms-messages-list">
                  {messages.length === 0 ? (
                    <div className="ms-thread-empty">
                      <MessageCircle size={40} className="empty-chat-icon" />
                      <p>Start the conversation with {activeThread.userName}</p>
                    </div>
                  ) : (
                    messages.map((msg, idx) => {
                      const isMe = String(msg.sender_id) === String(user?.id);
                      const msgDate = new Date(msg.created_at);
                      const today = new Date();
                      const isToday = msgDate.toDateString() === today.toDateString();
                      const timeStr = msgDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                      const dateStr = msgDate.toLocaleDateString([], { month: 'short', day: 'numeric' });
                      
                      return (
                        <div key={msg.id || idx} className={`ms-bubble-wrapper ${isMe ? 'sent' : 'received'}`}>
                          {!isMe && (
                            <div className="ms-avatar-sm">
                              {(msg.sender_name || 'U').charAt(0).toUpperCase()}
                            </div>
                          )}
                          <div className="ms-bubble-container">
                            <div className={`ms-bubble ${isMe ? 'sent' : 'received'}`}>
                              <div className="bubble-text">{msg.content}</div>
                            </div>
                            <div className="bubble-meta">
                              <span className="sender-name">
                                {isMe ? (user?.full_name || 'You') : (msg.sender_name || activeThread?.userName || 'Unknown')}
                              </span>
                              <span className="bubble-time">
                                {!isToday && <span>{dateStr} · </span>}
                                {timeStr}
                              </span>
                            </div>
                          </div>
                        </div>
                      );
                    })
                  )}
                  <div ref={messagesEndRef} />
                </div>
                <div className="ms-input-area">
                  <textarea
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={`Message ${activeThread.userName}...`}
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
              <div className="ms-thread-empty-state">
                <div className="empty-state-content">
                  <MessageCircle size={48} className="empty-state-icon" />
                  <h3>Your Messages</h3>
                  <p>Select a conversation from the list to start messaging.</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageSidebar;
