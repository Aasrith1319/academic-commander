"""
⚡ Academic Commander — Premium Streamlit Dashboard
Google Cloud Rapid Agent Hackathon 2026
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import random
import os

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Academic Commander",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS — Premium Dark Theme with Glassmorphism
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ══════════ Google Fonts ══════════ */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ══════════ Root Variables ══════════ */
:root {
    --bg-primary: #04040d;
    --bg-secondary: #08081a;
    --bg-tertiary: #0e0e27;
    --glass-bg: rgba(255, 255, 255, 0.03);
    --glass-border: rgba(255, 255, 255, 0.07);
    --glass-hover: rgba(255, 255, 255, 0.06);
    --accent-cyan: #00f0ff;
    --accent-blue: #3b82f6;
    --accent-purple: #d946ef;
    --accent-green: #10b981;
    --accent-yellow: #fbbf24;
    --accent-red: #f43f5e;
    --accent-orange: #f97316;
    --text-primary: #f3f4f6;
    --text-secondary: #9ca3af;
    --text-muted: #6b7280;
    --glow-cyan: 0 0 25px rgba(0, 240, 255, 0.2);
    --glow-blue: 0 0 25px rgba(59, 130, 246, 0.2);
    --glow-purple: 0 0 25px rgba(217, 70, 239, 0.2);
    --radius: 20px;
    --radius-sm: 12px;
    --transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

/* ══════════ Global Background ══════════ */
.stApp, [data-testid="stAppViewContainer"] {
    background: linear-gradient(145deg, var(--bg-primary) 0%, var(--bg-secondary) 40%, var(--bg-tertiary) 100%) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-primary) !important;
}

/* Background animated grain and ambient light rings */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: radial-gradient(circle at 10% 20%, rgba(0, 240, 255, 0.06) 0%, transparent 45%),
                      radial-gradient(circle at 90% 10%, rgba(217, 70, 239, 0.05) 0%, transparent 40%),
                      radial-gradient(circle at 50% 85%, rgba(59, 130, 246, 0.04) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

/* ══════════ Smooth Animations ══════════ */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(18px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse-glow {
    0%, 100% { opacity: 0.9; box-shadow: 0 0 8px rgba(16, 185, 129, 0.5); }
    50% { opacity: 0.4; box-shadow: 0 0 20px rgba(16, 185, 129, 0.9); }
}

@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ══════════ Scrollbar ══════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--accent-cyan), var(--accent-purple));
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover { background: var(--accent-blue); }

/* ══════════ Sidebar ══════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(5, 5, 15, 0.96) 0%, rgba(8, 8, 26, 0.98) 100%) !important;
    border-right: 1px solid var(--glass-border) !important;
    backdrop-filter: blur(25px);
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li,
[data-testid="stSidebar"] .stMarkdown span {
    color: var(--text-secondary) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ══════════ Headers ══════════ */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.5px;
}

/* ══════════ Glowing Title ══════════ */
.glow-title {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 900;
    font-size: 3.6rem;
    background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 30%, var(--accent-purple) 60%, var(--accent-cyan) 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-shift 6s ease infinite;
    text-align: center;
    margin-bottom: 0;
    letter-spacing: -2px;
    line-height: 1.1;
    filter: drop-shadow(0 2px 15px rgba(0, 240, 255, 0.15));
}

.glow-title-sub {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 400;
    font-size: 1.1rem;
    color: var(--text-secondary);
    text-align: center;
    margin-top: 8px;
    letter-spacing: 0.5px;
}

/* ══════════ Glass Card ══════════ */
.glass-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.005) 100%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius);
    padding: 26px;
    backdrop-filter: blur(24px) saturate(120%);
    -webkit-backdrop-filter: blur(24px) saturate(120%);
    transition: var(--transition);
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.12), transparent);
}

.glass-card:hover {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.01) 100%);
    border-color: rgba(0, 240, 255, 0.25);
    box-shadow: 0 12px 40px 0 rgba(0, 240, 255, 0.1),
                0 0 30px 0 rgba(217, 70, 239, 0.04);
    transform: translateY(-4px);
}

/* ══════════ Metric Card ══════════ */
.metric-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.005) 100%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius);
    padding: 22px 26px;
    backdrop-filter: blur(24px) saturate(120%);
    -webkit-backdrop-filter: blur(24px) saturate(120%);
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35);
    transition: var(--transition);
    animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: var(--radius) var(--radius) 0 0;
}

.metric-card.cyan::before { background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue)); }
.metric-card.purple::before { background: linear-gradient(90deg, var(--accent-purple), var(--accent-blue)); }
.metric-card.green::before { background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan)); }
.metric-card.orange::before { background: linear-gradient(90deg, var(--accent-orange), var(--accent-yellow)); }

.metric-card:hover {
    transform: translateY(-5px);
    border-color: rgba(255, 255, 255, 0.18);
    box-shadow: 0 15px 35px 0 rgba(0, 0, 0, 0.45),
                0 0 25px 0 rgba(0, 240, 255, 0.12);
}

.metric-value {
    font-family: 'Outfit', sans-serif;
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 6px 0;
    line-height: 1;
}

.metric-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.8px;
}

/* ══════════ Status Badge ══════════ */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 999px;
    padding: 6px 18px;
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--accent-green);
    letter-spacing: 0.8px;
}

.status-dot {
    width: 8px; height: 8px;
    background: var(--accent-green);
    border-radius: 50%;
    animation: pulse-glow 2s ease-in-out infinite;
}

/* ══════════ Progress Bar ══════════ */
.progress-container {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 999px;
    overflow: hidden;
    height: 12px;
    margin: 8px 0 16px 0;
    position: relative;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
}

.progress-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
}

.progress-fill::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
    animation: shimmer 1.5s infinite;
}

.progress-red .progress-fill {
    background: linear-gradient(90deg, var(--accent-red), var(--accent-orange));
    box-shadow: 0 0 12px rgba(244, 63, 94, 0.35);
}
.progress-yellow .progress-fill {
    background: linear-gradient(90deg, var(--accent-yellow), var(--accent-orange));
    box-shadow: 0 0 12px rgba(251, 191, 36, 0.35);
}
.progress-green .progress-fill {
    background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan));
    box-shadow: 0 0 12px rgba(16, 185, 129, 0.35);
}

/* ══════════ Terminal Window for Thinking Log ══════════ */
.terminal-window {
    background: rgba(4, 4, 12, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: var(--radius-sm);
    padding: 20px;
    backdrop-filter: blur(15px);
    box-shadow: inset 0 4px 30px rgba(0, 0, 0, 0.6), 0 10px 40px rgba(0, 0, 0, 0.5);
    margin-bottom: 24px;
    animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.terminal-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 18px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding-bottom: 12px;
}

.terminal-dot {
    width: 11px; height: 11px;
    border-radius: 50%;
}
.dot-red { background: var(--accent-red); }
.dot-yellow { background: var(--accent-yellow); }
.dot-green { background: var(--accent-green); }

.terminal-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--text-secondary);
    letter-spacing: 0.8px;
    margin-left: 6px;
    text-transform: uppercase;
}

.trace-entry {
    background: rgba(255, 255, 255, 0.015);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: var(--radius-sm);
    padding: 16px 20px;
    margin-bottom: 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    line-height: 1.7;
    transition: var(--transition);
}

.trace-entry:last-child {
    margin-bottom: 0;
}

.trace-entry:hover {
    background: rgba(255, 255, 255, 0.035);
    border-color: rgba(255, 255, 255, 0.08);
}

.trace-thought { border-left: 3px solid var(--accent-purple); }
.trace-action  { border-left: 3px solid var(--accent-cyan); }
.trace-observe { border-left: 3px solid var(--accent-green); }

.trace-tag {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 8px;
}

.tag-thought { background: rgba(217, 70, 239, 0.12); color: var(--accent-purple); border: 1px solid rgba(217, 70, 239, 0.2); }
.tag-action  { background: rgba(0, 240, 255, 0.12); color: var(--accent-cyan); border: 1px solid rgba(0, 240, 255, 0.2); }
.tag-observe { background: rgba(16, 185, 129, 0.12); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.2); }

/* ══════════ Timeline/Schedule ══════════ */
.timeline-container {
    position: relative;
    padding-left: 34px;
    margin-left: 12px;
    margin-top: 10px;
    animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.timeline-container::before {
    content: '';
    position: absolute;
    top: 5px; bottom: 5px; left: -1px;
    width: 2px;
    background: linear-gradient(180deg, var(--accent-cyan), var(--accent-purple), var(--accent-cyan));
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
}

.schedule-block {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.005) 100%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-sm);
    padding: 18px 22px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 18px;
    position: relative;
    transition: var(--transition);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.schedule-block:hover {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.01) 100%);
    transform: translateX(6px);
    border-color: rgba(255, 255, 255, 0.15);
}

/* Timeline dot indicator */
.schedule-block::after {
    content: '';
    position: absolute;
    left: -43px;
    top: 50%;
    transform: translateY(-50%);
    width: 16px; height: 16px;
    border-radius: 50%;
    background: var(--bg-secondary);
    border: 3px solid var(--accent-cyan);
    box-shadow: 0 0 10px var(--accent-cyan);
    transition: var(--transition);
    z-index: 10;
}

.schedule-block:hover::after {
    background: var(--accent-cyan);
    transform: translateY(-50%) scale(1.3);
    box-shadow: 0 0 15px var(--accent-cyan);
}

.schedule-block.type-review::after { border-color: var(--accent-purple); box-shadow: 0 0 10px var(--accent-purple); }
.schedule-block.type-review:hover::after { background: var(--accent-purple); }

.schedule-block.type-lecture::after { border-color: var(--accent-blue); box-shadow: 0 0 10px var(--accent-blue); }
.schedule-block.type-lecture:hover::after { background: var(--accent-blue); }

.schedule-block.type-exam::after { border-color: var(--accent-red); box-shadow: 0 0 10px var(--accent-red); }
.schedule-block.type-exam:hover::after { background: var(--accent-red); }

.schedule-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--accent-cyan);
    min-width: 110px;
}

.schedule-topic {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 1rem;
}

.schedule-type {
    font-size: 0.75rem;
    padding: 3px 12px;
    border-radius: 6px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    border: 1px solid transparent;
}

.type-lecture { background: rgba(59, 130, 246, 0.1); color: var(--accent-blue); border-color: rgba(59, 130, 246, 0.2); }
.type-review { background: rgba(217, 70, 239, 0.1); color: var(--accent-purple); border-color: rgba(217, 70, 239, 0.2); }
.type-practice { background: rgba(0, 240, 255, 0.1); color: var(--accent-cyan); border-color: rgba(0, 240, 255, 0.2); }
.type-exam { background: rgba(244, 63, 94, 0.1); color: var(--accent-red); border-color: rgba(244, 63, 94, 0.2); }

/* ══════════ Pipeline Card ══════════ */
.pipeline-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.005) 100%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-sm);
    padding: 18px 22px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: var(--transition);
}

.pipeline-card:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(59, 130, 246, 0.25);
    transform: translateX(4px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.pipeline-pass {
    color: var(--accent-green);
    font-weight: 700;
    text-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
}

.pipeline-fail {
    color: var(--accent-red);
    font-weight: 700;
    text-shadow: 0 0 10px rgba(244, 63, 94, 0.3);
}

/* ══════════ Tabs Styling ══════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 16px;
    padding: 6px;
    border: 1px solid var(--glass-border);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 12px 22px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text-secondary) !important;
    background: transparent;
    border: none;
    transition: var(--transition);
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    background: rgba(255, 255, 255, 0.04);
}

.stTabs [aria-selected="true"] {
    background: rgba(0, 240, 255, 0.08) !important;
    color: var(--accent-cyan) !important;
    border: 1px solid rgba(0, 240, 255, 0.18) !important;
    box-shadow: 0 4px 15px rgba(0, 240, 255, 0.05);
}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none;
}

/* ══════════ File Uploader ══════════ */
[data-testid="stFileUploader"] {
    border: 1px dashed rgba(0, 240, 255, 0.25) !important;
    border-radius: var(--radius-sm) !important;
    background: rgba(0, 240, 255, 0.02) !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--accent-cyan) !important;
    background: rgba(0, 240, 255, 0.04) !important;
}

/* ══════════ Divider ══════════ */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--glass-border), transparent);
    margin: 28px 0;
}

/* ══════════ Footer ══════════ */
.footer {
    text-align: center;
    padding: 40px 0 20px 0;
    font-size: 0.8rem;
    color: var(--text-muted);
    font-family: 'Plus Jakarta Sans', sans-serif;
    letter-spacing: 0.5px;
}

.footer strong {
    color: var(--text-secondary);
}

/* ══════════ Sidebar Profile ══════════ */
.sidebar-profile {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.005) 100%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-sm);
    padding: 20px;
    margin-bottom: 16px;
    backdrop-filter: blur(10px);
}

.sidebar-profile h4 {
    margin: 0 0 12px 0;
    font-size: 1rem;
    color: var(--text-primary);
}

.sidebar-stat {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    font-size: 0.88rem;
}

.sidebar-stat:last-child { border-bottom: none; }

.sidebar-stat-label { color: var(--text-muted); }
.sidebar-stat-value { color: var(--accent-cyan); font-weight: 600; }

/* ══════════ Quality Gauge ══════════ */
.gauge-ring {
    width: 130px; height: 130px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 16px;
    position: relative;
    box-shadow: 0 8px 25px rgba(0,0,0,0.5);
    transition: var(--transition);
}

.gauge-ring::before {
    content: '';
    position: absolute;
    inset: 6px;
    border-radius: 50%;
    background: var(--bg-secondary);
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.7);
}

.gauge-value {
    position: relative;
    font-family: 'Outfit', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    z-index: 1;
}

/* ══════════ Responsive ══════════ */
@media (max-width: 768px) {
    .glow-title { font-size: 2.2rem; }
    .metric-value { font-size: 1.8rem; }
}
</style>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────────────────────
# MONGODB CONNECTION (graceful fallback to mock data)
# ─────────────────────────────────────────────────────────────────────────────
MOCK_MODE = True
db = None

try:
    from pymongo import MongoClient
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
    client.admin.command("ping")
    db = client["academic_commander"]
    MOCK_MODE = False
except Exception:
    MOCK_MODE = True


def get_mastery_data():
    """Return topic mastery data from MongoDB or mock fallback."""
    if not MOCK_MODE and db is not None:
        try:
            records = list(db["weak_topic_index"].find({}, {"_id": 0}))
            if records:
                return [
                    {
                        "topic": r.get("topic_id", "Unknown Topic"),
                        "mastery": r.get("mastery_score", 50),
                        "last_reviewed": r.get("updated_at", "Never")[:10] if r.get("updated_at") else "Never"
                    }
                    for r in records
                ]
        except Exception:
            pass
    return [
        {"topic": "Linear Algebra", "mastery": 82, "last_reviewed": "2026-05-28"},
        {"topic": "Probability & Statistics", "mastery": 65, "last_reviewed": "2026-05-27"},
        {"topic": "Data Structures", "mastery": 91, "last_reviewed": "2026-05-28"},
        {"topic": "Machine Learning Fundamentals", "mastery": 47, "last_reviewed": "2026-05-26"},
        {"topic": "Database Systems", "mastery": 73, "last_reviewed": "2026-05-27"},
        {"topic": "Computer Networks", "mastery": 34, "last_reviewed": "2026-05-25"},
        {"topic": "Operating Systems", "mastery": 58, "last_reviewed": "2026-05-26"},
        {"topic": "Discrete Mathematics", "mastery": 88, "last_reviewed": "2026-05-28"},
        {"topic": "Software Engineering", "mastery": 71, "last_reviewed": "2026-05-27"},
        {"topic": "Artificial Intelligence", "mastery": 52, "last_reviewed": "2026-05-25"},
    ]


def get_schedule_data():
    """Return daily schedule from MongoDB or mock fallback."""
    if not MOCK_MODE and db is not None:
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            cursor = (
                db["daily_routine_blocks"]
                .find(
                    {
                        "start_time": {
                            "$gte": today_str + "T00:00:00",
                            "$lte": today_str + "T23:59:59",
                        }
                    },
                    {"_id": 0},
                )
                .sort("start_time", 1)
            )
            records = list(cursor)
            if records:
                formatted = []
                for r in records:
                    start_dt = datetime.fromisoformat(r["start_time"])
                    end_dt = start_dt + timedelta(minutes=r.get("duration_minutes", 60))
                    time_range = f"{start_dt.strftime('%H:%M')} – {end_dt.strftime('%H:%M')}"
                    
                    name = r.get("activity_name", "Study Block")
                    act_type = "practice"
                    emoji = "📖"
                    if "review" in name.lower() or "revise" in name.lower():
                        act_type = "review"
                        emoji = "📐"
                    elif "lecture" in name.lower() or "class" in name.lower():
                        act_type = "lecture"
                        emoji = "🤖"
                    elif "exam" in name.lower() or "midterm" in name.lower() or "prep" in name.lower():
                        act_type = "exam"
                        emoji = "📝"
                    elif "lab" in name.lower():
                        act_type = "practice"
                        emoji = "🗄️"
                        
                    formatted.append({
                        "time": time_range,
                        "topic": name,
                        "type": act_type,
                        "emoji": emoji
                    })
                return formatted
        except Exception:
            pass
    return [
        {"time": "08:00 – 09:30", "topic": "Linear Algebra Review", "type": "review", "emoji": "📐"},
        {"time": "09:45 – 11:15", "topic": "ML Fundamentals Lecture", "type": "lecture", "emoji": "🤖"},
        {"time": "11:30 – 12:30", "topic": "Data Structures Practice", "type": "practice", "emoji": "🌳"},
        {"time": "14:00 – 15:30", "topic": "Database Systems Lab", "type": "practice", "emoji": "🗄️"},
        {"time": "15:45 – 16:45", "topic": "Probability Problem Sets", "type": "practice", "emoji": "🎲"},
        {"time": "17:00 – 18:00", "topic": "Computer Networks Review", "type": "review", "emoji": "🌐"},
        {"time": "19:00 – 20:30", "topic": "AI Mid-Semester Prep", "type": "exam", "emoji": "📝"},
    ]


def get_pipeline_data():
    """Return CI/CD pipeline data from mock."""
    return [
        {"pipeline": "#1847", "stage": "test", "job": "unit-tests", "status": "passed", "duration": "42s", "timestamp": "2026-05-28 22:14"},
        {"pipeline": "#1847", "stage": "test", "job": "integration-tests", "status": "passed", "duration": "1m 18s", "timestamp": "2026-05-28 22:15"},
        {"pipeline": "#1847", "stage": "grade", "job": "auto-grade", "status": "passed", "duration": "23s", "timestamp": "2026-05-28 22:16"},
        {"pipeline": "#1846", "stage": "test", "job": "unit-tests", "status": "passed", "duration": "39s", "timestamp": "2026-05-28 18:05"},
        {"pipeline": "#1846", "stage": "test", "job": "integration-tests", "status": "passed", "duration": "1m 02s", "timestamp": "2026-05-28 18:06"},
        {"pipeline": "#1845", "stage": "test", "job": "unit-tests", "status": "passed", "duration": "41s", "timestamp": "2026-05-27 14:32"},
        {"pipeline": "#1845", "stage": "grade", "job": "auto-grade", "status": "passed", "duration": "21s", "timestamp": "2026-05-27 14:33"},
    ]


def get_quality_metrics():
    """Return Arize AI quality metrics (mock)."""
    return {
        "hallucination_score": 0.04,
        "avg_latency_ms": 287,
        "total_tokens": 184_520,
        "trace_count": 1_247,
        "accuracy": 0.96,
        "relevance": 0.93,
        "safety_score": 0.99,
        "cost_usd": 3.42,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 16px 0 8px 0;">
        <span style="font-size: 2.2rem;">⚡</span>
        <div style="font-family:'Inter',sans-serif; font-weight:800; font-size:1.25rem;
                    background: linear-gradient(135deg, #00d4ff, #a855f7);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                    background-clip: text; margin-top:4px;">
            Academic Commander
        </div>
        <div style="font-size:0.72rem; color:#5f6368; margin-top:2px; letter-spacing:1px; text-transform:uppercase;">
            Intelligent Study Agent
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Student Profile
    st.markdown("""
    <div class="sidebar-profile">
        <h4 style="color:#e8eaed;">👤 Student Profile</h4>
        <div class="sidebar-stat">
            <span class="sidebar-stat-label">Name</span>
            <span class="sidebar-stat-value">Aasrith K.</span>
        </div>
        <div class="sidebar-stat">
            <span class="sidebar-stat-label">Student ID</span>
            <span class="sidebar-stat-value">AC-2026-0429</span>
        </div>
        <div class="sidebar-stat">
            <span class="sidebar-stat-label">Semester</span>
            <span class="sidebar-stat-value">Spring 2026</span>
        </div>
        <div class="sidebar-stat">
            <span class="sidebar-stat-label">Program</span>
            <span class="sidebar-stat-value">B.Tech CS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # PDF Upload
    st.markdown("##### 📄 Upload Study Material")
    uploaded_file = st.file_uploader(
        "Drop a PDF to ingest",
        type=["pdf"],
        help="Upload lecture notes, textbooks, or assignments for AI-powered analysis.",
    )
    if uploaded_file is not None:
        st.success(f"✅ Uploaded: {uploaded_file.name}")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Agent Status
    st.markdown("""
    <div style="display:flex; align-items:center; justify-content:center; margin: 8px 0 4px 0;">
        <div class="status-badge">
            <div class="status-dot"></div>
            ADK AGENT OPERATIONAL
        </div>
    </div>
    <div style="text-align:center; font-size:0.7rem; color:#888; margin-bottom:12px;">
        google.adk.Agent + McpToolset × Gemini 3
    </div>
    """, unsafe_allow_html=True)

    # Quick Stats
    mastery_data = get_mastery_data()
    avg_mastery = sum(d["mastery"] for d in mastery_data) / len(mastery_data)

    st.markdown(f"""
    <div class="sidebar-profile">
        <h4 style="color:#e8eaed;">📊 Quick Stats</h4>
        <div class="sidebar-stat">
            <span class="sidebar-stat-label">Topics Tracked</span>
            <span class="sidebar-stat-value">{len(mastery_data)}</span>
        </div>
        <div class="sidebar-stat">
            <span class="sidebar-stat-label">Avg Mastery</span>
            <span class="sidebar-stat-value">{avg_mastery:.0f}%</span>
        </div>
        <div class="sidebar-stat">
            <span class="sidebar-stat-label">Upcoming Deadlines</span>
            <span class="sidebar-stat-value">3</span>
        </div>
        <div class="sidebar-stat">
            <span class="sidebar-stat-label">Study Streak</span>
            <span class="sidebar-stat-value">12 days 🔥</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mode indicator
    mode_text = "🟡 DEMO MODE" if MOCK_MODE else "🟢 LIVE DATA"
    st.caption(f"<div style='text-align:center; font-size:0.72rem; color:#5f6368;'>{mode_text}</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 20px 0 10px 0;">
    <div class="glow-title">⚡ Academic Commander</div>
    <div class="glow-title-sub">
        AI-Powered Autonomous Study Agent &nbsp;·&nbsp; Gemini 3 &nbsp;·&nbsp; Google Cloud Agent Builder
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TOP METRICS ROW
# ─────────────────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown("""
    <div class="metric-card cyan">
        <div class="metric-label">Topics Tracked</div>
        <div class="metric-value">10</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card purple">
        <div class="metric-label">Avg Mastery</div>
        <div class="metric-value">{avg_mastery:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="metric-card green">
        <div class="metric-label">Agent Traces</div>
        <div class="metric-value">1,247</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown("""
    <div class="metric-card orange">
        <div class="metric-label">CI/CD Pipelines</div>
        <div class="metric-value">47</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Mastery Matrix",
    "🧠 Agentic Thinking Log",
    "📅 Daily Schedule",
    "🚀 Pipeline Status",
    "🛡️ Agent Quality",
])


# ═══════════════════════ TAB 1: Mastery Matrix ═══════════════════════════════
with tab1:
    st.markdown("""
    <div class="glass-card">
        <h3 style="margin-top:0; font-size:1.15rem;">📈 Topic Mastery Overview</h3>
        <p style="color:var(--text-secondary); font-size:0.88rem; margin-bottom:20px;">
            Real-time mastery scores pulled from MongoDB. Color-coded by proficiency level.
        </p>
    """, unsafe_allow_html=True)

    for item in mastery_data:
        mastery = item["mastery"]
        topic = item["topic"]
        last_rev = item.get("last_reviewed", "N/A")

        if mastery < 40:
            color_class = "progress-red"
            badge_color = "#ef4444"
            badge_label = "NEEDS WORK"
        elif mastery < 70:
            color_class = "progress-yellow"
            badge_color = "#facc15"
            badge_label = "IN PROGRESS"
        else:
            color_class = "progress-green"
            badge_color = "#22c55e"
            badge_label = "PROFICIENT"

        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="font-weight:600; font-size:0.95rem;">{topic}</span>
                <span style="font-size:0.7rem; color:{badge_color}; background:rgba({','.join(str(int(badge_color.lstrip('#')[i:i+2], 16)) for i in (0, 2, 4))},0.12);
                      padding:2px 8px; border-radius:4px; margin-left:8px; font-weight:600;">{badge_label}</span>
            </div>
            <div style="display:flex; align-items:center; gap:12px;">
                <span style="font-size:0.75rem; color:var(--text-muted);">Last: {last_rev}</span>
                <span style="font-weight:700; font-size:1rem; color:{badge_color};">{mastery}%</span>
            </div>
        </div>
        <div class="progress-container {color_class}">
            <div class="progress-fill" style="width:{mastery}%;"></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════ TAB 2: Agentic Thinking Log ═════════════════════════
with tab2:
    st.markdown("""
    <div class="glass-card">
        <h3 style="margin-top:0; font-size:1.15rem;">🧠 Thought → Action → Observation Trace</h3>
        <p style="color:var(--text-secondary); font-size:0.88rem; margin-bottom:20px;">
            Live trace of the autonomous agent's reasoning loop powered by Gemini 3.
        </p>
    </div>
    """, unsafe_allow_html=True)

    trace_log = [
        {
            "type": "thought",
            "tag_class": "tag-thought",
            "entry_class": "trace-thought",
            "timestamp": "22:14:03",
            "content": "The student uploaded 'Ch7_Linear_Algebra.pdf'. I need to extract key concepts, identify prerequisite gaps, and update the mastery matrix. Let me first parse the PDF via the Ingestion MCP server."
        },
        {
            "type": "action",
            "tag_class": "tag-action",
            "entry_class": "trace-action",
            "timestamp": "22:14:04",
            "content": "→ <strong>MCP Call</strong>: <code>ingestion_server.extract_text(file='Ch7_Linear_Algebra.pdf')</code><br/>→ <strong>MCP Call</strong>: <code>elasticsearch_server.index_document(index='study_materials', body={...})</code>"
        },
        {
            "type": "observation",
            "tag_class": "tag-observe",
            "entry_class": "trace-observe",
            "timestamp": "22:14:06",
            "content": "✓ Extracted 24 pages, 847 sentences. Key topics identified: Eigenvalues, Eigenvectors, Diagonalization, SVD. Indexed to Elasticsearch with doc_id='sm_00482'. The student's mastery on Eigenvalues is currently 62% — below the 70% threshold."
        },
        {
            "type": "thought",
            "tag_class": "tag-thought",
            "entry_class": "trace-thought",
            "timestamp": "22:14:07",
            "content": "The Eigenvalues mastery is 62%, which is in the 'yellow zone'. I should generate a targeted practice set focusing on characteristic equations and diagonalization. Let me also check if there's an upcoming exam via the schedule."
        },
        {
            "type": "action",
            "tag_class": "tag-action",
            "entry_class": "trace-action",
            "timestamp": "22:14:08",
            "content": "→ <strong>MCP Call</strong>: <code>mongodb_server.query('schedule', {topic: /linear algebra/i, type: 'exam'})</code><br/>→ <strong>MCP Call</strong>: <code>mongodb_server.update('mastery', {topic: 'Linear Algebra'}, {$set: {subtopics: {eigenvalues: 0.62}}})</code>"
        },
        {
            "type": "observation",
            "tag_class": "tag-observe",
            "entry_class": "trace-observe",
            "timestamp": "22:14:09",
            "content": "✓ Found upcoming exam: 'Linear Algebra Mid-Semester' on 2026-06-03 (5 days away). Mastery subtopic updated. Priority level elevated to HIGH. Generating 15-question practice set with spaced repetition schedule."
        },
        {
            "type": "thought",
            "tag_class": "tag-thought",
            "entry_class": "trace-thought",
            "timestamp": "22:14:10",
            "content": "Exam in 5 days with sub-70% mastery on a key subtopic. I need to restructure today's remaining schedule to add an extra review block and push the GitLab assignment auto-grade to confirm the student's recent submission passed."
        },
        {
            "type": "action",
            "tag_class": "tag-action",
            "entry_class": "trace-action",
            "timestamp": "22:14:11",
            "content": "→ <strong>MCP Call</strong>: <code>gitlab_server.get_pipeline_status(project='math-201', pipeline_id=1847)</code><br/>→ <strong>MCP Call</strong>: <code>mongodb_server.update('schedule', {date: '2026-05-29'}, {$push: {blocks: {time: '20:30-21:30', topic: 'Eigenvalues Drill'}}})</code>"
        },
        {
            "type": "observation",
            "tag_class": "tag-observe",
            "entry_class": "trace-observe",
            "timestamp": "22:14:12",
            "content": "✓ Pipeline #1847: All tests PASSED (unit: 42s, integration: 1m18s, auto-grade: 23s). Score: 94/100. Schedule updated — added 'Eigenvalues Drill' block at 20:30. Arize trace logged with latency=287ms, tokens=1,204."
        },
    ]

    st.markdown("""
    <div class="terminal-window">
        <div class="terminal-header">
            <div class="terminal-dot dot-red"></div>
            <div class="terminal-dot dot-yellow"></div>
            <div class="terminal-dot dot-green"></div>
            <div class="terminal-title">GEMINI_AGENT_REASONING_SHELL ~ v3.0-flash</div>
        </div>
    """, unsafe_allow_html=True)

    for entry in trace_log:
        st.markdown(f"""
        <div class="trace-entry {entry['entry_class']}">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span class="trace-tag {entry['tag_class']}">{entry['type']}</span>
                <span style="font-size:0.7rem; color:var(--text-muted);">{entry['timestamp']}</span>
            </div>
            <div style="color:var(--text-secondary);">{entry['content']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════ TAB 3: Daily Schedule ═══════════════════════════════
with tab3:
    today_str = datetime.now().strftime("%A, %B %d, %Y")
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="margin-top:0; font-size:1.15rem;">📅 Today's Study Plan</h3>
        <p style="color:var(--text-secondary); font-size:0.88rem; margin-bottom:4px;">
            {today_str} &nbsp;·&nbsp; Auto-optimized by the scheduling agent
        </p>
    </div>
    """, unsafe_allow_html=True)

    schedule = get_schedule_data()
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    for block in schedule:
        type_class = f"type-{block['type']}"
        st.markdown(f"""
        <div class="schedule-block type-{block['type']}">
            <div class="schedule-time">{block['time']}</div>
            <div style="font-size:1.3rem;">{block.get('emoji', '📖')}</div>
            <div class="schedule-topic">{block['topic']}</div>
            <div style="flex:1;"></div>
            <span class="schedule-type {type_class}">{block['type']}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════ TAB 4: Pipeline Status ══════════════════════════════
with tab4:
    st.markdown("""
    <div class="glass-card">
        <h3 style="margin-top:0; font-size:1.15rem;">🚀 GitLab CI/CD Pipeline Results</h3>
        <p style="color:var(--text-secondary); font-size:0.88rem; margin-bottom:4px;">
            Automated test & grading pipelines for code assignments
        </p>
    </div>
    """, unsafe_allow_html=True)

    pipelines = get_pipeline_data()
    for p in pipelines:
        status_class = "pipeline-pass" if p["status"] == "passed" else "pipeline-fail"
        status_icon = "✅" if p["status"] == "passed" else "❌"
        st.markdown(f'<div class="pipeline-card" style="display:flex; justify-content:space-between; align-items:center; width:100%;"><div style="display:flex; align-items:center; gap:12px;"><span style="font-family:\'JetBrains Mono\',monospace; font-weight:700; color:var(--accent-cyan); font-size:0.9rem;">{p["pipeline"]}</span><span style="font-size:0.78rem; color:var(--text-muted); background:rgba(255,255,255,0.04); padding:2px 8px; border-radius:4px;">{p["stage"]}</span><span style="font-weight:600; color:var(--text-primary); font-size:0.9rem;">{p["job"]}</span></div><div style="display:flex; align-items:center; gap:16px;"><span style="font-size:0.78rem; color:var(--text-muted);">⏱ {p["duration"]}</span><span style="font-size:0.78rem; color:var(--text-muted);">{p["timestamp"]}</span><span class="{status_class}">{status_icon} {p["status"].upper()}</span></div></div>', unsafe_allow_html=True)

    # Summary row
    total = len(pipelines)
    passed = sum(1 for p in pipelines if p["status"] == "passed")
    failed = total - passed
    st.markdown(f"""
    <div class="glass-card" style="margin-top:16px;">
        <div style="display:flex; justify-content:space-around; text-align:center;">
            <div>
                <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:1px;">Total Jobs</div>
                <div style="font-size:1.8rem; font-weight:800; color:var(--accent-cyan);">{total}</div>
            </div>
            <div>
                <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:1px;">Passed</div>
                <div style="font-size:1.8rem; font-weight:800; color:var(--accent-green);">{passed}</div>
            </div>
            <div>
                <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:1px;">Failed</div>
                <div style="font-size:1.8rem; font-weight:800; color:var(--accent-red);">{failed}</div>
            </div>
            <div>
                <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:1px;">Pass Rate</div>
                <div style="font-size:1.8rem; font-weight:800; color:var(--accent-green);">{passed/total*100:.0f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════ TAB 5: Agent Quality ════════════════════════════════
with tab5:
    st.markdown("""
    <div class="glass-card">
        <h3 style="margin-top:0; font-size:1.15rem;">🛡️ Arize AI — Agent Observability</h3>
        <p style="color:var(--text-secondary); font-size:0.88rem; margin-bottom:4px;">
            Real-time quality metrics, hallucination detection, and trace analytics
        </p>
    </div>
    """, unsafe_allow_html=True)

    qm = get_quality_metrics()

    q1, q2, q3, q4 = st.columns(4)

    with q1:
        hall_pct = qm["hallucination_score"] * 100
        ring_color = "conic-gradient(#22c55e 0% {0}%, rgba(255,255,255,0.05) {0}% 100%)".format(int((1 - qm["hallucination_score"]) * 100))
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div class="gauge-ring" style="background:{ring_color};">
                <span class="gauge-value" style="color:#22c55e;">{hall_pct:.1f}%</span>
            </div>
            <div style="font-weight:700; font-size:0.9rem; color:var(--text-primary);">Hallucination Rate</div>
            <div style="font-size:0.78rem; color:var(--accent-green); margin-top:4px;">● Excellent</div>
        </div>
        """, unsafe_allow_html=True)

    with q2:
        acc_pct = qm["accuracy"] * 100
        ring_color2 = "conic-gradient(#00d4ff 0% {0}%, rgba(255,255,255,0.05) {0}% 100%)".format(int(acc_pct))
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div class="gauge-ring" style="background:{ring_color2};">
                <span class="gauge-value" style="color:#00d4ff;">{acc_pct:.0f}%</span>
            </div>
            <div style="font-weight:700; font-size:0.9rem; color:var(--text-primary);">Response Accuracy</div>
            <div style="font-size:0.78rem; color:var(--accent-cyan); margin-top:4px;">● High</div>
        </div>
        """, unsafe_allow_html=True)

    with q3:
        rel_pct = qm["relevance"] * 100
        ring_color3 = "conic-gradient(#a855f7 0% {0}%, rgba(255,255,255,0.05) {0}% 100%)".format(int(rel_pct))
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div class="gauge-ring" style="background:{ring_color3};">
                <span class="gauge-value" style="color:#a855f7;">{rel_pct:.0f}%</span>
            </div>
            <div style="font-weight:700; font-size:0.9rem; color:var(--text-primary);">Relevance Score</div>
            <div style="font-size:0.78rem; color:var(--accent-purple); margin-top:4px;">● Strong</div>
        </div>
        """, unsafe_allow_html=True)

    with q4:
        safe_pct = qm["safety_score"] * 100
        ring_color4 = "conic-gradient(#22c55e 0% {0}%, rgba(255,255,255,0.05) {0}% 100%)".format(int(safe_pct))
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div class="gauge-ring" style="background:{ring_color4};">
                <span class="gauge-value" style="color:#22c55e;">{safe_pct:.0f}%</span>
            </div>
            <div style="font-weight:700; font-size:0.9rem; color:var(--text-primary);">Safety Score</div>
            <div style="font-size:0.78rem; color:var(--accent-green); margin-top:4px;">● Excellent</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("", unsafe_allow_html=True)

    # Detailed metrics table
    s1, s2 = st.columns(2)
    with s1:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="font-size:1rem; margin-top:0;">⚙️ Performance Metrics</h4>
            <div class="sidebar-stat">
                <span class="sidebar-stat-label">Avg Latency</span>
                <span class="sidebar-stat-value">{qm['avg_latency_ms']} ms</span>
            </div>
            <div class="sidebar-stat">
                <span class="sidebar-stat-label">Total Tokens Used</span>
                <span class="sidebar-stat-value">{qm['total_tokens']:,}</span>
            </div>
            <div class="sidebar-stat">
                <span class="sidebar-stat-label">Trace Count</span>
                <span class="sidebar-stat-value">{qm['trace_count']:,}</span>
            </div>
            <div class="sidebar-stat">
                <span class="sidebar-stat-label">Est. API Cost</span>
                <span class="sidebar-stat-value">${qm['cost_usd']:.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with s2:
        st.markdown("""
        <div class="glass-card">
            <h4 style="font-size:1rem; margin-top:0;">📊 Trace Distribution</h4>
            <div class="sidebar-stat">
                <span class="sidebar-stat-label">Thought Traces</span>
                <span style="color:#a855f7; font-weight:600;">423</span>
            </div>
            <div class="sidebar-stat">
                <span class="sidebar-stat-label">Action Traces</span>
                <span style="color:#00d4ff; font-weight:600;">412</span>
            </div>
            <div class="sidebar-stat">
                <span class="sidebar-stat-label">Observation Traces</span>
                <span style="color:#22c55e; font-weight:600;">412</span>
            </div>
            <div class="sidebar-stat">
                <span class="sidebar-stat-label">Error Traces</span>
                <span style="color:#ef4444; font-weight:600;">0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    Powered by <strong>Google Cloud Agent Builder</strong> × <strong>Gemini 3</strong> &nbsp;|&nbsp;
    Built for <strong>Rapid Agent Hackathon 2026</strong> &nbsp;|&nbsp;
    MongoDB · Elasticsearch · GitLab · Arize AI
</div>
""", unsafe_allow_html=True)
