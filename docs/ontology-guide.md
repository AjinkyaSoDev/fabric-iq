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

| Requirement | Detail |
|---|---|
| Fabric capacity | **F64+** (or P2+ Premium) — Ontology is not available on F2/F4/F8/F16/F32 |
| Tenant setting | Admin Portal → Tenant settings → search **"Ontology"** → toggle **On** |
| Semantic model | `FabricIQ_Model` published to Fabric (see [README Step 5](../README.md)) |
| Role | Workspace **Contributor** or higher |

> ⚠️ If you see error `PowerBIFeatureDisabled`, the tenant setting is off. Ask your Fabric admin to enable it. Changes take up to 15 minutes to propagate.

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
