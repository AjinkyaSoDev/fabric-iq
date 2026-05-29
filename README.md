# Fabric IQ — Synthetic Data Workflow for Traffic, Transport & Water Management

End-to-end **Microsoft Fabric** POC that generates GGM-aligned synthetic data
for the *Verkeer & Vervoer* (IV3 2.x) and *Water & Milieu* (IV3 7.x) policy
domains, then walks it through a **bronze → silver → gold** medallion into a
**Direct Lake** semantic model ready for Power BI.

The workflow is built on the
[**Gemeentelijk Gegevensmodel (GGM)**](https://github.com/Gemeente-Delft/Gemeentelijk-Gegevensmodel)
by Gemeente Delft — the open-source logical data model for Dutch municipalities.

---

## Why this exists

* Demonstrate a **realistic Dutch municipal data product** without needing real
  (privacy-sensitive) sources.
* Show how the GGM logical model translates into a **Fabric Lakehouse** with
  the medallion pattern.
* Provide a starting point for **Fabric Copilot / AI Skills** demos on a
  domain-rich dataset (cross-domain alerting, anomaly detection, NL Q&A).

## Architecture

```
                    +-----------------------+
   GGM XMI  ──►     |  ggm/extract_schema   |  ──► schema_catalog.json
                    +-----------------------+
                                │
                                ▼
+----------+   synth   +-----------------+   bronze   +----------+   silver   +--------+   gold   +-----------------+
|  Faker   |──────────►| synth/run_gen…  |───────────►| Parquet  |───────────►| Parquet|─────────►| Star schema +    |
|  (nl_NL) |           | traffic, water  |            | per day  |            | typed  |          | cross-domain mart|
+----------+           +-----------------+            +----------+            +--------+          +-----------------+
                                                                                                          │
                                                                                                          ▼
                                                                                       semantic-model/model.bim
                                                                                       powerbi/TrafficWater.pbip
                                                                                       (Direct Lake)
```

## Quickstart (local)

```powershell
cd fabric-iq
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# generate 14 days of synthetic data into bronze, then build silver + gold
python -m synth.run_generate --days 14
python lakehouse\build.py

# run the data-quality smoke tests
pytest tests
```

Or run everything in one shot:

```powershell
.\run-demo.ps1
```

After the run, the gold layer at `lakehouse/gold/` contains:

| Table | Rows (default) | Purpose |
|---|---|---|
| `dim_locatie` | ~210 | Unified dim across road segments + waterways |
| `dim_tijd` | ~340 | Hourly time dimension |
| `fact_verkeer` | ~13k | Hourly vehicle counts per `wegvak` |
| `fact_waterpeil` | ~2.7k | Hourly water level (m NAP) per `watergang` |
| `fact_waterkwaliteit` | ~3.8k | NEN-aligned water-quality readings |
| `fact_cross_domain_alert` | varies | Hours where traffic peaks coincide with water-norm breaches |

## Deploy into Microsoft Fabric

1. Create a **Fabric Lakehouse** in your workspace.
2. Upload (or `azcopy`) `lakehouse/bronze/*` into the lakehouse's `Files/`
   area — or run notebook **01** directly inside the workspace to generate
   in place.
3. Import the four notebooks under `notebooks/` (`Workspace → New → Import notebook`).
4. Import the pipeline definition `pipelines/fabric_pipeline.json`
   (`Data Factory → New → Import pipeline`) and bind the
   `{{notebook_id_…}}` / `{{workspace_id}}` / `{{semantic_model_id}}`
   placeholders.
5. Create a **Direct Lake** semantic model from `semantic-model/model.bim`
   pointing at the Gold Delta tables.
6. Open `powerbi/TrafficWater.pbip` in Power BI Desktop and publish.

## Repository layout

```
fabric-iq/
├── ggm/
│   ├── extract_schema.py        # XMI → JSON catalog extractor
│   └── schema_catalog.json      # curated in-scope GGM subset (the contract)
├── synth/
│   ├── common.py                # nl_NL helpers, RD-coord bbox, diurnal profile
│   ├── run_generate.py          # CLI entrypoint
│   └── generators/
│       ├── traffic.py           # Wegvak, Verkeersmeting, Parkeerplaats, ...
│       └── water.py             # Watergang, Waterpeilmeting, Gemaal, ...
├── lakehouse/
│   ├── build.py                 # bronze → silver → gold (pandas + pyarrow)
│   ├── bronze/ silver/ gold/    # generated Parquet output
├── notebooks/                   # Fabric-compatible .ipynb (4 stages)
├── pipelines/
│   └── fabric_pipeline.json     # Fabric Data Pipeline (4 notebooks + refresh)
├── semantic-model/
│   └── model.bim                # Direct Lake tabular model
├── powerbi/
│   └── TrafficWater.pbip        # PBIP stub
├── tests/                       # pytest smoke tests for generators
├── requirements.txt
└── run-demo.ps1
```

## Scope & non-goals

In scope:
* 12 GGM entities across Verkeer & Vervoer and Water & Milieu.
* Time-series facts at hourly granularity.
* Cross-domain mart that joins traffic and water in space and time.

Not in scope (yet):
* Live streaming via **Eventstream / KQL DB** (Real-Time Intelligence).
* Real **BAG/BGT/BRK** integration.
* Production hardening (RBAC, Purview lineage, Key Vault, CI/CD).
* The existing SSIS-VM Bicep at the repo root — left untouched.

## Source-model citation

> *Het Gemeentelijk Gegevensmodel (GGM)* — Gemeente Delft, v2.4.0
> <https://github.com/Gemeente-Delft/Gemeentelijk-Gegevensmodel>
> Winner GemeenteDelers 2022 · Common Ground *Goud* status.

The synthetic data here is **not** real Delft data and must not be used as a
substitute for official municipal sources.
