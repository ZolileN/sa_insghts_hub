# 🇿🇦 SA Insight Hub

**South Africa's top 10 most valuable data categories — one interactive dashboard with an AI analyst built in.**

## Topics Covered

| # | Topic | Key Data |
|---|-------|----------|
| 1 | 🔴 Crime Statistics | SAPS annual crime by precinct & province |
| 2 | 🏠 Property Prices & Rental | Median prices, yield, price growth |
| 3 | 🔐 Bank Fraud & Financial Crime | SABRIC fraud categories & losses |
| 4 | 📉 Unemployment & Income | Stats SA QLFS — unemployment, income |
| 5 | ⚡ Load Shedding & Energy | Hours per month, tariffs, energy mix |
| 6 | 💰 Interest Rates & Inflation | SARB repo rate, CPI basket |
| 7 | 🏥 Healthcare & Disease Burden | HIV/TB prevalence, ART coverage |
| 8 | 🎓 Education & Matric Data | Pass rates by province & subject |
| 9 | 💱 ZAR Exchange Rate & Forex | Live USD/ZAR, FDI inflows |
| 10 | 💧 Water & Service Delivery | Dam levels, Blue Drop scores |

---

## 🤖 AI Q&A Layer

Every topic page has a **Claude-powered chat panel** at the bottom. Users can:
- Ask plain English questions: *"Which province has the safest suburbs?"*
- Click suggested questions for instant answers
- Have a multi-turn conversation with full history per topic
- Get province-aware answers when a province filter is active

**To enable AI Q&A:**
1. Get a free API key at [console.anthropic.com](https://console.anthropic.com)
2. Paste it into the **🤖 AI Q&A KEY** field in the sidebar
3. Your key is stored in the session only — never saved to disk

---

## Quick Start (Local)

```bash
git clone https://github.com/YOUR_USERNAME/sa-insight-hub
cd sa-insight-hub
pip install -r requirements.txt
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

---

## Deploy to Streamlit Cloud (Free, ~2 min)

1. Push this repo to GitHub (include the `.streamlit/` folder)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo → Branch: `main` → Main file: `app.py`
4. Click **Deploy**

**API key on Streamlit Cloud — use Secrets management:**
- App Settings → Secrets → add: `ANTHROPIC_API_KEY = "sk-ant-..."`
- Or let users paste their own key in the sidebar (current default)

---

## Secrets Management (Optional)

To pre-load the API key from Streamlit secrets, add this after the imports in `app.py`:

```python
if "ANTHROPIC_API_KEY" in st.secrets:
    st.session_state.setdefault("api_key", st.secrets["ANTHROPIC_API_KEY"])
```

---

## Project Structure

```
sa-insight-hub/
├── app.py                  # Main Streamlit app (1,150 lines)
├── requirements.txt        # Python dependencies
├── README.md
└── .streamlit/
    └── config.toml         # Dark theme + server config
```

---

## Data Sources

| Topic | Source |
|-------|--------|
| Crime | SAPS Annual Crime Report 2023/24 |
| Property | Lightstone · FNB Property Barometer · PropStats |
| Fraud | SABRIC Annual Report 2023 |
| Employment | Stats SA QLFS Q3 2024 |
| Energy | Eskom · EskomSePush · NERSA |
| Finance | SARB Monetary Policy · Stats SA CPI |
| Health | SANAC · DHIS2 · NDOH |
| Education | Department of Basic Education NSC 2024 |
| Forex | open.er-api.com (live) · SARB |
| Water | DWS Dam Levels · COGTA |

---

## Roadmap

- [x] All 10 topic dashboards with charts & KPIs
- [x] AI Q&A panel per topic (Claude API)
- [x] Suggested questions per topic
- [x] Multi-turn conversation with session history
- [x] Province-aware AI responses
- [x] Dark theme (config.toml)
- [ ] Live SAPS API scraper (quarterly update)
- [ ] Suburb-level crime heat map (Folium/pydeck)
- [ ] Email/WhatsApp alerts for dam levels & crime spikes
- [ ] User accounts + saved comparisons

---

Built by **Zolile Nonzapa** | SA Insight Hub v2.0
