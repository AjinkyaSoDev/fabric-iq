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

> ⚠️ **Windows users:** if you see a script execution error, run this first:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

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
  wrote Wegvak:        200 rows -> bronze\Wegvak
  wrote Verkeersmeting: 13440 rows -> bronze\Verkeersmeting
  ...
[2/3] Building silver + gold layers...
  gold/dim_locatie       208 rows
  gold/fact_verkeer    13440 rows
  ...
[3/3] Running quality tests...
============== 4 passed in 1.3s ==============
Done. Gold layer at: C:\...\fabric-iq\lakehouse\gold
```

> ⚙️ **Custom run:** `.\run-demo.ps1 -Days 30` generates 30 days of data instead.

---

### PART 2 — Deploy to Microsoft Fabric (30 min)

> 💡 The notebooks are fully self-contained. They clone the repo and generate data directly inside Fabric — **no manual file upload required**.

#### Step 3: Create a Fabric Lakehouse

1. Go to [app.fabric.microsoft.com](https://app.fabric.microsoft.com)
2. Open your workspace
3. Click **New → Lakehouse**
4. Name it: **`FabricIQ`**
5. Note your **Workspace ID** from the browser URL:
   `https://app.fabric.microsoft.com/groups/`**`<your-workspace-id>`**`/...`

#### Step 4: Import the 4 notebooks

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

#### Step 5: Generate gold tables and create the semantic model

1. Open notebook `01_bronze_ingest` and click ▶ **Run all** (waits ~3 min)
2. Open notebook `02_silver_curate` and click ▶ **Run all** (~1 min)
3. Open notebook `03_gold_marts` and click ▶ **Run all** (~1 min)
4. Open notebook `04_quality_checks` and click ▶ **Run all** (~30 sec)
5. In the `FabricIQ` lakehouse, you should see all `bronze_*`, `silver_*`, and `gold_*` tables under **Tables/**
6. Click **New semantic model** (top right of the Lakehouse)
7. Select all gold tables: `gold_dim_locatie`, `gold_dim_tijd`, `gold_fact_verkeer`, `gold_fact_waterpeil`, `gold_fact_waterkwaliteit`, `gold_fact_cross_domain_alert`
8. Name it: **`FabricIQ_Model`** → **Confirm**
9. Note the **semantic model ID** from its URL

#### Step 6: (Optional) Create an orchestration pipeline

> ⚠️ **Heads-up:** Fabric's pipeline UI does not have a reliable JSON-paste import. The easiest path is to **build the pipeline visually** rather than import the JSON file. The JSON file is provided as a reference for what activities to chain.

**Option A — Build visually (recommended):**

1. In your workspace → **New → Data pipeline** → name it `GGM_Synthetic_TrafficWater`
2. Add 4 **Notebook** activities (one per notebook), chained with **On success** dependencies:
   ```
   Bronze_Ingest ──► Silver_Curate ──► Gold_Marts ──► Quality_Checks
   ```
3. For each Notebook activity, point it at the corresponding notebook in your workspace
4. Add a **Semantic model refresh** activity at the end, pointing at `FabricIQ_Model`
5. Click **Save**

**Option B — Use the JSON file via Fabric REST API:**

Open `pipelines/fabric_pipeline.json`, replace the placeholders below, then POST it to the Fabric Items API:

| Placeholder | Replace with |
|---|---|
| `{{workspace_id}}` | Your workspace ID (Step 3) |
| `{{notebook_id_01}}` | ID of `01_bronze_ingest` (from notebook URL) |
| `{{notebook_id_02}}` | ID of `02_silver_curate` |
| `{{notebook_id_03}}` | ID of `03_gold_marts` |
| `{{notebook_id_04}}` | ID of `04_quality_checks` |
| `{{semantic_model_id}}` | ID of `FabricIQ_Model` (Step 5) |

Reference: [Fabric REST API – Create item](https://learn.microsoft.com/rest/api/fabric/core/items/create-item).

#### Step 7: Run the pipeline (if you created one)

1. Open the `GGM_Synthetic_TrafficWater` pipeline
2. Click **▶ Run**
3. Watch all activities execute in sequence. Total runtime: ~5–10 minutes.

> 💡 You can also skip the pipeline entirely and just re-run the notebooks manually for demos.

---

### PART 3 — Power BI Report (15 min)

> 💡 The `powerbi/TrafficWater.pbip` file is a **starter template / stub** — not a finished report. You'll build the visuals on top of the `FabricIQ_Model` semantic model.

#### Step 8: Build the report in Fabric (easiest path)

1. In Fabric, navigate to your `FabricIQ_Model` semantic model
2. Click **Create report → Start from scratch** (or **Auto-create**)
3. Drag fields from the gold tables onto the canvas to build visuals
4. Save the report in your workspace

#### Step 9: (Alternative) Build in Power BI Desktop

1. Open **Power BI Desktop** (2024+ with PBIP preview enabled)
2. **Get data → Power BI semantic models → `FabricIQ_Model`** (Direct Lake mode)
3. Build the visuals you want
4. **File → Save as → Power BI Project (.pbip)** to optionally replace `powerbi/TrafficWater.pbip`
5. **Home → Publish** → select your Fabric workspace

**Recommended report pages:**
- 🚦 **Verkeer overzicht** — Map of road segments colored by avg. speed, hourly vehicle count chart
- 💧 **Water overzicht** — Water level trends, KPI cards for % norm breaches, pH/O2/NO3/PO4 breakdown
- ⚠️ **Cross-domain alerts** — Heatmap of hours × districts where traffic peaks and water quality breaches coincide

See [`powerbi/README.md`](powerbi/README.md) for detailed page-by-page guidance.

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
| `run-demo.ps1` blocked | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first |
| Notebook can't find lakehouse | Re-add the `FabricIQ` lakehouse via **Add lakehouse** in the notebook |
| Notebook 01 git clone fails | The notebook clones from `https://github.com/AjinkyaSoDev/fabric-iq.git`. If you forked the repo, edit the `git clone` URL in cell 2 of `01_bronze_ingest.ipynb` to point at your fork |
| `spark` not defined in notebook | Make sure the notebook is running in a **Synapse PySpark** kernel (default in Fabric notebooks) |
| Gold tables not appearing | Run notebooks 01, 02, 03 in order; check the Tables/ folder in the Lakehouse |
| Direct Lake connection fails | Ensure the semantic model points at the `FabricIQ` lakehouse **Tables** (not Files) |
| Pipeline JSON import doesn't work | Use Option A in Step 6 — build the pipeline visually instead |

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
