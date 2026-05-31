import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, MessageSquare, Calendar, Activity, Zap, CheckCircle, Clock, AlertCircle, UploadCloud, Plus, X, BookOpen } from 'lucide-react';
import './index.css';

const TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'chat', label: 'Chat Console', icon: MessageSquare },
  { id: 'schedule', label: 'Daily Schedule', icon: Calendar },
  { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
  { id: 'pipeline', label: 'Pipeline Status', icon: Activity },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [metrics, setMetrics] = useState({ mastery_avg: '--', topics_tracked: 0, pending_labs: 0, study_streak: 0, feed: [], topics: [] });
  const [status, setStatus] = useState({ status: 'connecting', agent_available: false });
  const [showTopicModal, setShowTopicModal] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = () => {
    fetch('/api/status')
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(err => console.error("API error:", err));

    fetch('/api/metrics')
      .then(res => res.json())
      .then(data => setMetrics(data))
      .catch(err => console.error("Metrics error:", err));
  };

  const handleAddTopic = async (topicName) => {
    try {
      const res = await fetch('/api/topics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: topicName })
      });
      if(res.ok) {
        // Refresh metrics to show the new mock topic (if it were real data, it would return the updated list)
        fetchData();
      }
    } catch(e) {
      console.error(e);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      
      {/* Sidebar */}
      <motion.div 
        initial={{ x: -300 }}
        animate={{ x: 0 }}
        style={{ 
          width: '280px', 
          borderRight: '1px solid var(--glass-border)',
          background: 'linear-gradient(180deg, rgba(5, 5, 15, 0.96) 0%, rgba(8, 8, 26, 0.98) 100%)',
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
              <h1 className="glow-text" style={{ fontSize: '2.5rem', marginBottom: '8px' }}>Command Center</h1>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>Real-time overview of your academic operations.</p>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '40px' }}>
                <MetricCard title="Topics Tracked" value={metrics.topics_tracked} color="var(--accent-cyan)" />
                <MetricCard title="Avg Mastery" value={metrics.mastery_avg} color="var(--accent-purple)" />
                <MetricCard title="Pending Labs" value={metrics.pending_labs} color="var(--accent-green)" />
                <MetricCard title="Study Streak" value={`${metrics.study_streak} days 🔥`} color="var(--accent-orange)" />
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
                  <div style={{ flex: 1, overflowY: 'auto', paddingRight: '8px' }}>
                    {metrics.topics && metrics.topics.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {metrics.topics.map((topic, idx) => (
                          <div key={idx} style={{ background: 'var(--glass-bg)', padding: '12px 16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--glass-border)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                              <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{topic.name}</span>
                              <span style={{ color: 'var(--accent-purple)', fontWeight: 'bold' }}>{topic.mastery}%</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <div style={{ flex: 1, height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginRight: '16px' }}>
                                <div style={{ width: `${topic.mastery}%`, height: '100%', background: 'linear-gradient(90deg, var(--accent-cyan), var(--accent-purple))', borderRadius: '2px' }} />
                              </div>
                              <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>{topic.last_reviewed}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p style={{ color: 'var(--text-secondary)' }}>No topics tracked yet.</p>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'chat' && (
            <motion.div
              key="chat"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              style={{ height: 'calc(100vh - 80px)', display: 'flex', flexDirection: 'column' }}
            >
              <h1 className="glow-text" style={{ fontSize: '2.5rem', marginBottom: '24px' }}>Agent Interface</h1>
              <ChatInterface />
            </motion.div>
          )}

          {activeTab === 'schedule' && (
            <motion.div
              key="schedule"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <ScheduleView />
            </motion.div>
          )}

          {activeTab === 'knowledge' && (
            <motion.div
              key="knowledge"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <h1 className="glow-text" style={{ fontSize: '2.5rem', marginBottom: '8px' }}>Knowledge Base</h1>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>Upload documents for the agent to analyze and index.</p>
              <KnowledgeBaseView topics={metrics?.topics || []} />
            </motion.div>
          )}
          
          {activeTab === 'pipeline' && (
            <motion.div
              key="pipeline"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <h1 className="glow-text" style={{ fontSize: '2.5rem', marginBottom: '24px' }}>Pipeline Status</h1>
              <PipelineView />
            </motion.div>
          )}

        </AnimatePresence>
      </div>

      <TopicModal 
        isOpen={showTopicModal} 
        onClose={() => setShowTopicModal(false)} 
        onSubmit={handleAddTopic} 
      />
    </div>
  );
}

function MetricCard({ title, value, color }) {
  return (
    <motion.div 
      className="glass-panel"
      whileHover={{ y: -5, boxShadow: `0 15px 35px rgba(0,0,0,0.4), 0 0 20px ${color}20` }}
      style={{ padding: '24px', position: 'relative' }}
    >
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '3px', background: `linear-gradient(90deg, ${color}, transparent)` }} />
      <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '12px' }}>{title}</h3>
      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{value}</div>
    </motion.div>
  );
}

function TopicModal({ isOpen, onClose, onSubmit }) {
  const [topicName, setTopicName] = useState('');

  if(!isOpen) return null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(10px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100
    }}>
      <motion.div 
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="glass-panel"
        style={{ width: '400px', padding: '32px', position: 'relative' }}
      >
        <button onClick={onClose} style={{ position: 'absolute', top: '16px', right: '16px', background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
          <X size={20} />
        </button>
        <h2 style={{ color: 'var(--text-primary)', margin: '0 0 24px 0', fontSize: '1.5rem' }}>Add New Topic</h2>
        
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', color: 'var(--text-secondary)', marginBottom: '8px', fontSize: '0.9rem' }}>Topic Name</label>
          <input 
            value={topicName}
            onChange={e => setTopicName(e.target.value)}
            placeholder="e.g. Distributed Databases"
            style={{
              width: '100%', padding: '12px 16px', borderRadius: 'var(--radius-sm)',
              background: 'var(--bg-primary)', border: '1px solid var(--glass-border)',
              color: 'var(--text-primary)', outline: 'none'
            }}
          />
        </div>
        
        <motion.button 
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => {
            if(topicName.trim()) {
              onSubmit(topicName);
              setTopicName('');
              onClose();
            }
          }}
          style={{
            width: '100%', padding: '12px', borderRadius: 'var(--radius-sm)',
            background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))',
            color: '#fff', border: 'none', fontWeight: 'bold', cursor: 'pointer', fontSize: '1rem'
          }}
        >
          Track Subject
        </motion.button>
      </motion.div>
    </div>
  );
}

function KnowledgeBaseView({ topics }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState('');
  const fileInputRef = useRef(null);

  const handleFile = async (file) => {
    if(!file) return;
    setUploadStatus('uploading');
    
    const formData = new FormData();
    formData.append('file', file);
    if(selectedTopic) {
      formData.append('topic', selectedTopic);
    }
    
    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      if(res.ok) {
        setUploadStatus('success');
        setTimeout(() => setUploadStatus(null), 3000);
      } else {
        setUploadStatus('error');
      }
    } catch(e) {
      setUploadStatus('error');
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '40px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ width: '100%', maxWidth: '600px', marginBottom: '24px' }}>
        <label style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>Assign Upload to Topic</label>
        <select 
          value={selectedTopic} 
          onChange={e => setSelectedTopic(e.target.value)}
          style={{ width: '100%', padding: '12px', borderRadius: 'var(--radius-sm)', background: 'var(--bg-secondary)', border: '1px solid var(--glass-border)', color: 'var(--text-primary)' }}
        >
          <option value="">-- No specific topic --</option>
          {topics && topics.map((t, i) => (
            <option key={i} value={t.name}>{t.name}</option>
          ))}
        </select>
      </div>
      <input 
        type="file" 
        ref={fileInputRef} 
        style={{ display: 'none' }} 
        onChange={(e) => handleFile(e.target.files[0])}
      />
      
      <motion.div 
        whileHover={{ scale: 1.02 }}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFile(e.dataTransfer.files[0]);
        }}
        onClick={() => fileInputRef.current?.click()}
        style={{
          width: '100%', maxWidth: '600px', height: '250px',
          border: `2px dashed ${isDragging ? 'var(--accent-cyan)' : 'var(--glass-border)'}`,
          borderRadius: 'var(--radius-md)',
          background: isDragging ? 'rgba(0, 240, 255, 0.05)' : 'var(--glass-bg)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer', transition: 'all 0.2s', gap: '16px'
        }}
      >
        {uploadStatus === 'uploading' ? (
          <Activity size={48} color="var(--accent-blue)" style={{ animation: 'spin 2s linear infinite' }} />
        ) : uploadStatus === 'success' ? (
          <CheckCircle size={48} color="var(--accent-green)" />
        ) : (
          <UploadCloud size={48} color={isDragging ? 'var(--accent-cyan)' : 'var(--text-secondary)'} />
        )}
        
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ color: 'var(--text-primary)', margin: '0 0 8px 0' }}>
            {uploadStatus === 'uploading' ? 'Uploading document...' : uploadStatus === 'success' ? 'Upload Complete!' : 'Drag & Drop Document Here'}
          </h3>
          <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
            {uploadStatus ? 'The agent is processing the file.' : 'or click to browse your files (PDF, TXT, MD)'}
          </p>
        </div>
      </motion.div>
    </div>
  );
}

function ScheduleView() {
  const [schedule, setSchedule] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [newEvent, setNewEvent] = useState({ time: '', activity: '' });

  const fetchSchedule = () => fetch('/api/schedule').then(r => r.json()).then(setSchedule);

  useEffect(() => {
    fetchSchedule();
  }, []);

  const handleAdd = async () => {
    if(!newEvent.time || !newEvent.activity) return;
    try {
      const res = await fetch('/api/schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newEvent)
      });
      if(res.ok) {
        fetchSchedule(); // refresh
        setShowModal(false);
        setNewEvent({ time: '', activity: '' });
      }
    } catch(e) {
      console.error(e);
    }
  }

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 className="glow-text" style={{ fontSize: '2.5rem', margin: 0 }}>Daily Schedule</h1>
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowModal(true)}
          style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            padding: '10px 20px', borderRadius: 'var(--radius-sm)',
            background: 'linear-gradient(135deg, var(--accent-purple), var(--accent-blue))', 
            border: 'none', color: '#fff', cursor: 'pointer', fontSize: '1rem', fontWeight: 'bold'
          }}
        >
          <Plus size={18} /> Add Event
        </motion.button>
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {schedule.map((item, idx) => (
            <motion.div 
              key={idx}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              style={{ 
                display: 'flex', alignItems: 'center', gap: '20px', 
                padding: '20px', 
                background: 'var(--glass-bg)', 
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--glass-border)',
                borderLeft: `4px solid ${item.status === 'completed' ? 'var(--accent-green)' : item.status === 'in_progress' ? 'var(--accent-blue)' : 'var(--text-secondary)'}`
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '120px', color: 'var(--text-secondary)', fontWeight: 600 }}>
                <Clock size={18} />
                {item.time}
              </div>
              <div style={{ flex: 1, fontSize: '1.1rem', color: 'var(--text-primary)' }}>
                {item.activity}
              </div>
              <div>
                {item.status === 'completed' && <CheckCircle color="var(--accent-green)" />}
                {item.status === 'in_progress' && <Activity color="var(--accent-blue)" />}
                {item.status === 'pending' && <Calendar color="var(--text-secondary)" />}
              </div>
            </motion.div>
          ))}
          {schedule.length === 0 && <p style={{ color: 'var(--text-secondary)' }}>Loading schedule...</p>}
        </div>
      </div>

      {showModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(10px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100
        }}>
          <motion.div 
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            className="glass-panel"
            style={{ width: '400px', padding: '32px', position: 'relative' }}
          >
            <button onClick={() => setShowModal(false)} style={{ position: 'absolute', top: '16px', right: '16px', background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
              <X size={20} />
            </button>
            <h2 style={{ color: 'var(--text-primary)', margin: '0 0 24px 0', fontSize: '1.5rem' }}>Add Schedule Event</h2>
            
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', color: 'var(--text-secondary)', marginBottom: '8px', fontSize: '0.9rem' }}>Time (e.g. 03:00 PM)</label>
              <input 
                value={newEvent.time}
                onChange={e => setNewEvent({...newEvent, time: e.target.value})}
                style={{
                  width: '100%', padding: '12px 16px', borderRadius: 'var(--radius-sm)',
                  background: 'var(--bg-primary)', border: '1px solid var(--glass-border)',
                  color: 'var(--text-primary)', outline: 'none'
                }}
              />
            </div>
            
            <div style={{ marginBottom: '24px' }}>
              <label style={{ display: 'block', color: 'var(--text-secondary)', marginBottom: '8px', fontSize: '0.9rem' }}>Activity</label>
              <input 
                value={newEvent.activity}
                onChange={e => setNewEvent({...newEvent, activity: e.target.value})}
                style={{
                  width: '100%', padding: '12px 16px', borderRadius: 'var(--radius-sm)',
                  background: 'var(--bg-primary)', border: '1px solid var(--glass-border)',
                  color: 'var(--text-primary)', outline: 'none'
                }}
              />
            </div>

            <motion.button 
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleAdd}
              style={{
                width: '100%', padding: '12px', borderRadius: 'var(--radius-sm)',
                background: 'linear-gradient(135deg, var(--accent-purple), var(--accent-blue))',
                color: '#fff', border: 'none', fontWeight: 'bold', cursor: 'pointer', fontSize: '1rem'
              }}
            >
              Save Event
            </motion.button>
          </motion.div>
        </div>
      )}
    </>
  );
}

function ChatInterface() {
  const [messages, setMessages] = useState([{ role: 'assistant', content: 'Academic Commander initialized. How can I assist you today?' }]);
  const [input, setInput] = useState('');

  const send = async () => {
    if(!input.trim()) return;
    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
    } catch(e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection error to backend.' }]);
    }
  };

  return (
    <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '20px' }}>
      <div style={{ flex: 1, overflowY: 'auto', marginBottom: '20px', paddingRight: '10px' }}>
        {messages.map((m, i) => (
          <motion.div 
            initial={{ opacity: 0, x: m.role === 'user' ? 20 : -20 }}
            animate={{ opacity: 1, x: 0 }}
            key={i} 
            style={{ 
              marginBottom: '16px', 
              display: 'flex', 
              justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' 
            }}
          >
            <div style={{
              maxWidth: '75%',
              padding: '12px 16px',
              borderRadius: 'var(--radius-sm)',
              background: m.role === 'user' ? 'rgba(0, 240, 255, 0.1)' : 'var(--glass-bg)',
              border: `1px solid ${m.role === 'user' ? 'rgba(0, 240, 255, 0.2)' : 'var(--glass-border)'}`,
              color: 'var(--text-primary)'
            }}>
              {m.content}
            </div>
          </motion.div>
        ))}
      </div>
      <div style={{ display: 'flex', gap: '12px' }}>
        <input 
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Enter command..."
          style={{
            flex: 1,
            padding: '14px 20px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--glass-border)',
            background: 'var(--bg-primary)',
            color: 'var(--text-primary)',
            outline: 'none',
            fontSize: '1rem'
          }}
        />
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={send}
          style={{
            padding: '0 24px',
            borderRadius: 'var(--radius-sm)',
            background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))',
            color: '#fff',
            border: 'none',
            fontWeight: 'bold',
            cursor: 'pointer'
          }}
        >
          SEND
        </motion.button>
      </div>
    </div>
  );
}

function PipelineView() {
  const [pipelines, setPipelines] = useState([]);

  useEffect(() => {
    fetch('/api/pipelines').then(r => r.json()).then(setPipelines);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {pipelines.map((pipe, idx) => (
        <motion.div 
          key={idx}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.1 }}
          className="glass-panel" 
          style={{ padding: '24px' }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ color: 'var(--text-secondary)', fontFamily: 'monospace' }}>{pipe.id}</span>
              <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--text-primary)' }}>{pipe.name}</h3>
            </div>
            <div style={{ 
              padding: '6px 12px', 
              borderRadius: '20px', 
              fontSize: '0.85rem',
              fontWeight: 600,
              background: pipe.status === 'success' ? 'rgba(16, 185, 129, 0.1)' : pipe.status === 'failed' ? 'rgba(244, 63, 94, 0.1)' : 'rgba(59, 130, 246, 0.1)',
              color: pipe.status === 'success' ? 'var(--accent-green)' : pipe.status === 'failed' ? 'var(--accent-red)' : 'var(--accent-blue)'
            }}>
              {pipe.status.toUpperCase()}
            </div>
          </div>
          
          <div style={{ height: '8px', background: 'var(--glass-bg)', borderRadius: '4px', overflow: 'hidden' }}>
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${pipe.progress}%` }}
              transition={{ duration: 1, delay: 0.2 }}
              style={{ 
                height: '100%', 
                background: pipe.status === 'success' ? 'var(--accent-green)' : pipe.status === 'failed' ? 'var(--accent-red)' : 'var(--accent-blue)'
              }}
            />
          </div>
        </motion.div>
      ))}
      {pipelines.length === 0 && <p style={{ color: 'var(--text-secondary)' }}>Loading pipelines...</p>}
    </div>
  );
}
