"""Extract a JSON schema catalog from the GGM XMI source.

The upstream GGM (Gemeentelijk Gegevensmodel) is published as XMI by
Gemeente Delft: https://github.com/Gemeente-Delft/Gemeentelijk-Gegevensmodel

This script downloads the XMI (or reads a local copy), filters the model to
packages relevant to the Verkeer & Vervoer (IV3 2.x) and Water/Milieu (IV3 7.x)
domains, and emits a `schema_catalog.json` file consumable by the synthetic
data generators in `fabric-iq/synth/`.

A curated `schema_catalog.json` is checked in alongside this script so the
POC works out-of-the-box without depending on a successful XMI parse.
Re-run this script to refresh the catalog from upstream when GGM is bumped.

Usage:
    python extract_schema.py --xmi <path-or-url> --out schema_catalog.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

try:
    from lxml import etree
except ImportError:  # pragma: no cover - optional dep
    etree = None  # type: ignore

# GGM packages whose names contain any of these tokens are in scope.
DOMAIN_TOKENS = (
    "verkeer", "vervoer", "parkeren", "openbaar vervoer",
    "water", "riolering", "milieu",
)

# UML XMI namespace map (Enterprise Architect export).
NS = {
    "xmi": "http://schema.omg.org/spec/XMI/2.1",
    "uml": "http://schema.omg.org/spec/UML/2.1",
}


def _iter_classes(root) -> Iterable:
    yield from root.iter("{%s}Class" % NS["uml"])


def parse_xmi(xmi_path: Path) -> dict:
    if etree is None:
        raise RuntimeError("lxml is required to parse XMI. pip install lxml")

    tree = etree.parse(str(xmi_path))
    root = tree.getroot()

    entities: dict[str, dict] = {}
    for cls in _iter_classes(root):
        name = cls.get("name")
        if not name:
            continue
        parent = cls.getparent()
        package_name = (parent.get("name") or "").lower() if parent is not None else ""
        if not any(tok in package_name for tok in DOMAIN_TOKENS):
            continue

        attrs: dict[str, dict] = {}
        for attr in cls.findall("ownedAttribute"):
            aname = attr.get("name")
            if not aname:
                continue
            type_elem = attr.find("type")
            atype = type_elem.get("{%s}idref" % NS["xmi"]) if type_elem is not None else "string"
            attrs[aname] = {"type": _normalise_type(atype)}
        entities[name] = {
            "package": package_name,
            "attributes": attrs,
        }

    return {
        "version": "extracted",
        "ggm_version": "from-xmi",
        "entities": entities,
    }


def _normalise_type(raw: str) -> str:
    raw = (raw or "").lower()
    if any(t in raw for t in ("int", "geheel")):
        return "int"
    if any(t in raw for t in ("decimal", "real", "double", "float")):
        return "decimal"
    if "bool" in raw:
        return "bool"
    if "date" in raw or "datum" in raw:
        return "date"
    if "time" in raw or "tijd" in raw:
        return "timestamp"
    return "string"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--xmi", required=True, help="Path to GGM XMI file")
    p.add_argument("--out", default="schema_catalog.json")
    args = p.parse_args(argv)

    catalog = parse_xmi(Path(args.xmi))
    Path(args.out).write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(catalog['entities'])} entities to {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
