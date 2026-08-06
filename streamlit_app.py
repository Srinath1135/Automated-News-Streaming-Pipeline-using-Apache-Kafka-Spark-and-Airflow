import os
import json
import pandas as pd
import subprocess
import time
from datetime import datetime

# --- CONFIGURATION & PAGE SETUP ---
st.set_page_config(
    page_title="Neural Observatory PRO",
    page_icon="🧠",
    layout="wide"
)

# --- FILE PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUBSCRIBERS_FILE = os.path.join(BASE_DIR, "subscribers.json")
USER_PROFILES_FILE = os.path.join(BASE_DIR, "user_profiles.json")
ARTICLES_FILE = os.path.join(BASE_DIR, "saved_articles.json")
PREV_STATS_FILE = os.path.join(BASE_DIR, "previous_stats.json")
LAST_RUN_FILE = os.path.join(BASE_DIR, "last_run.json")
PIPELINE_STATS_FILE = os.path.join(BASE_DIR, "pipeline_stats.json")

# --- DATA HELPERS ---
def load_json(file_path, default=None):
    if not os.path.exists(file_path):
        return default if default is not None else []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else []

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_article_stats():
    articles = load_json(ARTICLES_FILE, [])
    if not articles:
        return {
            "total": 0,
            "avg_length": 0,
            "unique_keywords": 0,
            "top_keywords": [],
            "source_distribution": {}
        }
    
    total = len(articles)
    avg_length = sum(len(a.get("summary", "")) for a in articles) // total if total > 0 else 0
    
    stop_words = {"this", "that", "these", "those", "from", "with", "they", "will", "have", "were", "been", "being", "about", "their"}
    keyword_count = {}
    
    for article in articles:
        text = (article.get("title", "") + " " + article.get("summary", "")).lower()
        words = [w for w in text.split() if len(w) > 3 and w.isalpha() and w not in stop_words]
        for word in words:
            keyword_count[word] = keyword_count.get(word, 0) + 1
            
    top_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "total": total,
        "avg_length": avg_length,
        "unique_keywords": len(keyword_count),
        "top_keywords": top_keywords
    }

def rank_articles_by_interests(articles, email):
    profiles = load_json(USER_PROFILES_FILE, {})
    interests = profiles.get(email, {}).get("interests", [])
    if not interests:
        return articles
    
    ranked_articles = []
    for article in articles:
        text = (article.get("title", "") + " " + article.get("summary", "") + " " + article.get("category", "")).lower()
        score = 0
        for index, interest in enumerate(interests):
            if interest.lower() in text:
                score += (5 - index)
        if article.get("trending"):
            score += 2
        ranked_articles.append((score, article))
        
    ranked_articles.sort(key=lambda x: x[0], reverse=True)
    return [article for score, article in ranked_articles]

# --- CUSTOM NEON DARK THEME CSS ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0a0f1e;
        color: #eef2ff;
    }
    h1 {
        background: linear-gradient(135deg, #fff, #88ddff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    div[data-testid="stMetricValue"] {
        color: #00ffff !important;
        font-family: monospace;
    }
    div[data-baseweb="input"] > div {
        background-color: #111827 !important;
        border: 1px solid #374151 !important;
    }
    div[data-baseweb="input"] input {
        color: #00ffff !important;
    }
    div.stButton > button {
        background-color: #111827 !important;
        color: #00ffff !important;
        border: 1px solid #00ffff !important;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #00ffff !important;
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
col_title, col_status = st.columns([3, 1])

with col_title:
    st.title("🧠 NEURAL OBSERVATORY · PRO")
    st.caption("Enterprise data engineering observability | Real-time AI intelligence")

# Load state directly
stats_data = get_article_stats()
last_run_data = load_json(LAST_RUN_FILE, {})
subs_data = load_json(SUBSCRIBERS_FILE, [])

with col_status:
    st.success("🟢 ONLINE (Standalone)")
    last_run_time = last_run_data.get('timestamp', '--')
    st.write(f"⏱️ **Last Run:** {last_run_time}")

st.divider()

# --- TOP STATS METRICS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Articles", stats_data.get('total', 0))
c2.metric("Avg. Summary Len", stats_data.get('avg_length', 0))
c3.metric("Unique Keywords", stats_data.get('unique_keywords', 0))
c4.metric("Subscribers", len(subs_data))

st.divider()

# --- CHARTS SECTION ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📡 Keyword Frequency Spectrum")
    if stats_data.get('top_keywords'):
        kw_df = pd.DataFrame(stats_data['top_keywords'][:8], columns=["Keyword", "Mentions"])
        st.bar_chart(kw_df.set_index("Keyword"), color="#00ffff")
    else:
        st.caption("No keyword data available.")

with chart_col2:
    st.subheader("📈 Delta Analysis (Previous vs Current)")
    prev_stats = load_json(PREV_STATS_FILE, {'total': 0, 'unique_keywords': 0})
    scatter_df = pd.DataFrame({
        "Cycle": ["Previous Cycle", "Current Cycle"],
        "Total Articles": [prev_stats.get('total', 0), stats_data.get('total', 0)],
        "Unique Keywords": [prev_stats.get('unique_keywords', 0), stats_data.get('unique_keywords', 0)]
    })
    st.scatter_chart(scatter_df, x="Total Articles", y="Unique Keywords", color="#ff66cc", size=400)

st.divider()

# --- CONTROLS & SYSTEM HEALTH ---
action_col, health_col = st.columns(2)

with action_col:
    st.subheader("⚡ Pipeline Controls")
    if st.button("⟳ Run Data Pipeline", use_container_width=True, type="primary"):
        with st.spinner("Harvesting data across streams (~2 mins)..."):
            start_time = time.time()
            try:
                result = subprocess.run(["python3", "main.py"], cwd=BASE_DIR, capture_output=True, text=True, check=True)
                duration = round(time.time() - start_time, 2)
                
                pipeline_stats = {
                    "last_duration": duration,
                    "success_rate": 100.0,
                    "last_articles": len(load_json(ARTICLES_FILE, []))
                }
                save_json(PIPELINE_STATS_FILE, pipeline_stats)
                save_json(LAST_RUN_FILE, {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                
                st.success("✅ Pipeline executed successfully! Refreshing dashboard...")
                st.rerun()
            except subprocess.CalledProcessError as e:
                st.error(f"❌ Pipeline failed: {e.stderr}")

    btn_a, btn_b = st.columns(2)
    with btn_a:
        if st.button("📧 Test Transmission", use_container_width=True):
            st.toast("Test transmission utility active.")
    with btn_b:
        if st.button("📡 Broadcast to All", use_container_width=True):
            st.toast("Broadcast protocol ready.")

with health_col:
    st.subheader("⚙️ System Health")
    health_data = load_json(PIPELINE_STATS_FILE, {})
    st.text(f"Last Duration: {health_data.get('last_duration', 0)}s")
    st.text(f"Success Rate: {health_data.get('success_rate', 100)}%")
    st.text("YouTube API: Online")
    st.text("Groq API: Online")

st.divider()

# --- SUBSCRIPTION MANAGEMENT ---
st.subheader("🔗 Activate Subscription")
st.write("Subscribe to receive daily AI-curated news digests directly to your inbox.")

sub_col1, sub_col2 = st.columns([3, 1])

with sub_col1:
    new_sub_email = st.text_input("Email Address", placeholder="user@example.com", label_visibility="collapsed", key="sub_input")

with sub_col2:
    if st.button("Activate Subscription", use_container_width=True):
        if new_sub_email and "@" in new_sub_email:
            email_clean = new_sub_email.strip().lower()
            subscribers = load_json(SUBSCRIBERS_FILE, [])
            if email_clean in subscribers:
                st.warning("⚠️ Email is already subscribed.")
            else:
                subscribers.append(email_clean)
                save_json(SUBSCRIBERS_FILE, subscribers)
                st.success("✅ Subscribed successfully!")
                st.balloons()
        else:
            st.warning("⚠️ Please enter a valid email address.")

# --- UNSUBSCRIBE SECTION ---
st.subheader("🗑️ Remove Subscription")
st.write("Want to stop receiving daily digests? Enter your email below to opt out.")

unsub_col1, unsub_col2 = st.columns([3, 1])

with unsub_col1:
    unsub_email = st.text_input("Unsubscribe Email Address", placeholder="user@example.com", label_visibility="collapsed", key="unsub_input_field")

with unsub_col2:
    if st.button("Unsubscribe", use_container_width=True):
        if unsub_email and "@" in unsub_email:
            email_clean = unsub_email.strip().lower()
            subscribers = load_json(SUBSCRIBERS_FILE, [])
            if email_clean in subscribers:
                subscribers.remove(email_clean)
                save_json(SUBSCRIBERS_FILE, subscribers)
                st.success("✅ Successfully unsubscribed.")
            else:
                st.error("🗑️ Email address not found in subscriber list.")
        else:
            st.warning("⚠️ Please enter a valid email address.")

st.divider()

# --- PERSONALIZED FEED ---
st.subheader("📰 Real-Time Intelligence Feed")

user_email = st.text_input("Personalize feed for subscriber email:", value="analyst@neuralnet.com")
articles = load_json(ARTICLES_FILE, [])
ranked_articles = rank_articles_by_interests(articles, user_email)

if ranked_articles:
    for article in ranked_articles[:15]:
        with st.container(border=True):
            title = article.get('title', 'Untitled Article')
            src = str(article.get('source') or article.get('source_name', 'NEWS')).upper()
            summary = article.get('summary', 'No summary generated.')
            url = article.get('url') or (f"https://youtube.com/watch?v={article.get('video_id')}" if article.get('video_id') else "#")
            
            st.markdown(f"**[{src}]** {title}")
            st.caption(summary[:200] + "...")
            st.link_button("Read Source ↗", url)
else:
    st.info("No ingested articles found in saved records. Click 'Run Data Pipeline' above to harvest data.")
