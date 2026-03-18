# -*- coding: utf-8 -*-
"""Tests for the results module."""

import pytest

from autoresearcher.results import ResultsLog, ResultsStore


class TestResultsLog:
    def test_creates_file_with_header(self, tmp_path):
        log_path = tmp_path / "results.tsv"
        log = ResultsLog(log_path)
        assert log_path.exists()
        content = log_path.read_text()
        assert "commit" in content
        assert "accuracy" in content

    def test_append_and_read(self, tmp_path):
        log_path = tmp_path / "results.tsv"
        log = ResultsLog(log_path)
        log.append(
            commit="abc1234567",
            accuracy=0.85,
            cost_cents=1.5,
            status="keep",
            description="test run",
        )
        rows = log.read_all()
        assert len(rows) == 1
        assert rows[0]["commit"] == "abc1234"
        assert rows[0]["accuracy"] == "0.850"
        assert rows[0]["status"] == "keep"

    def test_append_multiple(self, tmp_path):
        log_path = tmp_path / "results.tsv"
        log = ResultsLog(log_path)
        log.append("aaa1111111", 0.7, 1.0, "keep", "first")
        log.append("bbb2222222", 0.9, 2.0, "keep", "second")
        log.append("ccc3333333", 0.6, 0.5, "skip", "third")
        rows = log.read_all()
        assert len(rows) == 3

    def test_best_accuracy(self, tmp_path):
        log_path = tmp_path / "results.tsv"
        log = ResultsLog(log_path)
        log.append("aaa1111111", 0.7, 1.0, "keep", "first")
        log.append("bbb2222222", 0.9, 2.0, "keep", "second")
        log.append("ccc3333333", 0.95, 0.5, "skip", "third")
        assert log.best_accuracy() == pytest.approx(0.9)

    def test_best_accuracy_empty(self, tmp_path):
        log_path = tmp_path / "results.tsv"
        log = ResultsLog(log_path)
        assert log.best_accuracy() == 0.0

    def test_best_accuracy_no_keep_rows(self, tmp_path):
        """best_accuracy returns 0.0 when rows exist but none have status 'keep'."""
        log_path = tmp_path / "results.tsv"
        log = ResultsLog(log_path)
        log.append("aaa1111111", 0.9, 1.0, "skip", "skipped")
        log.append("bbb2222222", 0.8, 2.0, "revert", "reverted")
        assert log.best_accuracy() == 0.0

    def test_read_all_nonexistent(self, tmp_path):
        log_path = tmp_path / "nonexistent.tsv"
        log = ResultsLog.__new__(ResultsLog)
        log.path = log_path
        assert log.read_all() == []


class TestResultsStore:
    def test_save_and_load(self, tmp_path):
        store = ResultsStore(tmp_path / "results")
        data = {"experiment": "test", "score": 0.85}
        path = store.save(data, "test_result.json")
        assert path.exists()
        loaded = store.load("test_result.json")
        assert loaded == data

    def test_creates_directory(self, tmp_path):
        results_dir = tmp_path / "nested" / "results"
        store = ResultsStore(results_dir)
        assert results_dir.is_dir()

    def test_load_latest(self, tmp_path):
        store = ResultsStore(tmp_path / "results")
        data = {"experiment": "test", "latest": True}
        store.save(data, "results_latest.json")
        loaded = store.load_latest()
        assert loaded is not None
        assert loaded["latest"] is True

    def test_load_latest_none(self, tmp_path):
        store = ResultsStore(tmp_path / "results")
        assert store.load_latest() is None

    def test_list_results(self, tmp_path):
        store = ResultsStore(tmp_path / "results")
        store.save({"a": 1}, "results_001.json")
        store.save({"b": 2}, "results_002.json")
        store.save({"c": 3}, "other.json")
        files = store.list_results()
        assert len(files) == 2
        assert all("results_" in f.name for f in files)
