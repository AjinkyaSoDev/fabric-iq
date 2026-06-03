"""Generators for Verkeer & Vervoer (IV3 2.x) entities."""
from __future__ import annotations

import random
from datetime import datetime
from typing import Iterable

import pandas as pd

from synth.common import (
    DELFT_OV_HALTES,
    DELFT_PARKEERGARAGES,
    DiurnalProfile,
    RVV_DESCRIPTIONS,
    hourly_range,
    new_id,
    random_straat,
    rd_point,
)

RVV_CODES = list(RVV_DESCRIPTIONS.keys())
WEGTYPES = ["autoweg", "gebiedsontsluitingsweg", "erftoegangsweg", "fietspad", "voetpad"]
WEGTYPE_SPEED = {
    "autoweg": 100, "gebiedsontsluitingsweg": 50,
    "erftoegangsweg": 30, "fietspad": 15, "voetpad": 15,
}


def gen_wegvakken(n: int = 200) -> pd.DataFrame:
    rows = []
    for _ in range(n):
        straatnaam, wijk_code, wegtype = random_straat()
        x, y = rd_point()
        rows.append({
            "wegvak_id": new_id(),
            "straatnaam": straatnaam,
            "wegtype": wegtype,
            "lengte_m": round(random.uniform(15, 850), 1),
            "max_snelheid": WEGTYPE_SPEED[wegtype],
            "wijk_code": wijk_code,
            "geom_x_rd": round(x, 2),
            "geom_y_rd": round(y, 2),
            "geldig_van": datetime(random.randint(1995, 2024), random.randint(1, 12), 1).date(),
        })
    return pd.DataFrame(rows)


def gen_verkeersborden(wegvakken: pd.DataFrame, n: int = 400) -> pd.DataFrame:
    rows = []
    for _ in range(n):
        rvv_code = random.choice(RVV_CODES)
        rows.append({
            "bord_id": new_id(),
            "wegvak_id": wegvakken["wegvak_id"].sample(1).iloc[0],
            "rvv_code": rvv_code,
            "omschrijving": RVV_DESCRIPTIONS[rvv_code],
            "installatie_datum": datetime(random.randint(2005, 2024), random.randint(1, 12), random.randint(1, 28)).date(),
        })
    return pd.DataFrame(rows)


def gen_verkeerslichten(wegvakken: pd.DataFrame, n: int = 60) -> pd.DataFrame:
    target = wegvakken[wegvakken["wegtype"].isin(["autoweg", "gebiedsontsluitingsweg"])]
    target = target if len(target) else wegvakken
    rows = []
    for _ in range(n):
        rows.append({
            "vri_id": new_id(),
            "wegvak_id": target["wegvak_id"].sample(1).iloc[0],
            "type": random.choices(["voertuig", "voetganger", "fiets", "ov"], weights=[0.55, 0.2, 0.15, 0.10])[0],
            "is_intelligent": random.random() < 0.35,
        })
    return pd.DataFrame(rows)


def gen_parkeerplaatsen(wegvakken: pd.DataFrame, n: int = 120) -> pd.DataFrame:
    rows = []
    for _ in range(n):
        soort = random.choices(
            ["straatparkeren", "parkeergarage", "P+R", "vergunninghouders"],
            weights=[0.6, 0.15, 0.05, 0.20],
        )[0]
        wegvak = wegvakken.sample(1).iloc[0]
        if soort == "parkeergarage":
            naam, capaciteit, tarief = random.choice(DELFT_PARKEERGARAGES)
        elif soort == "P+R":
            naam, capaciteit, tarief = "P+R Delft (Station)", random.randint(150, 300), 0.0
        else:
            label = {"straatparkeren": "Straatparkeren", "vergunninghouders": "Vergunninghouders"}[soort]
            naam = f"{label} {wegvak['straatnaam']}"
            capaciteit = random.randint(1, 30)
            tarief = round(random.choice([0.0, 1.5, 2.5, 3.0, 4.5]), 2)
        rows.append({
            "parkeer_id": new_id(),
            "naam": naam,
            "wegvak_id": wegvak["wegvak_id"],
            "capaciteit": capaciteit,
            "soort": soort,
            "is_elektrisch": random.random() < 0.25,
            "tarief_per_uur": tarief,
        })
    return pd.DataFrame(rows)


def gen_ovhaltes(wegvakken: pd.DataFrame, n: int = 45) -> pd.DataFrame:
    rows = []
    for _ in range(n):
        naam, modaliteit, lijn = random.choice(DELFT_OV_HALTES)
        rows.append({
            "halte_id": new_id(),
            "naam": naam,
            "modaliteit": modaliteit,
            "lijn": lijn,
            "wegvak_id": wegvakken["wegvak_id"].sample(1).iloc[0],
        })
    return pd.DataFrame(rows)


def gen_verkeersmetingen(
    wegvakken: pd.DataFrame,
    start: datetime,
    days: int = 14,
    sample_n: int = 40,
) -> pd.DataFrame:
    """Hourly counts for a sample of wegvakken."""
    sampled = wegvakken.sample(min(sample_n, len(wegvakken)))
    profile = DiurnalProfile()
    rows = []
    for _, w in sampled.iterrows():
        # busier baseline on through-roads
        base = {"autoweg": 800, "gebiedsontsluitingsweg": 350,
                "erftoegangsweg": 90, "fietspad": 60, "voetpad": 20}[w["wegtype"]]
        prof = DiurnalProfile(base=base)
        for dt in hourly_range(start, days):
            v = prof.vehicles_at(dt)
            rows.append({
                "wegvak_id": w["wegvak_id"],
                "meet_tijdstip": dt,
                "voertuigen_per_uur": v,
                "gem_snelheid_kmh": max(5, round(w["max_snelheid"] - random.uniform(0, 15) - 0.005 * v, 1)),
                "pct_zwaar_verkeer": round(random.uniform(0.02, 0.18), 3),
                "bron": random.choices(["lus", "camera", "floating-car-data"], weights=[0.6, 0.25, 0.15])[0],
            })
    return pd.DataFrame(rows)


def gen_all_traffic(start: datetime, days: int = 14) -> dict[str, pd.DataFrame]:
    wegvakken = gen_wegvakken()
    return {
        "Wegvak":         wegvakken,
        "Verkeersbord":   gen_verkeersborden(wegvakken),
        "Verkeerslicht":  gen_verkeerslichten(wegvakken),
        "Parkeerplaats":  gen_parkeerplaatsen(wegvakken),
        "OVHalte":        gen_ovhaltes(wegvakken),
        "Verkeersmeting": gen_verkeersmetingen(wegvakken, start, days),
    }
