# GGM Schema Reference

**Gemeentelijk Gegevensmodel (GGM)** — open Dutch municipal data standard by Gemeente Delft.

## Domains Used in Fabric IQ

### Verkeer & Vervoer (Traffic & Transport) — IV3 2.x
| Entity | Description |
|--------|-------------|
| `Wegvak` | Road segment with geometry and classification |
| `Verkeerstelling` | Hourly vehicle count measurement |
| `Voertuigtype` | Vehicle type classification |
| `Meetlocatie` | Sensor/measurement location |

### Water & Milieu (Water & Environment) — IV3 7.x
| Entity | Description |
|--------|-------------|
| `Watergang` | Waterway/canal segment |
| `Waterpeilmeting` | Hourly water level reading (m NAP) |
| `Waterkwaliteitsmeting` | NEN 6600-aligned quality reading |
| `Norm` | Quality threshold/norm value |

## Cross-Domain Alert Logic
`fact_cross_domain_alert` is generated when, in the same hour:
- A `wegvak` near a `watergang` has vehicle count > P90 threshold **AND**
- That `watergang` has a water quality parameter breaching its norm

## Source
- GGM XMI schema: `ggm/` directory
- Extracted catalog: `ggm/schema_catalog.json`
- Extractor script: `ggm/extract_schema.py`
