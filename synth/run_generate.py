"""Run all synthetic generators and write Parquet into the bronze layer.

Usage:
    python -m synth.run_generate --days 14 --out ../lakehouse/bronze
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from synth.generators import traffic, water


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=14, help="Days of time-series data")
    p.add_argument("--start", type=str, default=None, help="ISO start date (defaults to N days ago)")
    p.add_argument("--out", type=str, default=str(Path(__file__).resolve().parents[1] / "lakehouse" / "bronze"))
    args = p.parse_args(argv)

    start = (
        datetime.fromisoformat(args.start)
        if args.start
        else datetime.utcnow().replace(minute=0, second=0, microsecond=0) - timedelta(days=args.days)
    )

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    datasets: dict[str, pd.DataFrame] = {}
    datasets.update(traffic.gen_all_traffic(start, days=args.days))
    datasets.update(water.gen_all_water(start, days=args.days))

    for name, df in datasets.items():
        target = out_root / name
        target.mkdir(parents=True, exist_ok=True)
        if "meet_tijdstip" in df.columns:
            # partition time series by date for Fabric-friendly layout
            df = df.copy()
            df["ingest_date"] = pd.to_datetime(df["meet_tijdstip"]).dt.date.astype(str)
            for d, part in df.groupby("ingest_date"):
                part_dir = target / f"ingest_date={d}"
                part_dir.mkdir(parents=True, exist_ok=True)
                part.drop(columns=["ingest_date"]).to_parquet(part_dir / "part-0.parquet", index=False)
        else:
            df.to_parquet(target / "part-0.parquet", index=False)
        print(f"  wrote {name}: {len(df):>7} rows -> {target.relative_to(out_root.parent)}")

    print(f"\nBronze layer ready at: {out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
