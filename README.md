# Fabric IQ — Synthetic Data Workflow for Traffic, Transport & Water Management

> **End-to-end Microsoft Fabric demo** for Dutch municipal data using the open-source
> [Gemeentelijk Gegevensmodel (GGM)](https://github.com/Gemeente-Delft/Gemeentelijk-Gegevensmodel).
> Generates realistic synthetic traffic & water management data, processes it through a
> **bronze → silver → gold** medallion lakehouse, and surfaces it in a **Direct Lake**
> Power BI report — all without any real (privacy-sensitive) data.

---

## 🎯 Objective

This project demonstrates how a Dutch municipality can:

- Model their data using the open **GGM standard** (Gemeente Delft)
- Build a **production-grade medallion lakehouse** in Microsoft Fabric
- Generate and process **synthetic but realistic** time-series data for two policy domains:
  - 🚦 *Verkeer & Vervoer* (Traffic & Transport — IV3 2.x)
  - 💧 *Water & Milieu* (Water & Environment — IV3 7.x)
- Create a **cross-domain alert mart** where traffic peaks coincide with water quality breaches
- Deliver insights via **Power BI with Direct Lake** (no data import, real-time on Delta tables)
- Use **Fabric Copilot / AI Skills** for natural language Q&A on top of the domain-rich dataset

This is a **POC / demo template** — not production data. It is designed to be cloned, run,
and demonstrated to stakeholders in under an hour.

---

## 🏗️ Architecture

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

**Gold layer output (default 14-day run):**

| Table | Rows | Purpose |
|---|---|---|
| `dim_locatie` | ~210 | Unified dimension: road segments + waterways |
| `dim_tijd` | ~340 | Hourly time dimension |
| `fact_verkeer` | ~13k | Hourly vehicle counts per `wegvak` |
| `fact_waterpeil` | ~2.7k | Hourly water level (m NAP) per `watergang` |
| `fact_waterkwaliteit` | ~3.8k | NEN-aligned water quality readings |
| `fact_cross_domain_alert` | varies | Hours where traffic peaks + water norm breaches coincide |

---

## ✅ Prerequisites

### Tools to install on your machine

| Tool | Min. version | How to install |
|---|---|---|
| **Python** | 3.10+ | [python.org/downloads](https://www.python.org/downloads/) |
| **Git** | any | [git-scm.com](https://git-scm.com/downloads) |
| **Power BI Desktop** | 2024+ | [Microsoft Store](https://aka.ms/pbidesktopstore) or [aka.ms/pbid](https://aka.ms/pbid) |

### Microsoft Fabric

| Requirement | Notes |
|---|---|
| **Microsoft Fabric workspace** | With at least **F2 capacity** (trial capacity works) |
| **Fabric licence** | Free trial available at [app.fabric.microsoft.com](https://app.fabric.microsoft.com) |
| **Workspace Admin or Contributor role** | To create lakehouses, import notebooks, and pipelines |

> 💡 **No Azure subscription required** for the local run. You only need Fabric for the cloud deployment steps.

---

## 🚀 Step-by-Step Guide

### PART 1 — Local Setup (15 min)

#### Step 1: Clone the repository

```powershell
git clone https://github.com/AjinkyaSoDev/fabric-iq.git
cd fabric-iq
```

#### Step 2: Run the full demo locally

```powershell
.\run-demo.ps1
```

This single script will:
1. Create a Python virtual environment (`.venv`)
2. Install all dependencies (`faker`, `pandas`, `pyarrow`, `pytest`)
3. Generate **14 days** of synthetic traffic & water data → `lakehouse/bronze/`
4. Build the **silver** layer (type-cast, deduped, referential integrity) → `lakehouse/silver/`
5. Build the **gold** star schema marts → `lakehouse/gold/`
6. Run data quality smoke tests

Expected output:
```
[1/3] Generating bronze synthetic data (14 days)...
  wrote Wegvak:          150 rows -> lakehouse/bronze
  wrote Verkeersmeting: 50400 rows -> lakehouse/bronze
  ...
[2/3] Building silver + gold layers...
[3/3] Running quality tests...
Done. Gold layer at: C:\...\fabric-iq\lakehouse\gold
```

> ⚙️ **Custom run:** `.\run-demo.ps1 -Days 30` generates 30 days of data instead.

---

### PART 2 — Deploy to Microsoft Fabric (30 min)

#### Step 3: Create a Fabric Lakehouse

1. Go to [app.fabric.microsoft.com](https://app.fabric.microsoft.com)
2. Open your workspace
3. Click **New → Lakehouse**
4. Name it: **`FabricIQ`**
5. Note your **Workspace ID** from the browser URL:
   `https://app.fabric.microsoft.com/groups/`**`<your-workspace-id>`**`/...`

#### Step 4: Upload bronze data to OneLake

1. In the `FabricIQ` lakehouse, click **Files** in the Explorer pane (left side)
2. Click **Upload → Upload folder**
3. Browse to and select `lakehouse/bronze/` from your local clone
4. Wait for upload to complete — you should see folders like `Wegvak/`, `Verkeersmeting/`, etc. under `Files/bronze/`

#### Step 5: Import the 4 notebooks

1. In your workspace → **New → Import notebook**
2. Import each notebook **one at a time** (in order):
   - `notebooks/01_bronze_ingest.ipynb`
   - `notebooks/02_silver_curate.ipynb`
   - `notebooks/03_gold_marts.ipynb`
   - `notebooks/04_quality_checks.ipynb`
3. For **each** imported notebook:
   - Open it
   - Click **Add lakehouse** (left panel)
   - Select `FabricIQ`
4. Note each notebook's **ID** from its URL:
   `https://app.fabric.microsoft.com/groups/<workspace-id>/notebooks/`**`<notebook-id>`**

#### Step 6: Fill in the pipeline placeholders

Open `pipelines/fabric_pipeline.json` in any text editor (VS Code recommended) and replace all placeholders:

| Placeholder | Replace with |
|---|---|
| `{{workspace_id}}` | Your workspace ID (Step 3) |
| `{{notebook_id_01}}` | ID of `01_bronze_ingest` notebook |
| `{{notebook_id_02}}` | ID of `02_silver_curate` notebook |
| `{{notebook_id_03}}` | ID of `03_gold_marts` notebook |
| `{{notebook_id_04}}` | ID of `04_quality_checks` notebook |
| `{{semantic_model_id}}` | Fill in after Step 8 |

Save the file after editing.

#### Step 7: Import the pipeline

1. In your workspace → **New → Data pipeline**
2. In the pipeline editor, click the **{ }** (JSON view) button in the toolbar
3. Replace the entire content with your updated `fabric_pipeline.json`
4. Name the pipeline: **`GGM_Synthetic_TrafficWater`**
5. Click **Save**

#### Step 8: Create the Direct Lake semantic model

1. In the `FabricIQ` lakehouse, run notebook `03_gold_marts` once manually (click ▶ **Run all**) to create the Gold Delta tables under **Tables/**
2. Once gold tables are visible, click **New semantic model** (top right of the Lakehouse)
3. Select all gold tables: `dim_locatie`, `dim_tijd`, `fact_verkeer`, `fact_waterpeil`, `fact_waterkwaliteit`, `fact_cross_domain_alert`
4. Click **Confirm**
5. Name it: **`FabricIQ_Model`**
6. Note the **semantic model ID** from its URL and update `{{semantic_model_id}}` in your pipeline JSON, then re-import or update the pipeline

#### Step 9: Run the full pipeline

1. Open the `GGM_Synthetic_TrafficWater` pipeline
2. Click **▶ Run**
3. Watch all 5 activities execute in sequence:

```
Bronze_Ingest ──► Silver_Curate ──► Gold_Marts ──► Quality_Checks ──► Refresh_Semantic_Model
```

Each activity shows green ✅ on success. Total runtime: ~5–10 minutes.

---

### PART 3 — Power BI Report (10 min)

#### Step 10: Open in Power BI Desktop

1. Open **Power BI Desktop**
2. **File → Open report → Browse**
3. Select `powerbi/TrafficWater.pbip`
4. When prompted, connect to your `FabricIQ_Model` semantic model in Fabric
5. The report uses **Direct Lake** — no data import, reads directly from OneLake Delta tables

#### Step 11: Publish to Fabric

1. In Power BI Desktop → **Home → Publish**
2. Select your Fabric workspace
3. Open the published report in Fabric

**Recommended report pages to build:**
- 🚦 **Verkeer overzicht** — Map of road segments colored by avg. speed, hourly vehicle count chart
- 💧 **Water overzicht** — Water level trends, KPI cards for % norm breaches, pH/O2/NO3/PO4 breakdown
- ⚠️ **Cross-domain alerts** — Heatmap of hours × districts where traffic peaks and water quality breaches coincide

---

## 🗂️ Repository Layout

```
fabric-iq/
├── ggm/
│   ├── extract_schema.py        # XMI → JSON catalog extractor
│   └── schema_catalog.json      # Curated in-scope GGM subset (the data contract)
├── synth/
│   ├── common.py                # nl_NL helpers, RD-coord bbox, diurnal profile
│   ├── run_generate.py          # CLI entrypoint: python -m synth.run_generate --days 14
│   └── generators/
│       ├── traffic.py           # Wegvak, Verkeersmeting, Parkeerplaats, ...
│       └── water.py             # Watergang, Waterpeilmeting, Gemaal, ...
├── lakehouse/
│   ├── build.py                 # bronze → silver → gold (pandas + pyarrow)
│   ├── bronze/                  # Generated Parquet (partitioned by ingest_date)
│   ├── silver/                  # Cleansed + typed Parquet
│   └── gold/                    # Star schema Parquet (ready for Fabric Delta)
├── notebooks/
│   ├── 01_bronze_ingest.ipynb   # Generate + write bronze (Fabric + local)
│   ├── 02_silver_curate.ipynb   # Cleanse + type-cast → silver
│   ├── 03_gold_marts.ipynb      # Build star schema → gold
│   └── 04_quality_checks.ipynb  # Data quality smoke tests
├── pipelines/
│   └── fabric_pipeline.json     # Fabric Data Pipeline: 4 notebooks + model refresh
├── semantic-model/
│   └── model.bim                # Direct Lake tabular model definition
├── powerbi/
│   ├── TrafficWater.pbip        # Power BI Desktop project file
│   └── README.md                # Report page guidance
├── tests/
│   └── test_generators.py       # pytest smoke tests for synthetic generators
├── requirements.txt             # Python dependencies
└── run-demo.ps1                 # One-shot local demo runner
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `python` not found | Make sure Python 3.10+ is installed and added to PATH |
| `pip install` fails | Run PowerShell as Administrator, or use `python -m pip install -r requirements.txt` |
| Notebook can't find lakehouse | Re-add the `FabricIQ` lakehouse via **Add lakehouse** in the notebook |
| Pipeline placeholder error | Double-check all `{{...}}` values are replaced with real GUIDs in the JSON |
| Gold tables not appearing | Run notebook `03_gold_marts` manually first before creating the semantic model |
| Direct Lake connection fails | Ensure the semantic model points at `FabricIQ` lakehouse Tables, not Files |

---

## 📏 Scope & Non-Goals

**In scope:**
- 12 GGM entities across *Verkeer & Vervoer* and *Water & Milieu*
- Time-series facts at hourly granularity over N days
- Cross-domain mart joining traffic and water by space and time

**Not in scope (yet):**
- Live streaming via Eventstream / KQL DB (Real-Time Intelligence)
- Real BAG/BGT/BRK geographic integration
- Production hardening: RBAC, Purview lineage, Key Vault, CI/CD
- Multi-tenant or multi-workspace deployments

---

## 📚 Source Model Citation

> *Het Gemeentelijk Gegevensmodel (GGM)* — Gemeente Delft, v2.4.0
> <https://github.com/Gemeente-Delft/Gemeentelijk-Gegevensmodel>
> Winner GemeenteDelers 2022 · Common Ground *Goud* status.

The synthetic data in this project is **not** real Delft municipal data and must
not be used as a substitute for official sources.

---

## 🤝 Contributing

Issues and PRs welcome. If you extend this to additional GGM domains or add
Eventstream / Real-Time Intelligence support, please open a PR!
