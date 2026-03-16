import { useState, useEffect, useRef } from 'react'
import { getConversations, getThread, sendMessage, getUnreadCount } from '../services/api'
import { MessageCircle, Send, ArrowLeft, Circle } from 'lucide-react'

export default function MessageCenter() {
  const [conversations, setConversations] = useState([])
  const [activeThread, setActiveThread] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [unreadTotal, setUnreadTotal] = useState(0)
  const messagesEndRef = useRef(null)
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  useEffect(() => {
    fetchConversations()
    fetchUnread()
    const interval = setInterval(fetchUnread, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const fetchConversations = async () => {
    try {
      const res = await getConversations()
      setConversations(res.data)
    } catch (err) {
      console.error('Failed to load conversations:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchUnread = async () => {
    try {
      const res = await getUnreadCount()
      setUnreadTotal(res.data.unread_count)
    } catch (err) {
      // silently fail
    }
  }

  const openThread = async (userId, userName) => {
    setActiveThread({ userId, userName })
    try {
      const res = await getThread(userId)
      setMessages(res.data)
    } catch (err) {
      console.error('Failed to load thread:', err)
    }
    fetchConversations()
    fetchUnread()
  }

  const handleSend = async () => {
    if (!newMessage.trim() || !activeThread) return
    setSending(true)
    try {
      await sendMessage({
        receiver_id: activeThread.userId,
        content: newMessage.trim()
      })
      setNewMessage('')
      const res = await getThread(activeThread.userId)
      setMessages(res.data)
    } catch (err) {
      console.error('Failed to send message:', err)
    } finally {
      setSending(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (loading) {
    return (
      <div className="message-center">
        <div className="mc-loading">
          <div className="pulse-loader"></div>
          <p>Loading messages...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="message-center">
      <div className="mc-header">
        <h3>
          <MessageCircle size={20} /> Messages
          {unreadTotal > 0 && <span className="unread-badge">{unreadTotal}</span>}
        </h3>
      </div>

      <div className="mc-content">
        {/* Conversation List */}
        <div className={`mc-sidebar ${activeThread ? 'hidden-mobile' : ''}`}>
          {conversations.length === 0 ? (
            <div className="empty-state">
              <MessageCircle size={36} strokeWidth={1} />
              <p>No conversations yet</p>
            </div>
          ) : (
            conversations.map(conv => (
              <div
                key={conv.other_user_id}
                className={`conversation-item ${activeThread?.userId === conv.other_user_id ? 'active' : ''}`}
                onClick={() => openThread(conv.other_user_id, conv.other_user_name)}
              >
                <div className="conv-avatar">
                  {conv.other_user_name?.charAt(0)?.toUpperCase() || '?'}
                </div>
                <div className="conv-info">
                  <div className="conv-name">
                    {conv.other_user_name}
                    {conv.unread_count > 0 && (
                      <span className="unread-dot"><Circle size={8} fill="currentColor" /></span>
                    )}
                  </div>
                  <div className="conv-preview">{conv.last_message}</div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Thread View */}
        <div className={`mc-thread ${!activeThread ? 'hidden-mobile' : ''}`}>
          {activeThread ? (
            <>
              <div className="thread-header">
                <button className="btn-back" onClick={() => setActiveThread(null)}>
                  <ArrowLeft size={18} />
                </button>
                <div className="thread-avatar">
                  {activeThread.userName?.charAt(0)?.toUpperCase()}
                </div>
                <span className="thread-name">{activeThread.userName}</span>
              </div>

              <div className="thread-messages">
                {messages.map(msg => (
                  <div
                    key={msg.id}
                    className={`message-bubble ${msg.sender_id === user.id ? 'sent' : 'received'}`}
                  >
                    <div className="bubble-content">{msg.content}</div>
                    <div className="bubble-time">
                      {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              <div className="thread-input">
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type a message..."
                  rows={1}
                />
                <button
                  className="btn-send"
                  onClick={handleSend}
                  disabled={!newMessage.trim() || sending}
                >
                  <Send size={18} />
                </button>
              </div>
            </>
          ) : (
            <div className="empty-thread">
              <MessageCircle size={48} strokeWidth={1} />
              <p>Select a conversation to start messaging</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
