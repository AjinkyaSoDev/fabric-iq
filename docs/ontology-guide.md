# Creating a Fabric Ontology from the FabricIQ Semantic Model

> **Feature status:** Preview — requires **F64 or higher** capacity and the *Ontology* tenant setting enabled in the Fabric Admin Portal.

## What is a Fabric Ontology?

A Fabric **Ontology** is a knowledge graph layer built on top of a semantic model. It describes your data in human-readable **concepts**, **properties**, and **relationships** so that:

- **Fabric Copilot / AI Skills** can answer natural-language questions backed by your data
- Business users can explore data without knowing table names or DAX
- Cross-domain queries (e.g. "where do traffic peaks coincide with water quality breaches?") are answerable from a single conversational interface

Think of it as the semantic model telling Power BI *how to query* the data, while the ontology tells AI *what the data means*.

---

## Prerequisites

Work through all four levels before you try to create an ontology. Each level builds on the one before it.

### Level 0 — Accounts & Licences (start here if you're brand new to Fabric)

If you have never used Microsoft Fabric before, complete these steps first:

1. **Get a Microsoft account** (work/school M365 account, or a personal Microsoft account)
   - If your organisation uses Microsoft 365 you already have one — use your work email.
   - No M365? Sign up at [account.microsoft.com](https://account.microsoft.com).

2. **Start a Microsoft Fabric trial**
   - Go to [app.fabric.microsoft.com](https://app.fabric.microsoft.com) and sign in.
   - If you don't have a Fabric licence you'll be prompted to **Start free trial** (60 days, no credit card needed).
   - Accept the trial and wait ~1 minute for provisioning.

3. **Verify your Fabric licence**
   - In Fabric, click your profile photo (top right) → **Account manager**
   - You should see **Microsoft Fabric (Free)** or a trial / paid licence.
   - A free/trial licence is enough for most Fabric features, **but not for Ontology** — see Level 1.

   > 💡 If you're at a company, ask your IT/Microsoft admin whether you already have a Fabric licence through your Microsoft 365 subscription (E3/E5 or F3 often include it).

---

### Level 1 — Fabric Capacity (required for Ontology)

Fabric Ontology is a **premium preview feature** that only runs on specific capacity sizes.

#### What is a Fabric capacity?
A capacity is a reserved pool of compute resources (CPU, RAM) in Microsoft Azure that powers your Fabric workspace. Capacities are sized with an **F-SKU** (e.g. F2, F4, F64) — bigger = more power = higher cost.

#### Minimum SKU for Ontology

| SKU | Ontology supported? | Notes |
|---|---|---|
| F2 / F4 / F8 / F16 / F32 | ❌ No | Too small — Ontology feature is disabled |
| **F64** | ✅ Yes | Minimum required |
| F128, F256, F512, F1024, F2048 | ✅ Yes | Larger, more expensive |
| P2 / P3 / P4 / P5 (Premium) | ✅ Yes | Legacy Premium SKUs also qualify |

> ⚠️ **Trial capacities** are typically F64 equivalent — Ontology *may* be available on a Fabric trial. Check by attempting to create an ontology after enabling the tenant setting.

#### How to check your current capacity SKU

1. Go to [app.fabric.microsoft.com](https://app.fabric.microsoft.com) → ⚙️ **Admin portal**
2. Click **Capacity settings** in the left menu
3. Find your capacity in the list — the **SKU** column shows e.g. `F64`
4. If you don't see a capacity, or it's F2–F32, you'll need to upgrade or create a new one

#### How to get an F64 capacity (if you don't have one)

**Option A — Upgrade existing capacity (if you're the capacity admin):**
1. Admin portal → **Capacity settings** → click your capacity name
2. Click **Change size** → select **F64** or higher
3. Confirm — billing changes immediately (pay-as-you-go via Azure subscription)

**Option B — Create a new F64 capacity:**
1. You need an **Azure subscription** ([free tier available](https://azure.microsoft.com/free/) with $200 credit)
2. Go to [portal.azure.com](https://portal.azure.com) → **Create a resource** → search **Microsoft Fabric**
3. Select **Microsoft Fabric** → **Create**
4. Fill in: subscription, resource group, region, capacity name, size = **F64**, admin = your account
5. Click **Review + Create** → **Create** (takes ~2 minutes)
6. Back in Fabric Admin portal → **Capacity settings** → associate your workspace with the new capacity

**Option C — Ask your organisation's Azure/Fabric admin** to assign your workspace to an existing F64+ capacity.

---

### Level 2 — Fabric Workspace & Roles

You need the right workspace and permissions before you can manage tenant settings or create items.

#### Check your workspace role

1. In Fabric, open your workspace (left navigation → your workspace name)
2. Click **Manage access** (top right of the workspace)
3. Find your name — you need **Admin**, **Member**, or **Contributor** role
   - **Viewer** → cannot create items → ask workspace Admin to upgrade your role
   - **Contributor or higher** → you're good ✅

#### Workspace capacity assignment

Your workspace must be assigned to the F64+ capacity:

1. In your workspace → **Workspace settings** (⚙️ icon)
2. Go to the **Premium** tab (or **Licence info** tab)
3. Under **Licence mode**, confirm it shows **Fabric capacity** and the capacity name
4. If it shows **Pro** or **Premium per user**, click **Edit** → select your F64 capacity → **Save**

---

### Level 3 — FabricIQ Data Pipeline (Ontology sits on top of this)

The ontology connects to the `FabricIQ_Model` semantic model, which in turn reads the Gold Delta tables. All of this must exist before you create an ontology.

**Complete checklist (in order):**

- [ ] Fabric Lakehouse **`FabricIQ`** created in your workspace
- [ ] All 4 notebooks imported and the `FabricIQ` lakehouse attached to each
- [ ] Notebooks run in order (01 → 02 → 03 → 04) — gold tables visible under **Tables/** in the lakehouse
- [ ] Semantic model **`FabricIQ_Model`** created from the gold tables (Lakehouse → **New semantic model**)
- [ ] `FabricIQ_Model` shows all 6 gold tables: `dim_locatie`, `dim_tijd`, `fact_verkeer`, `fact_waterpeil`, `fact_waterkwaliteit`, `fact_cross_domain_alert`

> 📖 If any of the above are missing, follow [README — Parts 1 & 2](../README.md) first, then return here.

---

### Level 4 — Admin Portal Access (to enable the tenant setting)

Enabling the Ontology tenant setting requires **Fabric Administrator** privileges. This is separate from workspace roles.

#### Do you have Fabric Admin access?

1. Go to [app.fabric.microsoft.com](https://app.fabric.microsoft.com) → ⚙️ **Settings** (top right)
2. If you see **Admin portal** in the menu → you have admin access ✅
3. If you don't see it → you are not a Fabric Admin

#### If you are NOT a Fabric Admin

Ask your organisation's Fabric/Power BI administrator to:
1. Go to Admin portal → **Tenant settings** → search **Ontology**
2. Enable **"Users can create and use ontologies (preview)"**
3. Apply to **Entire organisation** or add you to a specific security group

You can send them this request template:

> *"Hi, I'm working on the Fabric IQ project and would like to use the Fabric Ontology preview feature. Could you please enable the 'Users can create and use ontologies' setting in the Fabric Admin Portal → Tenant settings? I also need my workspace to be on an F64+ capacity. Thank you."*

#### If you ARE a Fabric Admin

Proceed to Part 1 below.

---

### Prerequisites Summary Checklist

Before proceeding, confirm all boxes are checked:

- [ ] Microsoft account and Fabric licence (trial or paid)
- [ ] Workspace assigned to **F64 or higher** Fabric capacity
- [ ] Workspace role: **Contributor, Member, or Admin**
- [ ] Gold tables exist in the `FabricIQ` lakehouse (`dim_*`, `fact_*`)
- [ ] `FabricIQ_Model` semantic model published in the workspace
- [ ] Fabric Admin access (or admin contacted to enable setting)

> ✅ All checked? Continue to Part 1.

---

## Part 1 — Enable the Ontology Feature

1. Go to [app.fabric.microsoft.com](https://app.fabric.microsoft.com) → ⚙️ **Admin portal**
2. Navigate to **Tenant settings**
3. Search for **Ontology**
4. Under **Preview features**, enable **"Users can create and use ontologies"**
5. Apply to your organisation or a specific security group
6. Click **Apply** and wait ~15 minutes

---

## Part 2 — Create the Ontology for FabricIQ

### Step 1: Open the Ontology creator

1. In your Fabric workspace, click **New**
2. Search for **Ontology** → select it
3. Name it: **`FabricIQ_Ontology`**
4. Click **Create**

### Step 2: Connect to the FabricIQ_Model semantic model

1. Inside the ontology editor, click **Connect data source**
2. Select **Semantic model** → choose **`FabricIQ_Model`**
3. Fabric will auto-import the tables and relationships from the model as a starting point

---

## Part 3 — Map GGM Concepts to Ontology Entities

The Fabric IQ semantic model is built on the Dutch **Gemeentelijk Gegevensmodel (GGM)**. The table below shows how each Gold layer table maps to an ontology concept.

### Concept mapping

| Gold Table | Ontology Concept | Label (NL) | Description |
|---|---|---|---|
| `dim_locatie` | `Locatie` | Locatie | A physical location — road segment or waterway |
| `dim_tijd` | `TijdDimensie` | Tijdstip | Hourly time slot |
| `fact_verkeer` | `Verkeersmeting` | Verkeersmeting | Hourly vehicle count at a road segment |
| `fact_waterpeil` | `Waterpeilmeting` | Waterpeilmeting | Hourly water level in metres NAP |
| `fact_waterkwaliteit` | `Waterkwaliteitsmeting` | Waterkwaliteitsmeting | NEN-aligned water quality parameter reading |
| `fact_cross_domain_alert` | `CrossDomeinAlert` | Cross-domein alert | Hour where traffic peak AND water breach coincide |

### Configuring each concept in the ontology editor

For each concept, set these fields:

#### `Locatie` (from `dim_locatie`)

| Field | Value |
|---|---|
| **Display name** | Locatie |
| **Description** | Een meetlocatie — wegvak of watergang |
| **Key property** | `locatie_id` |
| **Label property** | `naam` |
| **Visible properties** | `naam`, `locatie_type`, `wijk_code`, `geom_x_rd`, `geom_y_rd` |

#### `Verkeersmeting` (from `fact_verkeer`)

| Field | Value |
|---|---|
| **Display name** | Verkeersmeting |
| **Description** | Uurtelling van voertuigen per wegvak (GGM: Verkeersmeting, IV3 2.x) |
| **Key property** | _(composite: `locatie_id` + `meet_tijdstip`)_ |
| **Visible properties** | `voertuigen_per_uur`, `gem_snelheid_kmh`, `pct_zwaar_verkeer`, `bron` |
| **Measures to expose** | `Totaal voertuigen`, `Gem. snelheid` |

#### `Waterpeilmeting` (from `fact_waterpeil`)

| Field | Value |
|---|---|
| **Display name** | Waterpeilmeting |
| **Description** | Uurlijkse waterpeilen in m NAP per watergang |
| **Visible properties** | `peil_nap_m`, `debiet_m3_s` |
| **Measures to expose** | `Gem. peil (m NAP)`, `Max debiet` |

#### `Waterkwaliteitsmeting` (from `fact_waterkwaliteit`)

| Field | Value |
|---|---|
| **Display name** | Waterkwaliteitsmeting |
| **Description** | NEN 6600-conforme meting van waterkwaliteitsparameters |
| **Visible properties** | `parameter`, `waarde`, `eenheid`, `norm_status` |
| **Measures to expose** | `% Overschrijdingen` |

#### `CrossDomeinAlert` (from `fact_cross_domain_alert`)

| Field | Value |
|---|---|
| **Display name** | Cross-domein alert |
| **Description** | Uren waar verkeerspiek samenvalt met normoverschrijding waterkwaliteit |

---

## Part 4 — Define Relationships Between Concepts

These mirror the relationships already defined in `semantic-model/model.bim`, but expressed semantically:

| Relationship | From | To | Cardinality | Label |
|---|---|---|---|---|
| `gemeten_op_locatie` | `Verkeersmeting` | `Locatie` | Many → One | Gemeten op locatie |
| `gemeten_op_tijdstip` | `Verkeersmeting` | `TijdDimensie` | Many → One | Gemeten op tijdstip |
| `peil_op_locatie` | `Waterpeilmeting` | `Locatie` | Many → One | Gemeten op locatie |
| `peil_op_tijdstip` | `Waterpeilmeting` | `TijdDimensie` | Many → One | Gemeten op tijdstip |
| `kwaliteit_op_locatie` | `Waterkwaliteitsmeting` | `Locatie` | Many → One | Gemeten op locatie |
| `kwaliteit_op_tijdstip` | `Waterkwaliteitsmeting` | `TijdDimensie` | Many → One | Gemeten op tijdstip |
| `alert_op_locatie` | `CrossDomeinAlert` | `Locatie` | Many → One | Alert op locatie |

In the ontology editor:
1. Click **Add relationship**
2. Select source concept → source property (`locatie_id` or `meet_tijdstip`)
3. Select target concept → target property
4. Set cardinality to **Many to one**
5. Give it a human-readable **label** (used in Copilot responses)

---

## Part 5 — Add Synonyms and NL Descriptions

Fabric Copilot uses synonyms and descriptions to understand natural-language queries. Add these for key concepts:

### `Locatie` synonyms
`locatie`, `meetpunt`, `wegvak`, `watergang`, `straat`, `locaties`

### `Verkeersmeting` synonyms
`verkeer`, `verkeerstelling`, `voertuigen`, `intensiteit`, `verkeersmeting`, `uurmeting`

### `Waterpeilmeting` synonyms
`waterpeil`, `peil`, `waterstand`, `NAP`, `debiet`

### `Waterkwaliteitsmeting` synonyms
`waterkwaliteit`, `kwaliteit`, `normoverschrijding`, `parameter`, `pH`, `zuurstof`

### `CrossDomeinAlert` synonyms
`alert`, `cross-domein`, `samenvallend`, `piek en overschrijding`

---

## Part 6 — Publish and Test with Copilot

### Publish

1. Click **Save** → **Publish** in the ontology editor
2. The ontology will appear in your workspace as `FabricIQ_Ontology`

### Test with natural-language questions

Once published, open a **Fabric Copilot** or create an **AI Skill** and connect it to `FabricIQ_Ontology`. Try these example queries:

```
Hoeveel voertuigen per uur zijn er gemeten op wegvak A13 gisteren?
```
```
Show me water quality norm breaches in the last 7 days.
```
```
Which locations had both a traffic peak and a water quality alert in the same hour?
```
```
Wat is het gemiddelde waterpeil per watergang deze week?
```

### Create an AI Skill on the Ontology

1. In your workspace → **New → AI Skill**
2. Connect it to **`FabricIQ_Ontology`** (not the semantic model directly)
3. Add example Q&A pairs to fine-tune responses:

| Question | Expected answer guidance |
|---|---|
| "Welke locaties hebben normoverschrijdingen?" | Query `fact_waterkwaliteit` filtered on `norm_status = 'overschrijding'` joined to `dim_locatie` |
| "Wanneer was het drukste verkeersmoment?" | MAX of `voertuigen_per_uur` from `fact_verkeer` with `dim_tijd` and `dim_locatie` |
| "Zijn er cross-domain alerts deze week?" | Filter `fact_cross_domain_alert` on current week via `dim_tijd` |

---

## Part 7 — Keep the Ontology in Sync

When you re-run the pipeline and regenerate gold tables, the semantic model auto-refreshes (Direct Lake). The ontology concepts stay in sync automatically — **no manual update needed** — because the ontology sits on top of the semantic model, not the raw tables.

If you **add new gold tables** (e.g. `fact_parkeren`):
1. Open `FabricIQ_Model` → add the new table and relationships
2. Open `FabricIQ_Ontology` → click **Refresh from semantic model**
3. Map the new table as a new concept following Part 3 above

---

## Architecture Summary

```
GGM Schema (ggm/schema_catalog.json)
          │
          ▼
Gold Delta Tables (Lakehouse)
  dim_locatie, dim_tijd
  fact_verkeer, fact_waterpeil, fact_waterkwaliteit
  fact_cross_domain_alert
          │ Direct Lake
          ▼
FabricIQ_Model (semantic-model/model.bim)
  Relationships, DAX measures, culture: nl-NL
          │
          ▼
FabricIQ_Ontology   ◄── This guide
  Concepts, synonyms, NL descriptions
          │
          ▼
Fabric Copilot / AI Skill
  Natural-language Q&A on GGM data
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `PowerBIFeatureDisabled` | Tenant setting off or insufficient SKU | See [Prerequisites](#prerequisites) and the [known issues](../.github/skills/fabric-iq/references/known-issues.md) |
| Ontology not visible in workspace | Feature not propagated yet | Wait 15 min after enabling tenant setting |
| Copilot gives wrong answers | Missing synonyms or descriptions | Add synonyms per Part 5 and add example Q&A in AI Skill |
| New table not reflected in ontology | Semantic model not updated | Add table to `FabricIQ_Model` first, then refresh ontology |
