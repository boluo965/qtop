#!/usr/bin/env python3
"""Run qtop against archived PBS samples and save rendered output.

Usage:
    python tools/validate_pbs_samples.py /path/to/qtop-test-repo/qtop5/results --limit 100 --output /tmp/qtop-pbs-rendered
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("samples_dir", type=Path)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("/tmp/qtop-pbs-rendered"))
    args = parser.parse_args()

    sample_dirs = sorted(path for path in args.samples_dir.iterdir() if path.is_dir())
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = []

    for sample_dir in sample_dirs:
        proc = subprocess.run(
            ["./qtop", "-b", "pbs", "-s", str(sample_dir), "-c", "ON"],
            text=True,
            capture_output=True,
            timeout=8,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            continue

        output_file = args.output / f"{sample_dir.name}.ans"
        output_file.write_text(proc.stdout)
        manifest.append(
            {
                "sample": sample_dir.name,
                "output": output_file.name,
                "stderr_tail": proc.stderr.splitlines()[-5:],
            }
        )
        if len(manifest) >= args.limit:
            break

    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"validated={len(manifest)} output={args.output}")
    return 0 if len(manifest) >= args.limit else 1


if __name__ == "__main__":
    raise SystemExit(main())
