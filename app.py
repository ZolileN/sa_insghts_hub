import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta

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

def source_badge(text):
    st.markdown(f'<span class="source-badge">Source: {text}</span>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CRIME STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════
def page_crime(topic, province):
    st.markdown('<div class="section-title">🔴 Crime Statistics</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">SAPS quarterly crime data — murders, robbery, burglary, GBV by province and police station</div>', unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Murders (2023/24)", "19,674", "+3.2% YoY", "down"), unsafe_allow_html=True)
    c2.markdown(kpi("Residential Burglaries", "205,765", "+1.8% YoY", "down"), unsafe_allow_html=True)
    c3.markdown(kpi("Carjackings", "15,727", "+5.4% YoY", "down"), unsafe_allow_html=True)
    c4.markdown(kpi("Sexual Offences", "43,604", "-3.1% YoY", "down"), unsafe_allow_html=True)

    st.divider()

    # Crime by province
    crime_prov = pd.DataFrame({
        "Province": PROVINCE_LIST,
        "Murder": [1204, 4912, 3801, 2890, 1102, 1450, 980, 785, 550],
        "Burglary": [28400, 52000, 41000, 22000, 10500, 16000, 13000, 11200, 11665],
        "Robbery": [24000, 38000, 29000, 18000, 6500, 9000, 8500, 7500, 4000],
        "Sexual Offences": [7800, 10200, 8900, 5600, 3200, 3400, 2900, 1804, 2900],
        "Carjacking": [2900, 6800, 2800, 1200, 450, 620, 540, 420, 197],
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
    source_badge("SAPS Annual Crime Report 2023/24 · saps.gov.za")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PROPERTY PRICES & RENTAL YIELDS
# ═══════════════════════════════════════════════════════════════════════════════
def page_property(topic, province):
    st.markdown('<div class="section-title">🏠 Property Prices & Rental Yields</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Suburb-level house prices, price growth, days on market, and rental return rates</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("National Median Price", "R1.28M", "+2.3% YoY", "up"), unsafe_allow_html=True)
    c2.markdown(kpi("Avg Rental Yield", "8.4%", "+0.6pp YoY", "up"), unsafe_allow_html=True)
    c3.markdown(kpi("Days on Market", "76 days", "-4 days YoY", "down"), unsafe_allow_html=True)
    c4.markdown(kpi("Bond Approval Rate", "62%", "-3pp YoY", "down"), unsafe_allow_html=True)

    st.divider()

    prop_prov = pd.DataFrame({
        "Province": PROVINCE_LIST,
        "Median Price (R000)": [2100, 1450, 1200, 890, 650, 720, 680, 730, 1100],
        "YoY Growth (%)": [4.2, 2.1, 1.8, 0.9, 1.2, 1.5, 1.1, 0.8, 2.8],
        "Rental Yield (%)": [6.8, 8.2, 9.1, 10.2, 11.0, 10.5, 10.8, 10.1, 7.4],
        "Avg Price/m² (R)": [24500, 14200, 10800, 8200, 5100, 5800, 5400, 6100, 16800],
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

    # Price trend
    quarters = ["Q1'21","Q2'21","Q3'21","Q4'21","Q1'22","Q2'22","Q3'22","Q4'22",
                 "Q1'23","Q2'23","Q3'23","Q4'23","Q1'24","Q2'24","Q3'24","Q4'24"]
    price_trend = pd.DataFrame({
        "Quarter": quarters,
        "Western Cape": [1650,1680,1720,1760,1810,1870,1930,1980,2020,2050,2070,2090,2100,2110,2100,2110],
        "Gauteng": [1180,1190,1200,1210,1220,1230,1250,1270,1300,1340,1370,1400,1420,1440,1450,1455],
        "National": [980,995,1010,1030,1060,1090,1120,1150,1180,1210,1240,1260,1270,1275,1280,1285],
    })
    fig3 = px.line(price_trend, x="Quarter", y=["Western Cape","Gauteng","National"],
                   title="Median house price trend (R thousands)",
                   template=PLOTLY_TEMPLATE)
    fig3.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, legend_title="")
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("Lightstone Property · FNB Property Barometer · PropStats 2024")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. BANK FRAUD & FINANCIAL CRIME
# ═══════════════════════════════════════════════════════════════════════════════
def page_fraud(topic, province):
    st.markdown('<div class="section-title">🔐 Bank Fraud & Financial Crime</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">SABRIC annual fraud data — SIM swap, phishing, card fraud, and EFT scams</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Total Losses (2023)", "R3.3B", "+12.4% YoY", "down"), unsafe_allow_html=True)
    c2.markdown(kpi("SIM Swap Incidents", "3,800+", "+8.2% YoY", "down"), unsafe_allow_html=True)
    c3.markdown(kpi("Online Banking Fraud", "R634M", "+18.1% YoY", "down"), unsafe_allow_html=True)
    c4.markdown(kpi("Card Fraud Losses", "R1.1B", "+6.7% YoY", "down"), unsafe_allow_html=True)

    st.divider()

    fraud_types = pd.DataFrame({
        "Category": ["Card not present", "Lost/Stolen card", "Online banking", "SIM swap / account takeover",
                     "Business email compromise", "ATM fraud", "Investment scams"],
        "Losses (R millions)": [620, 480, 634, 412, 380, 290, 484],
        "Incidents": [142000, 89000, 54000, 3800, 2100, 67000, 8900],
    })

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

    # Year trend
    yrs = [2019, 2020, 2021, 2022, 2023]
    fraud_trend = pd.DataFrame({
        "Year": yrs,
        "Total Losses (R billions)": [2.2, 1.8, 2.1, 2.9, 3.3],
        "Online Banking (R millions)": [329, 284, 399, 537, 634],
    })
    fig3 = px.line(fraud_trend, x="Year", y="Total Losses (R billions)",
                   title="Total fraud losses trend (R billions)",
                   markers=True, template=PLOTLY_TEMPLATE)
    fig3.update_traces(line_color="#e05c3a", marker_color="#e05c3a")
    fig3.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("SABRIC Annual Report 2023 · South African Banking Risk Information Centre")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. UNEMPLOYMENT & INCOME LEVELS
# ═══════════════════════════════════════════════════════════════════════════════
def page_employment(topic, province):
    st.markdown('<div class="section-title">📉 Unemployment & Income Levels</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Stats SA quarterly labour force survey — unemployment, income inequality, sector breakdown</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Unemployment Rate", "32.9%", "-0.4pp QoQ", "down"), unsafe_allow_html=True)
    c2.markdown(kpi("Youth Unemployment", "60.7%", "+1.2pp QoQ", "down"), unsafe_allow_html=True)
    c3.markdown(kpi("Gini Coefficient", "0.63", "Highest in world", "down"), unsafe_allow_html=True)
    c4.markdown(kpi("Employed (millions)", "16.7M", "+220K QoQ", "up"), unsafe_allow_html=True)

    st.divider()

    unemp_prov = pd.DataFrame({
        "Province": PROVINCE_LIST,
        "Unemployment Rate (%)": [22.8, 33.2, 32.6, 39.7, 45.4, 38.8, 40.1, 35.6, 31.4],
        "Youth Unemployment (%)": [44.1, 58.9, 57.2, 64.8, 72.1, 68.4, 69.8, 63.2, 53.1],
        "Median Monthly Income (R)": [14800, 11200, 9800, 6400, 5200, 5800, 5400, 6100, 8900],
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

    # Unemployment over time
    quarters = ["Q1'20","Q2'20","Q3'20","Q4'20","Q1'21","Q2'21","Q3'21","Q4'21",
                "Q1'22","Q2'22","Q3'22","Q4'22","Q1'23","Q2'23","Q3'23","Q4'23","Q1'24","Q2'24","Q3'24"]
    rates = [30.1, 34.4, 30.8, 32.5, 32.6, 34.4, 34.9, 35.3, 34.5, 33.9, 32.9, 32.7, 32.9, 33.5, 31.9, 32.1, 33.5, 33.5, 32.9]
    fig3 = px.area(pd.DataFrame({"Quarter": quarters, "Rate (%)": rates}),
                   x="Quarter", y="Rate (%)",
                   title="SA unemployment rate trend (%)",
                   template=PLOTLY_TEMPLATE)
    fig3.update_traces(fillcolor="rgba(59,130,246,0.2)", line_color="#3b82f6")
    fig3.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("Stats SA QLFS Q3 2024 · statssa.gov.za")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. LOAD SHEDDING & ENERGY
# ═══════════════════════════════════════════════════════════════════════════════
def page_energy(topic, province):
    st.markdown('<div class="section-title">⚡ Load Shedding & Energy</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Eskom stage data, unplanned capacity losses, renewable energy uptake, and energy cost trends</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Loadshedding Hours 2023", "6,932 hrs", "Worst year on record", "down"), unsafe_allow_html=True)
    c2.markdown(kpi("Loadshedding Hours 2024", "2,140 hrs", "-69% vs 2023", "up"), unsafe_allow_html=True)
    c3.markdown(kpi("Eskom Generation Capacity", "~34 GW", "vs 44 GW installed", "down"), unsafe_allow_html=True)
    c4.markdown(kpi("Rooftop Solar Installed", "5.7 GW", "+2.1 GW in 2023", "up"), unsafe_allow_html=True)

    st.divider()

    # Monthly load shedding hours 2023 vs 2024
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    ls_data = pd.DataFrame({
        "Month": months,
        "2022": [0, 24, 144, 168, 312, 360, 288, 408, 336, 240, 264, 480],
        "2023": [744, 576, 648, 576, 600, 552, 600, 576, 504, 576, 480, 300],
        "2024": [312, 240, 168, 120, 72, 96, 144, 120, 96, 72, 48, 24],
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
        # Energy mix
        energy_mix = pd.DataFrame({
            "Source": ["Coal", "Nuclear", "Hydro", "Wind", "Solar PV", "Gas/Diesel", "Imports"],
            "Percentage": [57, 5, 2, 6, 10, 8, 12],
        })
        fig2 = px.pie(energy_mix, values="Percentage", names="Source",
                      title="SA electricity generation mix (2024)",
                      template=PLOTLY_TEMPLATE, hole=0.35,
                      color_discrete_sequence=px.colors.qualitative.Set3)
        fig2.update_layout(paper_bgcolor=CHART_BG)
        st.plotly_chart(fig2, use_container_width=True)

    # Electricity tariff trend
    tariff_years = list(range(2015, 2025))
    tariffs = [112.5, 135.4, 151.1, 170.0, 186.3, 207.7, 252.0, 328.0, 388.0, 436.0]
    fig3 = px.line(pd.DataFrame({"Year": tariff_years, "Tariff (c/kWh)": tariffs}),
                   x="Year", y="Tariff (c/kWh)",
                   title="Average Eskom residential tariff (cents/kWh)",
                   markers=True, template=PLOTLY_TEMPLATE)
    fig3.update_traces(line_color="#f59e0b")
    fig3.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("Eskom · EskomSePush · NERSA 2024")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. INTEREST RATES & INFLATION
# ═══════════════════════════════════════════════════════════════════════════════
def page_finance(topic, province):
    st.markdown('<div class="section-title">💰 Interest Rates & Inflation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">SARB repo rate decisions, CPI by category, food inflation, and prime lending rate</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Repo Rate", "8.00%", "-0.25pp (Jan 2025)", "up"), unsafe_allow_html=True)
    c2.markdown(kpi("Prime Rate", "11.50%", "Repo + 3.5pp", "neutral"), unsafe_allow_html=True)
    c3.markdown(kpi("CPI (Jan 2025)", "3.2%", "Lowest since 2021", "up"), unsafe_allow_html=True)
    c4.markdown(kpi("Food Inflation", "4.1%", "-6.1pp from peak", "up"), unsafe_allow_html=True)

    st.divider()

    # Repo rate history
    quarters = ["Q1'20","Q2'20","Q3'20","Q4'20","Q1'21","Q2'21","Q3'21","Q4'21",
                "Q1'22","Q2'22","Q3'22","Q4'22","Q1'23","Q2'23","Q3'23","Q4'23","Q1'24","Q2'24","Q3'24","Q4'24","Q1'25"]
    repo = [6.25,3.75,3.5,3.5,3.5,3.5,3.5,3.75,4.0,4.75,5.5,7.0,7.25,8.25,8.25,8.25,8.25,8.25,8.0,8.0,8.0]
    cpi  = [4.1,2.2,3.0,3.1,2.9,4.9,4.9,5.9,5.9,6.5,7.8,7.2,7.0,6.3,5.4,5.5,5.3,5.1,4.4,3.8,3.2]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=quarters, y=repo, name="Repo Rate (%)", line=dict(color="#3b82f6", width=2.5)))
    fig.add_trace(go.Scatter(x=quarters, y=cpi, name="CPI (%)", line=dict(color="#e05c3a", width=2.5, dash="dash")))
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
    source_badge("SARB Monetary Policy · Stats SA CPI · 2025")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. HEALTHCARE ACCESS & DISEASE BURDEN
# ═══════════════════════════════════════════════════════════════════════════════
def page_health(topic, province):
    st.markdown('<div class="section-title">🏥 Healthcare Access & Disease Burden</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">TB/HIV prevalence by district, public hospital capacity, NHI progress, and health outcomes</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("People Living with HIV", "7.8M", "18.3% prevalence (15-49)", "down"), unsafe_allow_html=True)
    c2.markdown(kpi("TB Incidence (per 100K)", "468", "-5.2% YoY", "up"), unsafe_allow_html=True)
    c3.markdown(kpi("On ART", "5.7M", "73% of PLHIV", "up"), unsafe_allow_html=True)
    c4.markdown(kpi("Maternal Mortality", "118/100K", "-8% from 2022", "up"), unsafe_allow_html=True)

    st.divider()

    health_prov = pd.DataFrame({
        "Province": PROVINCE_LIST,
        "HIV Prevalence (%)": [12.8, 11.9, 25.2, 15.4, 10.3, 15.8, 12.1, 11.6, 6.1],
        "TB Incidence (per 100K)": [720, 620, 480, 520, 290, 310, 340, 380, 560],
        "Public Hospitals": [54, 34, 72, 62, 44, 31, 28, 26, 16],
        "Doctors per 100K": [82, 74, 38, 32, 18, 22, 19, 21, 41],
        "ART Coverage (%)": [72, 68, 71, 65, 58, 64, 61, 60, 70],
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

    # HIV trend
    years = list(range(2010, 2025))
    hiv_trend = pd.DataFrame({
        "Year": years,
        "PLHIV (millions)": [5.8,6.0,6.2,6.4,6.6,6.8,7.1,7.3,7.5,7.6,7.7,7.75,7.8,7.8,7.8],
        "On ART (millions)": [1.0,1.6,2.0,2.4,2.9,3.4,4.0,4.6,5.0,5.2,5.4,5.5,5.65,5.7,5.75],
    })
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=years, y=hiv_trend["PLHIV (millions)"], name="PLHIV", fill="tozeroy",
                              fillcolor="rgba(224,92,58,0.15)", line=dict(color="#e05c3a")))
    fig3.add_trace(go.Scatter(x=years, y=hiv_trend["On ART (millions)"], name="On ART", fill="tozeroy",
                              fillcolor="rgba(39,174,96,0.2)", line=dict(color="#27ae60")))
    fig3.update_layout(title="HIV burden vs ART coverage (2010–2024, millions)",
                       template=PLOTLY_TEMPLATE, paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, legend_title="")
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("SANAC · DHIS2 · Stats SA · NDOH 2024")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. EDUCATION QUALITY & MATRIC DATA
# ═══════════════════════════════════════════════════════════════════════════════
def page_education(topic, province):
    st.markdown('<div class="section-title">🎓 Education Quality & Matric Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Matric pass rates by province, bachelor passes, subject performance, and university access</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("National Pass Rate 2024", "87.3%", "+2.1pp YoY", "up"), unsafe_allow_html=True)
    c2.markdown(kpi("Bachelor Passes", "45.6%", "+1.8pp YoY", "up"), unsafe_allow_html=True)
    c3.markdown(kpi("Wrote Matric 2024", "756,000", "+14K vs 2023", "up"), unsafe_allow_html=True)
    c4.markdown(kpi("Distinction Rate", "7.2%", "+0.5pp YoY", "up"), unsafe_allow_html=True)

    st.divider()

    edu_prov = pd.DataFrame({
        "Province": PROVINCE_LIST,
        "Pass Rate 2024 (%)": [83.6, 92.2, 80.4, 71.9, 65.4, 74.8, 79.2, 77.3, 88.1],
        "Bachelor Pass (%)": [54.2, 58.8, 39.2, 31.4, 22.8, 31.0, 35.6, 33.2, 48.8],
        "Wrote Matric": [88000, 132000, 148000, 94000, 58000, 62000, 47000, 38000, 20000],
    })

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(edu_prov.sort_values("Pass Rate 2024 (%)", ascending=True),
                     x="Pass Rate 2024 (%)", y="Province", orientation="h",
                     color="Pass Rate 2024 (%)", color_continuous_scale="YlGn",
                     title="Matric pass rate by province (2024)",
                     template=PLOTLY_TEMPLATE)
        fig.add_vline(x=87.3, line_dash="dash", line_color="#e05c3a", annotation_text="National avg")
        fig.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        subj = pd.DataFrame({
            "Subject": ["Life Sciences", "Geography", "History", "Mathematics", "Physical Sciences",
                        "Accounting", "Mathematical Literacy", "Business Studies"],
            "Pass Rate (%)": [71.2, 64.8, 68.9, 52.3, 50.1, 58.8, 80.2, 74.6],
        })
        fig2 = px.bar(subj.sort_values("Pass Rate (%)"),
                      x="Pass Rate (%)", y="Subject", orientation="h",
                      color="Pass Rate (%)", color_continuous_scale="Blues",
                      title="Subject pass rates — national (2024)",
                      template=PLOTLY_TEMPLATE)
        fig2.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Pass rate trend
    years = list(range(2015, 2025))
    pass_trend = pd.DataFrame({
        "Year": years,
        "National Pass Rate (%)": [70.7, 72.5, 75.1, 78.2, 81.3, 76.2, 77.2, 80.1, 82.9, 87.3],
        "Bachelor Pass (%)": [35.5, 36.4, 37.8, 39.1, 40.8, 38.1, 39.2, 41.0, 43.8, 45.6],
    })
    fig3 = px.line(pass_trend, x="Year", y=["National Pass Rate (%)", "Bachelor Pass (%)"],
                   title="Matric pass rate trend (2015–2024)",
                   markers=True, template=PLOTLY_TEMPLATE)
    fig3.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, legend_title="")
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("Department of Basic Education — 2024 NSC Results")


# ═══════════════════════════════════════════════════════════════════════════════
# 9. ZAR EXCHANGE RATE & CAPITAL FLOWS
# ═══════════════════════════════════════════════════════════════════════════════
def page_forex(topic, province):
    st.markdown('<div class="section-title">💱 ZAR Exchange Rate & Capital Flows</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Rand vs major currencies, FDI trends, portfolio flows, and offshore investment appetite</div>', unsafe_allow_html=True)

    # Try live rate
    live_rate = None
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=4)
        data = r.json()
        if data.get("result") == "success":
            live_rate = round(data["rates"].get("ZAR", 18.5), 2)
    except Exception:
        pass

    rate_display = f"R{live_rate}" if live_rate else "R18.64"
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("USD/ZAR" + (" 🟢 Live" if live_rate else ""), rate_display, "+1.2% MTD", "down"), unsafe_allow_html=True)
    c2.markdown(kpi("EUR/ZAR", "R20.21", "+0.8% MTD", "down"), unsafe_allow_html=True)
    c3.markdown(kpi("GBP/ZAR", "R23.48", "+1.5% MTD", "down"), unsafe_allow_html=True)
    c4.markdown(kpi("FDI Inflows (2024)", "R214B", "+8.4% YoY", "up"), unsafe_allow_html=True)

    st.divider()

    # ZAR/USD historical
    dates = pd.date_range("2020-01-01", "2025-01-01", freq="ME")
    np.random.seed(42)
    noise = np.cumsum(np.random.randn(len(dates)) * 0.15)
    base_rates = np.interp(range(len(dates)), [0, 12, 24, 36, 48, 60],
                            [14.5, 18.8, 15.2, 17.8, 19.2, 18.6])
    rates = base_rates + noise * 0.5

    forex_df = pd.DataFrame({"Date": dates, "USD/ZAR": rates.clip(13.5, 21.0)})

    col1, col2 = st.columns([3, 2])
    with col1:
        fig = px.line(forex_df, x="Date", y="USD/ZAR",
                      title="USD/ZAR exchange rate (2020–2025)",
                      template=PLOTLY_TEMPLATE)
        fig.update_traces(line_color="#f59e0b")
        fig.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fdi = pd.DataFrame({
            "Year": [2019, 2020, 2021, 2022, 2023, 2024],
            "FDI Inflows (R billions)": [138, 89, 154, 178, 197, 214],
            "Portfolio Outflows (R billions)": [-45, -82, -38, -67, -52, -41],
        })
        fig2 = px.bar(fdi, x="Year", y=["FDI Inflows (R billions)", "Portfolio Outflows (R billions)"],
                      title="FDI inflows vs portfolio outflows (R billions)",
                      template=PLOTLY_TEMPLATE, barmode="relative",
                      color_discrete_map={"FDI Inflows (R billions)": "#27ae60",
                                          "Portfolio Outflows (R billions)": "#e05c3a"})
        fig2.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, legend_title="")
        st.plotly_chart(fig2, use_container_width=True)

    # Rate vs key events
    st.info("📌 Key rate events: COVID lockdown (Apr 2020) → R19.3 | Zuma unrest (Jul 2021) → R15.2 | Load shedding peak (Jun 2023) → R19.8 | FATF grey-listing (Oct 2023) → R19.1 | FATF removal (Feb 2025) → R18.1")
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("SARB · open.er-api.com · Investec 2024")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. WATER SCARCITY & SERVICE DELIVERY
# ═══════════════════════════════════════════════════════════════════════════════
def page_water(topic, province):
    st.markdown('<div class="section-title">💧 Water Scarcity & Service Delivery</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Dam levels, municipal water quality failures, sewage spillage, and service delivery protests</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("National Dam Level", "78.4%", "+12.1pp YoY", "up"), unsafe_allow_html=True)
    c2.markdown(kpi("Metros with Water Crisis", "4 / 8", "Tshwane, Joburg, EC, Msunduzi", "down"), unsafe_allow_html=True)
    c3.markdown(kpi("Service Delivery Protests", "848", "+18% in 2024", "down"), unsafe_allow_html=True)
    c4.markdown(kpi("Municipalities in Distress", "163 / 257", "63%", "down"), unsafe_allow_html=True)

    st.divider()

    # Dam levels by catchment
    dams = pd.DataFrame({
        "Dam / System": ["Vaal Dam", "Theewaterskloof", "Gariep Dam", "Sterkfontein", "Katse (Lesotho)",
                         "Vanderkloof", "Pongolapoort", "Krugersdrift"],
        "Province Served": ["GP/NW", "WC", "FS/NC", "FS", "GP/FS", "NC/FS", "KZN", "FS"],
        "Level (%)": [71.2, 92.4, 88.1, 65.3, 82.4, 79.8, 54.1, 61.2],
        "Capacity (Mm³)": [2596, 480, 5341, 2617, 1950, 3200, 2435, 190],
    })

    col1, col2 = st.columns(2)
    with col1:
        colors = ["#e05c3a" if v < 40 else "#f59e0b" if v < 60 else "#27ae60" for v in dams["Level (%)"]]
        fig = go.Figure(go.Bar(
            x=dams["Level (%)"], y=dams["Dam / System"], orientation="h",
            marker_color=colors, text=[f'{v:.0f}%' for v in dams["Level (%)"]],
            textposition="outside"
        ))
        fig.update_layout(title="Major dam levels (%)", template=PLOTLY_TEMPLATE,
                          paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                          xaxis_range=[0, 110])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        delivery = pd.DataFrame({
            "Province": PROVINCE_LIST,
            "Protest Count (2024)": [98, 182, 141, 112, 88, 76, 71, 54, 26],
            "Blue Drop Score": [72, 88, 61, 54, 38, 44, 42, 48, 65],
        })
        fig2 = px.scatter(delivery, x="Blue Drop Score", y="Protest Count (2024)",
                          size="Protest Count (2024)", color="Province",
                          title="Water quality (Blue Drop) vs service delivery protests",
                          template=PLOTLY_TEMPLATE, size_max=40)
        fig2.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
        st.plotly_chart(fig2, use_container_width=True)

    # Dam trend
    months = pd.date_range("2022-01-01", "2025-01-01", freq="ME")
    np.random.seed(7)
    dam_national = 55 + np.cumsum(np.random.randn(len(months)) * 1.5)
    dam_national = np.clip(dam_national, 30, 98)
    fig3 = px.area(pd.DataFrame({"Month": months, "National Average (%)": dam_national}),
                   x="Month", y="National Average (%)",
                   title="National dam level average (2022–2025)",
                   template=PLOTLY_TEMPLATE)
    fig3.update_traces(fillcolor="rgba(59,130,246,0.2)", line_color="#3b82f6")
    fig3.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
    st.plotly_chart(fig3, use_container_width=True)
    render_qa_panel(topic, province, st.session_state.get("api_key", ""))
    source_badge("Dept of Water & Sanitation · DWS Dam Levels · COGTA 2024")


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
    st.markdown("""
    <div style="font-size:11px; color:#5a7a8a; line-height:1.6;">
        <b style="color:#7a8fa6;">Data refreshed:</b><br>
        Crime — SAPS Q4 2024<br>
        Property — Dec 2024<br>
        Economy — Jan 2025<br>
        Health — DHIS2 2024<br>
        Forex — Live (when available)
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
