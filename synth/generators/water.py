"""Generators for Water & Milieu (IV3 7.x) entities."""
from __future__ import annotations

import random
from datetime import datetime

import pandas as pd

from synth.common import (
    DELFT_WATERGANGEN,
    WATER_QUALITY_RANGES,
    hourly_range,
    new_id,
    random_wijk,
    sample_water_quality,
    seasonal_water_level,
)

RIOOLTYPES = ["gemengd", "hwa", "dwa"]
DIAMETERS = [200, 250, 300, 400, 500, 600, 800, 1000, 1200]
MATERIALEN = ["beton", "pvc", "gres", "gietijzer"]


def gen_watergangen(n: int | None = None) -> pd.DataFrame:
    names = DELFT_WATERGANGEN if n is None else random.choices(DELFT_WATERGANGEN, k=n)
    rows = []
    for name in names:
        wijk_code, _ = random_wijk()
        rows.append({
            "watergang_id": new_id(),
            "naam": name,
            "categorie": random.choices(["primair", "secundair", "tertiair"], weights=[0.25, 0.45, 0.30])[0],
            "lengte_m": round(random.uniform(120, 4200), 1),
            "breedte_m": round(random.uniform(1.5, 30), 1),
            "wijk_code": wijk_code,
        })
    return pd.DataFrame(rows)


def gen_rioolstrengen(n: int = 250) -> pd.DataFrame:
    rows = []
    for _ in range(n):
        rows.append({
            "streng_id": new_id(),
            "type": random.choices(RIOOLTYPES, weights=[0.55, 0.30, 0.15])[0],
            "diameter_mm": random.choice(DIAMETERS),
            "materiaal": random.choices(MATERIALEN, weights=[0.5, 0.35, 0.10, 0.05])[0],
            "aanleg_jaar": random.randint(1950, 2024),
        })
    return pd.DataFrame(rows)


def gen_gemalen(watergangen: pd.DataFrame, n: int = 12) -> pd.DataFrame:
    rows = []
    for i in range(n):
        rows.append({
            "gemaal_id": new_id(),
            "naam": f"Gemaal {random.choice(['Noord','Zuid','Oost','West','Centrum'])} {i+1}",
            "watergang_id": watergangen["watergang_id"].sample(1).iloc[0],
            "capaciteit_m3_h": random.choice([200, 500, 1000, 2500, 5000, 10000, 25000]),
            "is_in_bedrijf": random.random() > 0.05,
        })
    return pd.DataFrame(rows)


def gen_lozingspunten(watergangen: pd.DataFrame, n: int = 30) -> pd.DataFrame:
    rows = []
    for _ in range(n):
        rows.append({
            "lozing_id": new_id(),
            "watergang_id": watergangen["watergang_id"].sample(1).iloc[0],
            "type": random.choices(["overstort", "RWZI", "industrie", "hemelwater"],
                                   weights=[0.5, 0.05, 0.10, 0.35])[0],
        })
    return pd.DataFrame(rows)


def gen_waterpeilmetingen(watergangen: pd.DataFrame, start: datetime, days: int = 14) -> pd.DataFrame:
    rows = []
    for _, w in watergangen.iterrows():
        # category-dependent baseline
        base = {"primair": -0.42, "secundair": -0.55, "tertiair": -0.65}[w["categorie"]]
        for dt in hourly_range(start, days):
            peil = seasonal_water_level(dt, base_nap_m=base)
            rows.append({
                "watergang_id": w["watergang_id"],
                "meet_tijdstip": dt,
                "peil_nap_m": peil,
                "debiet_m3_s": round(max(0, random.gauss(2.5, 1.2)), 3),
            })
    return pd.DataFrame(rows)


def gen_waterkwaliteitsmetingen(
    watergangen: pd.DataFrame, start: datetime, days: int = 14,
    interval_hours: int = 6,
) -> pd.DataFrame:
    rows = []
    parameters = list(WATER_QUALITY_RANGES.keys())
    for _, w in watergangen.iterrows():
        for dt in hourly_range(start, days):
            if dt.hour % interval_hours != 0:
                continue
            for param in parameters:
                val, unit, status = sample_water_quality(param)
                rows.append({
                    "watergang_id": w["watergang_id"],
                    "meet_tijdstip": dt,
                    "parameter": param,
                    "waarde": val,
                    "eenheid": unit,
                    "norm_status": status,
                })
    return pd.DataFrame(rows)


def gen_all_water(start: datetime, days: int = 14) -> dict[str, pd.DataFrame]:
    watergangen = gen_watergangen()
    return {
        "Watergang":             watergangen,
        "Rioolstreng":           gen_rioolstrengen(),
        "Gemaal":                gen_gemalen(watergangen),
        "Lozingspunt":           gen_lozingspunten(watergangen),
        "Waterpeilmeting":       gen_waterpeilmetingen(watergangen, start, days),
        "Waterkwaliteitsmeting": gen_waterkwaliteitsmetingen(watergangen, start, days),
    }
