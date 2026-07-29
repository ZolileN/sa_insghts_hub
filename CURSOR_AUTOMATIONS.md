# Cursor Automations — scheduled data refresh

Use [Cursor Automations](https://cursor.com/automations) to run scrapers on a schedule via Cloud Agents. No VPS, GitHub Actions, or cron-job.org required.

**Flow:** Cloud Agent → `./scripts/cursor_agent_refresh.sh` → `git push origin master` → Vercel redeploys.

---

## Prerequisites

1. **Cursor plan** with Cloud Agents + Automations (Pro or above).
2. **GitHub** connected with **read-write** access to this repo ([Integrations](https://cursor.com/dashboard/integrations)).
3. **Cloud environment** for `ZolileN/sa_insghts_hub` ([Environments](https://cursor.com/dashboard/cloud-agents#environments)) — this repo’s environment should install Python deps (`pip install -r requirements.txt`).
4. **Branch protection:** `master` must allow pushes from the Cursor GitHub app (or your account for private automations). If protected, use PR workflow instead (see below).

---

## Create four automations

Open [cursor.com/automations/new](https://cursor.com/automations/new) for each row below.

| Name | Schedule (cron, UTC) | Prompt file |
|------|----------------------|-------------|
| Libo — realtime data | `*/30 * * * *` (every 30 min) | `automations/realtime.prompt.txt` |
| Libo — weekly water | `0 6 * * 1` (Mon 06:00) | `automations/weekly.prompt.txt` |
| Libo — monthly topics | `0 5 1 * *` (1st of month 05:00) | `automations/monthly.prompt.txt` |
| Libo — quarterly full | `0 4 1 1,4,7,10 *` (Jan/Apr/Jul/Oct 04:00) | `automations/quarterly.prompt.txt` |

### Settings (each automation)

| Setting | Value |
|---------|--------|
| Repository | `github.com/ZolileN/sa_insghts_hub` |
| Branch | `master` |
| Model | Cheapest/fastest available (task is shell-only) |
| Pull request creation | **Off** (direct push to `master` for Vercel) |
| Computer use | Off (not needed) |

Copy the prompt from the linked file in this repo (or paste from sections below).

---

## Prompts (copy-paste)

### Realtime (`forex` + `energy`)

```
Run data refresh only. Do not edit source code.

1. Ensure dependencies: if `.venv` is missing, run `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2. Run: `./scripts/cursor_agent_refresh.sh realtime`
3. That script runs forex + energy scrapers and pushes to `origin/master` if JSON changed.
4. If the script exits 0 with "No changes to commit", report success with no deploy needed.
5. If git push fails, report the error. Do not modify files outside `data/` or `logs/`.
6. Do not open a pull request — changes must land on `master` for Vercel.
```

### Weekly (`water`)

```
Run data refresh only. Do not edit source code.

1. Ensure dependencies: if `.venv` is missing, run `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2. Run: `./scripts/cursor_agent_refresh.sh weekly`
3. That script runs the water scraper and pushes to `origin/master` if JSON changed.
4. DWS may fail outside South Africa — if scraper fails but script exits 0 with no changes, report that as acceptable.
5. Do not open a pull request — push must land on `master`.
```

### Monthly (`finance`, `property`, `employment`, `health`)

```
Run data refresh only. Do not edit source code.

1. Ensure dependencies: if `.venv` is missing, run `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2. Run: `./scripts/cursor_agent_refresh.sh monthly`
3. That script runs finance, property, employment, health scrapers and pushes to `origin/master` if JSON changed.
4. Do not open a pull request — push must land on `master`.
```

### Quarterly (all 10 topics)

```
Run data refresh only. Do not edit source code.

1. Ensure dependencies: if `.venv` is missing, run `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2. Run: `./scripts/cursor_agent_refresh.sh quarterly`
3. That script runs all 10 scrapers (parallel, up to 30 min) and pushes to `origin/master` if JSON changed.
4. Do not open a pull request — push must land on `master`.
```

---

## On-demand refresh

Start a Cloud Agent anytime with the same prompts, or ask: *“Run `./scripts/cursor_agent_refresh.sh quarterly` and push data.”*

---

## Billing

Each scheduled run is a **Cloud Agent run** billed at API rates for the model you choose. Use a small/fast model — the agent only runs shell commands.

Docs: [Automations](https://cursor.com/docs/cloud-agent/automations.md) · [Pricing](https://cursor.com/docs/models-and-pricing.md)

---

## If `master` is branch-protected

1. Turn **Pull request creation** **On** in the automation.
2. Change prompts to: run the refresh script, then open a PR instead of pushing.
3. Enable auto-merge on the repo, or merge PRs manually.

---

## Alternatives

| Method | Doc |
|--------|-----|
| Manual on your machine | [CRON_SETUP.md](CRON_SETUP.md) |
| Server crontab | `cron_manager.sh install` |
| cron-job.org webhook | `webhook_server.py` + `CRON_SETUP.md` |

GitHub Actions scraping is **disabled** in this repo.
