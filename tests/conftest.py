# -*- coding: utf-8 -*-
"""Shared fixtures for autoresearcher tests."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def tmp_experiment_dir(tmp_path):
    """Create a temporary experiment directory with a config file."""
    config = {
        "experiment_id": "test-exp-001",
        "cycles": 3,
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config))
    return tmp_path, config_file


@pytest.fixture
def tmp_results_tsv(tmp_path):
    """Create a temporary path for a results TSV file."""
    return tmp_path / "results.tsv"


@pytest.fixture
def tmp_results_dir(tmp_path):
    """Create a temporary directory for JSON results storage."""
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    return results_dir
