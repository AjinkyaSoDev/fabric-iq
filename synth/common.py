"""Shared helpers for generating realistic Dutch municipal synthetic data.

Focus: Delft (lat ~52.01, lon ~4.36). Coordinates are expressed in the
Dutch national CRS Rijksdriehoek (EPSG:28992) which is what the GGM and
most Dutch geo-datasets (BAG, BGT, BRK) use.
"""
from __future__ import annotations

import math
import random
import string
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from faker import Faker

fake = Faker("nl_NL")
Faker.seed(42)
random.seed(42)

# Bounding box for Delft in RD New (EPSG:28992) - approx.
DELFT_RD_BBOX = {
    "x_min": 82_500,
    "x_max": 87_500,
    "y_min": 444_000,
    "y_max": 449_500,
}

DELFT_WIJKEN = [
    ("WK050301", "Binnenstad"),
    ("WK050302", "Vrijenban"),
    ("WK050303", "Hof van Delft"),
    ("WK050304", "Voordijkshoorn"),
    ("WK050305", "Voorhof"),
    ("WK050306", "Buitenhof"),
    ("WK050307", "Tanthof-West"),
    ("WK050308", "Tanthof-Oost"),
    ("WK050309", "Wippolder"),
    ("WK050310", "Schieoevers"),
]

DELFT_WATERGANGEN = [
    "Schie", "Oude Delft", "Nieuwe Delft", "Vliet", "Buitenwatersloot",
    "Kerkpolderwetering", "Tanthofkade", "Delftse Hout-vaart",
]


def new_id() -> str:
    return str(uuid.uuid4())


def rd_point() -> tuple[float, float]:
    """Random point inside the Delft RD bounding box."""
    b = DELFT_RD_BBOX
    return (
        random.uniform(b["x_min"], b["x_max"]),
        random.uniform(b["y_min"], b["y_max"]),
    )


def random_wijk() -> tuple[str, str]:
    return random.choice(DELFT_WIJKEN)


def kenteken() -> str:
    """Plausible Dutch licence plate, current sidecode 7+ style: 1-AAA-11."""
    letters = "".join(random.choices(string.ascii_uppercase.replace("O", "").replace("I", ""), k=3))
    return f"{random.randint(1,9)}-{letters}-{random.randint(10,99)}"


def bag_address() -> dict:
    """Approximate BAG-shaped address record."""
    return {
        "straatnaam": fake.street_name(),
        "huisnummer": random.randint(1, 350),
        "postcode": fake.postcode(),
        "woonplaats": "Delft",
    }


@dataclass(frozen=True)
class DiurnalProfile:
    """Simple sinusoidal traffic profile: morning + evening rush."""
    base: float = 120.0          # avg vehicles/hour off-peak
    morning_peak: int = 8         # hour of day
    evening_peak: int = 17
    peak_factor: float = 6.0      # multiplier at peak vs base

    def vehicles_at(self, dt: datetime) -> int:
        h = dt.hour + dt.minute / 60.0
        morning = math.exp(-((h - self.morning_peak) ** 2) / 2.0)
        evening = math.exp(-((h - self.evening_peak) ** 2) / 2.0)
        weekend = 0.55 if dt.weekday() >= 5 else 1.0
        v = self.base * (1 + (self.peak_factor - 1) * (morning + evening)) * weekend
        v *= random.uniform(0.85, 1.15)  # noise
        return max(0, int(round(v)))


def seasonal_water_level(dt: datetime, base_nap_m: float = -0.42) -> float:
    """Yearly + tidal-ish sinusoid for water level relative to NAP."""
    day_of_year = dt.timetuple().tm_yday
    yearly = 0.18 * math.sin(2 * math.pi * (day_of_year - 80) / 365.0)  # high in spring
    daily = 0.06 * math.sin(2 * math.pi * dt.hour / 24.0)
    noise = random.gauss(0, 0.03)
    return round(base_nap_m + yearly + daily + noise, 3)


# NEN-ish reference ranges for urban surface water (illustrative only).
WATER_QUALITY_RANGES = {
    "pH":              (6.5, 8.5, "pH"),
    "O2_mg_l":         (5.0, 12.0, "mg/l"),
    "NO3_mg_l":        (0.0, 10.0, "mg/l"),
    "PO4_mg_l":        (0.0, 0.15, "mg/l"),
    "Cl_mg_l":         (50.0, 300.0, "mg/l"),
    "temperatuur_c":   (2.0, 24.0, "°C"),
    "troebelheid_NTU": (0.5, 25.0, "NTU"),
}


def sample_water_quality(parameter: str) -> tuple[float, str, str]:
    lo, hi, unit = WATER_QUALITY_RANGES[parameter]
    # 10% chance of an out-of-norm reading
    if random.random() < 0.1:
        val = hi * random.uniform(1.05, 1.6)
        status = "overschrijding"
    else:
        val = random.uniform(lo, hi)
        status = "binnen_norm"
    return round(val, 3), unit, status


def hourly_range(start: datetime, days: int) -> Iterable[datetime]:
    for h in range(days * 24):
        yield start + timedelta(hours=h)
