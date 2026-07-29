# AGENTS.md

## Cursor Cloud specific instructions

SA Insight Hub is a single-service Streamlit dashboard (`app.py`) backed by cached
JSON in `data/*.json`, plus optional data scrapers (`run_scrapers.py` +
`scrapers/`). There is no build step, no test suite, and no linter configured in
this repo.

### Running the app (main service)
- Start the dashboard with `python3 -m streamlit run app.py`. Use `python3 -m streamlit`
  because the `streamlit` console script installs to `~/.local/bin`, which is not on PATH.
- It serves on `http://localhost:8501`. Standard run command is documented in `README.md`.
- The dashboard renders fully from the committed `data/*.json` fallback files, so it works
  with no network access, no API keys, and without running any scraper first.

### Scrapers (optional)
- `python3 run_scrapers.py` fetches live South African public data; `--dry-run`,
  `--topics <name...>`, and `--parallel` are supported (see `README.md`).
- Running scrapers overwrites `data/*.json` and `data/manifest.json` (these files ARE
  committed, despite the README implying `data/` is git-ignored). Revert scraper-caused
  edits with `git checkout -- data/` unless you intend to commit refreshed data.
- Scrapers hit external gov/finance sites; individual topics may fail if a source is down
  or blocked. The app still works from cached data.

### AI Q&A panel
- The bottom-of-page Claude Q&A panel needs an Anthropic API key (entered in the sidebar
  or via `.streamlit/secrets.toml`). It is optional; all dashboards/charts work without it.

### Notes
- `runtime.txt` pins python-3.11 (for Streamlit Cloud); the dev VM runs Python 3.12, which
  works fine.
