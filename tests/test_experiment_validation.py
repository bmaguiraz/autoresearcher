# -*- coding: utf-8 -*-
"""Tests for BaseExperiment input validation."""

import json
from pathlib import Path

import pytest

from autoresearcher.experiment import BaseExperiment, RetryConfig


class ValidationExperiment(BaseExperiment):
    """Minimal concrete implementation for testing validation."""

    def evaluate(self, cycle):
        return {"score": 1.0}

    def optimize(self, result):
        pass


def _make_config(tmp_path, experiment_id="test-exp", cycles=5):
    """Helper to create a test config file."""
    config = {"experiment_id": experiment_id, "cycles": cycles}
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    return config_path


class TestExperimentIdValidation:
    def test_valid_experiment_id(self, tmp_path):
        """Valid non-empty string should pass validation."""
        config_path = _make_config(tmp_path, experiment_id="valid-id")
        exp = ValidationExperiment(config_path)
        assert exp.experiment_id == "valid-id"

    def test_empty_string_experiment_id(self, tmp_path):
        """Empty string should raise ValueError."""
        config_path = _make_config(tmp_path, experiment_id="")
        with pytest.raises(ValueError, match="experiment_id must be a non-empty string"):
            ValidationExperiment(config_path)

    def test_whitespace_only_experiment_id(self, tmp_path):
        """Whitespace-only string should raise ValueError."""
        config_path = _make_config(tmp_path, experiment_id="   ")
        with pytest.raises(ValueError, match="experiment_id must be a non-empty string"):
            ValidationExperiment(config_path)

    def test_non_string_experiment_id(self, tmp_path):
        """Non-string types should raise ValueError."""
        config_path = _make_config(tmp_path, experiment_id=123)
        with pytest.raises(ValueError, match="experiment_id must be a non-empty string"):
            ValidationExperiment(config_path)


class TestMaxCyclesValidation:
    def test_valid_positive_max_cycles(self, tmp_path):
        """Positive integer should pass validation."""
        config_path = _make_config(tmp_path, cycles=10)
        exp = ValidationExperiment(config_path)
        assert exp.max_cycles == 10

    def test_zero_max_cycles(self, tmp_path):
        """Zero should raise ValueError."""
        config_path = _make_config(tmp_path, cycles=0)
        with pytest.raises(ValueError, match="max_cycles must be a positive integer"):
            ValidationExperiment(config_path)

    def test_negative_max_cycles(self, tmp_path):
        """Negative integer should raise ValueError."""
        config_path = _make_config(tmp_path, cycles=-5)
        with pytest.raises(ValueError, match="max_cycles must be a positive integer"):
            ValidationExperiment(config_path)

    def test_float_max_cycles(self, tmp_path):
        """Float should raise ValueError."""
        config_path = _make_config(tmp_path, cycles=5.5)
        with pytest.raises(ValueError, match="max_cycles must be a positive integer"):
            ValidationExperiment(config_path)

    def test_string_max_cycles(self, tmp_path):
        """String should raise ValueError."""
        config_path = _make_config(tmp_path, cycles="5")
        with pytest.raises(ValueError, match="max_cycles must be a positive integer"):
            ValidationExperiment(config_path)


class TestRetryConfigValidation:
    def test_valid_retry_config(self, tmp_path):
        """Valid RetryConfig instance should pass validation."""
        config_path = _make_config(tmp_path)
        rc = RetryConfig(max_retries=5)
        exp = ValidationExperiment(config_path, retry_config=rc)
        assert exp.retry_config.max_retries == 5

    def test_default_retry_config(self, tmp_path):
        """Default RetryConfig should pass validation."""
        config_path = _make_config(tmp_path)
        exp = ValidationExperiment(config_path)
        assert isinstance(exp.retry_config, RetryConfig)
        assert exp.retry_config.max_retries == 3

    def test_dict_retry_config(self, tmp_path):
        """Dict should raise ValueError."""
        config_path = _make_config(tmp_path)
        with pytest.raises(ValueError, match="retry_config must be a RetryConfig instance"):
            ValidationExperiment(config_path, retry_config={"max_retries": 5})

    def test_string_retry_config(self, tmp_path):
        """String should raise ValueError."""
        config_path = _make_config(tmp_path)
        with pytest.raises(ValueError, match="retry_config must be a RetryConfig instance"):
            ValidationExperiment(config_path, retry_config="invalid")

    def test_int_retry_config(self, tmp_path):
        """Integer should raise ValueError."""
        config_path = _make_config(tmp_path)
        with pytest.raises(ValueError, match="retry_config must be a RetryConfig instance"):
            ValidationExperiment(config_path, retry_config=5)
