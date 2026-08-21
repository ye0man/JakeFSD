# JakeFSD

> Open-source, local-first IDE for data pipelines. Design with AI, run deterministically.

JakeFSD is a desktop application that helps data analysts and code-light technical users design, generate, and iterate on ETL/ELT pipelines through natural-language conversation. The AI assists at **design time**; the resulting pipeline runs deterministically, so your outputs are repeatable and inspectable.

- **Local-first:** Pipelines run on your machine by default using Python, SQL, DuckDB, and SQLite.
- **Cloud-ready:** At scale, JakeFSD emits infrastructure-as-code and cloud-native artifacts for your own AWS, Databricks, Snowflake, or BigQuery accounts.
- **Open source:** Apache-2.0.

## Docs

- [`docs/DESIGN.md`](./docs/DESIGN.md) — product thesis, architecture, connector contract, MVP scope, and technology stack.
- [`docs/ROADMAP.md`](./docs/ROADMAP.md) — milestones and task breakdown from MVP to v1.0 full release.

## Stack

| Layer | Technology |
|---|---|
| Desktop shell | Tauri (Rust core + React/TypeScript UI) |
| Frontend | React + TypeScript |
| Pipeline runtime & CLI | Python 3.11+ |
| CLI framework | Typer |
| LLM abstraction | LiteLLM (OpenAI, Anthropic, OpenRouter, local models) |

## Project Layout

```
JakeFSD/
├── src/                    # React frontend
├── src-tauri/              # Tauri Rust app
├── python/                 # Python runtime + CLI
│   └── jakefsd/
├── docs/                   # DESIGN.md and ROADMAP.md
└── README.md
```

## Prerequisites

- [Node.js](https://nodejs.org/) 20+ and npm
- [Rust](https://www.rust-lang.org/tools/install) (required by Tauri)
- [Python](https://www.python.org/) 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip for Python dependencies

## Development Setup

### 1. Clone the repo

```bash
git clone https://github.com/ye0man/JakeFSD.git
cd JakeFSD
```

### 2. Install Python runtime

Using `uv`:

```bash
cd python
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

Using `pip`:

```bash
cd python
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Verify the CLI:

```bash
jakefsd --version
```

### 3. Install frontend dependencies

From the repo root:

```bash
npm install
```

### 4. Run the desktop app in dev mode

```bash
npm run tauri dev
```

This starts the Vite dev server and the Tauri desktop window. The React frontend can invoke the Python runtime through Tauri commands.

## Status

Early implementation. The first milestone (MVP: local batch pipelines) is tracked in GitHub Issues and Milestones.

## License

Apache-2.0. See [`LICENSE`](./LICENSE).
