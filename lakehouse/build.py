"""Build silver and gold layers from the bronze synthetic data.

Silver: cleansed + typed + referential-integrity filtered.
Gold:   star-schema marts ready for the semantic model.

This module uses pandas + pyarrow so it runs locally without Spark. The
notebooks under `notebooks/` show the equivalent PySpark calls for Fabric.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
BRONZE = ROOT / "bronze"
SILVER = ROOT / "silver"
GOLD = ROOT / "gold"


def _read(layer: Path, name: str) -> pd.DataFrame:
    base = layer / name
    if not base.exists():
        raise FileNotFoundError(base)
    parts = list(base.rglob("*.parquet"))
    if not parts:
        raise FileNotFoundError(f"No parquet under {base}")
    return pd.concat((pd.read_parquet(p) for p in parts), ignore_index=True)


def _write(layer: Path, name: str, df: pd.DataFrame) -> None:
    out = layer / name
    out.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out / "part-0.parquet", index=False)
    print(f"  {layer.name}/{name:<28} {len(df):>8} rows")


def build_silver() -> None:
    SILVER.mkdir(parents=True, exist_ok=True)
    wegvak = _read(BRONZE, "Wegvak").drop_duplicates("wegvak_id")
    watergang = _read(BRONZE, "Watergang").drop_duplicates("watergang_id")

    _write(SILVER, "Wegvak", wegvak)
    _write(SILVER, "Watergang", watergang)

    for child, fk in [
        ("Verkeersbord", "wegvak_id"),
        ("Verkeerslicht", "wegvak_id"),
        ("Parkeerplaats", "wegvak_id"),
        ("OVHalte", "wegvak_id"),
        ("Verkeersmeting", "wegvak_id"),
    ]:
        df = _read(BRONZE, child)
        df = df[df[fk].isin(wegvak["wegvak_id"])]
        _write(SILVER, child, df)

    for child, fk in [
        ("Gemaal", "watergang_id"),
        ("Lozingspunt", "watergang_id"),
        ("Waterpeilmeting", "watergang_id"),
        ("Waterkwaliteitsmeting", "watergang_id"),
    ]:
        df = _read(BRONZE, child)
        df = df[df[fk].isin(watergang["watergang_id"])]
        _write(SILVER, child, df)

    _write(SILVER, "Rioolstreng", _read(BRONZE, "Rioolstreng"))


def build_gold() -> None:
    GOLD.mkdir(parents=True, exist_ok=True)

    wegvak = _read(SILVER, "Wegvak")
    watergang = _read(SILVER, "Watergang")
    verkeer = _read(SILVER, "Verkeersmeting")
    peil = _read(SILVER, "Waterpeilmeting")
    kwaliteit = _read(SILVER, "Waterkwaliteitsmeting")

    # dim_locatie unifies road segments and waterways for cross-domain analysis
    dim_locatie = pd.concat([
        wegvak.assign(locatie_type="wegvak").rename(columns={"wegvak_id": "locatie_id", "straatnaam": "naam"})[
            ["locatie_id", "naam", "locatie_type", "wijk_code", "geom_x_rd", "geom_y_rd"]
        ],
        watergang.assign(locatie_type="watergang", geom_x_rd=None, geom_y_rd=None).rename(
            columns={"watergang_id": "locatie_id"}
        )[["locatie_id", "naam", "locatie_type", "wijk_code", "geom_x_rd", "geom_y_rd"]],
    ], ignore_index=True)
    _write(GOLD, "dim_locatie", dim_locatie)

    times = pd.concat([
        pd.to_datetime(verkeer["meet_tijdstip"]),
        pd.to_datetime(peil["meet_tijdstip"]),
        pd.to_datetime(kwaliteit["meet_tijdstip"]),
    ]).drop_duplicates().sort_values()
    dim_tijd = pd.DataFrame({"tijdstip": times})
    dim_tijd["datum"] = dim_tijd["tijdstip"].dt.date
    dim_tijd["uur"] = dim_tijd["tijdstip"].dt.hour
    dim_tijd["weekdag"] = dim_tijd["tijdstip"].dt.day_name()
    dim_tijd["is_weekend"] = dim_tijd["tijdstip"].dt.weekday >= 5
    _write(GOLD, "dim_tijd", dim_tijd)

    _write(GOLD, "fact_verkeer", verkeer.rename(columns={"wegvak_id": "locatie_id"}))
    _write(GOLD, "fact_waterpeil", peil.rename(columns={"watergang_id": "locatie_id"}))
    _write(GOLD, "fact_waterkwaliteit", kwaliteit.rename(columns={"watergang_id": "locatie_id"}))

    # Cross-domain alerts mart: hours where traffic peak AND water-norm overschrijding co-occur per wijk
    overschrijdingen = kwaliteit[kwaliteit["norm_status"] == "overschrijding"].copy()
    overschrijdingen["uur"] = pd.to_datetime(overschrijdingen["meet_tijdstip"]).dt.floor("h")
    verkeer_h = verkeer.copy()
    verkeer_h["uur"] = pd.to_datetime(verkeer_h["meet_tijdstip"]).dt.floor("h")
    verkeer_h = verkeer_h.merge(wegvak[["wegvak_id", "wijk_code"]], on="wegvak_id")
    overschrijdingen = overschrijdingen.merge(
        watergang[["watergang_id", "wijk_code"]], on="watergang_id"
    )
    cross = verkeer_h.groupby(["wijk_code", "uur"], as_index=False)["voertuigen_per_uur"].sum().merge(
        overschrijdingen.groupby(["wijk_code", "uur"], as_index=False).size().rename(columns={"size": "overschrijdingen"}),
        on=["wijk_code", "uur"], how="inner",
    )
    _write(GOLD, "fact_cross_domain_alert", cross)


if __name__ == "__main__":
    print("Building silver...")
    build_silver()
    print("\nBuilding gold...")
    build_gold()
    print(f"\nDone. Gold layer at: {GOLD}")
