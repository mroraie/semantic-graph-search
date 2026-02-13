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
        return {
            "dijkstra": ComplexityAnalysis(
                algorithm_name="Dijkstra",
                time_best="O(V + E log V)",
                time_average="O(E log V)",
                time_worst="O(E log V)",
                space_best="O(V)",
                space_average="O(V)",
                space_worst="O(V)",
                description="Shortest path algorithm for non-negative weights."
            ),
            "a_star": ComplexityAnalysis(
                algorithm_name="A*",
                time_best="O(E)",
                time_average="O(E)",
                time_worst="O(b^d)",
                space_best="O(V)",
                space_average="O(V)",
                space_worst="O(b^d)",
                description="Heuristic-guided search for faster pathfinding."
            ),
            "bfs": ComplexityAnalysis(
                algorithm_name="BFS",
                time_best="O(1)",
                time_average="O(V + E)",
                time_worst="O(V + E)",
                space_best="O(1)",
                space_average="O(V)",
                space_worst="O(V)",
                description="Breadth-first search for unweighted graphs."
            ),
            "floyd_warshall": ComplexityAnalysis(
                algorithm_name="Floyd-Warshall",
                time_best="O(V^3)",
                time_average="O(V^3)",
                time_worst="O(V^3)",
                space_best="O(V^2)",
                space_average="O(V^2)",
                space_worst="O(V^2)",
                description="All-pairs shortest path algorithm."
            )
        }


class GraphMetrics:
    """
    Computes structural graph metrics to assist in selecting suitable algorithms for Phase 2.
    """

    @staticmethod
    def analyze_graph_structure(graph) -> Dict:
        """Analyzes basic graph structure metrics."""
        stats = graph.get_statistics()
        num_nodes = stats.get("num_nodes", 0)
        num_edges = stats.get("num_edges", 0)
        
        density = 0
        if num_nodes > 1:
            density = (2 * num_edges) / (num_nodes * (num_nodes - 1))
        
        # Calculate degrees
        degrees = []
        all_similarities = []
        for node in graph.nodes:
            neighbors = graph.edges.get(node, [])
            degrees.append(len(neighbors))
            for edge in neighbors:
                all_similarities.append(edge.similarity)
        
        avg_degree = sum(degrees) / num_nodes if num_nodes > 0 else 0
        min_degree = min(degrees) if degrees else 0
        avg_sim = sum(all_similarities) / len(all_similarities) if all_similarities else 0
        max_sim = max(all_similarities) if all_similarities else 0

        return {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "density": density,
            "average_degree": avg_degree,
            "min_degree": min_degree,
            "average_similarity": avg_sim,
            "max_similarity": max_sim,
            "graph_type": "dense" if density > 0.4 else "sparse"
        }
