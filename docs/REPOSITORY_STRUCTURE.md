# Repository Structure

This repository is organized so that production runtime code, content-generation infrastructure, tests, documentation, and historical working artifacts are clearly separated.

## Production entry points

- `app.py` — Flask application entry point and top-level routes.
- `config.py` — application configuration and environment handling.
- `models.py` — primary database models and initialization logic.
- `run_production.bat` / `scripts/` — production and operational entry scripts.

## Core application and generation stack

- `core/` — shared domain logic, generation orchestration, import pipelines, healers, services, and common infrastructure.
- `skills/` — published executable problem generators/checkers used by the application.
- `generators/` — reusable generator implementations.
- `validators/` — validation components used by generation and runtime workflows.
- `gencode_closed_loop/` — closed-loop generation/evaluation workflow.
- `agent_skills/`, `agent_skills_v2/`, `agent_skills_v3/` — skill specifications and generation/evaluation metadata.
- `agent_tools/` — tooling for benchmark, validation, analysis, and skill maintenance.

## Adaptive learning and ML

- `core/adaptive/` — production progression, PPO routing, deterministic fallback, and remediation logic.
- `models/` — model artifacts required by adaptive-learning workflows.
- `runtime/` — runtime services and publish/runtime state used by the application.
- `知識圖譜/`, `自適應複習/` — retained knowledge-graph and historical adaptive-learning assets.

## Data and curriculum assets

- `datasource/` — source/reference data used by import and generation workflows.
- `textbook_import/` — textbook import assets and supporting material.
- `configs/`, `config/` — structured configuration and prompt/config registries.

## Web application

- `templates/` — Flask/Jinja templates.
- `static/` — browser assets and question assets.

## Quality assurance

- `tests/` — maintained regression and integration tests. These are part of the project quality gate and should remain version-controlled.
- `reports/` — retained formal audit/evaluation reports. Generated dry-run and local diagnostic outputs are excluded by `.gitignore`.

## Documentation

- `README.md` — project overview and primary entry document.
- `docs/` — long-lived architecture, design, contracts, and operational documentation.
- `AGENTS.md` — repository-level agent/runtime engineering instructions.

## Historical and temporary material

- `temp/archive/` — historical one-off diagnostics, repair scripts, old generated reports, and backup/intermediate artifacts retained only for traceability. Nothing under this area is a production runtime dependency.
- `tmp/`, local `temp/`, caches, test outputs, dependency installs, database backups, and generated diagnostics are excluded from future commits by `.gitignore`.

## Repository hygiene rule

New production code should live in the appropriate maintained module (`core/`, `scripts/`, `tests/`, etc.). One-off probes, migration experiments, generated logs, local exports, and temporary verification artifacts should not be added to the repository root. Keep them under an ignored temporary directory unless they become a maintained part of the system.
