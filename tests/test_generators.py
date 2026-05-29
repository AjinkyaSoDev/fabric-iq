"""Smoke tests for synthetic generators."""
from datetime import datetime

import pandas as pd
import pytest

from synth.generators import traffic, water


@pytest.fixture(scope="module")
def start():
    return datetime(2025, 1, 1)


def test_traffic_referential_integrity(start):
    ds = traffic.gen_all_traffic(start, days=2)
    wegvak_ids = set(ds["Wegvak"]["wegvak_id"])
    for child in ("Verkeersbord", "Verkeerslicht", "Parkeerplaats", "OVHalte", "Verkeersmeting"):
        assert set(ds[child]["wegvak_id"]).issubset(wegvak_ids), f"{child} has orphan FK"


def test_water_referential_integrity(start):
    ds = water.gen_all_water(start, days=2)
    w_ids = set(ds["Watergang"]["watergang_id"])
    for child in ("Gemaal", "Lozingspunt", "Waterpeilmeting", "Waterkwaliteitsmeting"):
        assert set(ds[child]["watergang_id"]).issubset(w_ids), f"{child} has orphan FK"


def test_traffic_value_ranges(start):
    ds = traffic.gen_all_traffic(start, days=1)
    vm = ds["Verkeersmeting"]
    assert vm["voertuigen_per_uur"].between(0, 6000).all()
    assert vm["pct_zwaar_verkeer"].between(0, 1).all()


def test_water_value_ranges(start):
    ds = water.gen_all_water(start, days=1)
    peil = ds["Waterpeilmeting"]
    assert peil["peil_nap_m"].between(-3.5, 1.5).all()
    kwal = ds["Waterkwaliteitsmeting"]
    assert kwal["norm_status"].isin(["binnen_norm", "overschrijding", "onbekend"]).all()
