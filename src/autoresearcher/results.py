# -*- coding: utf-8 -*-
"""Result tracking and persistence utilities."""

import csv
import json
from pathlib import Path
from typing import Any


class ResultsLog:
    """Append-only TSV log for experiment results."""

    HEADER = ["commit", "accuracy", "cost_cents", "status", "description"]

    def __init__(self, path: str | Path):
        self.path = Path(path)
        if not self.path.exists():
            self._write_header()

    def _write_header(self) -> None:
        with open(self.path, "w", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(self.HEADER)

    def append(
        self,
        commit: str,
        accuracy: float,
        cost_cents: float,
        status: str,
        description: str,
    ) -> None:
        """Append a result row to the log."""
        with open(self.path, "a", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow([commit[:7], f"{accuracy:.3f}", f"{cost_cents:.1f}", status, description])

    def read_all(self) -> list[dict[str, str]]:
        """Read all results from the log."""
        if not self.path.exists():
            return []
        with open(self.path, newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            return list(reader)

    def best_accuracy(self) -> float:
        """Return the highest accuracy recorded."""
        rows = self.read_all()
        if not rows:
            return 0.0
        return max(float(r["accuracy"]) for r in rows if r.get("status") == "keep")


class ResultsStore:
    """JSON-based result storage for experiment outputs."""

    def __init__(self, results_dir: str | Path):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def save(self, data: dict[str, Any], filename: str) -> Path:
        """Save results data to a JSON file."""
        filepath = self.results_dir / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        return filepath

    def load(self, filename: str) -> dict[str, Any]:
        """Load results from a JSON file."""
        filepath = self.results_dir / filename
        with open(filepath) as f:
            return json.load(f)

    def load_latest(self) -> dict[str, Any] | None:
        """Load the most recent results file."""
        latest = self.results_dir / "results_latest.json"
        if latest.exists():
            return self.load("results_latest.json")
        return None

    def list_results(self) -> list[Path]:
        """List all result files sorted by modification time."""
        return sorted(self.results_dir.glob("results_*.json"), key=lambda p: p.stat().st_mtime)
