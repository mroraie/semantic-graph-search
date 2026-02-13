"""
Phase 2 – Complexity & Graph Analysis
=====================================
Practical application of complexity analysis and graph structural metrics for Phase 2 algorithms.
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class ComplexityAnalysis:
    """Complexity analysis for a search algorithm."""

    algorithm_name: str
    time_best: str
    time_average: str
    time_worst: str
    space_best: str
    space_average: str
    space_worst: str
    description: str


class AlgorithmComplexityAnalyzer:
    """Algorithm complexity analyzer (Phase 2 version)."""

    @staticmethod
    def get_all_analyses() -> Dict[str, ComplexityAnalysis]:
        """Retrieve analyses for all algorithms."""
        from analysis import AlgorithmComplexityAnalyzer as BaseAnalyzer  # Using base version

        return BaseAnalyzer.get_all_analyses()


class GraphMetrics:
    """
    Computes structural graph metrics to assist in selecting suitable algorithms for Phase 2.
    """

    @staticmethod
    def analyze_graph_structure(graph) -> Dict:
        from analysis import GraphMetrics as BaseMetrics

        return BaseMetrics.analyze_graph_structure(graph)


