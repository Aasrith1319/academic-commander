import re

file_path = r"c:\Users\AASRITH\Downloads\academic commander\app\main.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Locate the page config start
start_idx = content.find("st.set_page_config(")
if start_idx == -1:
    print("Could not find page config start!")
    exit(1)

# Locate the mongodb connection comment start (which marks the end of the CSS section)
end_marker = "# ─────────────────────────────────────────────────────────────────────────────\n# MONGODB CONNECTION"
end_idx = content.find(end_marker)
if end_idx == -1:
    # Try with CRLF
    end_marker = "# ─────────────────────────────────────────────────────────────────────────────\r\n# MONGODB CONNECTION"
    end_idx = content.find(end_marker)

if end_idx == -1:
    print("Could not find end marker!")
    exit(1)

new_style_block = """st.set_page_config(
    page_title="Academic Commander",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS — Premium Dark Theme with Glassmorphism
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(\"\"\"
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
\"\"\", unsafe_allow_html=True)
"""

# Splitting and replacing
parts = content.split("st.set_page_config(")
prefix = parts[0]

# Locate where the MONGODB CONNECTION starts in the rest of the text
suffix_start = content.find(end_marker)
suffix = content[suffix_start:]

restored_content = prefix + new_style_block + suffix

with open(file_path, "w", encoding="utf-8") as f:
    f.write(restored_content)

print("SUCCESS: Style and configuration rewritten successfully!")
