# Siemens Supplier Capability Studio — Streamlit Cloud demo

A runnable **independent student prototype** of Siemens Energy's proposed supplier capability-building workflow, built from the project data and working materials. It is **not an official Siemens platform**, supplier assessment, policy or investment approval system. No real Siemens or supplier records are present in the provided synthetic cases.

## Launch locally (Mac, Windows, Linux)

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On your Mac, if necessary use `python3` instead of `python` in both commands. Streamlit opens a local URL (usually `http://localhost:8501`).

## Deploy on Streamlit Community Cloud

1. Unzip this project. Create a **private GitHub repository** and upload the **contents** of this folder, so `app.py` and `requirements.txt` are at the repository root. Do **not** include credentials or internal Siemens datasets.
2. At [share.streamlit.io](https://share.streamlit.io/), sign in with GitHub and choose *Create app*. Select your repository, branch, and `app.py` as the entrypoint.
3. Deploy. Streamlit installs the packages in `requirements.txt`, runs `app.py`, and provides a `.streamlit.app` URL.
4. In app settings/secrets, set `APP_PASSWORD` to a strong demo password if permitted. `APP_PASSWORD` is a **simple demo gate, not enterprise authentication**. Use approved audience restrictions and hosting policies before sharing.
5. Only add `OPENAI_API_KEY` and enable the optional external model analysis when your organization has authorized that model provider and the data you send. Default mode needs **no API key**.

**Important data warning:** The project includes the 55 question texts extracted from the user-supplied *Supplier Questionnaire Survey and Rating.pdf* in `data/official_questionnaire.json`, and the team's embedded sector research text in `data/benchmark_research.json`. Do **not** publish these files in a public repository or public Streamlit app without confirming the sharing rights and sponsor approval. For a public demonstration, remove or replace those with approved/synthetic versions, or host privately in an environment approved for project content. A private GitHub repository does not, by itself, guarantee that the hosted app or its data is private.

## What's included

| File/path | Purpose |
|---|---|
| `app.py` | Native Streamlit app: all eight stages, supplier portfolio, survey, interventions, business case, agents, research, mock Snowflake, copilot, export/import |
| `engine.py` | Pure Python decision gates, calculations, scoped interventions and source lookups |
| `optional_ai.py` | Optional real three-specialist model calls; cannot override stage gates |
| `data/cases_seed.json` | Four fictional suppliers: capacity ramp, new pre-award investment, yield and resilience |
| `data/criteria.csv` | The project's 16 criteria under A/B/C |
| `data/interventions.json` | 21 screening-stage candidate intervention records with case references and limitations |
| `data/benchmark_research.json` | Four embedded research collections with paragraph-level source locations |
| `data/official_questionnaire.json` | 55 rated questions and the six basic fields from the supplied questionnaire; 16-criterion crosswalk is provisional |
| `data/snowflake_mock.json` | Four fictional supplier snapshots organized around the four Siemens data domains |
| `connectors/snowflake_adapter.py` | **Optional, unconnected**, read-only Snowflake integration template |
| `connectors/VIEW_CONTRACT.sql` | Proposed Snowflake view contract for Siemens IT review |
| `.streamlit/config.toml` | Streamlit theme |
| `.streamlit/secrets.toml.example` | Example secret configuration (not real credentials) |
| `tests/test_engine.py` | Business-case and gate regression checks |

## What actually works

- Each visitor receives four independent synthetic cases **in Streamlit session memory**. Edit any case, advance stage-by-stage and export JSON to resume a case in another session.
- Stage 1 captures business need, Stage 2 records the supplier diagnosis, Stage 3 matches interventions to the 16 criteria with sources, and Stage 4 calculates Siemens expected net value and supplier investment economics.
- Stage 4 uses **four gates**: technical; timing/resources; Siemens economic attractiveness; supplier willingness. The independent `engine.py` logic enforces missing evidence, human shortlist review and simulated financial approval.
- Stage 5 tracks agreement and dual simulated approvals; Stage 6 tracks action completion and evidence; Stage 7 checks measured results and verifier; Stage 8 stores handover and lessons.
- If upstream evidence or financial assumptions change, the engine invalidates recorded downstream stage completions and clears prior simulated financial GO.
- Official survey responses can be recorded on 55 questions (rating 1–5); these are not treated as independently verified diagnoses. Project criterion mapping is illustrative and must be validated with Siemens.
- Benchmark library and candidate interventions have citations to the team's sector documents and working presentation. These are **leads**, not transferability or sponsor approvals.
- The Snowflake demo shows four synthetic sources and can attach a snapshot to a case, which **reopens the assessor gate**. The optional connector is a template, not a live connection.
- The local copilot is an evidence-bounded rules-based explainer. Optional model calls can independently generate A/B/C drafts, but these do **not** make investments or approvals.

## Financial interpretation

```
Siemens expected net value = Potential Siemens gain
                            × P(technical closure)
                            × P(on-time completion)
                            × P(sustained improvement)
                            − Siemens intervention cost
```

The probabilities are **illustrative scenario assumptions**, not learned or calibrated forecasts. The separately displayed supplier balance is an **undiscounted illustrative** sum of supplier-side benefits less CapEx/OpEx. Potential overlap among retained savings, productivity relief, and buyer-funded contributions must be checked before any use in practice.

## Cloud storage & security limitations

- **Session-only**: Streamlit Community Cloud does not give this package durable storage. Closing a session/restarting a deployment may lose edits. Export JSON and re-import later. Different visitors do not overwrite each other's cases.
- **No enterprise authentication**: `APP_PASSWORD` is a lightweight student demo gate; it is not suitable for confidential Siemens information or real supplier records. No user accounts, access approvals, or organization SSO are implemented.
- **No live Snowflake**: read-only connector requires Snowflake admin-approved views, credentials, network policy, and security review. Do not paste credentials into the code or UI.
- **No autonomous decisions**: users must still verify evidence and authorize procurement and investment choices outside the tool. Supplier scores, intervention screening, and financial scenarios are not Siemens policy.

## Suggested walkthrough

Select **Atlas Precision Components**. Open Stage 4 to see the illustrative €12m gain × 60% probability − €2m cost = ~€5.2m net; inspect the separate supplier economic balance. Change an input and observe the prior simulated GO clear. Select **Meridian Thermal Systems**, a new synthetic supplier, to see the pre-award investment and supplier willingness blockers. In **Specialist agents**, inspect different A/B/C intervention leads. In **Snowflake data**, attach a synthetic snapshot and confirm Stage 2 must be reviewed again.
