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

# Quick lookup: wijk_code -> wijk name.
WIJK_NAAM = dict(DELFT_WIJKEN)

# Real Delft waterways with a realistic hydrological classification and the
# wijk they predominantly run through. Categorie follows Hoogheemraadschap
# Delfland conventions (primair = boezem, secundair/tertiair = polder).
WATERGANG_CATALOG = [
    ("Schie",                "primair",   "WK050310"),  # Schieoevers
    ("Delftse Schie",        "primair",   "WK050302"),  # Vrijenban
    ("Oude Delft",           "secundair", "WK050301"),  # Binnenstad
    ("Nieuwe Delft",         "secundair", "WK050301"),  # Binnenstad
    ("Buitenwatersloot",     "secundair", "WK050303"),  # Hof van Delft
    ("Westsingelgracht",     "secundair", "WK050301"),  # Binnenstad
    ("Rijn-Schiekanaal",     "primair",   "WK050309"),  # Wippolder
    ("Vliet",                "primair",   "WK050309"),  # Wippolder
    ("Kerkpolderwetering",   "tertiair",  "WK050304"),  # Voordijkshoorn
    ("Tanthofkade",          "tertiair",  "WK050307"),  # Tanthof-West
    ("Abtswoudse Vaart",     "secundair", "WK050308"),  # Tanthof-Oost
    ("Delftse Hout-vaart",   "secundair", "WK050302"),  # Vrijenban
    ("Zuidkolk",             "tertiair",  "WK050305"),  # Voorhof
    ("Buitenhofvijver",      "tertiair",  "WK050306"),  # Buitenhof
]

# Backwards-compatible flat list of waterway names.
DELFT_WATERGANGEN = [naam for naam, _cat, _wijk in WATERGANG_CATALOG]

# Curated, real Delft streets mapped to their wijk and road classification.
# (straatnaam, wijk_code, wegtype). A single street yields several wegvakken.
DELFT_STRATEN = [
    # Binnenstad (WK050301)
    ("Oude Delft",              "WK050301", "erftoegangsweg"),
    ("Koornmarkt",              "WK050301", "erftoegangsweg"),
    ("Wijnhaven",               "WK050301", "erftoegangsweg"),
    ("Brabantse Turfmarkt",     "WK050301", "erftoegangsweg"),
    ("Nieuwe Langendijk",       "WK050301", "erftoegangsweg"),
    ("Phoenixstraat",           "WK050301", "gebiedsontsluitingsweg"),
    ("Westvest",                "WK050301", "gebiedsontsluitingsweg"),
    # Vrijenban (WK050302)
    ("Vrijenbanselaan",         "WK050302", "gebiedsontsluitingsweg"),
    ("Insulindeweg",            "WK050302", "erftoegangsweg"),
    ("Maria Duystlaan",         "WK050302", "erftoegangsweg"),
    # Hof van Delft (WK050303)
    ("Hof van Delftlaan",       "WK050303", "gebiedsontsluitingsweg"),
    ("Roland Holstlaan",        "WK050303", "gebiedsontsluitingsweg"),
    ("Van Bleyswijckstraat",    "WK050303", "erftoegangsweg"),
    ("Krakeelpolderweg",        "WK050303", "gebiedsontsluitingsweg"),
    # Voordijkshoorn (WK050304)
    ("Reinier de Graafweg",     "WK050304", "gebiedsontsluitingsweg"),
    ("Aart van der Leeuwlaan",  "WK050304", "gebiedsontsluitingsweg"),
    ("Delflandplein",           "WK050304", "erftoegangsweg"),
    # Voorhof (WK050305)
    ("Voorhofdreef",            "WK050305", "gebiedsontsluitingsweg"),
    ("Martinus Nijhofflaan",    "WK050305", "gebiedsontsluitingsweg"),
    ("Papsouwselaan",           "WK050305", "gebiedsontsluitingsweg"),
    ("Troelstralaan",           "WK050305", "erftoegangsweg"),
    ("Westlandseweg",           "WK050305", "autoweg"),
    # Buitenhof (WK050306)
    ("Buitenhofdreef",          "WK050306", "gebiedsontsluitingsweg"),
    ("Beukenlaan",              "WK050306", "erftoegangsweg"),
    ("Bachsingel",              "WK050306", "erftoegangsweg"),
    ("Mozartlaan",              "WK050306", "erftoegangsweg"),
    # Tanthof-West (WK050307)
    ("Tanthofdreef",            "WK050307", "gebiedsontsluitingsweg"),
    ("Baljuwlaan",              "WK050307", "erftoegangsweg"),
    ("Abtswoudseweg",           "WK050307", "gebiedsontsluitingsweg"),
    # Tanthof-Oost (WK050308)
    ("Clara van Sparwoudestraat", "WK050308", "erftoegangsweg"),
    ("Vorrinkplaats",           "WK050308", "erftoegangsweg"),
    ("Professor Schermerhornstraat", "WK050308", "erftoegangsweg"),
    # Wippolder (WK050309)
    ("Julianalaan",             "WK050309", "gebiedsontsluitingsweg"),
    ("Mekelweg",                "WK050309", "gebiedsontsluitingsweg"),
    ("Rotterdamseweg",          "WK050309", "gebiedsontsluitingsweg"),
    ("Schoemakerstraat",        "WK050309", "erftoegangsweg"),
    ("Michiel de Ruyterweg",    "WK050309", "gebiedsontsluitingsweg"),
    # Schieoevers (WK050310)
    ("Schieweg",                "WK050310", "gebiedsontsluitingsweg"),
    ("Nijverheidstraat",        "WK050310", "erftoegangsweg"),
    ("Engelsestraat",           "WK050310", "erftoegangsweg"),
    ("Kruithuisweg",            "WK050310", "autoweg"),
]

# Delft postcode (PC4) per wijk — used for plausible BAG-style addresses.
DELFT_POSTCODE_PC4 = {
    "WK050301": ["2611", "2612"],
    "WK050302": ["2613", "2614"],
    "WK050303": ["2613", "2622"],
    "WK050304": ["2625", "2624"],
    "WK050305": ["2624", "2625"],
    "WK050306": ["2622", "2623"],
    "WK050307": ["2627", "2628"],
    "WK050308": ["2627", "2629"],
    "WK050309": ["2628", "2629"],
    "WK050310": ["2627", "2611"],
}

# RVV 1990 sign code -> official Dutch description.
RVV_DESCRIPTIONS = {
    "A01": "Maximumsnelheid",
    "A02": "Einde maximumsnelheid",
    "B06": "Verleen voorrang aan bestuurders op de kruisende weg",
    "C01": "Gesloten in beide richtingen voor voertuigen",
    "C02": "Eenrichtingsweg, in deze richting gesloten",
    "E06": "Gehandicaptenparkeerplaats",
    "G11": "Verplicht fietspad",
    "J16": "Slipgevaar",
    "L02": "Voetgangersoversteekplaats",
}

# Real Delft public-transport stops: (naam, modaliteit, lijn).
DELFT_OV_HALTES = [
    ("Delft, Station",                 "trein", "Intercity/Sprinter"),
    ("Delft Campus",                   "trein", "Sprinter"),
    ("Delft, Stationsplein",           "tram",  "1"),
    ("Delft, Prinsenhof",              "tram",  "1"),
    ("Delft, Vrijenbanselaan",         "tram",  "19"),
    ("Delft, TU-wijk / Mekelpark",     "tram",  "19"),
    ("Delft, Technopolis",             "tram",  "19"),
    ("Delft, Aula TU",                 "bus",   "40"),
    ("Delft, Kruithuisweg",            "bus",   "37"),
    ("Delft, Tanthof",                 "bus",   "62"),
    ("Delft, Voorhof",                 "bus",   "61"),
    ("Delft, Buitenhof",               "bus",   "60"),
    ("Delft, Reinier de Graaf Gasthuis", "bus", "33"),
    ("Delft, Martinus Nijhofflaan",    "bus",   "69"),
    ("Delft, Phoenixstraat",           "bus",   "174"),
]

# Real Delft parking garages: (naam, capaciteit, tarief_per_uur).
DELFT_PARKEERGARAGES = [
    ("Parkeergarage Markt (Phoenix)", 350, 3.5),
    ("Parkeergarage Zuidpoort",       420, 3.0),
    ("Parkeergarage Prinsenhof",      300, 3.0),
    ("Parkeergarage Koepoort",        375, 3.5),
    ("Van Leeuwenhoekgarage",         620, 2.5),
    ("P+R Delft (Station)",           285, 0.0),
]

# Real / plausible Delfland pumping stations serving the Delft polders.
DELFT_GEMALEN = [
    "Gemaal Schie",
    "Gemaal Westland",
    "Gemaal Tanthof",
    "Gemaal Voordijkshoorn",
    "Gemaal Buitenwatersloot",
    "Gemaal Abtswoude",
    "Gemaal Kerkpolder",
    "Boezemgemaal Delft",
    "Gemaal Harnaschpolder",
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


def random_straat() -> tuple[str, str, str]:
    """Return (straatnaam, wijk_code, wegtype) for a real Delft street."""
    return random.choice(DELFT_STRATEN)


def delft_postcode(wijk_code: str | None = None) -> str:
    """Plausible Delft postcode (e.g. '2611 AB') for the given wijk."""
    if wijk_code and wijk_code in DELFT_POSTCODE_PC4:
        pc4 = random.choice(DELFT_POSTCODE_PC4[wijk_code])
    else:
        pc4 = random.choice([p for prefixes in DELFT_POSTCODE_PC4.values() for p in prefixes])
    letters = "".join(random.choices(string.ascii_uppercase, k=2))
    return f"{pc4} {letters}"


def bag_address(wijk_code: str | None = None) -> dict:
    """Approximate BAG-shaped address record anchored in Delft."""
    straatnaam, straat_wijk, _wegtype = random_straat()
    wijk = wijk_code or straat_wijk
    return {
        "straatnaam": straatnaam,
        "huisnummer": random.randint(1, 350),
        "postcode": delft_postcode(wijk),
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
