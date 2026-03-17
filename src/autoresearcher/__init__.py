"""Autoresearcher: AI-powered autonomous research and optimization platform."""

__version__ = "0.1.0"

from autoresearcher.experiment import BaseExperiment, ExperimentResult, ExperimentSummary
from autoresearcher.metrics import MetricDefinition, MetricsTracker
from autoresearcher.results import ResultsLog, ResultsStore

__all__ = [
    "BaseExperiment",
    "ExperimentResult",
    "ExperimentSummary",
    "MetricDefinition",
    "MetricsTracker",
    "ResultsLog",
    "ResultsStore",
]
