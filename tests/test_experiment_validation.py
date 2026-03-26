# -*- coding: utf-8 -*-
"""Unit tests for BaseExperiment input validation."""

import json
import pytest
from pathlib import Path
from autoresearcher.experiment import BaseExperiment, RetryConfig


class TestExperiment(BaseExperiment):
    """Concrete implementation for testing."""

    def evaluate(self, cycle: int) -> dict[str, float]:
        return {"test_metric": 1.0}

    def optimize(self, result) -> None:
        pass


def test_valid_initialization(tmp_path: Path):
    """Test successful initialization with valid inputs."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({
        "experiment_id": "test-exp",
        "cycles": 3
    }))

    exp = TestExperiment(config_file)
    assert exp.experiment_id == "test-exp"
    assert exp.max_cycles == 3
    assert isinstance(exp.retry_config, RetryConfig)


def test_experiment_id_must_be_non_empty_string(tmp_path: Path):
    """Test that empty experiment_id raises ValueError."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({
        "experiment_id": "",
        "cycles": 3
    }))

    with pytest.raises(ValueError, match="experiment_id must be a non-empty string"):
        TestExperiment(config_file)


def test_experiment_id_must_be_string(tmp_path: Path):
    """Test that non-string experiment_id raises ValueError."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({
        "experiment_id": 123,
        "cycles": 3
    }))

    with pytest.raises(ValueError, match="experiment_id must be a non-empty string"):
        TestExperiment(config_file)


def test_experiment_id_whitespace_only(tmp_path: Path):
    """Test that whitespace-only experiment_id raises ValueError."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({
        "experiment_id": "   ",
        "cycles": 3
    }))

    with pytest.raises(ValueError, match="experiment_id must be a non-empty string"):
        TestExperiment(config_file)


def test_max_cycles_must_be_positive(tmp_path: Path):
    """Test that non-positive max_cycles raises ValueError."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({
        "experiment_id": "test-exp",
        "cycles": 0
    }))

    with pytest.raises(ValueError, match="max_cycles must be a positive integer"):
        TestExperiment(config_file)


def test_max_cycles_must_be_integer(tmp_path: Path):
    """Test that non-integer max_cycles raises ValueError."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({
        "experiment_id": "test-exp",
        "cycles": 3.5
    }))

    with pytest.raises(ValueError, match="max_cycles must be a positive integer"):
        TestExperiment(config_file)


def test_max_cycles_negative(tmp_path: Path):
    """Test that negative max_cycles raises ValueError."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({
        "experiment_id": "test-exp",
        "cycles": -1
    }))

    with pytest.raises(ValueError, match="max_cycles must be a positive integer"):
        TestExperiment(config_file)


def test_retry_config_must_be_instance(tmp_path: Path):
    """Test that invalid retry_config raises ValueError."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({
        "experiment_id": "test-exp",
        "cycles": 3
    }))

    with pytest.raises(ValueError, match="retry_config must be a RetryConfig instance"):
        TestExperiment(config_file, retry_config="not a config")


def test_retry_config_with_dict(tmp_path: Path):
    """Test that dict retry_config raises ValueError."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({
        "experiment_id": "test-exp",
        "cycles": 3
    }))

    with pytest.raises(ValueError, match="retry_config must be a RetryConfig instance"):
        TestExperiment(config_file, retry_config={"max_retries": 5})


def test_custom_retry_config(tmp_path: Path):
    """Test successful initialization with custom RetryConfig."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({
        "experiment_id": "test-exp",
        "cycles": 3
    }))

    custom_config = RetryConfig(max_retries=5, base_delay=2.0)
    exp = TestExperiment(config_file, retry_config=custom_config)
    assert exp.retry_config.max_retries == 5
    assert exp.retry_config.base_delay == 2.0
