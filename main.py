import streamlit as st
import streamlit.components.v1 as components
import random
import uuid
import warnings

from services.news_service import (
    fetch_news,
    extract_full_article
)

from services.explanation_service import (
    generate_explanation,
    generate_deep_context
)

from utils.text_cleaner import (
    clean_article_text,
    filter_relevant_content
)

# ============================================================
# WARNINGS
# ============================================================
warnings.filterwarnings("ignore")

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="AI News Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# SESSION STATE
# ============================================================
if "articles" not in st.session_state:
    st.session_state.articles = []

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = str(uuid.uuid4())

if "expanded_article_uid" not in st.session_state:
    st.session_state.expanded_article_uid = None

# ============================================================
# 🎯 ACCORDION INTERACTION CALLBACK FUNCTIONS
# ============================================================
def toggle_article_accordion(article_id):
    """
    Handles accordion state mutations cleanly before rendering pipelines trigger,
    ensuring opening a new item programmatically folds open components.
    """
    if st.session_state.expanded_article_uid == article_id:
        st.session_state.expanded_article_uid = None
    else:
        st.session_state.expanded_article_uid = article_id

# ============================================================
# SOURCE CLEANER
# ============================================================
def clean_source_name(raw: str) -> str:
    if not raw:
        return "News Source"
    if "|" in raw:
        return raw.split("|")[-1].strip()
    if " - " in raw:
        return raw.split(" - ")[-1].strip()
    return raw.strip()

# ============================================================
# REFRESH FUNCTION
# ============================================================
def perform_hard_refresh():
    for key in list(st.session_state.keys()):
        if (
            key.startswith("summary_")
            or
            key.startswith("context_")
        ):
            del st.session_state[key]

    st.session_state.refresh_token = str(uuid.uuid4())
    st.session_state.expanded_article_uid = None

    fresh_articles = fetch_news(
        region=st.session_state.region_selector,
        category=st.session_state.category_selector
    )

    unique_articles = []
    seen_links = set()

    for article in fresh_articles:
        if article["link"] not in seen_links:
            unique_articles.append(article)
            seen_links.add(article["link"])

    random.shuffle(unique_articles)
    st.session_state.articles = unique_articles[:8]

# ============================================================
# INITIAL FETCH
# ============================================================
if not st.session_state.articles:
    initial_articles = fetch_news(
        region="India",
        category="All"
    )
    random.shuffle(initial_articles)
    st.session_state.articles = initial_articles[:8]

# ============================================================
# COLORS
# ============================================================
BG = "#181825"
CARD_BG = "rgba(36, 33, 58, 0.68)"
CARD_BORDER = "rgba(180, 167, 255, 0.10)"
TEXT = "#F5F3FF"
TEXT_SOFT = "#B7B2D9"
ACCENT = "#B4A7FF"
ACCENT_LIGHT = "#CFC7FF"
SUMMARY_BG = "rgba(56, 50, 84, 0.45)"
CONTEXT_BG = "rgba(48, 44, 76, 0.52)"
BUTTON_BG = "rgba(180,167,255,0.06)"
SHADOW = "0 6px 24px rgba(0,0,0,0.18)"

# ============================================================
# CSS
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp {{
    background: radial-gradient(circle at top left, #262240 0%, #181825 45%);
    color: {TEXT};
    font-family: 'Inter', sans-serif;
}}

#MainMenu, footer, header {{
    visibility: hidden;
}}

[data-testid="stDecoration"] {{
    display: none;
}}

.block-container {{
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}}

[data-testid="stVerticalBlockBorderWrapper"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}}

.main-title {{
    text-align: center;
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 800;
    margin-bottom: 0.3rem;
    background: linear-gradient(135deg, {ACCENT}, {ACCENT_LIGHT});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.sub-title {{
    text-align: center;
    color: {TEXT_SOFT};
    font-size: 1rem;
    margin-bottom: 2.5rem;
}}

.filter-panel {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    backdrop-filter: blur(18px);
    border-radius: 24px;
    padding: 1.2rem;
    margin-bottom: 2rem;
    box-shadow: {SHADOW};
}}

.news-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    backdrop-filter: blur(16px);
    border-radius: 24px;
    margin-bottom: 20px !important;
    overflow: hidden;
    transition: all 0.25s ease;
    box-shadow: {SHADOW};
}}

.news-card:hover {{
    border-color: rgba(180,167,255,0.20);
}}

.news-card.is-open {{
    border-color: rgba(180,167,255,0.35);
    box-shadow: 0 0 0 1px rgba(183,166,255,0.10), 0 8px 32px rgba(0,0,0,0.28);
}}

/* ── 🎯 DEDICATED HEADER BOX COMPONENT ── */
.dedicated-card-header {{
    background: rgba(255, 255, 255, 0.02) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
    width: 100% !important;
    transition: background 0.2s ease;
}}
.news-card.is-open .dedicated-card-header {{
    background: rgba(180, 167, 255, 0.04) !important;
    border-bottom: 1px solid rgba(180, 167, 255, 0.15) !important;
}}

.title-btn div[data-testid="stButton"] > button {{
    background: transparent !important;
    border: none !important;
    color: {TEXT} !important;
    text-align: left !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    line-height: 1.55 !important;
    padding: 1.3rem 1.5rem !important;
    width: 100% !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    min-height: unset !important;
    height: auto !important;
    white-space: normal !important;
    word-break: break-word !important;
    justify-content: flex-start !important;
}}

.title-btn div[data-testid="stButton"] > button:hover {{
    color: {ACCENT_LIGHT} !important;
}}

.arrow {{
    font-size: 0.95rem;
    color: {ACCENT};
    padding-top: 1.45rem;
    text-align: center;
    font-weight: bold;
    user-select: none;
}}

.article-panel {{
    padding: 1.5rem 1.5rem 1.6rem 1.5rem;
}}

.source-badge {{
    display: inline-flex;
    align-items: center;
    padding: 0.38rem 0.85rem;
    border-radius: 999px;
    background: rgba(180,167,255,0.08);
    color: {ACCENT_LIGHT};
    font-size: 0.72rem;
    font-weight: 700;
    margin-bottom: 1.2rem;
    border: 1px solid rgba(180,167,255,0.12);
}}

.summary-box {{
    background: {SUMMARY_BG};
    border: 1px solid rgba(180,167,255,0.08);
    border-radius: 20px;
    padding: 1.1rem 1.2rem;
    margin-top: 0.2rem;
    margin-bottom: 1.2rem;
    line-height: 1.95;
    font-size: 0.98rem;
}}

.context-box {{
    background: {CONTEXT_BG};
    border: 1px solid rgba(180,167,255,0.08);
    border-radius: 20px;
    padding: 1.1rem 1.2rem;
    margin-top: 1.2rem;
    line-height: 2;
    font-size: 0.96rem;
}}

.box-label {{
    display: block;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 0.65rem;
    color: {ACCENT};
    text-transform: uppercase;
}}

div[data-testid="stButton"] > button {{
    height: 50px;
    border-radius: 16px;
    border: 1px solid rgba(180,167,255,0.10);
    background: rgba(180,167,255,0.06);
    color: #E8E2FF;
    font-weight: 700;
    font-size: 0.9rem;
    transition: 0.2s ease;
}}

div[data-testid="stButton"] > button:hover {{
    background: rgba(180,167,255,0.12);
    border-color: rgba(180,167,255,0.18);
    transform: translateY(-1px);
}}

.read-original-btn {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    height: 50px !important;
    border-radius: 16px !important;
    background: rgba(180,167,255,0.06) !important;
    border: 1px solid rgba(180,167,255,0.10) !important;
    color: #E8E2FF !important;
    text-decoration: none !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    transition: 0.2s ease;
}}

.read-original-btn:hover {{
    background: rgba(180,167,255,0.12) !important;
    transform: translateY(-1px);
}}

@media (max-width: 768px) {{
    .block-container {{ padding-top: 1rem; }}
    .article-panel {{ padding: 1.2rem 1rem; }}
    .title-btn div[data-testid="stButton"] > button {{
        font-size: 1.05rem !important;
        padding: 1.1rem 1rem !important;
    }}
    div[data-testid="stButton"] > button {{ height: 46px; }}
    .read-original-btn {{ height: 46px !important; }}
    .arrow {{ padding-top: 1.2rem; }}
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="main-title">🧠 AI News Intelligence</div>
<div class="sub-title">Real-time News Explained Clearly with AI</div>
""", unsafe_allow_html=True)

# ============================================================
# FILTER PANEL
# ============================================================
st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1.4, 2.2, 1.1])

with c1:
    st.segmented_control(
        "🌍 Region", options=["India", "World"], default="India",
        key="region_selector", on_change=perform_hard_refresh
    )
with c2:
    st.selectbox(
        "📂 Category", ["All", "Politics", "Technology", "Finance", "Sports", "Entertainment"],
        key="category_selector", on_change=perform_hard_refresh
    )
with c3:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.button("🔄 Refresh", use_container_width=True, on_click=perform_hard_refresh)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# ARTICLE FEED
# ============================================================
for article in st.session_state.articles:
    article_id = (
        article["title"]
        .replace(" ", "_")
        .replace("/", "")
        .replace(":", "")
        [:80]
    )

    summary_key = f"summary_{article_id}_{st.session_state.refresh_token}"
    context_key = f"context_{article_id}_{st.session_state.refresh_token}"
    is_open = (st.session_state.expanded_article_uid == article_id)
    clean_src = clean_source_name(article.get("source", ""))

    open_class = "news-card is-open" if is_open else "news-card"
    st.markdown(f'<div class="{open_class}">', unsafe_allow_html=True)

    # ── 🎯 DEDICATED HEADER BOX WRAPPER CONTAINER ──
    st.markdown('<div class="dedicated-card-header">', unsafe_allow_html=True)
    header_col1, header_col2 = st.columns([20, 1])

    with header_col1:
        st.markdown('<div class="title-btn">', unsafe_allow_html=True)
        # RESUME FEATURE: Triggers synchronous accordion state changes prior to page draw passes
        st.button(
            article["title"], 
            key=f"title_{article_id}", 
            use_container_width=True,
            on_click=toggle_article_accordion,
            args=(article_id,)
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with header_col2:
        st.markdown(f'<div class="arrow">{"▲" if is_open else "▼"}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) # close dedicated card header Box

    # ========================================================
    # EXPANDED CONTENT
    # ========================================================
    if is_open:
        st.markdown('<div class="article-panel">', unsafe_allow_html=True)
        st.markdown(f'<div class="source-badge">📡 {clean_src}</div>', unsafe_allow_html=True)

        cleaned_text = clean_article_text(article["summary"])
        filtered_text = filter_relevant_content(article["title"], cleaned_text)

        # ── AI SUMMARY ──
        if summary_key not in st.session_state:
            with st.spinner("Generating AI summary..."):
                st.session_state[summary_key] = generate_explanation(article["title"], filtered_text)

        st.markdown(f"""
        <div class="summary-box">
            <span class="box-label">✨ AI Summary</span>
            {st.session_state[summary_key]}
        </div>""", unsafe_allow_html=True)

        # ── INTERACTION CONTROL BUTTONS ──
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            context_clicked = st.button("🔍 More Context", key=f"context_btn_{article_id}", use_container_width=True)

        with btn_col2:
            st.markdown(f"""
            <a class="read-original-btn" href="{article["link"]}" target="_blank">
                📰 Read Original Article
            </a>""", unsafe_allow_html=True)

        # ── DEEP CONTEXT ──
        if context_clicked:
            if context_key not in st.session_state:
                with st.spinner("Generating deep context..."):
                    full_text = extract_full_article(article["link"])
                    context_source = full_text if full_text else article["summary"]
                    context_clean = filter_relevant_content(article["title"], context_source)
                    st.session_state[context_key] = generate_deep_context(article["title"], context_clean)
                st.rerun()

        if context_key in st.session_state:
            st.markdown(f"""
            <div class="context-box">
                <span class="box-label">🌍 Deep Context</span>
                {st.session_state[context_key]}
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True) # close article-panel
    st.markdown('</div>', unsafe_allow_html=True)     # close news-card

# ============================================================
# BACK TO TOP BUTTON
# ============================================================
components.html("""
<script>
(function () {
    if (window.parent.document.getElementById("scrollTopBtn")) return;
    const btn = window.parent.document.createElement("button");
    btn.id = "scrollTopBtn";
    btn.innerHTML = "↑";
    btn.style.cssText = [
        "position:fixed","bottom:24px","right:24px",
        "width:50px","height:50px","border-radius:50%",
        "border:1px solid rgba(183,166,255,0.28)",
        "background:rgba(183,166,255,0.18)",
        "backdrop-filter:blur(12px)",
        "color:white","font-size:20px","font-weight:800",
        "cursor:pointer","z-index:999999","display:none",
        "box-shadow:0 8px 24px rgba(0,0,0,0.30)"
    ].join(";");

    window.parent.document.body.appendChild(btn);
    const s = window.parent.document.querySelector('[data-testid="stAppViewContainer"]') || window.parent;
    
    s.addEventListener("scroll", () => {
        btn.style.display = s.scrollTop > 250 ? "block" : "none";
    });
    btn.addEventListener("click", () => {
        s.scrollTo({ top: 0, behavior: "smooth" });
    });
})();
</script>
""", height=0)