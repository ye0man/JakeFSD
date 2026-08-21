# JakeFSD Roadmap

> *How JakeFSD grows from a local batch pipeline IDE to a full-stack, open-source data harness capable of emitting enterprise-grade pipelines.*

---

## Milestone Summary

| Milestone | Theme | Goal | Status |
|---|---|---|---|
| **M1** | MVP | Prove the chat → plan → generate → run-local loop | Planned |
| **M2** | Production Local | Make local pipelines reliable, multi-source, and schedulable | Planned |
| **M3** | Cloud Emit | Generate configs and code for user-owned cloud targets | Planned |
| **M4** | Team & Governance | Collaboration, versioning, data quality, and lineage | Planned |
| **M5** | Full Release | Streaming, enterprise auth, CI/CD hooks, and enterprise connectors | Planned |

---

## M1 — MVP: Local Batch Pipelines

**Duration:** Shortest milestone; the first shippable release.

### Goals

- Validate the core design loop: describe intent in chat, review the generated DAG, run the pipeline locally.
- Demonstrate deterministic output from AI-generated code.
- Keep scope narrow enough to build and test quickly.

### In Scope

- Desktop app with chat pane + visual canvas.
- One pipeline per project.
- **Sources:** local CSV and JSON files; one simple REST API with API-key authentication.
- **Transforms:** AI-generated Pandas or SQL operations; user can edit.
- **Storage:** DuckDB or SQLite.
- **Outputs:** CSV export, local HTML report, or Google Sheets write.
- **Scheduling:** local cron-like runner.
- Basic preview of stage outputs.

### Example Projects

These are realistic pipelines a user should be able to complete with M1:

#### Project 1 — Monthly SaaS Metrics Report
- **Data:** Stripe charges API + local CSV of customer sign-up dates.
- **Pipeline:** collect charges, join with customer file, aggregate MRR per month.
- **Output:** local HTML dashboard with MRR trend chart + CSV download.

#### Project 2 — Lead Scoring Sheet
- **Data:** local CSV of inbound leads + Clearbit/HubSpot enrichment API.
- **Pipeline:** read leads, call enrichment API for each company domain, dedupe rows, score by company size and intent signals.
- **Output:** updated Google Sheet with score column.

#### Project 3 — Personal Expense Tracker
- **Data:** monthly bank CSV exports stored in a local folder.
- **Pipeline:** union files, normalize transaction descriptions, categorize transactions by rules.
- **Output:** HTML report with monthly totals by category.

### Success Criteria

- A new user completes one example project end-to-end in under 30 minutes without writing code.
- Re-running the pipeline produces the same output given the same inputs.
- Generated artifacts (manifest, SQL/Python) are editable and readable.

### Out of Scope

- Cloud deployment.
- Multiple sources in one pipeline.
- Streaming or real-time processing.
- Multi-user features.
- Advanced error recovery.

---

## M2 — Production Local: Reliable Recurring Pipelines

**Theme:** Make local pipelines robust enough for daily/weekly operational use.

### Goals

- Support pipelines with multiple sources and incremental loads.
- Add observability so analysts can trust their scheduled runs.
- Handle common failures without manual intervention.

### In Scope

- Multi-source pipelines with joins and unions.
- Incremental loads based on a watermark column or checkpoint.
- Built-in retry and backoff policies.
- Run history, logs, and basic data-diff views.
- Notifications via email or webhook on failure or completion.
- Source discovery: auto-detect schemas, preview samples.
- Connector-level tests: validate a connector config before using it.
- Secret management: API keys stored in OS keychain or environment variables.

### Example Projects

#### Project 4 — Weekly Investor Update
- **Data:** Stripe revenue, bank balance (CSV), and web traffic (API or CSV).
- **Pipeline:** join weekly snapshots, compute week-over-week growth, flag anomalies.
- **Output:** emailed HTML report every Monday at 8 AM.

#### Project 5 — Inventory Alert
- **Data:** Shopify product API (inventory levels) + supplier lead time CSV.
- **Pipeline:** compare stock levels to reorder thresholds, calculate days of supply.
- **Output:** Slack webhook alert when items fall below threshold.

---

## M3 — Cloud Emit: Generate for User-Owned Cloud

**Theme:** Bridge from a local working prototype to a production cloud pipeline.

### Goals

- Let users keep the same design-time UX but target cloud runtimes.
- Produce clean, portable code and infrastructure-as-code artifacts.
- Never host user data on JakeFSD infrastructure.

### In Scope

- Cloud targets: AWS, Databricks, Snowflake, BigQuery, GCP.
- Emit artifacts:
  - Terraform or Pulumi IaC for storage/compute/scheduler.
  - dbt project structure for transformations.
  - Python/PySpark jobs for heavy processing.
  - Airflow or Dagster DAG definitions.
- CLI commands: `jakefsd emit --target` and `jakefsd deploy --profile`.
- Cloud credential profiles; integrations with IAM roles, service principals, etc.
- Cost/size estimation before emitting.
- A cloud preview mode that runs a sample of data on the target.

### Example Projects

#### Project 6 — Marketing Attribution at Scale
- **Data:** raw click-stream events in S3 + ad spend CSV + CRM accounts.
- **Pipeline:** load to Snowflake, join click events to conversions, attribute revenue to campaigns.
- **Output:** dbt models in Snowflake + Tableau-ready export; orchestrated by Airflow.

#### Project 7 — E-Commerce Analytics Warehouse
- **Data:** Shopify orders API, Stripe payments API, warehouse inventory CSV.
- **Pipeline:** incrementally load into Postgres/DuckDB, build fact/dimension models.
- **Output:** BI-ready tables + scheduled dbt runs.

---

## M4 — Team & Governance: Collaboration and Trust

**Theme:** Move from a personal tool to a team-grade product.

### Goals

- Enable sharing, review, and governance of pipelines.
- Add data-quality checks and lineage so teams can trust what runs.

### In Scope

- Git integration: commit, diff, merge, and review pipeline manifests.
- Project versioning and rollback.
- Connector registry: publish, share, and install custom connectors.
- User roles and permissions (owner, editor, viewer) for local projects.
- Data-quality framework: Great Expectations-style checks per stage.
- Column-level lineage graph.
- Audit log of who changed what and when.
- SSO/LDAP authentication for enterprise installations.

### Example Projects

#### Project 8 — Finance-Controlled Reporting Pipeline
- **Data:** NetSuite/SQL accounting data + manually maintained mapping sheets.
- **Pipeline:** data-quality checks before every load, version-controlled SQL models, lineage view.
- **Output:** board-ready report with sign-off trail and audit log.

#### Project 9 — Shared Customer 360 Project
- **Data:** multiple team-owned sources (CRM, support, product usage).
- **Pipeline:** shared connector registry, role-based access, data contracts per source.
- **Output:** governed DuckDB/Snowflake model consumed by multiple analysts.

---

## M5 — Full Release: Enterprise Scale and Streaming

**Theme:** Complete the vision: a single harness that scales from a laptop to an ad server.

### Goals

- Support high-throughput streaming and event-driven pipelines.
- Provide all enterprise hooks needed for production deployments.
- Offer a stable, well-documented platform and connector ecosystem.

### In Scope

- Streaming connectors: Kafka, Kinesis, Pub/Sub, Redpanda.
- Real-time transformations with windowing and stateful operators.
- CI/CD hooks: run pipeline tests, previews, and deployments from GitHub/GitLab Actions.
- Advanced orchestration: emit to Dagster, Airflow, Prefect, Mage.
- Enterprise connectors: Salesforce, HubSpot, Workday, SAP, ERPs.
- Advanced monitoring: data freshness SLAs, anomaly detection, alerting rules.
- Multi-cloud and hybrid deployments.
- Stable public API for extending the desktop app and CLI.
- Full documentation, example gallery, and contributor guidelines.

### Example Project

#### Project 10 — Ad Server Event Pipeline (Enterprise TB-scale)
- **Data:** millions of bid/impression/click events streamed from an ad server.
- **Pipeline:** ingest via Kafka/Kinesis, normalize and enrich in Spark/Databricks, aggregate to KeyDB/Snowflake.
- **Output:** real-time dashboards (Grafana/Metabase) and hourly reconciliation reports.

---

## Cross-Milestone Dependencies

| Dependency | Unblocked At |
|---|---|
| Connector contract finalized | M1 |
| Local runtime stable | M2 |
| Manifest versioning scheme | M2 |
| Cloud credential profiles | M3 |
| IaC harness | M3 |
| Data-quality check framework | M4 |
| Connector registry / packaging | M4 |
| Streaming runtime contract | M5 |

---

## Release Labels

- **M1–M2:** Early Access / Local-only
- **M3–M4:** Public Beta / Cloud-ready
- **M5:** Stable v1.0 / Full Release

---

## Decisions for Later

The roadmap intentionally defers some decisions until more is known:

1. **Packaging and distribution.** Exact installer formats and update mechanisms will be chosen during M1.
2. **Connector marketplace.** Governance model for third-party connectors will be finalized during M4.
3. **Paid support / hosting.** JakeFSD itself remains open source under Apache-2.0; optional support or managed-connector offerings are deferred to post-v1.0.
4. **Mobile companion app.** Not currently planned; will revisit only after desktop and CLI are stable.
