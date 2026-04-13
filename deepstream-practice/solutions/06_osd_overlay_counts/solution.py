#!/usr/bin/env python3
"""Run the lesson 06 reference solution."""

from pathlib import Path
import runpy


REFERENCE = Path(__file__).resolve().parents[2] / "lessons" / "06_osd_overlay_counts" / "05_reference.py"


if __name__ == "__main__":
    runpy.run_path(str(REFERENCE), run_name="__main__")
