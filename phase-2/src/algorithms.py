"""
Phase 2 – Semantic Graph Search Algorithms (Full Implementation)
================================================================
Full implementation of search algorithms for the semantic graph.
"""

import math
from typing import List, Tuple, Optional, Dict, Set, Callable
from dataclasses import dataclass
from collections import deque
import heapq


@dataclass
class SearchResult:
    """Search result for analytical and testing tools."""
    path: List[str]
    total_similarity: float
    path_length: int
    nodes_visited: int
    nodes_explored: int

    def __repr__(self) -> str:
        return (
            f"SearchResult(path_length={self.path_length}, "
            f"similarity={self.total_similarity:.3f}, visited={self.nodes_visited})"
        )


# --- Core Algorithms (Independent Functions) ---

def bfs_impl(
    nodes: Set[str],
    edges: Dict[str, List],
    start: str,
    max_depth: Optional[int] = None,
    min_similarity: float = 0.0,
) -> List[str]:
    """Breadth-First Search on semantic graph with similarity threshold."""
    if start not in nodes:
        return []

    visited: Set[str] = {start}
    order: List[str] = []
    q: deque = deque([(start, 0)])

    while q:
        node, depth = q.popleft()
        order.append(node)

        if max_depth is not None and depth >= max_depth:
            continue

        for edge in edges.get(node, []):
            if edge.similarity < min_similarity:
                continue
            nxt = edge.target
            if nxt in visited:
                continue
            visited.add(nxt)
            q.append((nxt, depth + 1))
    return order


def dfs_impl(
    nodes: Set[str],
    edges: Dict[str, List],
    start: str,
    max_depth: Optional[int] = None,
    min_similarity: float = 0.0,
) -> List[str]:
    """Depth-First Search on semantic graph with similarity threshold."""
    if start not in nodes:
        return []

    visited: Set[str] = set()
    order: List[str] = []
    stack: List[Tuple[str, int]] = [(start, 0)]

    while stack:
        node, depth = stack.pop()
        if node in visited:
            continue

        visited.add(node)
        order.append(node)

        if max_depth is not None and depth >= max_depth:
            continue

        neighbors = [
            edge.target
            for edge in edges.get(node, [])
            if edge.similarity >= min_similarity
        ]

        for nxt in reversed(neighbors):
            if nxt not in visited:
                stack.append((nxt, depth + 1))
    return order


def dijkstra_impl(
    nodes: Set[str],
    edges: Dict[str, List],
    start: str,
    goal: str,
    min_similarity: float = 0.0,
) -> Tuple[Optional[float], List[str]]:
    """Dijkstra's algorithm on semantic graph by converting similarity to cost."""
    if start not in nodes or goal not in nodes:
        return None, []

    dist: Dict[str, float] = {start: 0.0}
    prev: Dict[str, Optional[str]] = {start: None}
    heap: List[Tuple[float, str]] = [(0.0, start)]
    visited_count = 0

    while heap:
        cur_dist, node = heapq.heappop(heap)
        visited_count += 1

        if cur_dist != dist.get(node, float("inf")):
            continue

        if node == goal:
            break

        for edge in edges.get(node, []):
            if edge.similarity < min_similarity:
                continue

            sim = edge.similarity
            if sim <= 0.0:
                continue

            cost = -math.log(sim)
            nxt = edge.target
            new_dist = cur_dist + cost

            if new_dist < dist.get(nxt, float("inf")):
                dist[nxt] = new_dist
                prev[nxt] = node
                heapq.heappush(heap, (new_dist, nxt))

    if goal not in dist:
        return None, []

    path: List[str] = []
    cur: Optional[str] = goal
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return dist[goal], path


def a_star_impl(
    nodes: Set[str],
    edges: Dict[str, List],
    start: str,
    goal: str,
    heuristic: Optional[Callable[[str, str], float]] = None,
    min_similarity: float = 0.0,
) -> Tuple[Optional[float], List[str]]:
    """A* algorithm for guided search in semantic graph."""
    if start not in nodes or goal not in nodes:
        return None, []

    h = heuristic if heuristic is not None else (lambda _n, _g: 0.0)
    g_score: Dict[str, float] = {start: 0.0}
    came_from: Dict[str, Optional[str]] = {start: None}
    open_heap: List[Tuple[float, float, str]] = [(h(start, goal), 0.0, start)]

    while open_heap:
        f_cur, g_cur, node = heapq.heappop(open_heap)

        if g_cur != g_score.get(node, float("inf")):
            continue

        if node == goal:
            break

        for edge in edges.get(node, []):
            if edge.similarity < min_similarity:
                continue

            sim = edge.similarity
            if sim <= 0.0:
                continue

            cost = -math.log(sim)
            nxt = edge.target
            tentative_g = g_cur + cost

            if tentative_g < g_score.get(nxt, float("inf")):
                g_score[nxt] = tentative_g
                came_from[nxt] = node
                f_nxt = tentative_g + h(nxt, goal)
                heapq.heappush(open_heap, (f_nxt, tentative_g, nxt))

    if goal not in g_score:
        return None, []

    path: List[str] = []
    cur: Optional[str] = goal
    while cur is not None:
        path.append(cur)
        cur = came_from.get(cur)
    path.reverse()
    return g_score[goal], path


def floyd_warshall_impl(
    nodes_list: List[str],
    edges: Dict[str, List],
    min_similarity: float = 0.0,
) -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], Optional[str]]]:
    """Floyd–Warshall algorithm for all-pairs shortest paths."""
    dist: Dict[Tuple[str, str], float] = {}
    next_hop: Dict[Tuple[str, str], Optional[str]] = {}

    for u in nodes_list:
        for v in nodes_list:
            if u == v:
                dist[(u, v)] = 0.0
                next_hop[(u, v)] = v
            else:
                dist[(u, v)] = float("inf")
                next_hop[(u, v)] = None

    for u in nodes_list:
        for edge in edges.get(u, []):
            if edge.similarity < min_similarity:
                continue
            sim = edge.similarity
            if sim <= 0.0:
                continue
            cost = -math.log(sim)
            v = edge.target
            if cost < dist[(u, v)]:
                dist[(u, v)] = cost
                next_hop[(u, v)] = v

    for k in nodes_list:
        for i in nodes_list:
            dik = dist[(i, k)]
            if dik == float("inf"):
                continue
            for j in nodes_list:
                alt = dik + dist[(k, j)]
                if alt < dist[(i, j)]:
                    dist[(i, j)] = alt
                    next_hop[(i, j)] = next_hop[(i, k)]

    return dist, next_hop


# --- High-level Wrapper Classes (Legacy Wrappers) ---

class SemanticBFS:
    @staticmethod
    def search(
        graph,
        start: str,
        goal: str,
        min_similarity: float = 0.0,
    ) -> Optional[SearchResult]:
        """BFS search returning SearchResult."""
        if start not in graph.nodes or goal not in graph.nodes:
            return None

        queue = deque([(start, [start], 1.0)])
        visited = {start}
        explored = 0

        while queue:
            curr, path, sim = queue.popleft()
            explored += 1
            if curr == goal:
                return SearchResult(path, sim, len(path), len(visited), explored)

            neighbors = sorted(
                graph.get_neighbors(curr),
                key=lambda e: e.similarity,
                reverse=True,
            )
            for edge in neighbors:
                if edge.similarity >= min_similarity and edge.target not in visited:
                    visited.add(edge.target)
                    queue.append((edge.target, path + [edge.target], sim * edge.similarity))
        return None


class SemanticDijkstra:
    @staticmethod
    def search(
        graph,
        start: str,
        goal: str,
        min_similarity: float = 0.0,
    ) -> Optional[SearchResult]:
        """High-level Dijkstra search."""
        cost, path = dijkstra_impl(graph.nodes, graph.edges, start, goal, min_similarity)
        if cost is None:
            return None
        total_sim = 1.0
        for i in range(len(path) - 1):
            w = graph.get_edge_weight(path[i], path[i + 1])
            if w is None:
                continue
            total_sim *= w
        return SearchResult(path, total_sim, len(path), len(path), 0)


class SemanticAStar:
    @staticmethod
    def search(
        graph,
        start: str,
        goal: str,
        min_similarity: float = 0.0,
        heuristic: Optional[Callable[[str, str], float]] = None,
    ) -> Optional[SearchResult]:
        """High-level A* search."""
        cost, path = a_star_impl(
            graph.nodes,
            graph.edges,
            start,
            goal,
            heuristic,
            min_similarity,
        )
        if cost is None:
            return None
        total_sim = 1.0
        for i in range(len(path) - 1):
            w = graph.get_edge_weight(path[i], path[i + 1])
            if w is None:
                continue
            total_sim *= w
        return SearchResult(path, total_sim, len(path), len(path), 0)


class HybridSearch:
    @staticmethod
    def search(
        graph,
        start: str,
        goal: str,
        bfs_depth_limit: int = 3,
        min_similarity: float = 0.3,
    ) -> Optional[SearchResult]:
        """
        Hybrid algorithm: BFS for short paths, then Dijkstra if needed.
        """
        res = SemanticBFS.search(graph, start, goal, min_similarity)
        if res and res.path_length <= bfs_depth_limit:
            return res
        return SemanticDijkstra.search(graph, start, goal, min_similarity)


