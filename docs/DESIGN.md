# JakeFSD — Full Stack Data Harness

> *Open-source, local-first IDE for data pipelines. Design with AI, run deterministically.*

---

## Problem & User

**User:** Data analysts, operations generalists, and code-light technical people who need reliable data pipelines without becoming data engineers.

**Pain:** Building even a simple pipeline today means stitching together sources, transforms, schedules, storage, and outputs across half a dozen tools. Most "AI data" products skip the pipeline entirely and ask an LLM to generate a report on demand — which is fast, expensive, and unrepeatable. Hallucinated metrics, drift, and opaque prompts make that approach unsuitable for anything operational.

**JakeFSD's answer:** Use an AI agent only at **design time** to plan and generate a deterministic pipeline. After generation, the pipeline runs the same way every time. The analyst gets an editable, inspectable, versionable workflow — not a chatbot answer.

---

## Product Definition

JakeFSD is an open-source, local-first desktop IDE for data pipelines. A conversational AI agent (the **Chief Data Architect**) helps the user design, generate, and iterate on ETL/ELT pipelines. Pipelines execute deterministically.

- **Small workloads:** generated code runs locally in the app (Python, SQL, DuckDB/SQLite).
- **Large workloads:** JakeFSD emits configs and code that deploy into the user's own cloud accounts (AWS, Databricks, Snowflake). JakeFSD remains the generator and monitor; it does not become a hosted execution platform.

### Golden Path

1. Analyst opens the desktop app and describes what they need in the chat panel.
2. The Chief Data Architect proposes a pipeline: sources, transforms, storage, and output.
3. The analyst confirms or edits the proposal on the visual canvas.
4. JakeFSD generates deterministic code and configuration.
5. The pipeline runs locally at small scale, or is emitted for the user's cloud platform at enterprise scale.
6. The analyst can inspect, rerun, schedule, and iterate from the same IDE.

### Project Information

| Property | Value |
|---|---|
| License | Apache-2.0 |
| Default LLM providers | OpenAI, Anthropic, OpenRouter; local models supported |
| Distribution | Open-source desktop app + CLI |

---

## Core Concepts

### Design Time vs. Runtime

JakeFSD separates AI-assisted **design time** from deterministic **runtime**:

| Design Time (AI-assisted) | Runtime (deterministic) |
|---|---|
| Chat to describe intent and refine plan | Generated Python, SQL, YAML, Terraform |
| Propose connectors and transformations | Local runner or emitted cloud configs |
| Ask clarifying questions and suggest defaults | Schedule, execute, retry, log runs |
| Surface explanation and alternatives | Produce outputs, raise alerts, write errors |

No LLM touches actual data rows at runtime.

### The Chief Data Architect

The **Chief Data Architect** is the orchestration layer, not a single monolithic model call. Internally it is a stateful planner that:

1. Parses user intent and project context.
2. Decides what is missing and asks for it, or proposes assumptions.
3. Selects connector templates and stage implementations.
4. Generates a draft pipeline as an editable graph.
5. Produces the final runnable artifact.

It exposes its behavior to the user as a teammate in the chat pane: *"Looks like you want a weekly SaaS metrics digest. I suggest DuckDB for storage, an HTML report emailed to you, and a scheduled run every Monday at 8am. Want to tweak?"*

### Pipeline Model

A pipeline is a directed acyclic graph (DAG) of **stages** connected by **streams**. Each stream has a schema contract.

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Collect │────▶│  Clean  │────▶│Transform│────▶│  Load   │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
        \                                        /
         \                                      /
          \────────────── Report ◄─────────────/
```

A stage is defined by:
- **Type**: one of Collect, Clean, Transform, Load, Analyze, Report.
- **Connector**: the concrete implementation used.
- **Configuration**: inputs required by the connector.
- **Input schema**: what the stage expects to receive.
- **Output schema**: what the stage produces.
- **Mode**: `batch` or `stream`.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      DESKTOP APPLICATION                     │
│  ┌─────────────┐    ┌─────────────────────┐   ┌──────────┐ │
│  │ Chat Pane   │◄──▶│ Chief Data          │   │ Canvas   │ │
│  │             │    │ Architect & Planner │   │ View     │ │
│  └─────────────┘    └─────────────────────┘   └──────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ generates / edits
┌───────────────────────────▼─────────────────────────────────┐
│                    Pipeline Manifest                        │
│  YAML/TOML DAG + generated Python modules + SQL files         │
└───────────────────────────┬─────────────────────────────────┘
                            │ executes / emits
            ┌───────────────┴───────────────┐
            ▼                               ▼
┌───────────────────────┐       ┌───────────────────────────┐
│    LOCAL RUNTIME      │       │     CLOUD EMITTER         │
│  • Python executor    │       │  Terraform / IaC          │
│  • DuckDB / SQLite    │       │  dbt / Spark / Snowflake   │
│  • Cron scheduler     │       │  Airflow / Dagster DAGs     │
│  • Local dashboard    │       │  Deployed to user account   │
└───────────────────────┘       └───────────────────────────┘
```

### Components

| Component | Responsibility |
|---|---|
| **Chat Pane** | Natural-language session with the Chief Data Architect; tie intent to concrete pipeline changes. |
| **Canvas** | Visual DAG; nodes are stages, edges are streams; click to inspect or edit config. |
| **Planner / Orchestrator** | Stateful design-time logic; drives generation, handles clarification, applies learned preferences. |
| **Pipeline Manifest** | Declarative project file: DAG, connectors, configs, generated code references. |
| **Local Runtime** | Executes generated Python and SQL against DuckDB/SQLite with a built-in scheduler. |
| **Cloud Emitter** | Transforms the manifest into user-account IaC and cloud-native code for large-scale targets. |
| **Connector Registry** | Library of reusable source, transform, load, and output modules with contracts. |

---

## Connector Contract

Connectors are the pluggable units JakeFSD uses at each stage. Every connector declares:

| Field | Meaning |
|---|---|
| `name` | Stable identifier, e.g., `csv_file`, `stripe_api`, `duckdb_load` |
| `stage_type` | `collect`, `clean`, `transform`, `load`, `analyze`, `report` |
| `input_schema` | Expected upstream schema, or `null` for sources |
| `output_schema` | Produced schema, including typed fields |
| `config_schema` | JSON Schema of required/optional parameters |
| `auth_type` | `none`, `api_key`, `oauth2`, `sasl`, `iam_role`, etc. |
| `mode` | `batch` or `stream` |
| `retry_policy` | Default retry/backoff behavior |
| `example` | Minimal working example of config and output |

The orchestrator chooses connectors by matching intent, scale, and cost constraints. Connectors are replaceable: a pipeline built for CSV + DuckDB can be re-targeted to S3 + Snowflake by swapping source and load connectors, provided schema contracts are satisfied.

---

## Pipeline Stages

JakeFSD organizes work into six stage types. Each stage is ultimately a deterministic transformation applied by a connector.

| Stage | Role | Example Connectors |
|---|---|---|
| **Collect** | Ingestion from files, APIs, databases, streams, webhooks | `csv_file`, `json_api`, `postgres_reader`, `webhook_receiver`, `kafka_stream` |
| **Clean** | Validate, dedupe, cast types, handle nulls | Schema validation, duplicate removal, normalization rules |
| **Transform** | Shape data: joins, aggregations, feature engineering, windowing | Pandas/SQL operations, dbt models, generated Python functions |
| **Load** | Persist to storage | `sqlite_load`, `duckdb_load`, `s3_parquet`, `snowflake_load` |
| **Analyze** | Compute summaries, detect anomalies, generate query views | Statistical summaries, trend models, anomaly flags |
| **Report** | Deliver output | `html_dashboard`, `csv_export`, `gsheet_writer`, `webhook_trigger`, `email_digest` |

A connector may be **native** (ships with JakeFSD), **generated** (produced by the AI for a custom API), or **third-party** (installed from a registry).

---

## Output Decision Framework

The Chief Data Architect proposes an output shape based on what the data is *for*:

| Purpose | Description | Typical Outputs |
|---|---|---|
| **DECIDE** | "I need to understand if X is happening" | Static HTML report, PDF, ad-hoc CSV export |
| **TRACK** | "I need to monitor X over time" | Scheduled email/GSheet, BI dashboard, live shared view |
| **ACTIVATE** | "I need to trigger something automatically" | Webhook, Slack alert, Zapier/Make action, script trigger |

These map to implementation choices:

- **DECIDE** → read-heavy, small audience, low cadence → HTML/PDF/CSV.
- **TRACK** → recurring summary for a team → scheduled GSheet, dashboard with auto-refresh.
- **ACTIVATE** → event-driven threshold → webhook or automation connector on a condition.

### Diagnostic Questions

The Chief Data Architect uses this information but does not require the analyst to know the answer. It proposes defaults and asks for confirmation:

1. **Audience** — Just you? Team? Leadership? External?
2. **Cadence** — One-time, recurring, or near real-time?
3. **Decision mode** — Human review required, or automated action?
4. **Freshness** — Historical batch, incremental load, or streaming?

---

## Scale Tiers

Scale is not only about data volume. It is about concurrency, latency, sharing, operational burden, and cost. JakeFSD scales by changing the *runtime target*, not by becoming a hosted platform.

| Tier | Triggering Conditions | Runtime Target | JakeFSD Output |
|---|---|---|---|
| **Local / Single Analyst** | MB–GB, single user, batch, low cost | Local Python + DuckDB/SQLite + built-in scheduler | Runs inside the app; generates local reports |
| **Team / Recurring** | GBs, multiple users, scheduled jobs, shared storage | Postgres/TimescaleDB + Airflow/Dagster on user infra | Emits runnable Python + SQL + DAG configs |
| **Enterprise / TB+** | TBs, streaming, strict SLAs, org-wide governance | Snowflake/BigQuery/S3 + Spark/Databricks + IaC | Emits Terraform/IaC + optimized Spark/SQL + CI/CD scaffolding |

At every tier the *design principles* stay the same; only the *target runtime* and *connector choices* change. A pipeline can start locally and later be re-emitted to a cloud target as requirements grow.

### Auto-Selection Heuristics (advisory)

The orchestrator may suggest a tier based on:
- Estimated data volume from a sampled preview.
- Recurrence and freshness requirements.
- Sharing and team concurrency needs.
- User-stated cost or latency constraints.

The user retains final control and can override any suggestion.

---

## Interfaces

### Primary Interface: Desktop Application

The desktop app combines three views:
- **Chat pane:** describe intent, review proposals, approve changes.
- **Canvas:** visual DAG of the current pipeline; inspect/reconfigure nodes.
- **Preview pane:** sample output at any stage, run logs, run history.

Think: *VS Code for data pipelines* — open it and it works locally, with CLI power available when needed.

### Secondary Interface: CLI

A first-class CLI for scaffolding, testing, and CI/CD workflows:

```bash
jakefsd init <project-name>            # scaffold new project
jakefsd connect <source-type>          # add and test a data source
jakefsd plan                           # generate/visualize proposed DAG
jakefsd run [--stage <stage>]          # execute pipeline, optionally one stage
jakefsd preview <stage>                # preview output of a stage
jakefsd schedule                       # manage local cron-like schedules
jakefsd export --format yaml|toml      # serialize pipeline to config
jakefsd emit --target aws|databricks   # generate cloud IaC/code
jakefsd deploy --target <profile>      # deploy emitted artifacts to user account
```

### Config Format

YAML/TOML is the serialization format for the pipeline manifest, not a parallel primary UI. A generated pipeline can be reviewed, hand-edited, and committed to version control.

```yaml
pipeline:
  name: "stripe_monthly_metrics"
  version: "0.1.0"
  schedule: "0 8 * * MON"

  source:
    connector: stripe_api
    config:
      api_key: "${STRIPE_API_KEY}"
      event_filter: "charge.succeeded"

  transform:
    connector: sql_transform
    file: "./sql/monthly_mrr.sql"

  load:
    connector: duckdb_load
    config:
      database: "./data/metrics.duckdb"
      table: "monthly_mrr"

  report:
    connector: html_dashboard
    config:
      template: "./templates/mrr.html"
      out: "./reports/monthly_mrr.html"
```

---

## Data Privacy & Security

JakeFSD is built on a strict separation between metadata and data.

| Category | What it includes | Where it goes |
|---|---|---|
| **Metadata / schemas** | Source URLs, table names, column names, types, pipeline structure | May be sent to the LLM provider during design-time planning. |
| **Credentials** | API keys, tokens, password material | Stored in the OS credential store or local encrypted keystore; never sent to LLM. |
| **Data rows** | Actual values, records, payloads | Processed only by the user's chosen runtime (local or user-owned cloud). Never sent to LLM unless explicitly sampled for preview by user. |

### Credentials

- Local runs: credentials are resolved from environment variables or the OS keychain.
- Cloud targets: credentials live in the user's cloud secrets manager or IAM role; JakeFSD emits references, not values.

### Privacy Modes

- **Connected mode (default):** uses OpenAI/Anthropic/OpenRouter for planning.
- **Local mode:** uses a compatible local model (e.g., via Ollama/LM Studio) for design-time planning. No data leaves the machine.

---

## Orchestrator Behavior

The Chief Data Architect follows these behavior rules:

1. **Infer from context.** Reuse already-configured sources, learned defaults, and past decisions before asking again.
2. **Propose, don't quiz.** Surface a concrete pipeline proposal and let the user confirm or edit, rather than asking a long questionnaire.
3. **Explain tradeoffs.** When scale, cost, or connector options differ, state the pros and cons in plain language.
4. **Keep artifacts editable.** Generated code and config are not black boxes; the user can inspect and modify them.
5. **Prefer local first.** Suggest a local runtime unless the use case clearly requires cloud scale.
6. **Remember preferences.** Store per-user preferences (default output format, cadence, cloud profile, etc.) in a local project store, not in the cloud.

---

## Design Principles

1. **Deterministic output over stochastic answers.** AI designs the pipeline; the pipeline produces repeatable results.
2. **Local-first.** Runs entirely on the user's machine by default; cloud is opt-in.
3. **No lock-in.** Every generated artifact is plain code, SQL, YAML, or standard IaC. Users can walk away.
4. **Analyst-friendly UX.** Natural-language chat and visual canvas make pipelines approachable without hiding what is happening.
5. **Scale by emission, not hosting.** Enterprise scale is achieved by emitting configs and code for the user's own infrastructure.
6. **Open source.** Apache-2.0; contribution and extension are encouraged.

---

## MVP Scope

The v0.1 milestone is intentionally narrow. It proves the core loop: chat → plan → generate → run locally.

**In scope for v0.1:**
- One pipeline per project.
- Chat-based design with the Chief Data Architect.
- Visual canvas showing the pipeline DAG.
- Sources: local CSV/JSON files, one REST API with API-key auth.
- Transform: generated Pandas/SQL operations editable by the user.
- Storage: DuckDB or SQLite.
- Output: CSV, local HTML report, or Google Sheets.
- Scheduling: local cron-like runner.

**Out of scope for v0.1:**
- Cloud deployment emission.
- Streaming connectors.
- Multi-source joins.
- Multi-user collaboration/permissions.
- Real-time dashboards.
- Data quality/observability beyond basic run logs.

See [ROADMAP.md](./ROADMAP.md) for how JakeFSD grows from this MVP to full release.

---

## Out of Scope & Non-Goals

To keep the product focused, JakeFSD does **not** aim to:

1. Replace existing best-of-breed tools (dbt, Airflow, Snowflake, etc.). It integrates with and generates code for them.
2. Become a hosted SaaS execution platform. Runtime stays local or on the user's own cloud.
3. Provide general-purpose BI or notebook exploration. Dashboards are purpose-built outputs of pipelines, not open-ended analytics.
4. Assume real-time/streaming by default. Streaming is supported at later milestones.
5. Store user data centrally. Data and credentials remain under user control.

---

## Glossary

| Term | Definition |
|---|---|
| **Chief Data Architect** | The conversational AI planner/orchestrator inside JakeFSD. |
| **Connector** | Reusable module that implements one stage for a specific source, transform, or destination. |
| **Pipeline Manifest** | The declarative project file that defines the DAG, connectors, and configs. |
| **Stage** | A node in the pipeline DAG: Collect, Clean, Transform, Load, Analyze, Report. |
| **Cloud Emitter** | Component that converts a local-ready manifest into user-account IaC and code. |
| **Stream** | A typed data flow between two stages, described by an output schema. |
