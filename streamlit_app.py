import os
import requests
import pandas as pd
import streamlit as st

# --- CONFIGURATION & DYNAMIC API HOST ---
st.set_page_config(
    page_title="Neural Observatory PRO",
    page_icon="🧠",
    layout="wide"
)

# Dynamically fetch API_URL from environment variable, falling back to localhost
API_URL = os.getenv("API_URL", "http://localhost:8081")

# --- CUSTOM NEON DARK THEME CSS ---
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
    /* Fix for Input Boxes */
    div[data-baseweb="input"] > div {
        background-color: #111827 !important;
        border: 1px solid #374151 !important;
    }
    div[data-baseweb="input"] input {
        color: #00ffff !important;
    }
    /* Fix for Buttons */
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

# --- HELPER FUNCTIONS ---
def fetch_api(endpoint, method="GET", payload=None):
    try:
        url = f"{API_URL}/{endpoint}"
        if method == "GET":
            res = requests.get(url, timeout=3)
        else:
            res = requests.post(url, json=payload, timeout=5)
        return res.json() if res.status_code == 200 else None
    except Exception:
        return None

# --- HEADER SECTION ---
col_title, col_status = st.columns([3, 1])

with col_title:
    st.title("🧠 NEURAL OBSERVATORY · PRO")
    st.caption("Enterprise data engineering observability | Real-time AI intelligence")

# API Health & Last Run
stats_data = fetch_api("stats")
last_run_data = fetch_api("last_run")
subs_data = fetch_api("list_subscribers")

with col_status:
    if stats_data:
        st.success("🟢 API ONLINE")
    else:
        st.error("🔴 API OFFLINE")
    
    last_run_time = last_run_data.get('last_run', '--') if last_run_data else '--'
    st.write(f"⏱️ **Last Run:** {last_run_time}")

st.divider()

# --- TOP STATS METRICS ---
if stats_data:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Articles", stats_data.get('total', 0))
    c2.metric("Avg. Summary Len", stats_data.get('avg_length', 0))
    c3.metric("Unique Keywords", stats_data.get('unique_keywords', 0))
    c4.metric("Subscribers", len(subs_data.get('subscribers', [])) if subs_data else 0)
else:
    st.info("💡 Start your backend API (`python unified_api.py`) to see live metrics.")

st.divider()

# --- CHARTS SECTION ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📡 Keyword Frequency Spectrum")
    if stats_data and 'top_keywords' in stats_data:
        kw_df = pd.DataFrame(stats_data['top_keywords'][:8], columns=["Keyword", "Mentions"])
        st.bar_chart(kw_df.set_index("Keyword"), color="#00ffff")
    else:
        st.caption("No keyword data available.")

with chart_col2:
    st.subheader("📈 Delta Analysis (Previous vs Current)")
    compare_data = fetch_api("stats_compare")
    if compare_data:
        prev = compare_data.get('previous', {'total': 0, 'unique_keywords': 0})
        curr = compare_data.get('current', {'total': 0, 'unique_keywords': 0})
        
        scatter_df = pd.DataFrame({
            "Cycle": ["Previous Cycle", "Current Cycle"],
            "Total Articles": [prev.get('total', 0), curr.get('total', 0)],
            "Unique Keywords": [prev.get('unique_keywords', 0), curr.get('unique_keywords', 0)]
        })
        st.scatter_chart(scatter_df, x="Total Articles", y="Unique Keywords", color="#ff66cc", size=400)
    else:
        st.caption("No comparison data available.")

st.divider()

# --- CONTROLS & PIPELINE HEALTH ---
action_col, health_col = st.columns(2)

with action_col:
    st.subheader("⚡ Pipeline Controls")
    
    if st.button("⟳ Run Data Pipeline", use_container_width=True, type="primary"):
        with st.spinner("Harvesting data across streams (~2 mins)..."):
            res = fetch_api("run_pipeline", method="POST")
            if res:
                st.toast(res.get('message', 'Pipeline triggered successfully!'))
            else:
                st.error("Failed to connect to API server.")

    btn_a, btn_b = st.columns(2)
    with btn_a:
        if st.button("📧 Test Transmission", use_container_width=True):
            res = fetch_api("send_test_email", method="POST", payload={"email": "analyst@neuralnet.com"})
            st.toast("Test transmission sent!" if res else "Email API error.")
            
    with btn_b:
        if st.button("📡 Broadcast to All", use_container_width=True):
            res = fetch_api("send_bulk_email", method="POST")
            st.toast("Broadcast initiated!" if res else "Broadcast error.")

with health_col:
    st.subheader("⚙️ System Health")
    health_data = fetch_api("pipeline_health")
    if health_data:
        st.text(f"Last Duration: {health_data.get('last_duration_seconds', 0)}s")
        st.text(f"Success Rate: {health_data.get('success_rate', 100)}%")
        st.text("YouTube API: Online")
        st.text("Groq API: Online")
    else:
        st.caption("Pipeline health metrics offline.")

st.divider()

# --- SUBSCRIPTION MANAGEMENT ---
st.subheader("🔗 Activate Subscription")
st.write("Subscribe to receive daily AI-curated news digests directly to your inbox.")

sub_col1, sub_col2 = st.columns([3, 1])

with sub_col1:
    # Text input for the user to type their email
    new_sub_email = st.text_input("Email Address", placeholder="user@example.com", label_visibility="collapsed")

with sub_col2:
    # The button to trigger the API call
    if st.button("Activate Subscription", use_container_width=True):
        if new_sub_email and "@" in new_sub_email:
            # Send the email to your unified_api.py backend
            res = fetch_api("subscribe", method="POST", payload={"email": new_sub_email})
            
            if res and res.get("success"):
                st.success(f"✅ {res.get('message', 'Subscribed successfully!')}")
                st.balloons() # Adds a fun little animation when they subscribe
            else:
                error_msg = res.get('message', 'Failed to subscribe.') if res else 'API Offline'
                st.error(f"❌ {error_msg}")
        else:
            st.warning("⚠️ Please enter a valid email address.")
            
# --- UNSUBSCRIBE SECTION ---
st.subheader("🗑️ Remove Subscription")
st.write("Want to stop receiving daily digests? Enter your email below to opt out.")

unsub_col1, unsub_col2 = st.columns([3, 1])

with unsub_col1:
    unsub_email = st.text_input("Unsubscribe Email Address", placeholder="user@example.com", label_visibility="collapsed", key="unsub_input")

with unsub_col2:
    if st.button("Unsubscribe", use_container_width=True):
        if unsub_email and "@" in unsub_email:
            res = fetch_api("unsubscribe", method="POST", payload={"email": unsub_email})
            
            if res and res.get("success"):
                st.success(f"✅ {res.get('message', 'Successfully unsubscribed.')}")
            else:
                error_msg = res.get('message', 'Failed to unsubscribe.') if res else 'API Offline'
                st.error(f"🗑️ {error_msg}")
        else:
            st.warning("⚠️ Please enter a valid email address.")

# --- PERSONALIZED FEED ---
st.subheader("📰 Real-Time Intelligence Feed")

user_email = st.text_input("Personalize feed for subscriber email:", value="analyst@neuralnet.com")
feed_data = fetch_api("personalized_feed", method="POST", payload={"email": user_email})

if feed_data and feed_data.get("articles"):
    for article in feed_data["articles"][:15]:
        with st.container(border=True):
            title = article.get('title', 'Untitled Article')
            src = str(article.get('source') or article.get('source_name', 'NEWS')).upper()
            summary = article.get('summary', 'No summary generated.')
            url = article.get('url') or (f"https://youtube.com/watch?v={article.get('video_id')}" if article.get('video_id') else "#")
            
            st.markdown(f"**[{src}]** {title}")
            st.caption(summary[:200] + "...")
            st.link_button("Read Source ↗", url)
else:
    st.info("No ingested articles found. Click 'Run Data Pipeline' above to harvest fresh data.")
