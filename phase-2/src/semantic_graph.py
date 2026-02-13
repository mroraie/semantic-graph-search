"""
Phase 2 – Semantic Graph Data Structure (Full Implementation)
=============================================================
Full implementation of the semantic graph data structure for experiments and analysis.
"""

from typing import Dict, List, Tuple, Optional, Set, Callable
from dataclasses import dataclass
import json

from phase_2.src.algorithms import (
    bfs_impl,
    dfs_impl,
    dijkstra_impl,
    a_star_impl,
    floyd_warshall_impl,
)


@dataclass
class Edge:
    """Graph edge with semantic weight."""
    target: str
    similarity: float  # Semantic similarity weight (0 to 1)

    def __repr__(self) -> str:
        return f"Edge({self.target}, sim={self.similarity:.3f})"


class SemanticGraph:
    """
    Semantic graph for storing and managing conceptual relationships between words/phrases.

    Attributes:
        nodes: Set of nodes.
        edges: Dictionary mapping node -> list of edges.
        similarity_threshold: Minimum similarity required to create an edge.
    """

    def __init__(self, similarity_threshold: float = 0.3) -> None:
        """
        Args:
            similarity_threshold: Minimum similarity to create an edge (default: 0.3).
        """
        self.nodes: Set[str] = set()
        self.edges: Dict[str, List[Edge]] = {}
        self.similarity_threshold = similarity_threshold

    # --- Graph Structure ---

    def add_node(self, node: str) -> None:
        """Adds a node to the graph."""
        if node not in self.nodes:
            self.nodes.add(node)
            self.edges[node] = []

    def add_edge(self, source: str, target: str, similarity: float) -> None:
        """
        Adds an edge between two nodes.

        Args:
            source: Source node.
            target: Target node.
            similarity: Semantic similarity (0 to 1).
        """
        if similarity < self.similarity_threshold:
            return  # Edge not created if similarity is too low

        self.add_node(source)
        self.add_node(target)

        # If edge already exists, update weight with maximum similarity
        for edge in self.edges[source]:
            if edge.target == target:
                edge.similarity = max(edge.similarity, similarity)
                return

        # Add new edge
        self.edges[source].append(Edge(target, similarity))

    def add_bidirectional_edge(self, node1: str, node2: str, similarity: float) -> None:
        """Adds a bidirectional edge."""
        self.add_edge(node1, node2, similarity)
        self.add_edge(node2, node1, similarity)

    def get_neighbors(self, node: str) -> List[Edge]:
        """Returns neighbors of a node."""
        return self.edges.get(node, [])

    def get_edge_weight(self, source: str, target: str) -> Optional[float]:
        """Returns edge weight between two nodes."""
        for edge in self.get_neighbors(source):
            if edge.target == target:
                return edge.similarity
        return None

    def has_edge(self, source: str, target: str) -> bool:
        """Checks if an edge exists."""
        return self.get_edge_weight(source, target) is not None

    def get_all_nodes(self) -> List[str]:
        """Returns list of all nodes."""
        return list(self.nodes)

    def get_all_edges(self) -> List[Tuple[str, str, float]]:
        """Returns list of all edges."""
        all_edges: List[Tuple[str, str, float]] = []
        for source, edges_list in self.edges.items():
            for edge in edges_list:
                all_edges.append((source, edge.target, edge.similarity))
        return all_edges

    def get_statistics(self) -> Dict:
        """Returns graph statistics."""
        num_edges = sum(len(edges) for edges in self.edges.values())
        avg_degree = num_edges / len(self.nodes) if self.nodes else 0

        return {
            "num_nodes": len(self.nodes),
            "num_edges": num_edges,
            "average_degree": avg_degree,
            "similarity_threshold": self.similarity_threshold,
        }

    # --- Save and Load ---

    def to_dict(self) -> Dict:
        """Converts graph to dictionary for storage."""
        return {
            "nodes": list(self.nodes),
            "edges": [
                {"source": source, "target": edge.target, "similarity": edge.similarity}
                for source, edges_list in self.edges.items()
                for edge in edges_list
            ],
            "similarity_threshold": self.similarity_threshold,
        }

    def save_to_file(self, filepath: str) -> None:
        """Saves graph to JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> "SemanticGraph":
        """Loads graph from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        graph = cls(similarity_threshold=data.get("similarity_threshold", 0.3))
        for edge_data in data["edges"]:
            graph.add_edge(
                edge_data["source"],
                edge_data["target"],
                edge_data["similarity"],
            )
        return graph

    # --- High-level Algorithm Interfaces ---

    def bfs(
        self,
        start: str,
        max_depth: Optional[int] = None,
        min_similarity: Optional[float] = None,
    ) -> List[str]:
        """Executes BFS on semantic graph starting from a node."""
        threshold = self.similarity_threshold if min_similarity is None else min_similarity
        return bfs_impl(
            self.nodes,
            self.edges,
            start,
            max_depth=max_depth,
            min_similarity=threshold,
        )

    def dfs(
        self,
        start: str,
        max_depth: Optional[int] = None,
        min_similarity: Optional[float] = None,
    ) -> List[str]:
        """Executes DFS on semantic graph starting from a node."""
        threshold = self.similarity_threshold if min_similarity is None else min_similarity
        return dfs_impl(
            self.nodes,
            self.edges,
            start,
            max_depth=max_depth,
            min_similarity=threshold,
        )

    def dijkstra(
        self,
        start: str,
        goal: str,
        min_similarity: Optional[float] = None,
    ) -> Tuple[Optional[float], List[str]]:
        """Finds optimal path between two nodes using Dijkstra."""
        threshold = self.similarity_threshold if min_similarity is None else min_similarity
        return dijkstra_impl(self.nodes, self.edges, start, goal, min_similarity=threshold)

    def a_star(
        self,
        start: str,
        goal: str,
        heuristic: Optional[Callable[[str, str], float]] = None,
        min_similarity: Optional[float] = None,
    ) -> Tuple[Optional[float], List[str]]:
        """Finds optimal path between two nodes using A*."""
        threshold = self.similarity_threshold if min_similarity is None else min_similarity
        return a_star_impl(
            self.nodes,
            self.edges,
            start,
            goal,
            heuristic=heuristic,
            min_similarity=threshold,
        )

    def floyd_warshall(
        self,
        min_similarity: Optional[float] = None,
    ) -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], Optional[str]]]:
        """Calculates shortest paths between all node pairs using Floyd-Warshall."""
        threshold = self.similarity_threshold if min_similarity is None else min_similarity
        return floyd_warshall_impl(list(self.nodes), self.edges, min_similarity=threshold)

    def reconstruct_path(
        self,
        start: str,
        goal: str,
        next_hop: Dict[Tuple[str, str], Optional[str]],
    ) -> List[str]:
        """Reconstructs path from start to goal using Floyd-Warshall output."""
        if (start, goal) not in next_hop or next_hop[(start, goal)] is None:
            return []

        path = [start]
        cur = start
        while cur != goal:
            cur = next_hop.get((cur, goal))
            if cur is None:
                return []
            path.append(cur)

        return path

    def build_from_similarities(
        self,
        concepts: List[str],
        similarity_matrix: List[List[float]],
        threshold: Optional[float] = None,
    ) -> None:
        """Builds graph from a pre-computed similarity matrix."""
        t = threshold if threshold is not None else self.similarity_threshold
        n = len(concepts)
        for i in range(n):
            for j in range(i + 1, n):
                sim = similarity_matrix[i][j]
                if sim >= t:
                    self.add_bidirectional_edge(concepts[i], concepts[j], sim)

    def __repr__(self) -> str:
        stats = self.get_statistics()
        return f"SemanticGraph(nodes={stats['num_nodes']}, edges={stats['num_edges']})"


