# Power BI project (PBIP) — TrafficWater

This folder is a **PBIP stub**. Open `TrafficWater.pbip` in Power BI Desktop
(version 2024 or later, with the *Power BI Project* preview enabled) to
materialise a full project structure.

Recommended report pages to build on top of the Gold semantic model:

1. **Verkeer overzicht** – Map of `dim_locatie` (wegvak markers) colored by
   *Gem. snelheid*, line chart of *Totaal voertuigen* per uur per wijk, top-10
   busiest road segments.
2. **Water overzicht** – Line chart of *Gem. peil (m NAP)* over time per
   watergang categorie, KPI cards for *% Overschrijdingen*, breakdown by
   parameter (pH, O2, NO3, PO4, …).
3. **Cross-domain alerts** – Heat-map of hours × wijken where traffic peaks
   coincide with water-quality threshold breaches (uses
   `fact_cross_domain_alert`).

The model is wired for **Direct Lake** mode so it reads Gold Delta tables
in OneLake with no import step.
