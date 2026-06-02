---
name: fabric-iq
description: 'Fabric IQ synthetic data demo for Dutch municipal (GGM) traffic and water management on Microsoft Fabric. Use when: setting up Fabric IQ, running the demo, fixing pipeline errors, deploying notebooks, troubleshooting bronze/silver/gold medallion layers, fixing %pip magic errors, debugging Data Factory pipelines, understanding the GGM schema, generating synthetic traffic or water data, configuring lakehouse, Power BI Direct Lake, quality checks, creating ontology, Fabric ontology setup, ontology from semantic model, PowerBIFeatureDisabled, AI Skill on ontology, natural language Q&A on data, GGM concept mapping.'
argument-hint: 'Optional: describe what you want to do (e.g. "fix pipeline error", "explain gold layer")'
---

# Fabric IQ Skill

End-to-end Microsoft Fabric demo for Dutch municipal data using the **Gemeentelijk Gegevensmodel (GGM)**. Generates synthetic traffic & water data through a **bronze → silver → gold** medallion lakehouse, surfaced in Power BI Direct Lake.

## Repo Structure

```
fabric-iq/
├── synth/                   # Python synthetic data generators
│   ├── generators/
│   │   ├── traffic.py       # Verkeer & Vervoer (IV3 2.x)
│   │   └── water.py         # Water & Milieu (IV3 7.x)
│   └── run_generate.py      # CLI entrypoint
├── lakehouse/build.py        # Silver + gold Delta table builder
├── notebooks/
│   ├── 01_bronze_ingest.ipynb
│   ├── 02_silver_curate.ipynb
│   ├── 03_gold_marts.ipynb
│   └── 04_quality_checks.ipynb
├── pipelines/               # Fabric Data Factory pipeline JSONs
├── tests/                   # pytest smoke tests
├── conftest.py              # Root conftest so pytest finds synth/
└── run-demo.ps1             # Full local demo script
```

## Common Tasks

### Create an Ontology from the semantic model
Fabric Ontology (preview) requires F64+ capacity and the tenant setting enabled.
Full step-by-step (concept mapping, relationships, synonyms, AI Skill setup): [ontology-guide](../../../../docs/ontology-guide.md)

Quick path:
1. Admin Portal → Tenant settings → enable **Ontology**
2. Workspace → **New → Ontology** → name `FabricIQ_Ontology`
3. Connect to `FabricIQ_Model` semantic model
4. Map each gold table to a concept (see guide Part 3)
5. Add GGM synonyms (Dutch + English) for Copilot discovery
6. Publish → test with Fabric Copilot or create an **AI Skill**

### Run the full local demo
```powershell
.\run-demo.ps1           # Default 14 days
.\run-demo.ps1 -Days 30  # Custom range
```
If execution policy blocks it: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

### Fix `%pip` magic error in Fabric pipelines
Fabric pipelines **disable `%pip` magic**. Replace any `%pip install ...` cell with:
```python
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "<packages>"], check=True)
```
See [known issues](./references/known-issues.md) for full details.

### Fix `ModuleNotFoundError: No module named 'synth'`
A root-level `conftest.py` must exist so pytest adds the repo root to `sys.path`.
File should exist at `fabric-iq/conftest.py` — create it if missing (even empty).

### Deploy notebooks to Fabric
1. In Fabric workspace, open each notebook and click **Import**
2. Upload from `notebooks/` in order: `01` → `02` → `03` → `04`
3. Attach the `FabricIQ` Lakehouse via the left-hand panel in each notebook
4. Add all 4 notebooks as inputs to the `GGM_Synthetic_TrafficWater` pipeline

### Run notebooks in the correct order
| Step | Notebook | Output |
|------|----------|--------|
| 1 | `01_bronze_ingest` | `bronze_*` Delta tables |
| 2 | `02_silver_curate` | `silver_*` Delta tables |
| 3 | `03_gold_marts` | `dim_*`, `fact_*` Delta tables |
| 4 | `04_quality_checks` | Quality report + assertions |

### Understand the data model
See [GGM schema reference](./references/ggm-schema.md) for domain entities and IV3 mapping.

### Understand the gold layer tables
| Table | Rows (14d) | Purpose |
|-------|-----------|---------|
| `dim_locatie` | ~210 | Road segments + waterways |
| `dim_tijd` | ~340 | Hourly time dimension |
| `fact_verkeer` | ~13k | Hourly vehicle counts per `wegvak` |
| `fact_waterpeil` | ~2.7k | Hourly water level (m NAP) |
| `fact_waterkwaliteit` | ~3.8k | NEN-aligned water quality |
| `fact_cross_domain_alert` | varies | Traffic peaks + water breaches |

## Architecture

```
GGM XMI → schema_catalog.json
                │
                ▼
Faker (nl_NL) → synth/generators → Bronze Delta → Silver Delta → Gold Star Schema
                                                                        │
                                                                        ▼
                                                              Power BI Direct Lake
```

## Key Dependencies
- `faker`, `pandas`, `pyarrow` — synthetic data generation
- `delta-spark` / Spark (in Fabric) — Delta table writes
- `pytest` — smoke tests
- Microsoft Fabric: Data Engineering (Spark), Data Factory, Power BI

## More References
- [**Ontology Guide**](../../../../docs/ontology-guide.md) — Full step-by-step: create Fabric Ontology from FabricIQ_Model
- [Known Issues & Fixes](./references/known-issues.md)
- [GGM Schema](./references/ggm-schema.md)
