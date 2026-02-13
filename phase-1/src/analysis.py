from typing import Dict
from dataclasses import dataclass


@dataclass
class ComplexityAnalysis:
    algorithm_name: str
    time_best: str
    time_average: str
    time_worst: str
    space_best: str
    space_average: str
    space_worst: str
    description: str


class AlgorithmComplexityAnalyzer:
    @staticmethod
    def get_all_analyses() -> Dict[str, ComplexityAnalysis]:
        return {
            "semantic_bfs": ComplexityAnalysis(
                algorithm_name="Semantic BFS",
                time_best="O(1)",
                time_average="O(V + E)",
                time_worst="O(V + E)",
                space_best="O(1)",
                space_average="O(V)",
                space_worst="O(V)",
                description="Semantic BFS: Best O(1), Avg/Worst O(V + E), Space O(V)",
            ),
            "semantic_dfs": ComplexityAnalysis(
                algorithm_name="Semantic DFS",
                time_best="O(1)",
                time_average="O(V + E)",
                time_worst="O(V + E)",
                space_best="O(1)",
                space_average="O(V)",
                space_worst="O(V)",
                description="Semantic DFS: Time O(V + E), Space O(V)",
            ),
            "dijkstra": ComplexityAnalysis(
                algorithm_name="Dijkstra",
                time_best="O(V log V)",
                time_average="O((V + E) log V)",
                time_worst="O((V + E) log V)",
                space_best="O(V)",
                space_average="O(V)",
                space_worst="O(V)",
                description="Dijkstra: Time O((V + E) log V), Space O(V)",
            ),
            "astar": ComplexityAnalysis(
                algorithm_name="A*",
                time_best="O(V log V)",
                time_average="O((V + E) log V)",
                time_worst="O((V + E) log V)",
                space_best="O(V)",
                space_average="O(V)",
                space_worst="O(V)",
                description="A*: Time O((V + E) log V), Space O(V)",
            ),
            "floyd_warshall": ComplexityAnalysis(
                algorithm_name="Floyd–Warshall",
                time_best="O(V^3)",
                time_average="O(V^3)",
                time_worst="O(V^3)",
                space_best="O(V^2)",
                space_average="O(V^2)",
                space_worst="O(V^2)",
                description="Floyd–Warshall: Time O(V^3), Space O(V^2)",
            ),
        }

    @staticmethod
    def compare_algorithms() -> str:
        return (
            "مقایسه الگوریتم‌ها:\n"
            "- BFS/DFS: O(V+E)\n"
            "- Dijkstra/A*: O((V+E)logV)\n"
            "- Floyd–Warshall: O(V^3)\n"
        )

