import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, MessageSquare, Calendar, Activity, Zap, CheckCircle, Clock, AlertCircle, UploadCloud, Plus, X, BookOpen, BarChart3, Sun, Moon, Trash2, Send, FileText } from 'lucide-react';
import './index.css';

const TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'chat', label: 'Chat Console', icon: MessageSquare },
  { id: 'schedule', label: 'Daily Schedule', icon: Calendar },
  { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
  { id: 'pipeline', label: 'Pipeline Status', icon: Activity },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [metrics, setMetrics] = useState({ mastery_avg: '--', topics_tracked: 0, pending_labs: 0, study_streak: 0, feed: [], topics: [] });
  const [status, setStatus] = useState({ status: 'connecting', agent_available: false });
  const [showTopicModal, setShowTopicModal] = useState(false);
  const [theme, setTheme] = useState('dark');
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profileData, setProfileData] = useState({ name: '', major: '', year: '', gpa: '', university: '' });

  useEffect(() => {
    fetchData();
    // Apply theme
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const fetchData = () => {
    fetch('/api/status')
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(err => console.error("API error:", err));

    fetch('/api/metrics')
      .then(res => res.json())
      .then(data => setMetrics(data); if(data.student) setProfileData(data.student); })
      .catch(err => console.error("Metrics error:", err));
  };

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const handleAddTopic = async (topicName) => {
    try {
      const res = await fetch('/api/topics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: topicName })
      });
      if(res.ok) {
        fetchData();
      }
    } catch(e) {
      console.error(e);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      
      {/* Sidebar */}
      <motion.div 
        initial={{ x: -300 }}
        animate={{ x: 0 }}
        style={{ 
          width: '280px', 
          borderRight: '1px solid var(--glass-border)',
          background: 'linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%)',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '40px' }}>
          <Zap size={32} color="var(--accent-cyan)" />
          <h2 className="glow-text" style={{ fontSize: '1.4rem', margin: 0 }}>Academic Commander</h2>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
          {TABS.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <motion.button
                key={tab.id}
                whileHover={{ scale: 1.02, x: 5 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '12px',
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-sm)',
                  border: isActive ? '1px solid var(--glass-border)' : '1px solid transparent',
                  background: isActive ? 'var(--glass-bg)' : 'transparent',
                  color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  transition: 'background 0.2s',
                  textAlign: 'left'
                }}
              >
                <Icon size={20} color={isActive ? 'var(--accent-cyan)' : 'var(--text-secondary)'} />
                <span style={{ fontWeight: isActive ? 600 : 400 }}>{tab.label}</span>
              </motion.button>
            )
          })}
        </nav>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <button 
            onClick={toggleTheme}
            style={{
              display: 'flex', alignItems: 'center', gap: '10px',
              padding: '12px', borderRadius: 'var(--radius-sm)',
              background: 'var(--glass-bg)', border: '1px solid var(--glass-border)',
              color: 'var(--text-primary)', cursor: 'pointer'
            }}
          >
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
          </button>

          <div className="glass-panel" style={{ padding: '16px', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{
                width: '10px', height: '10px', borderRadius: '50%',
                background: status.agent_available ? 'var(--accent-green)' : 'var(--accent-red)',
                boxShadow: `0 0 10px ${status.agent_available ? 'var(--accent-green)' : 'var(--accent-red)'}`
              }} />
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                {status.status === 'connecting' ? 'Connecting...' : status.agent_available ? 'ADK AGENT OPERATIONAL' : 'ADK CONFIG ERROR'}
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main Content Area */}
      <div style={{ flex: 1, padding: '40px', overflowY: 'auto' }}>
        <AnimatePresence mode="wait">
          
          {activeTab === 'dashboard' && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
                <div>
                  <h1 className="glow-text" style={{ fontSize: '2.5rem', marginBottom: '8px' }}>
                    Welcome back, {metrics.student ? metrics.student.name : 'Commander'}
                  </h1>
                  <p style={{ color: 'var(--text-secondary)' }}>
                    {metrics.student ? `${metrics.student.major} • ${metrics.student.year} • GPA: ${metrics.student.gpa} • ${metrics.student.university}` : 'Real-time overview of your academic operations.'}
                  </p>
                </div>
                <button 
                  onClick={() => setShowProfileModal(true)}
                  style={{ padding: '10px 20px', background: 'var(--glass-bg)', color: 'var(--text-primary)', border: '1px solid var(--glass-border)', borderRadius: '8px', cursor: 'pointer', display: 'flex', gap: '8px', alignItems: 'center' }}
                >
                   Edit Profile
                </button>
              </header>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '40px' }}>
                <MetricCard title="Topics Tracked" value={metrics.topics_tracked} color="var(--accent-cyan)" onClick={() => setActiveTab('knowledge')} />
                <MetricCard title="Avg Mastery" value={metrics.mastery_avg} color="var(--accent-purple)" onClick={() => setActiveTab('analytics')} />
                <MetricCard title="Pending Labs" value={metrics.pending_labs} color="var(--accent-green)" onClick={() => setActiveTab('pipeline')} />
                <MetricCard title="Study Streak" value={`${metrics.study_streak} days 🔥`} color="var(--accent-orange)" onClick={() => setActiveTab('schedule')} />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                {/* Live Activity Feed */}
                <div className="glass-panel" style={{ padding: '24px' }}>
                  <h3 style={{ marginBottom: '20px', color: 'var(--text-primary)' }}>Live Activity Feed</h3>
                  {metrics.feed && metrics.feed.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {metrics.feed.map((item, idx) => (
                        <div key={idx} style={{ display: 'flex', gap: '16px', alignItems: 'center', paddingBottom: '16px', borderBottom: idx < metrics.feed.length - 1 ? '1px solid var(--glass-border)' : 'none' }}>
                          <div style={{ padding: '8px', background: 'var(--glass-bg)', borderRadius: '50%' }}>
                            <Activity size={16} color="var(--accent-cyan)" />
                          </div>
                          <div style={{ flex: 1 }}>
                            <div style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>{item.event}</div>
                            <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '4px' }}>{item.time}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ color: 'var(--text-secondary)' }}>No recent activity.</p>
                  )}
                </div>

                {/* Tracked Topics */}
                <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', maxHeight: '400px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h3 style={{ margin: 0, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '12px' }}>
                      Tracked Topics
                      <span style={{ fontSize: '0.8rem', padding: '4px 8px', background: 'var(--glass-bg)', borderRadius: '12px' }}>{metrics.topics_tracked} Total</span>
                    </h3>
                    <motion.button 
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setShowTopicModal(true)}
                      style={{
                        display: 'flex', alignItems: 'center', gap: '6px',
                        padding: '6px 12px', borderRadius: 'var(--radius-sm)',
                        background: 'rgba(0, 240, 255, 0.1)', border: '1px solid rgba(0, 240, 255, 0.3)',
                        color: 'var(--accent-cyan)', cursor: 'pointer', fontSize: '0.85rem'
                      }}
                    >
                      <Plus size={14} /> Add Topic
                    </motion.button>
                  </div>
                  
                  <div style={{ overflowY: 'auto', flex: 1, paddingRight: '8px' }}>
                    {metrics.topics && metrics.topics.length > 0 ? (
                      metrics.topics.map((t, idx) => (
                        <div key={idx} style={{ marginBottom: '16px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                            <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{t.name}</span>
                            <span style={{ color: t.mastery > 80 ? 'var(--accent-green)' : t.mastery > 50 ? 'var(--accent-yellow)' : 'var(--accent-red)' }}>{t.mastery}%</span>
                          </div>
                          <div style={{ height: '6px', background: 'var(--glass-bg)', borderRadius: '3px', overflow: 'hidden' }}>
                            <motion.div 
                              initial={{ width: 0 }}
                              animate={{ width: `${t.mastery}%` }}
                              transition={{ duration: 1, delay: 0.2 }}
                              style={{ 
                                height: '100%', 
                                background: t.mastery > 80 ? 'var(--accent-green)' : t.mastery > 50 ? 'var(--accent-yellow)' : 'var(--accent-red)'
                              }} 
                            />
                          </div>
                        </div>
                      ))
                    ) : (
                      <p style={{ color: 'var(--text-secondary)' }}>No topics tracked yet.</p>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'chat' && <ChatConsoleView metrics={metrics} />}
          {activeTab === 'schedule' && <ScheduleView />}
          {activeTab === 'knowledge' && <KnowledgeBaseView topics={metrics.topics} />}
          {activeTab === 'pipeline' && <PipelineStatusView />}
          {activeTab === 'analytics' && <AnalyticsView />}
        </AnimatePresence>
      </div>

      {showTopicModal && <AddTopicModal onClose={() => setShowTopicModal(false)} onAdd={handleAddTopic} />}
    </div>
  );
}

function MetricCard({ title, value, color, onClick }) {
  return (
    <motion.div
      whileHover={{ y: -5, boxShadow: `0 10px 30px -10px ${color}` }}
      onClick={onClick}
      className="glass-panel"
      style={{
        padding: '24px',
        borderTop: `2px solid ${color}`,
        cursor: onClick ? 'pointer' : 'default'
      }}
    >
      <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '12px', fontWeight: 600 }}>{title}</div>
      <div style={{ color: 'var(--text-primary)', fontSize: '2.5rem', fontWeight: 800, fontFamily: 'Outfit' }}>{value}</div>
    </motion.div>
  );
}

function ChatConsoleView({ metrics }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState('');
  const [selectedFile, setSelectedFile] = useState('');
  const [files, setFiles] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Fetch chat history
    fetch('/api/chat_history')
      .then(res => res.json())
      .then(data => {
        if(data && data.length > 0) setMessages(data);
        else setMessages([{ role: 'agent', content: 'Hello! I am Academic Commander. Ask me anything about your studies or upload materials for analysis.' }]);
      })
      .catch(err => console.error(err));

    // Fetch uploaded files for dropdown
    fetch('/api/files')
      .then(res => res.json())
      .then(data => setFiles(data))
      .catch(err => console.error(err));
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text) => {
    const msg = text || input;
    if (!msg.trim()) return;

    const newMessages = [...messages, { role: 'user', content: msg, topic: selectedTopic, file: selectedFile }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, topic: selectedTopic, file: selectedFile })
      });
      const data = await res.json();
      setMessages([...newMessages, { role: 'agent', content: data.reply }]);
    } catch (err) {
      setMessages([...newMessages, { role: 'agent', content: 'Error connecting to agent.' }]);
    } finally {
      setLoading(false);
    }
  };

  const suggestions = [
    "What topics do I need to study for finals?",
    "Generate a coding lab for Linear Algebra",
    "Explain my latest weak areas",
    "How is my study streak looking?"
  ];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h1 className="glow-text" style={{ fontSize: '2rem', marginBottom: '24px' }}>Chat Console</h1>
      
      <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div style={{ flex: 1, padding: '24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ display: 'flex', gap: '16px', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
              <div style={{
                width: '40px', height: '40px', borderRadius: '50%',
                background: msg.role === 'user' ? 'var(--accent-purple)' : 'var(--accent-cyan)',
                display: 'flex', alignItems: 'center', justifyContent: 'center'
              }}>
                {msg.role === 'user' ? <Zap size={20} color="white" /> : <Zap size={20} color="black" />}
              </div>
              <div style={{
                maxWidth: '70%', padding: '16px', borderRadius: 'var(--radius-sm)',
                background: msg.role === 'user' ? 'rgba(217, 70, 239, 0.1)' : 'rgba(0, 240, 255, 0.05)',
                border: msg.role === 'user' ? '1px solid rgba(217, 70, 239, 0.2)' : '1px solid rgba(0, 240, 255, 0.1)',
                color: 'var(--text-primary)', lineHeight: 1.6
              }}>
                {(msg.topic || msg.file) && (
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '8px', display: 'flex', gap: '8px' }}>
                    {msg.topic && <span style={{ background: 'var(--glass-bg)', padding: '2px 6px', borderRadius: '4px' }}>Topic: {msg.topic}</span>}
                    {msg.file && <span style={{ background: 'var(--glass-bg)', padding: '2px 6px', borderRadius: '4px' }}>File: {msg.file}</span>}
                  </div>
                )}
                <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ display: 'flex', gap: '16px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Zap size={20} color="black" />
              </div>
              <div style={{ padding: '16px', color: 'var(--text-secondary)' }}>Agent is reasoning...</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Context Selectors & Suggestions */}
        <div style={{ padding: '16px 24px', background: 'rgba(0,0,0,0.2)', borderTop: '1px solid var(--glass-border)' }}>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
            {suggestions.map((s, i) => (
              <button key={i} onClick={() => handleSend(s)} style={{
                padding: '6px 12px', background: 'var(--glass-bg)', border: '1px solid var(--glass-border)',
                borderRadius: '16px', color: 'var(--accent-cyan)', cursor: 'pointer', fontSize: '0.85rem'
              }}>
                {s}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', gap: '16px', marginBottom: '12px' }}>
             <select 
                value={selectedTopic} 
                onChange={(e) => setSelectedTopic(e.target.value)}
                style={{ padding: '8px', borderRadius: '8px', background: 'var(--bg-secondary)', color: 'var(--text-primary)', border: '1px solid var(--glass-border)' }}
             >
                <option value="">-- Optional Topic Context --</option>
                {metrics.topics && metrics.topics.map((t, i) => <option key={i} value={t.name}>{t.name}</option>)}
             </select>

             <select 
                value={selectedFile} 
                onChange={(e) => setSelectedFile(e.target.value)}
                style={{ padding: '8px', borderRadius: '8px', background: 'var(--bg-secondary)', color: 'var(--text-primary)', border: '1px solid var(--glass-border)' }}
             >
                <option value="">-- Optional File Context --</option>
                {files && files.map((f, i) => <option key={i} value={f.name}>{f.name}</option>)}
             </select>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Message the Academic Commander..."
              style={{
                flex: 1, padding: '16px', borderRadius: 'var(--radius-sm)',
                background: 'var(--bg-secondary)', border: '1px solid var(--glass-border)',
                color: 'var(--text-primary)', outline: 'none', fontSize: '1rem'
              }}
            />
            <button
              onClick={() => handleSend()}
              style={{
                padding: '0 24px', borderRadius: 'var(--radius-sm)',
                background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))',
                color: 'white', border: 'none', cursor: 'pointer', fontWeight: 600,
                display: 'flex', alignItems: 'center', gap: '8px'
              }}
            >
              <Send size={18} /> Send
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function ScheduleView() {
  const [schedule, setSchedule] = useState([]);

  useEffect(() => {
    fetch('/api/schedule')
      .then(res => res.json())
      .then(data => setSchedule(data))
      .catch(err => console.error(err));
  }, []);

  const handleComplete = (idx) => {
    const updated = [...schedule];
    updated[idx].status = 'completed';
    setSchedule(updated);
  };

  const handleDelete = (idx) => {
    const updated = schedule.filter((_, i) => i !== idx);
    setSchedule(updated);
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <h1 className="glow-text" style={{ fontSize: '2rem', marginBottom: '8px' }}>Daily Schedule</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>AI-optimized study routine based on deadlines and weak topics.</p>

      <div className="glass-panel" style={{ padding: '32px' }}>
        {schedule.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {schedule.map((item, i) => (
              <div key={i} style={{ 
                display: 'flex', alignItems: 'center', gap: '20px', padding: '20px', 
                background: 'var(--glass-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--glass-border)',
                opacity: item.status === 'completed' ? 0.6 : 1,
                transition: 'all 0.3s'
              }}>
                <div style={{ color: 'var(--accent-cyan)', fontWeight: 600, width: '80px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Clock size={16} />
                  {item.time.substring(11, 16)}
                </div>
                <div style={{ flex: 1, color: item.status === 'completed' ? 'var(--text-secondary)' : 'var(--text-primary)', textDecoration: item.status === 'completed' ? 'line-through' : 'none', fontWeight: 500, fontSize: '1.1rem' }}>
                  {item.activity}
                </div>
                
                <div style={{ display: 'flex', gap: '12px' }}>
                   {item.status !== 'completed' && (
                     <button onClick={() => handleComplete(i)} style={{ background: 'transparent', border: '1px solid var(--accent-green)', color: 'var(--accent-green)', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
                       <CheckCircle size={16} /> Done
                     </button>
                   )}
                   <button onClick={() => handleDelete(i)} style={{ background: 'transparent', border: '1px solid var(--accent-red)', color: 'var(--accent-red)', padding: '8px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
                     <Trash2 size={16} />
                   </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--text-secondary)' }}>No schedule events found.</p>
        )}
      </div>
    </motion.div>
  );
}

function KnowledgeBaseView({ topics }) {
  const [uploading, setUploading] = useState(false);
  const [topic, setTopic] = useState('');
  const [files, setFiles] = useState([]);
  const fileInputRef = useRef(null);

  const fetchFiles = () => {
    fetch('/api/files')
      .then(res => res.json())
      .then(data => setFiles(data))
      .catch(console.error);
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if(!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    if(topic) formData.append('topic', topic);

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      if(res.ok) {
        alert("Upload successful! The agent is now analyzing this document.");
        fetchFiles();
      }
    } catch(err) {
      alert("Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <h1 className="glow-text" style={{ fontSize: '2rem', marginBottom: '8px' }}>Knowledge Base</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>Upload study materials, syllabi, or lecture notes.</p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <div className="glass-panel" style={{ padding: '40px', textAlign: 'center' }}>
          <UploadCloud size={48} color="var(--accent-cyan)" style={{ marginBottom: '20px' }} />
          <h3 style={{ marginBottom: '16px' }}>Ingest New Material</h3>
          
          <select 
            value={topic}
            onChange={e => setTopic(e.target.value)}
            style={{ 
              width: '100%', padding: '12px', marginBottom: '24px', 
              background: 'var(--bg-secondary)', border: '1px solid var(--glass-border)',
              color: 'var(--text-primary)', borderRadius: 'var(--radius-sm)'
            }}
          >
            <option value="">-- Optional: Assign to Topic --</option>
            {topics && topics.map((t, i) => <option key={i} value={t.name}>{t.name}</option>)}
          </select>

          <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleUpload} />
          
          <button 
            onClick={() => fileInputRef.current.click()}
            disabled={uploading}
            style={{
              padding: '12px 24px', borderRadius: 'var(--radius-sm)',
              background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))',
              color: 'white', border: 'none', cursor: 'pointer', fontWeight: 600, width: '100%'
            }}
          >
            {uploading ? 'Ingesting & Processing...' : 'Select File to Upload'}
          </button>
        </div>

        {/* Uploaded Files Viewer */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
           <h3 style={{ marginBottom: '20px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={20} color="var(--accent-purple)"/> Uploaded Files
           </h3>
           <div style={{ flex: 1, overflowY: 'auto' }}>
              {files.length > 0 ? (
                 <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {files.map((f, i) => (
                       <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: 'var(--glass-bg)', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
                          <div>
                            <span style={{ color: 'var(--accent-cyan)', display: 'block' }}>{f.name}</span>
                            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{(f.size / 1024).toFixed(1)} KB</span>
                          </div>
                          <button 
                            onClick={async () => {
                               if(window.confirm(`Delete ${f.name}?`)) {
                                  try {
                                     const res = await fetch(`/api/files/${f.name}`, { method: 'DELETE' });
                                     if(res.ok) {
                                        setFiles(files.filter(file => file.name !== f.name));
                                     } else {
                                        alert('Failed to delete file.');
                                     }
                                  } catch (e) {
                                     console.error(e);
                                  }
                               }
                            }}
                            title="Delete File"
                            style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--accent-red)' }}>
                            <Trash2 size={18} />
                          </button>
                       </div>
                    ))}
                 </div>
              ) : (
                 <p style={{ color: 'var(--text-secondary)' }}>No files uploaded yet in the ingestion directory.</p>
              )}
           </div>
        </div>
      </div>
    </motion.div>
  );
}

function PipelineStatusView() {
  const [pipelines, setPipelines] = useState([]);

  useEffect(() => {
    fetch('/api/pipelines')
      .then(res => res.json())
      .then(data => setPipelines(data))
      .catch(console.error);
  }, []);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <h1 className="glow-text" style={{ fontSize: '2rem', marginBottom: '8px' }}>Pipeline Status</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>Live CI/CD grading runs from GitLab.</p>

      <div className="glass-panel" style={{ padding: '32px' }}>
        {pipelines.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {pipelines.map((p, i) => (
              <div key={i} style={{ background: 'var(--glass-bg)', padding: '24px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--glass-border)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <span style={{ color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono' }}>{p.id}</span>
                    <strong style={{ color: 'var(--text-primary)', fontSize: '1.1rem' }}>{p.name}</strong>
                  </div>
                  <div style={{
                    padding: '4px 12px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase',
                    background: p.status === 'success' ? 'rgba(16, 185, 129, 0.1)' : p.status === 'failed' ? 'rgba(244, 63, 94, 0.1)' : 'rgba(251, 191, 36, 0.1)',
                    color: p.status === 'success' ? 'var(--accent-green)' : p.status === 'failed' ? 'var(--accent-red)' : 'var(--accent-yellow)',
                    border: `1px solid ${p.status === 'success' ? 'var(--accent-green)' : p.status === 'failed' ? 'var(--accent-red)' : 'var(--accent-yellow)'}`
                  }}>
                    {p.status}
                  </div>
                </div>
                <div style={{ height: '8px', background: 'rgba(0,0,0,0.2)', borderRadius: '4px', overflow: 'hidden' }}>
                  <motion.div 
                    initial={{ width: 0 }} animate={{ width: `${p.progress}%` }} transition={{ duration: 1 }}
                    style={{ height: '100%', background: p.status === 'success' ? 'var(--accent-green)' : p.status === 'failed' ? 'var(--accent-red)' : 'var(--accent-yellow)' }}
                  />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--text-secondary)' }}>No active pipelines.</p>
        )}
      </div>
    </motion.div>
  );
}

function AnalyticsView() {
  const [data, setData] = useState(null);

  useEffect(() => {
     fetch('/api/analytics')
       .then(res => res.json())
       .then(d => setData(d))
       .catch(err => console.error(err));
  }, []);

  if(!data) return <div style={{ color: 'var(--text-secondary)' }}>Loading analytics...</div>;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <h1 className="glow-text" style={{ fontSize: '2rem', marginBottom: '8px' }}>Deep Analytics</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>Performance trends and mental well-being metrics.</p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
         <div className="glass-panel" style={{ padding: '32px', textAlign: 'center' }}>
            <h3 style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>Student Mental Score</h3>
            <div style={{ fontSize: '4rem', fontWeight: 800, color: data.mental_score > 70 ? 'var(--accent-green)' : 'var(--accent-yellow)', fontFamily: 'Outfit' }}>
               {data.mental_score}
            </div>
            <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>Burnout Risk: <span style={{ color: data.burnout_risk === 'Low' ? 'var(--accent-green)' : 'var(--accent-red)' }}>{data.burnout_risk}</span></p>
         </div>

         <div className="glass-panel" style={{ padding: '32px', textAlign: 'center' }}>
            <h3 style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>Aggregate Study Score</h3>
            <div style={{ fontSize: '4rem', fontWeight: 800, color: 'var(--accent-cyan)', fontFamily: 'Outfit' }}>
               {data.study_score}
            </div>
            <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>Based on {data.focus_hours} focus hours this week.</p>
         </div>
      </div>

      <div className="glass-panel" style={{ padding: '32px' }}>
         <h3 style={{ color: 'var(--text-primary)', marginBottom: '20px' }}>Topic Mastery Distribution</h3>
         <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {data.topics_distribution.map((t, i) => (
               <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ width: '200px', color: 'var(--text-secondary)' }}>{t.name}</div>
                  <div style={{ flex: 1, height: '12px', background: 'var(--glass-bg)', borderRadius: '6px', overflow: 'hidden' }}>
                     <motion.div initial={{ width: 0 }} animate={{ width: `${t.value}%` }} transition={{ duration: 1, delay: i * 0.1 }} style={{ height: '100%', background: t.value > 80 ? 'var(--accent-green)' : t.value > 50 ? 'var(--accent-yellow)' : 'var(--accent-red)' }} />
                  </div>
                  <div style={{ width: '40px', textAlign: 'right', color: 'var(--text-primary)' }}>{t.value}%</div>
               </div>
            ))}
         </div>
      </div>
    </motion.div>
  );
}

function AddTopicModal({ onClose, onAdd }) {
  const [topic, setTopic] = useState('');
  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(10px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="glass-panel" style={{ width: '400px', padding: '32px', background: 'var(--bg-secondary)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
          <h3 style={{ margin: 0 }}>Add New Topic</h3>
          <X size={20} cursor="pointer" onClick={onClose} color="var(--text-secondary)" />
        </div>
        <input 
          autoFocus
          type="text" 
          value={topic} 
          onChange={e => setTopic(e.target.value)} 
          placeholder="e.g. Neural Networks"
          style={{ width: '100%', padding: '12px', marginBottom: '24px', background: 'var(--bg-primary)', border: '1px solid var(--glass-border)', color: 'var(--text-primary)', borderRadius: 'var(--radius-sm)' }}
        />
        <button 
          onClick={() => { onAdd(topic); onClose(); }}
          style={{ width: '100%', padding: '12px', borderRadius: 'var(--radius-sm)', background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))', color: 'white', border: 'none', cursor: 'pointer', fontWeight: 600 }}
        >
          Track Topic
        </button>
      </motion.div>
    </div>
  );
}
