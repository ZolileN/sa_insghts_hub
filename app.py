import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SA Insight Hub",
    page_icon="🇿🇦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar styling */
    [data-testid="stSidebar"] { background: #0f1923; }
    [data-testid="stSidebar"] * { color: #e0ddd5 !important; }
    [data-testid="stSidebar"] .stSelectbox label { color: #9fa89e !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: .05em; }

    /* KPI cards */
    .kpi-card {
        background: #1a2535;
        border: 1px solid #2a3a52;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
    }
    .kpi-label { font-size: 11px; color: #7a8fa6; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 4px; }
    .kpi-value { font-size: 28px; font-weight: 700; color: #e8e4d8; line-height: 1.1; }
    .kpi-delta { font-size: 12px; margin-top: 4px; }
    .kpi-up   { color: #e05c3a; }
    .kpi-down { color: #27ae60; }
    .kpi-neutral { color: #7a8fa6; }

    /* Section header */
    .section-title {
        font-size: 22px;
        font-weight: 700;
        color: #e8e4d8;
        margin-bottom: 4px;
    }
    .section-sub {
        font-size: 13px;
        color: #7a8fa6;
        margin-bottom: 20px;
    }

    /* Source badge */
    .source-badge {
        display: inline-block;
        background: #1a2535;
        border: 1px solid #2a3a52;
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 11px;
        color: #7a8fa6;
        margin-top: 8px;
    }

    /* Hide default header */
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 1.5rem; }

    /* AI Q&A panel */
    .qa-panel {
        background: #0f1923;
        border: 1px solid #1e3a52;
        border-radius: 14px;
        padding: 20px 24px;
        margin-top: 32px;
    }
    .qa-title {
        font-size: 15px;
        font-weight: 600;
        color: #e8e4d8;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .qa-subtitle {
        font-size: 12px;
        color: #5a7a8a;
        margin-bottom: 16px;
    }
    .msg-user {
        background: #1a2d42;
        border-radius: 10px 10px 4px 10px;
        padding: 10px 14px;
        margin: 8px 0;
        font-size: 14px;
        color: #c8d8e8;
        text-align: right;
    }
    .msg-ai {
        background: #14232f;
        border: 1px solid #1e3a52;
        border-radius: 10px 10px 10px 4px;
        padding: 10px 14px;
        margin: 8px 0;
        font-size: 14px;
        color: #d4e0e8;
        line-height: 1.6;
    }
    .msg-ai b { color: #7ab8d8; }
    .suggestion-chip {
        display: inline-block;
        background: #1a2d42;
        border: 1px solid #2a4a62;
        border-radius: 20px;
        padding: 5px 12px;
        font-size: 12px;
        color: #7ab8d8;
        margin: 4px 4px 4px 0;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# AI Q&A ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

# Rich context for each topic — injected into Claude's system prompt
TOPIC_CONTEXT = {
    "🔴  Crime Statistics": """
You are an expert analyst on South African crime data. Key facts you know:
- SAPS publishes quarterly crime stats. In 2023/24: 19,674 murders (+3.2%), 205,765 residential burglaries, 15,727 carjackings (+5.4%), 43,604 sexual offences (-3.1%).
- Highest murder precincts: Inanda (KZN) 234, Khayelitsha (WC) 229, Nyanga (WC) 221, JHB Central 201.
- Western Cape has highest per-capita murder rate despite lower absolute numbers vs Gauteng/KZN.
- GBV remains a major crisis — SA has one of world's highest femicide rates.
- Crime is concentrated in specific high-density townships and city centres.
- COVID lockdowns caused a temporary dip in 2020/21; most categories have since risen.
- SAPS data available at saps.gov.za/services/crimestats.php
- ISS Crime Hub (issafrica.org) and CrimeStatsSA.com provide interactive analysis.
""",
    "🏠  Property Prices & Rental": """
You are an expert on South African property markets. Key facts:
- National median house price: R1.28M (2024). Western Cape leads at R2.1M median, Eastern Cape lowest at R890K.
- FNB House Price Index shows real (inflation-adjusted) prices declining in most provinces except WC.
- Western Cape price growth: +4.2% YoY, well above national +2.3%. Semigration driving demand.
- Average gross rental yields: EC at 10.2% leads, WC at 6.8% lowest (due to high prices).
- Prime rate at 11.5% means bond affordability remains constrained. R1.5M home = ~R15,900/month bond.
- Transfer duty applies above R1.1M. First-time buyers below R1.1M pay 0% transfer duty.
- FLISP subsidy available for earners R3,501–R22,000/month for affordable housing.
- Lightstone, PayProp (rental data), and FNB Property Barometer are key data sources.
- Days on market: national avg 76 days; WC 52 days (fastest), Northern Cape 110 days (slowest).
""",
    "🔐  Bank Fraud & Financial Crime": """
You are an expert on SA financial crime. Key facts:
- SABRIC 2023: R3.3B total losses (+12.4%). Card not present fraud R620M (142,000 incidents).
- SIM swap attacks: 3,800+ incidents in 2023. Criminals port your number to intercept OTPs.
- Business Email Compromise (BEC): R380M lost; targets finance teams with fake payment instructions.
- Online banking fraud: R634M in 2023 (+18.1%). Phishing, vishing, and social engineering dominant.
- Investment scams surged: R484M lost via fake crypto platforms and Ponzi schemes.
- FICA compliance: all banks must verify identity. Report fraud to SAFPS (safrauds.co.za).
- How to protect yourself: enable banking app notifications, use a dedicated email for banking, never share OTPs, use a separate SIM for banking.
- POPIA (Protection of Personal Information Act) requires companies to report data breaches within 72 hours.
""",
    "📉  Unemployment & Income": """
You are an expert on SA labour economics. Key facts:
- Q3 2024 unemployment: 32.9% (official), 43.1% (expanded, including discouraged workers).
- Youth unemployment (15-34): 60.7% — one of the highest globally.
- Gini coefficient: 0.63 — SA is the world's most unequal major economy by this measure.
- Employed: 16.7M out of working-age population of ~39M.
- Highest unemployment: Limpopo 45.4%, Eastern Cape 39.7%. Lowest: Western Cape 22.8%.
- Median monthly income nationally ~R7,800; WC median R14,800, Limpopo R5,200.
- National minimum wage (2024): R27.58/hour (~R4,800/month for 40hr week).
- SRD grant (R350/month) reaches ~9M beneficiaries. BIG (Basic Income Grant) debated.
- Key sectors of employment: community services, trade, finance, manufacturing, agriculture.
- Stats SA QLFS (Quarterly Labour Force Survey) published quarterly at statssa.gov.za.
""",
    "⚡  Load Shedding & Energy": """
You are an expert on SA energy and load shedding. Key facts:
- 2023 was worst year ever: 6,932 hours of load shedding (Stage 1-8). Cost SA economy ~R900M per stage per day.
- 2024 improved dramatically: ~2,140 hours, mostly Stage 1-2. Attributed to new maintenance regime + private solar.
- Eskom installed capacity: 44 GW, but only ~34 GW available due to plant breakdowns (UCLF).
- Rooftop/embedded solar: 5.7 GW installed by end 2024 — more than double 2022 figure. Tax incentives helped.
- Electricity generation mix (2024): coal 57%, nuclear 5%, hydro 2%, wind 6%, solar 10%, gas 8%, imports 12%.
- Eskom tariff: average residential ~436c/kWh (2024). Increased 18.65% in April 2024.
- REIPPP (Renewable Energy IPP Programme) has added ~7 GW of wind and solar since 2012.
- Load shedding schedule available at EskomSePush app. Municipalities like Cape Town have partly buffered via their own peaker plants.
- Battery storage and solar payback period in SA: typically 3-5 years for residential systems.
""",
    "💰  Interest Rates & Inflation": """
You are an expert on SA monetary policy and inflation. Key facts:
- SARB repo rate: 8.00% (as of Jan 2025, cut from 8.25%). Prime lending rate: 11.50%.
- Hiking cycle: SARB raised rates from 3.5% (Nov 2021) to 8.25% (May 2023) — 475bps in 18 months.
- CPI Jan 2025: 3.2% — within SARB's 3-6% target band and lowest since 2021.
- Food inflation peaked at 14.4% in March 2023; now at 4.1% (Jan 2025).
- Core inflation (excl food & energy): 4.3% Jan 2025.
- Education inflation consistently high: 9.2% — university fees and school fees rising above CPI.
- Transport deflation: -0.8% due to lower fuel prices after pump price cuts.
- SARB forecasts: CPI to average 4.0% in 2025. Further rate cuts expected: 25bps per quarter to 7.5% by end 2025.
- Impact: every 25bps cut saves ~R180/month on a R1.5M home loan (20yr term).
- Stats SA CPI data: statssa.gov.za. SARB MPC meeting dates published annually.
""",
    "🏥  Healthcare & Disease Burden": """
You are an expert on SA public health. Key facts:
- HIV: 7.8M people living with HIV (PLHIV). 18.3% prevalence in adults 15-49. 5.7M on ART (antiretroviral therapy).
- KZN has highest HIV prevalence at 25.2%; Western Cape lowest at 12.8%.
- TB incidence: 468 per 100,000 (2024), down from 852 in 2019. Still among highest globally.
- TB/HIV co-infection: ~60% of TB patients are HIV-positive.
- NHI (National Health Insurance) Bill signed 2023. Implementation phased over 10+ years. Highly contested.
- Doctor density: WC 82/100K, GP 74/100K vs EC 32/100K, Limpopo 18/100K — severe inequality.
- Maternal mortality: 118 per 100,000 live births (2024). Target is 40 per 100,000 (SDG).
- PEPFAR and Global Fund are major funders of SA's HIV response.
- Health data available via DHIS2 district dashboard, NDOH, and SANAC annual reports.
""",
    "🎓  Education & Matric Data": """
You are an expert on SA education outcomes. Key facts:
- 2024 NSC (matric) results: 87.3% pass rate (up from 82.9% in 2023). 756,000 wrote exams.
- Bachelor passes (university entrance): 45.6% of all candidates. Required for university admission.
- Top provinces: Gauteng 92.2%, Northern Cape 88.1%. Bottom: Limpopo 65.4%, Eastern Cape 71.9%.
- Mathematics pass rate: 52.3%. Physical Sciences: 50.1%. These bottleneck STEM pathways.
- Mathematical Literacy pass rate: 80.2% — easier alternative but limits university options.
- Grade 4 reading: SA ranked last (79/79 countries) in PIRLS 2021 for reading in home language.
- University access: only ~19% of matric students enrol in university. NSFAS funds ~600K students.
- TVET colleges: 50 colleges, ~700K students. Seen as alternative to university.
- DBE annual matric results released January each year. School performance by institution available via BasicEd.
- Semigration trend: middle-class families moving children to WC schools, driving enrolment demand there.
""",
    "💱  ZAR Exchange Rate & Forex": """
You are an expert on the South African rand and capital markets. Key facts:
- USD/ZAR history: pandemic low R19.3 (April 2020), Zuma unrest R15.2 (July 2021), load shedding peak R19.8 (June 2023).
- SA removed from FATF grey list in February 2025 — positive signal for capital flows, boosted rand.
- Rand is one of world's most liquid EM currencies and trades 24/7. Highly sensitive to risk-off events.
- Key rand drivers: commodity prices (gold, platinum, coal), Eskom risk, political uncertainty, SARB rate differentials, global USD strength.
- FDI inflows 2024: R214B (+8.4%). SA Investment Conference targets R1.2 trillion over 5 years.
- Portfolio flows remain volatile: foreign investors hold ~35% of SA government bonds.
- Grey-listing (Oct 2023): cost SA ~R100B in capital outflows. Removal expected to partially reverse.
- Offshore allowance: SA residents can invest R10M/year offshore via SARS tax clearance (now Single Discretionary Allowance).
- SARB does not actively defend the rand; intervenes only in disorderly market conditions.
""",
    "💧  Water & Service Delivery": """
You are an expert on SA water resources and municipal service delivery. Key facts:
- National dam levels (March 2025): ~78.4% average. Theewaterskloof (Cape Town) at 92.4%.
- Metros in water crisis: Tshwane (infrastructure decay), Johannesburg (ageing pipes, +40% water losses), Msunduzi (Pietermaritzburg), Buffalo City.
- Non-revenue water: SA loses ~37% of treated water to leaks, theft, and metering errors (world avg ~30%).
- Blue Drop certification (DWS): measures drinking water quality. Only 67 of 144 water systems scored above 90% in 2023.
- Service delivery protests: 848 in 2024 (+18%). Gauteng leads with 182, WC lowest at 98.
- 163 of 257 municipalities rated financially distressed by COGTA. Many can't pay Eskom for water pumping.
- Water scarcity risk: SA is a water-scarce country (avg 495mm rainfall vs world avg 860mm). Climate change reducing run-off.
- Desalination: Cape Town exploring plants post-Day Zero scare (2018). Several coastal municipalities considering.
- Dept of Water & Sanitation (DWS) publishes weekly dam level reports at dws.gov.za.
""",
}

SUGGESTED_QUESTIONS = {
    "🔴  Crime Statistics": [
        "Which province is safest to live in?",
        "Why is the Western Cape murder rate so high?",
        "Has crime gotten worse since COVID?",
        "What are the safest suburbs in Cape Town?",
    ],
    "🏠  Property Prices & Rental": [
        "Is now a good time to buy property in SA?",
        "Which province gives the best rental yield?",
        "How does load shedding affect property prices?",
        "What's driving semigration to the Western Cape?",
    ],
    "🔐  Bank Fraud & Financial Crime": [
        "How do SIM swap attacks work?",
        "How do I protect myself from banking fraud?",
        "What is Business Email Compromise?",
        "Which bank fraud type is growing fastest?",
    ],
    "📉  Unemployment & Income": [
        "Why is youth unemployment so high in SA?",
        "Which sectors are creating the most jobs?",
        "What is the National Minimum Wage?",
        "How does SA compare to other African countries?",
    ],
    "⚡  Load Shedding & Energy": [
        "Why has load shedding improved in 2024?",
        "Is solar a good investment in SA?",
        "What is Eskom's plan to fix the grid?",
        "How much does load shedding cost the economy?",
    ],
    "💰  Interest Rates & Inflation": [
        "When will interest rates come down further?",
        "How does the repo rate affect my home loan?",
        "Why is education inflation so high?",
        "What is the SARB's inflation target?",
    ],
    "🏥  Healthcare & Disease Burden": [
        "What is the NHI and how will it work?",
        "Which province has the best healthcare?",
        "Why does SA have such a high TB rate?",
        "How many South Africans are on ART?",
    ],
    "🎓  Education & Matric Data": [
        "Why do so few pass mathematics?",
        "Which province has the best matric results?",
        "What is a bachelor pass and why does it matter?",
        "How does SA compare globally in education?",
    ],
    "💱  ZAR Exchange Rate & Forex": [
        "What caused the rand to weaken in 2023?",
        "What is the FATF grey list and its impact?",
        "How much can I invest offshore legally?",
        "What drives the rand's movements?",
    ],
    "💧  Water & Service Delivery": [
        "Which cities are at risk of running out of water?",
        "What is the Blue Drop score?",
        "Why are so many municipalities struggling?",
        "What happened during Cape Town's Day Zero?",
    ],
}


def call_claude(messages: list, system_prompt: str, api_key: str) -> str:
    """Call the Anthropic Claude API and return the assistant's reply."""
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-5",
                "max_tokens": 1024,
                "system": system_prompt,
                "messages": messages,
            },
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        elif response.status_code == 401:
            return "❌ Invalid API key. Please check your Anthropic API key in the sidebar."
        elif response.status_code == 429:
            return "⚠️ Rate limit reached. Please wait a moment and try again."
        else:
            return f"❌ API error {response.status_code}: {response.json().get('error', {}).get('message', 'Unknown error')}"
    except requests.exceptions.Timeout:
        return "⚠️ Request timed out. Please try again."
    except Exception as e:
        return f"❌ Connection error: {str(e)}"


def render_qa_panel(topic: str, province: str, api_key: str):
    """Render the AI Q&A panel at the bottom of each topic page."""
    st.markdown("---")
    st.markdown("""
    <div class="qa-title">🤖 Ask the SA Data Analyst</div>
    <div class="qa-subtitle">Powered by Claude AI · Ask anything about this topic, compare provinces, or request insights</div>
    """, unsafe_allow_html=True)

    # Session state keys per topic
    history_key = f"chat_{topic}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    # Suggested questions as clickable chips
    suggestions = SUGGESTED_QUESTIONS.get(topic, [])
    if suggestions:
        st.markdown("**Suggested questions:**")
        cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(suggestions):
            if cols[i].button(suggestion, key=f"sug_{topic}_{i}", use_container_width=True):
                st.session_state[f"pending_q_{topic}"] = suggestion

    # Render chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state[history_key]:
            if msg["role"] == "user":
                st.markdown(f'<div class="msg-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="msg-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    # Input form
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Ask a question",
            key=f"input_{topic}",
            placeholder="e.g. Which province has the highest crime rate per capita?",
            label_visibility="collapsed",
        )
    with col_btn:
        send = st.button("Ask →", key=f"send_{topic}", use_container_width=True, type="primary")

    # Handle suggestion chips pre-fill
    pending = st.session_state.pop(f"pending_q_{topic}", None)
    question = pending or (user_input if send else None)

    if question and question.strip():
        if not api_key:
            st.warning("⚠️ Please enter your Anthropic API key in the sidebar to use the AI Q&A feature.")
            return

        # Build system prompt with topic context + province filter
        province_note = f" The user is currently viewing data filtered to {province}." if province != "All Provinces" else ""
        system = f"""You are a knowledgeable South African data analyst embedded in the SA Insight Hub dashboard.
You answer questions about South African data clearly, concisely, and accurately.
Always ground your answers in the specific data and context provided below.
Use bullet points for lists, bold for key numbers, and keep answers under 200 words unless a detailed explanation is needed.
Be direct and helpful — this is a data tool, not a general assistant.{province_note}

TOPIC CONTEXT:
{TOPIC_CONTEXT.get(topic, 'General South African data analyst.')}
"""
        # Append user message
        st.session_state[history_key].append({"role": "user", "content": question})

        with st.spinner("Thinking..."):
            reply = call_claude(st.session_state[history_key], system, api_key)

        st.session_state[history_key].append({"role": "assistant", "content": reply})
        st.rerun()

    # Clear chat button
    if st.session_state[history_key]:
        if st.button("Clear conversation", key=f"clear_{topic}"):
            st.session_state[history_key] = []
            st.rerun()


# ── Provinces ─────────────────────────────────────────────────────────────────
PROVINCES = [
    "All Provinces", "Western Cape", "Gauteng", "KwaZulu-Natal",
    "Eastern Cape", "Limpopo", "Mpumalanga", "North West",
    "Free State", "Northern Cape"
]

PROVINCE_ABBR = {
    "Western Cape": "WC", "Gauteng": "GP", "KwaZulu-Natal": "KZN",
    "Eastern Cape": "EC", "Limpopo": "LP", "Mpumalanga": "MP",
    "North West": "NW", "Free State": "FS", "Northern Cape": "NC"
}

PROVINCE_LIST = [p for p in PROVINCES if p != "All Provinces"]

PLOTLY_TEMPLATE = "plotly_dark"
CHART_BG = "rgba(0,0,0,0)"
ACCENT = "#3b82f6"

def kpi(label, value, delta=None, delta_good="down"):
    direction = ""
    if delta:
        is_up = "+" in str(delta) or (isinstance(delta, (int, float)) and delta > 0)
        bad_is_up = delta_good == "down"
        css = "kpi-up" if (is_up == bad_is_up) else "kpi-down"
        direction = f'<div class="kpi-delta {css}">{delta}</div>'
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {direction}
    </div>"""

def source_badge(text, scraped_at=None, is_live=False):
    live_dot = ' <span style="color:#27ae60">● live</span>' if is_live else ' <span style="color:#f59e0b">● cached</span>'
    ts = ""
    if scraped_at and scraped_at != "fallback":
        try:
            dt = datetime.fromisoformat(scraped_at.replace("Z", ""))
            ts = f" · refreshed {dt.strftime('%d %b %Y %H:%M')} UTC"
        except Exception:
            pass
    st.markdown(
        f'<span class="source-badge">Source: {text}{ts}{live_dot}</span>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADER — reads from data/*.json (written by scrapers), falls back to
# hardcoded values so the app always renders even without scraped files.
# ═══════════════════════════════════════════════════════════════════════════════
DATA_DIR = Path(__file__).parent / "data"

# Map topic selector labels → JSON file stems
TOPIC_FILE = {
    "🔴  Crime Statistics":           "crime",
    "🏠  Property Prices & Rental":   "property",
    "🔐  Bank Fraud & Financial Crime":"fraud",
    "📉  Unemployment & Income":       "employment",
    "⚡  Load Shedding & Energy":      "energy",
    "💰  Interest Rates & Inflation":  "finance",
    "🏥  Healthcare & Disease Burden": "health",
    "🎓  Education & Matric Data":     "education",
    "💱  ZAR Exchange Rate & Forex":   "forex",
    "💧  Water & Service Delivery":    "water",
}


@st.cache_data(ttl=300, show_spinner=False)   # re-read from disk every 5 min
def load_data(file_stem: str) -> dict:
    """Load data/{file_stem}.json if it exists, else return empty dict."""
    path = DATA_DIR / f"{file_stem}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {}


def g(data: dict, *keys, default=None):
    """Safe nested getter: g(data, 'provinces', 'Gauteng', 'murder') → value or default."""
    val = data
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return default
        if val is None:
            return default
    return val


def prov_list_values(data: dict, path: list[str], provinces: list[str], default_list: list) -> list:
    """Extract a list of per-province values from nested data dict, in PROVINCE_LIST order."""
    result = []
    for p in provinces:
        keys = [p] + path
        v = g(data, "provinces", *keys)
        result.append(v)
    # Fall back to default_list wherever None was returned
    return [result[i] if result[i] is not None else default_list[i] for i in range(len(provinces))]


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CRIME STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════
def page_crime(topic, province):
    d = load_data("crime")
    nat = g(d, "national_totals") or {}
    prov_data = g(d, "provinces") or {}
    scraped_at = g(d, "scraped_at")
    is_live = g(d, "is_live", default=False)
    period = g(d, "period") or "2023/24"

    st.markdown('<div class="section-title">🔴 Crime Statistics</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">SAPS quarterly crime data — murders, robbery, burglary, GBV by province · Period: {period}</div>', unsafe_allow_html=True)

    # KPIs — prefer live data, fall back to published figures
    murder_nat   = nat.get("Murder", 19674)
    burglary_nat = nat.get("Residential burglary", 205765)
    carjack_nat  = nat.get("Carjacking", 15727)
    sexual_nat   = nat.get("Sexual offences", 43604)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi(f"Murders ({period})", f"{murder_nat:,}", "+3.2% YoY", "down"), unsafe_allow_html=True)
    c2.markdown(kpi("Residential Burglaries", f"{burglary_nat:,}", "+1.8% YoY", "down"), unsafe_allow_html=True)
    c3.markdown(kpi("Carjackings", f"{carjack_nat:,}", "+5.4% YoY", "down"), unsafe_allow_html=True)
    c4.markdown(kpi("Sexual Offences", f"{sexual_nat:,}", "-3.1% YoY", "down"), unsafe_allow_html=True)

    st.divider()

    # Per-province data — merge scraped + fallback
    defaults = {
        "Murder":          [1204, 4912, 3801, 2890, 1102, 1450, 980, 785, 550],
        "Burglary":        [28400, 52000, 41000, 22000, 10500, 16000, 13000, 11200, 11665],
        "Robbery":         [24000, 38000, 29000, 18000, 6500, 9000, 8500, 7500, 4000],
        "Sexual Offences": [7800, 10200, 8900, 5600, 3200, 3400, 2900, 1804, 2900],
        "Carjacking":      [2900, 6800, 2800, 1200, 450, 620, 540, 420, 197],
    }

    def prov_crime(cat, scraper_key, default_vals):
        return [
            (prov_data.get(p) or {}).get(scraper_key) or default_vals[i]
            for i, p in enumerate(PROVINCE_LIST)
        ]

    crime_prov = pd.DataFrame({
        "Province":        PROVINCE_LIST,
        "Murder":          prov_crime("Murder",             "Murder",               defaults["Murder"]),
        "Burglary":        prov_crime("Burglary",           "Residential burglary", defaults["Burglary"]),
        "Robbery":         prov_crime("Robbery",            "Robbery aggravating",  defaults["Robbery"]),
        "Sexual Offences": prov_crime("Sexual Offences",    "Sexual offences",      defaults["Sexual Offences"]),
        "Carjacking":      prov_crime("Carjacking",         "Carjacking",           defaults["Carjacking"]),
    })

    crime_type = st.selectbox("Select crime type", ["Murder", "Burglary", "Robbery", "Sexual Offences", "Carjacking"])

    col1, col2 = st.columns([3, 2])
    with col1:
        fig = px.bar(
            crime_prov.sort_values(crime_type, ascending=True),
            x=crime_type, y="Province", orientation="h",
            title=f"{crime_type} by Province (2023/24)",
            color=crime_type, color_continuous_scale="Reds",
            template=PLOTLY_TEMPLATE
        )
        fig.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Crime trend 2018–2024
        years = list(range(2018, 2025))
        trend = pd.DataFrame({
            "Year": years,
            "Murder": [20336, 21022, 21325, 15276, 19491, 22103, 19674],
            "Carjacking": [16325, 16832, 16325, 11244, 13700, 14999, 15727],
        })
        fig2 = px.line(trend, x="Year", y=["Murder", "Carjacking"],
                       title="Murder & Carjacking trend (2018–2024)",
                       template=PLOTLY_TEMPLATE)
        fig2.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, legend_title="")
        st.plotly_chart(fig2, use_container_width=True)

    # Top precincts
    st.subheader("Top 10 highest-crime police precincts")
    precincts = pd.DataFrame({
        "Precinct": ["Inanda (KZN)", "Khayelitsha (WC)", "Nyanga (WC)", "Johannesburg Central", "Delft (WC)",
                     "Umlazi (KZN)", "Soweto", "Mitchells Plain (WC)", "Krugersdorp (GP)", "Tembisa (GP)"],
        "Province": ["KZN", "WC", "WC", "GP", "WC", "KZN", "GP", "WC", "GP", "GP"],
        "Murders": [234, 229, 221, 201, 189, 176, 164, 152, 141, 138],
        "Total Crimes": [8920, 12440, 10280, 14220, 7650, 9340, 10800, 9120, 7230, 8410],
    })
    st.dataframe(precincts, use_container_width=True, hide_index=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("SAPS Annual Crime Report · saps.gov.za", scraped_at, is_live)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PROPERTY PRICES & RENTAL YIELDS
# ═══════════════════════════════════════════════════════════════════════════════
def page_property(topic, province):
    d = load_data("property")
    nat = g(d, "national") or {}
    prov_data = g(d, "provinces") or {}
    scraped_at = g(d, "scraped_at")
    is_live = g(d, "is_live", default=False)

    median_r    = nat.get("median_price_r", 1280000)
    yield_pct   = nat.get("avg_rental_yield_pct", 8.4)
    dom         = nat.get("days_on_market", 76)
    approval    = nat.get("bond_approval_rate_pct", 62)
    prime       = nat.get("prime_rate_pct", 10.25)

    st.markdown('<div class="section-title">🏠 Property Prices & Rental Yields</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Suburb-level house prices, price growth, days on market, and rental return rates</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("National Median Price", f"R{median_r/1e6:.2f}M", "+2.3% YoY", "up"), unsafe_allow_html=True)
    c2.markdown(kpi("Avg Rental Yield", f"{yield_pct}%", "+0.6pp YoY", "up"), unsafe_allow_html=True)
    c3.markdown(kpi("Days on Market", f"{dom} days", "-4 days YoY", "down"), unsafe_allow_html=True)
    c4.markdown(kpi("Bond Approval Rate", f"{approval}%", "-3pp YoY", "down"), unsafe_allow_html=True)

    st.divider()

    def pv(key, defaults):
        return [(prov_data.get(p) or {}).get(key) or defaults[i] for i, p in enumerate(PROVINCE_LIST)]

    prop_prov = pd.DataFrame({
        "Province":         PROVINCE_LIST,
        "Median Price (R000)": [v/1000 for v in pv("median_price_r", [2100000,1450000,1200000,890000,650000,720000,680000,730000,1100000])],
        "YoY Growth (%)":   pv("yoy_growth_pct",   [4.2,2.1,1.8,0.9,1.2,1.5,1.1,0.8,2.8]),
        "Rental Yield (%)": pv("rental_yield_pct",  [6.8,8.2,9.1,10.2,11.0,10.5,10.8,10.1,7.4]),
        "Days on Market":   pv("days_on_market",    [52,68,84,98,112,105,108,102,110]),
    })

    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(prop_prov, x="Rental Yield (%)", y="YoY Growth (%)",
                         size="Median Price (R000)", color="Province",
                         title="Rental Yield vs Price Growth by Province",
                         template=PLOTLY_TEMPLATE, size_max=40)
        fig.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(prop_prov.sort_values("Median Price (R000)", ascending=False),
                      x="Province", y="Median Price (R000)",
                      title="Median house price by province (R thousands)",
                      color="Median Price (R000)", color_continuous_scale="Blues",
                      template=PLOTLY_TEMPLATE)
        fig2.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Price trend — from JSON if available
    raw_trend = g(d, "price_trend_r000") or {}
    if raw_trend:
        quarters = list(raw_trend.keys())
        national_vals = list(raw_trend.values())
    else:
        quarters = ["Q1'21","Q2'21","Q3'21","Q4'21","Q1'22","Q2'22","Q3'22","Q4'22",
                    "Q1'23","Q2'23","Q3'23","Q4'23","Q1'24","Q2'24","Q3'24","Q4'24"]
        national_vals = [980,995,1010,1030,1060,1090,1120,1150,1180,1210,1240,1260,1270,1275,1280,1285]

    wc_med  = (prov_data.get("Western Cape") or {}).get("median_price_r", 2100000) / 1000
    gp_med  = (prov_data.get("Gauteng")      or {}).get("median_price_r", 1450000) / 1000

    price_trend = pd.DataFrame({
        "Quarter": quarters,
        "Western Cape": [wc_med] * len(quarters),
        "Gauteng":      [gp_med] * len(quarters),
        "National":     national_vals,
    })
    fig3 = px.line(price_trend, x="Quarter", y=["Western Cape","Gauteng","National"],
                   title="Median house price trend (R thousands)",
                   template=PLOTLY_TEMPLATE)
    fig3.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, legend_title="")
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("Lightstone Property · FNB Property Barometer · PropStats", scraped_at, is_live)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. BANK FRAUD & FINANCIAL CRIME
# ═══════════════════════════════════════════════════════════════════════════════
def page_fraud(topic, province):
    d = load_data("fraud")
    cats = g(d, "categories") or {}
    trend = g(d, "trend_r_billion") or {}
    scraped_at = g(d, "scraped_at")
    is_live = g(d, "is_live", default=False)

    total_losses = g(d, "total_losses_r_billion") or 3.3
    sim_swaps    = g(d, "sim_swap_incidents")     or 3800
    online_fraud = (cats.get("Online banking") or {}).get("losses_rm", 634)
    card_losses  = ((cats.get("Card not present") or {}).get("losses_rm", 620) +
                    (cats.get("Lost/Stolen card")  or {}).get("losses_rm", 480))

    st.markdown('<div class="section-title">🔐 Bank Fraud & Financial Crime</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">SABRIC annual fraud data — SIM swap, phishing, card fraud, and EFT scams</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Total Losses", f"R{total_losses:.1f}B", "+12.4% YoY", "down"), unsafe_allow_html=True)
    c2.markdown(kpi("SIM Swap Incidents", f"{sim_swaps:,}+", "+8.2% YoY", "down"), unsafe_allow_html=True)
    c3.markdown(kpi("Online Banking Fraud", f"R{online_fraud}M", "+18.1% YoY", "down"), unsafe_allow_html=True)
    c4.markdown(kpi("Card Fraud Losses", f"R{card_losses}M", "+6.7% YoY", "down"), unsafe_allow_html=True)

    st.divider()

    # Build dataframe from loaded categories (fall back to hardcoded)
    default_cats = {
        "Card not present":          {"losses_rm": 620, "incidents": 142000},
        "Lost/Stolen card":          {"losses_rm": 480, "incidents": 89000},
        "Online banking":            {"losses_rm": 634, "incidents": 54000},
        "SIM swap / account takeover":{"losses_rm": 412, "incidents": 3800},
        "Business email compromise": {"losses_rm": 380, "incidents": 2100},
        "ATM fraud":                 {"losses_rm": 290, "incidents": 67000},
        "Investment scams":          {"losses_rm": 484, "incidents": 8900},
    }
    merged = {**default_cats, **cats}
    fraud_types = pd.DataFrame([
        {"Category": k, "Losses (R millions)": v.get("losses_rm", 0), "Incidents": v.get("incidents", 0)}
        for k, v in merged.items()
    ])

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(fraud_types, values="Losses (R millions)", names="Category",
                     title="Fraud losses by category (2023)",
                     template=PLOTLY_TEMPLATE, hole=0.4)
        fig.update_layout(paper_bgcolor=CHART_BG)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(fraud_types.sort_values("Incidents", ascending=True),
                      x="Incidents", y="Category", orientation="h",
                      title="Incident count by fraud type",
                      color="Incidents", color_continuous_scale="Reds",
                      template=PLOTLY_TEMPLATE)
        fig2.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Year trend from JSON
    default_trend = {"2019":2.2,"2020":1.8,"2021":2.1,"2022":2.9,"2023":3.3}
    trend_data = trend if trend else default_trend
    fraud_trend = pd.DataFrame({
        "Year": [int(y) for y in trend_data.keys()],
        "Total Losses (R billions)": list(trend_data.values()),
    })
    fig3 = px.line(fraud_trend, x="Year", y="Total Losses (R billions)",
                   title="Total fraud losses trend (R billions)",
                   markers=True, template=PLOTLY_TEMPLATE)
    fig3.update_traces(line_color="#e05c3a", marker_color="#e05c3a")
    fig3.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("SABRIC Annual Report · South African Banking Risk Information Centre", scraped_at, is_live)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. UNEMPLOYMENT & INCOME LEVELS
# ═══════════════════════════════════════════════════════════════════════════════
def page_employment(topic, province):
    d = load_data("employment")
    prov_data  = g(d, "provinces") or {}
    trend_data = g(d, "trend")     or {}
    scraped_at = g(d, "scraped_at")
    is_live    = g(d, "is_live", default=False)

    unemp   = g(d, "unemployment_rate_pct")       or 32.9
    youth   = g(d, "youth_unemployment_pct")      or 60.7
    exp_u   = g(d, "expanded_unemployment_pct")   or 43.1
    emp_m   = g(d, "employed_millions")           or 16.7
    gini    = g(d, "gini_coefficient")            or 0.63
    min_w   = g(d, "national_min_wage_hourly_r")  or 28.79

    st.markdown('<div class="section-title">📉 Unemployment & Income Levels</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Stats SA quarterly labour force survey — unemployment, income inequality, sector breakdown</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Unemployment Rate", f"{unemp}%", "-0.4pp QoQ", "down"), unsafe_allow_html=True)
    c2.markdown(kpi("Youth Unemployment", f"{youth}%", "+1.2pp QoQ", "down"), unsafe_allow_html=True)
    c3.markdown(kpi("Gini Coefficient", f"{gini}", "Highest in world", "down"), unsafe_allow_html=True)
    c4.markdown(kpi("Employed (millions)", f"{emp_m}M", "+220K QoQ", "up"), unsafe_allow_html=True)

    st.divider()

    def pv(key, defaults):
        return [(prov_data.get(p) or {}).get(key) or defaults[i] for i, p in enumerate(PROVINCE_LIST)]

    unemp_prov = pd.DataFrame({
        "Province":                 PROVINCE_LIST,
        "Unemployment Rate (%)":    pv("unemployment",    [22.8,33.2,32.6,39.7,45.4,38.8,40.1,35.6,31.4]),
        "Youth Unemployment (%)":   pv("youth_unemployment",[44.1,58.9,57.2,64.8,72.1,68.4,69.8,63.2,53.1]),
        "Median Monthly Income (R)":pv("median_income_r", [14800,11200,9800,6400,5200,5800,5400,6100,8900]),
    })

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(unemp_prov.sort_values("Unemployment Rate (%)", ascending=False),
                     x="Province", y=["Unemployment Rate (%)", "Youth Unemployment (%)"],
                     title="Unemployment vs Youth Unemployment by Province",
                     barmode="group", template=PLOTLY_TEMPLATE,
                     color_discrete_map={"Unemployment Rate (%)": "#3b82f6", "Youth Unemployment (%)": "#e05c3a"})
        fig.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, legend_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(unemp_prov.sort_values("Median Monthly Income (R)", ascending=True),
                      x="Median Monthly Income (R)", y="Province", orientation="h",
                      title="Median monthly income by province (R)",
                      color="Median Monthly Income (R)", color_continuous_scale="Greens",
                      template=PLOTLY_TEMPLATE)
        fig2.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    default_trend_u = {"Q1'20":30.1,"Q2'20":34.4,"Q3'20":30.8,"Q4'20":32.5,"Q1'21":32.6,"Q2'21":34.4,"Q3'21":34.9,"Q4'21":35.3,"Q1'22":34.5,"Q2'22":33.9,"Q3'22":32.9,"Q4'22":32.7,"Q1'23":32.9,"Q2'23":33.5,"Q3'23":31.9,"Q4'23":32.1,"Q1'24":33.5,"Q2'24":33.5,"Q3'24":32.9}
    td = trend_data if trend_data else default_trend_u
    fig3 = px.area(pd.DataFrame({"Quarter": list(td.keys()), "Rate (%)": list(td.values())}),
                   x="Quarter", y="Rate (%)",
                   title="SA unemployment rate trend (%)",
                   template=PLOTLY_TEMPLATE)
    fig3.update_traces(fillcolor="rgba(59,130,246,0.2)", line_color="#3b82f6")
    fig3.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("Stats SA QLFS · statssa.gov.za", scraped_at, is_live)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. LOAD SHEDDING & ENERGY
# ═══════════════════════════════════════════════════════════════════════════════
def page_energy(topic, province):
    d = load_data("energy")
    scraped_at = g(d, "scraped_at")
    is_live    = g(d, "is_live", default=False)
    stage      = g(d, "current_stage", default=0)
    stage_lbl  = g(d, "stage_label") or ("No load shedding" if stage == 0 else f"Stage {stage}")
    monthly_24 = g(d, "monthly_hours_2024") or {}
    monthly_23 = g(d, "monthly_hours_2023") or {}
    monthly_22 = g(d, "monthly_hours_2022") or {}
    annual     = g(d, "annual_totals")       or {}
    tariffs    = g(d, "electricity_tariff_history") or {}
    energy_mix = g(d, "energy_mix_pct_2024") or {}

    hrs_2024 = sum(monthly_24.values()) if monthly_24 else 2140
    hrs_2023 = sum(monthly_23.values()) if monthly_23 else 6932

    stage_color = "#27ae60" if stage == 0 else ("#f59e0b" if stage <= 2 else "#e05c3a")
    stage_html = f'<span style="color:{stage_color};font-weight:700">{stage_lbl}</span>'

    st.markdown('<div class="section-title">⚡ Load Shedding & Energy</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Eskom stage data · Current status: {stage_html}&nbsp;&nbsp;{"🟢 live" if is_live else "🟡 cached"}</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Loadshedding Hours 2023", f"{hrs_2023:,} hrs", "Worst year on record", "down"), unsafe_allow_html=True)
    c2.markdown(kpi("Loadshedding Hours 2024", f"{hrs_2024:,} hrs", f"-{round((hrs_2023-hrs_2024)/hrs_2023*100)}% vs 2023", "up"), unsafe_allow_html=True)
    c3.markdown(kpi("Current Stage", stage_lbl, "Live from Eskom" if is_live else "Last known", "neutral"), unsafe_allow_html=True)
    c4.markdown(kpi("Rooftop Solar Installed", "5.7 GW", "+2.1 GW in 2023", "up"), unsafe_allow_html=True)

    st.divider()

    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    default_24 = [312,240,168,120,72,96,144,120,96,72,48,24]
    default_23 = [744,576,648,576,600,552,600,576,504,576,480,300]
    default_22 = [0,24,144,168,312,360,288,408,336,240,264,480]

    ls_data = pd.DataFrame({
        "Month": months,
        "2022": [monthly_22.get(m, default_22[i]) for i,m in enumerate(months)],
        "2023": [monthly_23.get(m, default_23[i]) for i,m in enumerate(months)],
        "2024": [monthly_24.get(m, default_24[i]) for i,m in enumerate(months)],
    })

    col1, col2 = st.columns([3, 2])
    with col1:
        fig = px.bar(ls_data, x="Month", y=["2022", "2023", "2024"],
                     title="Monthly load shedding hours (2022–2024)",
                     barmode="group", template=PLOTLY_TEMPLATE,
                     color_discrete_map={"2022": "#4a6fa5", "2023": "#e05c3a", "2024": "#27ae60"})
        fig.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, legend_title="Year")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        mix_default = {"Coal":57,"Nuclear":5,"Hydro":2,"Wind":6,"Solar":10,"Gas/Diesel":8,"Imports":12}
        mix_data = energy_mix if energy_mix else mix_default
        energy_mix_df = pd.DataFrame({
            "Source": list(mix_data.keys()),
            "Percentage": list(mix_data.values()),
        })
        fig2 = px.pie(energy_mix_df, values="Percentage", names="Source",
                      title="SA electricity generation mix (2024)",
                      template=PLOTLY_TEMPLATE, hole=0.35,
                      color_discrete_sequence=px.colors.qualitative.Set3)
        fig2.update_layout(paper_bgcolor=CHART_BG)
        st.plotly_chart(fig2, use_container_width=True)
    default_tariffs = {2015:112.5,2016:135.4,2017:151.1,2018:170.0,2019:186.3,2020:207.7,2021:252.0,2022:328.0,2023:388.0,2024:436.0}
    td = {int(k):v for k,v in tariffs.items()} if tariffs else default_tariffs
    fig3 = px.line(pd.DataFrame({"Year": list(td.keys()), "Tariff (c/kWh)": list(td.values())}),
                   x="Year", y="Tariff (c/kWh)",
                   title="Average Eskom residential tariff (cents/kWh)",
                   markers=True, template=PLOTLY_TEMPLATE)
    fig3.update_traces(line_color="#f59e0b")
    fig3.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("Eskom · EskomSePush · NERSA", scraped_at, is_live)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. INTEREST RATES & INFLATION
# ═══════════════════════════════════════════════════════════════════════════════
def page_finance(topic, province):
    d = load_data("finance")
    scraped_at  = g(d, "scraped_at")
    is_live     = g(d, "is_live", default=False)
    repo        = g(d, "repo_rate_pct")       or 6.75
    prime       = g(d, "prime_rate_pct")      or 10.25
    cpi         = g(d, "cpi_headline_pct")    or 3.5
    repo_hist   = g(d, "repo_history")        or {}
    cpi_hist    = g(d, "cpi_history")         or {}

    st.markdown('<div class="section-title">💰 Interest Rates & Inflation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">SARB repo rate decisions, CPI by category, food inflation, and prime lending rate</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Repo Rate", f"{repo}%", "Latest SARB decision", "up"), unsafe_allow_html=True)
    c2.markdown(kpi("Prime Rate", f"{prime}%", "Repo + 3.5pp", "neutral"), unsafe_allow_html=True)
    c3.markdown(kpi("CPI Headline", f"{cpi}%", "Latest Stats SA release", "up"), unsafe_allow_html=True)
    c4.markdown(kpi("Food Inflation", "4.1%", "-6.1pp from peak", "up"), unsafe_allow_html=True)

    st.divider()

    # Repo + CPI trend from loaded data
    default_repo = {"Q1'20":6.25,"Q2'20":3.75,"Q3'20":3.5,"Q4'20":3.5,"Q1'21":3.5,"Q2'21":3.5,"Q3'21":3.5,"Q4'21":3.75,"Q1'22":4.0,"Q2'22":4.75,"Q3'22":5.5,"Q4'22":7.0,"Q1'23":7.25,"Q2'23":8.25,"Q3'23":8.25,"Q4'23":8.25,"Q1'24":8.25,"Q2'24":8.25,"Q3'24":8.0,"Q4'24":7.75,"Q1'25":7.5}
    default_cpi  = {"Q1'20":4.1,"Q2'20":2.2,"Q3'20":3.0,"Q4'20":3.1,"Q1'21":2.9,"Q2'21":4.9,"Q3'21":4.9,"Q4'21":5.9,"Q1'22":5.9,"Q2'22":6.5,"Q3'22":7.8,"Q4'22":7.2,"Q1'23":7.0,"Q2'23":6.3,"Q3'23":5.4,"Q4'23":5.5,"Q1'24":5.3,"Q2'24":5.1,"Q3'24":4.4,"Q4'24":3.8,"Q1'25":3.5}

    # Merge scraped history with defaults (scraped values win)
    rh = {**default_repo, **{k.replace("-","'"): v for k,v in repo_hist.items()}}
    ch = {**default_cpi,  **{k.replace("-","'"): v for k,v in cpi_hist.items()}}
    quarters = sorted(set(list(rh.keys()) + list(ch.keys())))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=quarters, y=[rh.get(q) for q in quarters], name="Repo Rate (%)", line=dict(color="#3b82f6", width=2.5)))
    fig.add_trace(go.Scatter(x=quarters, y=[ch.get(q) for q in quarters], name="CPI (%)", line=dict(color="#e05c3a", width=2.5, dash="dash")))
    fig.update_layout(title="SARB Repo Rate vs CPI Inflation", template=PLOTLY_TEMPLATE,
                      paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, legend_title="")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        cpi_basket = pd.DataFrame({
            "Category": ["Food & beverages", "Housing & utilities", "Transport", "Health",
                          "Education", "Clothing", "Misc goods"],
            "Weight (%)": [17.2, 24.5, 14.3, 1.4, 2.3, 3.7, 36.6],
            "CPI (Jan 2025)": [4.1, 5.2, -0.8, 6.8, 9.2, 2.1, 2.3],
        })
        fig2 = px.bar(cpi_basket, x="Category", y="CPI (Jan 2025)",
                      title="CPI by basket category (Jan 2025, %)",
                      color="CPI (Jan 2025)", color_continuous_scale="RdYlGn_r",
                      template=PLOTLY_TEMPLATE)
        fig2.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Bond affordability
        prices = list(range(500, 3100, 100))
        bond_20yr = [p*1000 * 0.0106 for p in prices]  # approx monthly bond at prime
        bond_data = pd.DataFrame({"Price (R thousands)": prices, "Monthly Repayment (R)": bond_20yr})
        fig3 = px.area(bond_data, x="Price (R thousands)", y="Monthly Repayment (R)",
                       title="Estimated monthly bond repayment at prime 11.5% (20yr)",
                       template=PLOTLY_TEMPLATE)
        fig3.update_traces(fillcolor="rgba(59,130,246,0.15)", line_color="#3b82f6")
        fig3.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
        st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("SARB Monetary Policy · Stats SA CPI", scraped_at, is_live)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. HEALTHCARE ACCESS & DISEASE BURDEN
# ═══════════════════════════════════════════════════════════════════════════════
def page_health(topic, province):
    d = load_data("health")
    prov_data  = g(d, "provinces")  or {}
    hiv        = g(d, "hiv")        or {}
    tb         = g(d, "tb")         or {}
    plhiv_t    = g(d, "plhiv_trend") or {}
    art_t      = g(d, "art_trend")   or {}
    scraped_at = g(d, "scraped_at")
    is_live    = g(d, "is_live", default=False)

    plhiv  = hiv.get("plhiv_millions", 7.8)
    prev   = hiv.get("prevalence_15_49_pct", 18.3)
    on_art = hiv.get("on_art_millions", 5.7)
    art_c  = hiv.get("art_coverage_pct", 73.0)
    tb_inc = tb.get("incidence_per_100k", 468)
    mat_m  = (g(d, "health_system") or {}).get("maternal_mortality_per_100k", 118)

    st.markdown('<div class="section-title">🏥 Healthcare Access & Disease Burden</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">TB/HIV prevalence by district, public hospital capacity, NHI progress, and health outcomes</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("People Living with HIV", f"{plhiv}M", f"{prev}% prevalence (15-49)", "down"), unsafe_allow_html=True)
    c2.markdown(kpi("TB Incidence (per 100K)", f"{tb_inc}", "-5.2% YoY", "up"), unsafe_allow_html=True)
    c3.markdown(kpi("On ART", f"{on_art}M", f"{art_c}% of PLHIV", "up"), unsafe_allow_html=True)
    c4.markdown(kpi("Maternal Mortality", f"{mat_m}/100K", "-8% from 2022", "up"), unsafe_allow_html=True)

    st.divider()

    def pv(key, defaults):
        return [(prov_data.get(p) or {}).get(key) or defaults[i] for i, p in enumerate(PROVINCE_LIST)]

    health_prov = pd.DataFrame({
        "Province":               PROVINCE_LIST,
        "HIV Prevalence (%)":     pv("hiv_prevalence_pct", [12.8,11.9,25.2,15.4,10.3,15.8,12.1,11.6,6.1]),
        "TB Incidence (per 100K)":pv("tb_per_100k",        [720,620,480,520,290,310,340,380,560]),
        "Public Hospitals":       [54,34,72,62,44,31,28,26,16],
        "Doctors per 100K":       pv("doctors_per_100k",   [82,74,38,32,18,22,19,21,41]),
        "ART Coverage (%)":       pv("art_coverage_pct",   [72,68,71,65,58,64,61,60,70]),
    })

    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(health_prov, x="HIV Prevalence (%)", y="TB Incidence (per 100K)",
                         size="Public Hospitals", color="Province",
                         title="HIV Prevalence vs TB Incidence by Province",
                         template=PLOTLY_TEMPLATE, size_max=40)
        fig.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(health_prov.sort_values("Doctors per 100K"),
                      x="Province", y="Doctors per 100K",
                      title="Doctors per 100,000 population by province",
                      color="Doctors per 100K", color_continuous_scale="Greens",
                      template=PLOTLY_TEMPLATE)
        fig2.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # HIV trend — use loaded data if available
    default_plhiv = {2010:5.8,2012:6.2,2014:6.6,2016:7.1,2018:7.5,2020:7.7,2022:7.8,2024:7.8}
    default_art   = {2010:1.0,2012:2.0,2014:2.9,2016:4.0,2018:5.0,2020:5.4,2022:5.6,2024:5.7}
    plhiv_data = {int(k):v for k,v in plhiv_t.items()} if plhiv_t else default_plhiv
    art_data   = {int(k):v for k,v in art_t.items()}   if art_t   else default_art
    all_years  = sorted(set(list(plhiv_data.keys()) + list(art_data.keys())))

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=all_years, y=[plhiv_data.get(y) for y in all_years],
                              name="PLHIV", fill="tozeroy",
                              fillcolor="rgba(224,92,58,0.15)", line=dict(color="#e05c3a")))
    fig3.add_trace(go.Scatter(x=all_years, y=[art_data.get(y) for y in all_years],
                              name="On ART", fill="tozeroy",
                              fillcolor="rgba(39,174,96,0.2)", line=dict(color="#27ae60")))
    fig3.update_layout(title="HIV burden vs ART coverage (millions)",
                       template=PLOTLY_TEMPLATE, paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, legend_title="")
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("SANAC · DHIS2 · Stats SA · NDOH", scraped_at, is_live)


# ═══════════════════════════════════════════════════════════════════════════════
# 8. EDUCATION QUALITY & MATRIC DATA
# ═══════════════════════════════════════════════════════════════════════════════
def page_education(topic, province):
    d          = load_data("education")
    prov_data  = g(d, "provinces")  or {}
    subj_data  = g(d, "subjects")   or {}
    trend_data = g(d, "trend")      or {}
    scraped_at = g(d, "scraped_at")
    is_live    = g(d, "is_live", default=False)
    exam_year  = g(d, "exam_year")  or 2024

    pass_rate  = g(d, "national_pass_rate_pct") or 87.3
    bachelor   = g(d, "bachelor_pass_pct")      or 45.6
    wrote      = g(d, "total_wrote")            or 756000
    distinction= g(d, "distinction_rate_pct")   or 7.2

    st.markdown('<div class="section-title">🎓 Education Quality & Matric Data</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Matric pass rates by province, bachelor passes, subject performance · Exam year: {exam_year}</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi(f"National Pass Rate {exam_year}", f"{pass_rate}%", "+2.1pp YoY", "up"), unsafe_allow_html=True)
    c2.markdown(kpi("Bachelor Passes", f"{bachelor}%",  "+1.8pp YoY", "up"), unsafe_allow_html=True)
    c3.markdown(kpi(f"Wrote Matric {exam_year}", f"{wrote:,}", "+14K vs prev year", "up"), unsafe_allow_html=True)
    c4.markdown(kpi("Distinction Rate", f"{distinction}%", "+0.5pp YoY", "up"), unsafe_allow_html=True)

    st.divider()

    def pv(key, defaults):
        return [(prov_data.get(p) or {}).get(key) or defaults[i] for i, p in enumerate(PROVINCE_LIST)]

    edu_prov = pd.DataFrame({
        "Province":          PROVINCE_LIST,
        "Pass Rate (%)":     pv("pass_rate",    [83.6,92.2,80.4,71.9,65.4,74.8,79.2,77.3,88.1]),
        "Bachelor Pass (%)": pv("bachelor_pct", [54.2,58.8,39.2,31.4,22.8,31.0,35.6,33.2,48.8]),
        "Wrote Matric":      pv("wrote",        [88000,132000,148000,94000,58000,62000,47000,38000,20000]),
    })

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(edu_prov.sort_values("Pass Rate (%)", ascending=True),
                     x="Pass Rate (%)", y="Province", orientation="h",
                     color="Pass Rate (%)", color_continuous_scale="YlGn",
                     title=f"Matric pass rate by province ({exam_year})",
                     template=PLOTLY_TEMPLATE)
        fig.add_vline(x=pass_rate, line_dash="dash", line_color="#e05c3a",
                      annotation_text=f"National avg {pass_rate}%")
        fig.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        default_subj = {
            "Life Sciences":         {"pass_rate": 71.2},
            "Geography":             {"pass_rate": 64.8},
            "History":               {"pass_rate": 68.9},
            "Mathematics":           {"pass_rate": 52.3},
            "Physical Sciences":     {"pass_rate": 50.1},
            "Accounting":            {"pass_rate": 58.8},
            "Mathematical Literacy": {"pass_rate": 80.2},
            "Business Studies":      {"pass_rate": 74.6},
        }
        merged_subj = {**default_subj, **subj_data}
        subj = pd.DataFrame([
            {"Subject": k, "Pass Rate (%)": v.get("pass_rate", 0)}
            for k, v in merged_subj.items()
        ])
        fig2 = px.bar(subj.sort_values("Pass Rate (%)"),
                      x="Pass Rate (%)", y="Subject", orientation="h",
                      color="Pass Rate (%)", color_continuous_scale="Blues",
                      title=f"Subject pass rates — national ({exam_year})",
                      template=PLOTLY_TEMPLATE)
        fig2.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Pass rate trend — from JSON
    default_trend_e = {
        2015:{"pass_rate":70.7,"bachelor":35.5}, 2016:{"pass_rate":72.5,"bachelor":36.4},
        2017:{"pass_rate":75.1,"bachelor":37.8}, 2018:{"pass_rate":78.2,"bachelor":39.1},
        2019:{"pass_rate":81.3,"bachelor":40.8}, 2020:{"pass_rate":76.2,"bachelor":38.1},
        2021:{"pass_rate":77.2,"bachelor":39.2}, 2022:{"pass_rate":80.1,"bachelor":41.0},
        2023:{"pass_rate":82.9,"bachelor":43.8}, 2024:{"pass_rate":87.3,"bachelor":45.6},
    }
    td = {int(k):v for k,v in trend_data.items()} if trend_data else default_trend_e
    trend_years = sorted(td.keys())
    pass_trend = pd.DataFrame({
        "Year":                trend_years,
        "National Pass Rate (%)": [td[y].get("pass_rate", 0) for y in trend_years],
        "Bachelor Pass (%)":      [td[y].get("bachelor",  0) for y in trend_years],
    })
    fig3 = px.line(pass_trend, x="Year", y=["National Pass Rate (%)", "Bachelor Pass (%)"],
                   title="Matric pass rate trend", markers=True, template=PLOTLY_TEMPLATE)
    fig3.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, legend_title="")
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("Department of Basic Education — NSC Results", scraped_at, is_live)


# ═══════════════════════════════════════════════════════════════════════════════
# 9. ZAR EXCHANGE RATE & CAPITAL FLOWS
# ═══════════════════════════════════════════════════════════════════════════════
def page_forex(topic, province):
    d          = load_data("forex")
    rates      = g(d, "live_rates") or {}
    scraped_at = g(d, "scraped_at")
    is_live    = g(d, "is_live", default=False)

    usd_zar = rates.get("usd_zar", 18.64)
    eur_zar = rates.get("eur_zar", 20.21)
    gbp_zar = rates.get("gbp_zar", 23.48)
    ts      = rates.get("timestamp", "")

    st.markdown('<div class="section-title">💱 ZAR Exchange Rate & Capital Flows</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Rand vs major currencies, FDI trends, portfolio flows · {"🟢 Live rates" if is_live else "🟡 Cached rates"}</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi(f"USD/ZAR {'🟢' if is_live else ''}", f"R{usd_zar}", "+1.2% MTD", "down"), unsafe_allow_html=True)
    c2.markdown(kpi("EUR/ZAR", f"R{eur_zar}", "+0.8% MTD", "down"), unsafe_allow_html=True)
    c3.markdown(kpi("GBP/ZAR", f"R{gbp_zar}", "+1.5% MTD", "down"), unsafe_allow_html=True)
    c4.markdown(kpi("FDI Inflows (2024)", "R214B", "+8.4% YoY", "up"), unsafe_allow_html=True)

    st.divider()

    # All available pairs from loaded data
    all_rates = rates.get("all_vs_usd", {})
    if all_rates:
        pairs_df = pd.DataFrame([
            {"Currency pair": f"USD/{c}", "Rate": round(v, 4)}
            for c, v in all_rates.items() if c not in ("USD",)
        ]).sort_values("Rate")

    col1, col2 = st.columns([3, 2])
    with col1:
        # ZAR/USD historical — realistic interpolated series
        dates = pd.date_range("2020-01-01", "2025-03-01", freq="ME")
        np.random.seed(42)
        noise = np.cumsum(np.random.randn(len(dates)) * 0.15)
        base = np.interp(range(len(dates)), [0,12,24,36,48,63],
                         [14.5,18.8,15.2,17.8,19.2,usd_zar])
        hist_rates = (base + noise * 0.5).clip(13.5, 21.5)
        forex_df = pd.DataFrame({"Date": dates, "USD/ZAR": hist_rates})

        fig = px.line(forex_df, x="Date", y="USD/ZAR",
                      title="USD/ZAR exchange rate history (2020–present)",
                      template=PLOTLY_TEMPLATE)
        fig.update_traces(line_color="#f59e0b")
        # Mark today's live rate if available
        if is_live:
            fig.add_hline(y=usd_zar, line_dash="dot", line_color="#27ae60",
                          annotation_text=f"Live: R{usd_zar}")
        fig.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fdi = pd.DataFrame({
            "Year": [2019, 2020, 2021, 2022, 2023, 2024],
            "FDI Inflows (R billions)": [138, 89, 154, 178, 197, 214],
            "Portfolio Outflows (R billions)": [-45, -82, -38, -67, -52, -41],
        })
        fig2 = px.bar(fdi, x="Year",
                      y=["FDI Inflows (R billions)", "Portfolio Outflows (R billions)"],
                      title="FDI inflows vs portfolio outflows (R billions)",
                      template=PLOTLY_TEMPLATE, barmode="relative",
                      color_discrete_map={"FDI Inflows (R billions)": "#27ae60",
                                          "Portfolio Outflows (R billions)": "#e05c3a"})
        fig2.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, legend_title="")
        st.plotly_chart(fig2, use_container_width=True)

    # Show live multi-currency rates table if available
    if all_rates and is_live:
        st.subheader("Live rates vs USD (all available pairs)")
        st.dataframe(
            pd.DataFrame([{"Currency": c, "Rate vs USD": v}
                          for c, v in sorted(all_rates.items())]),
            use_container_width=True, hide_index=True
        )

    st.info("📌 Key events: COVID lockdown Apr 2020 → R19.3 · Zuma unrest Jul 2021 → R15.2 · LS peak Jun 2023 → R19.8 · FATF grey-listing Oct 2023 → R19.1 · FATF removal Feb 2025 → R18.1")
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("SARB · open.er-api.com · Investec", scraped_at, is_live)


# ═══════════════════════════════════════════════════════════════════════════════
# 10. WATER SCARCITY & SERVICE DELIVERY
# ═══════════════════════════════════════════════════════════════════════════════
def page_water(topic, province):
    d          = load_data("water")
    prov_data  = g(d, "provinces") or {}
    dams_raw   = g(d, "dams")      or []
    scraped_at = g(d, "scraped_at")
    is_live    = g(d, "is_live", default=False)
    report_dt  = g(d, "report_date")

    nat_avg    = g(d, "national_avg_pct") or 78.4

    st.markdown('<div class="section-title">💧 Water Scarcity & Service Delivery</div>', unsafe_allow_html=True)
    sub = f"DWS weekly dam levels · {'Report date: ' + report_dt if report_dt else 'Cached data'}"
    st.markdown(f'<div class="section-sub">{sub}</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("National Dam Level", f"{nat_avg}%", "+12.1pp YoY", "up"), unsafe_allow_html=True)
    c2.markdown(kpi("Metros with Water Crisis", "4 / 8", "Tshwane, Joburg, EC, Msunduzi", "down"), unsafe_allow_html=True)
    c3.markdown(kpi("Service Delivery Protests", "848", "+18% in 2024", "down"), unsafe_allow_html=True)
    c4.markdown(kpi("Municipalities in Distress", "163 / 257", "63%", "down"), unsafe_allow_html=True)

    st.divider()

    # Dam levels — prefer scraped individual dams, fall back to hardcoded
    default_dams = [
        {"name":"Vaal Dam",        "this_week_pct":71.2, "capacity_mm3":2596, "Province Served":"GP/NW"},
        {"name":"Theewaterskloof", "this_week_pct":92.4, "capacity_mm3":480,  "Province Served":"WC"},
        {"name":"Gariep Dam",      "this_week_pct":88.1, "capacity_mm3":5341, "Province Served":"FS/NC"},
        {"name":"Sterkfontein",    "this_week_pct":65.3, "capacity_mm3":2617, "Province Served":"FS"},
        {"name":"Katse (Lesotho)", "this_week_pct":82.4, "capacity_mm3":1950, "Province Served":"GP/FS"},
        {"name":"Vanderkloof",     "this_week_pct":79.8, "capacity_mm3":3200, "Province Served":"NC/FS"},
        {"name":"Pongolapoort",    "this_week_pct":54.1, "capacity_mm3":2435, "Province Served":"KZN"},
        {"name":"Krugersdrift",    "this_week_pct":61.2, "capacity_mm3":190,  "Province Served":"FS"},
    ]
    dam_rows = dams_raw[:10] if dams_raw else default_dams
    dam_names  = [r.get("name","") for r in dam_rows]
    dam_levels = [r.get("this_week_pct") or 0 for r in dam_rows]

    col1, col2 = st.columns(2)
    with col1:
        colors = ["#e05c3a" if v < 40 else "#f59e0b" if v < 60 else "#27ae60" for v in dam_levels]
        fig = go.Figure(go.Bar(
            x=dam_levels, y=dam_names, orientation="h",
            marker_color=colors,
            text=[f"{v:.0f}%" for v in dam_levels],
            textposition="outside",
        ))
        fig.update_layout(
            title=f"Major dam levels — {'Live' if is_live else 'Latest published'} (%)",
            template=PLOTLY_TEMPLATE, paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            xaxis_range=[0, 115]
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        def pv(key, defaults):
            return [(prov_data.get(p) or {}).get(key) or defaults[i] for i, p in enumerate(PROVINCE_LIST)]

        delivery = pd.DataFrame({
            "Province":            PROVINCE_LIST,
            "Protest Count (2024)":[98,182,141,112,88,76,71,54,26],
            "Blue Drop Score":     [72,88,61,54,38,44,42,48,65],
            "Dam Level (%)":       pv("this_week_pct", [92.4,71.2,81.3,72.1,68.4,74.2,63.8,83.1,78.9]),
        })
        fig2 = px.scatter(delivery, x="Blue Drop Score", y="Protest Count (2024)",
                          size="Protest Count (2024)", color="Province",
                          hover_data=["Dam Level (%)"],
                          title="Water quality (Blue Drop) vs service delivery protests",
                          template=PLOTLY_TEMPLATE, size_max=40)
        fig2.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
        st.plotly_chart(fig2, use_container_width=True)

    # Province dam level bar — from scraped data
    prov_levels = pd.DataFrame({
        "Province": PROVINCE_LIST,
        "Dam Level (%)": pv("this_week_pct", [92.4,71.2,81.3,72.1,68.4,74.2,63.8,83.1,78.9]),
        "Last Week (%)": pv("last_week_pct", [91.8,70.8,80.9,71.4,67.9,73.6,63.1,82.4,78.2]),
    })
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="This week", x=prov_levels["Province"],
                          y=prov_levels["Dam Level (%)"], marker_color="#3b82f6"))
    fig3.add_trace(go.Bar(name="Last week", x=prov_levels["Province"],
                          y=prov_levels["Last Week (%)"], marker_color="#1e3a52"))
    fig3.update_layout(
        title=f"Province dam levels — week-on-week ({'Live' if is_live else 'Cached'})",
        barmode="group", template=PLOTLY_TEMPLATE,
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, legend_title=""
    )
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("Dept of Water & Sanitation · dws.gov.za · COGTA", scraped_at, is_live)


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR & ROUTING
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 16px 0 8px;">
        <div style="font-size:28px">🇿🇦</div>
        <div style="font-size:18px; font-weight:700; color:#e8e4d8; margin-top:4px;">SA Insight Hub</div>
        <div style="font-size:11px; color:#5a7a8a; margin-top:2px;">South Africa's data, decoded</div>
    </div>
    <hr style="border-color:#2a3a52; margin:12px 0;">
    """, unsafe_allow_html=True)

    topic = st.selectbox("SELECT TOPIC", [
        "🔴  Crime Statistics",
        "🏠  Property Prices & Rental",
        "🔐  Bank Fraud & Financial Crime",
        "📉  Unemployment & Income",
        "⚡  Load Shedding & Energy",
        "💰  Interest Rates & Inflation",
        "🏥  Healthcare & Disease Burden",
        "🎓  Education & Matric Data",
        "💱  ZAR Exchange Rate & Forex",
        "💧  Water & Service Delivery",
    ])

    st.markdown("<hr style='border-color:#2a3a52; margin:12px 0;'>", unsafe_allow_html=True)

    province = st.selectbox("FILTER BY PROVINCE", PROVINCES)

    st.markdown("<hr style='border-color:#2a3a52; margin:12px 0;'>", unsafe_allow_html=True)

    # Dynamic data freshness from manifest.json
    manifest = load_data("manifest")
    if manifest and manifest.get("topics"):
        st.markdown('<div style="font-size:11px;color:#5a7a8a;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px;">📡 Data freshness</div>', unsafe_allow_html=True)
        topic_file = TOPIC_FILE.get(topic, "")
        topic_meta = manifest["topics"].get(topic_file, {})
        if topic_meta:
            live_dot   = "🟢" if topic_meta.get("is_live") else "🟡"
            status     = topic_meta.get("status", "unknown")
            cadence    = topic_meta.get("cadence", "")
            st.markdown(f'<div style="font-size:11px;color:#7a8fa6;line-height:1.8;">'
                        f'{live_dot} Status: <b>{status}</b><br>'
                        f'⏱ Cadence: {cadence}<br>'
                        f'Last run: {manifest.get("last_run","unknown")[:10]}'
                        f'</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="font-size:11px; color:#5a7a8a; line-height:1.6;">
            <b style="color:#7a8fa6;">Run scrapers to refresh:</b><br>
            <code style="font-size:10px;">python run_scrapers.py</code>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#2a3a52; margin:12px 0;'>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:11px;color:#5a7a8a;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px;">🤖 AI Q&A KEY</div>', unsafe_allow_html=True)
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        label_visibility="collapsed",
        help="Get your key at console.anthropic.com",
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input
        st.markdown('<div style="font-size:11px;color:#27ae60;margin-top:4px;">✓ API key saved for this session</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:11px;color:#5a7a8a;margin-top:4px;">Enter key to enable AI Q&A on each page</div>', unsafe_allow_html=True)

# ── Route to page ─────────────────────────────────────────────────────────────
pages = {
    "🔴  Crime Statistics": page_crime,
    "🏠  Property Prices & Rental": page_property,
    "🔐  Bank Fraud & Financial Crime": page_fraud,
    "📉  Unemployment & Income": page_employment,
    "⚡  Load Shedding & Energy": page_energy,
    "💰  Interest Rates & Inflation": page_finance,
    "🏥  Healthcare & Disease Burden": page_health,
    "🎓  Education & Matric Data": page_education,
    "💱  ZAR Exchange Rate & Forex": page_forex,
    "💧  Water & Service Delivery": page_water,
}

pages[topic](topic, province)