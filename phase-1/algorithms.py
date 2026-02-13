from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Set, Callable


@dataclass
class SearchResult:
    path: List[str]
    total_similarity: float
    path_length: int
    nodes_visited: int
    nodes_explored: int



def bfs_impl(
    nodes: Set[str],
    edges: Dict[str, List[str]],
    start: str,
    max_depth: Optional[int] = None,
    min_similarity: float = 0.0,
) -> List[str]:
    raise NotImplementedError("Phase 1: الگوریتم‌ها به‌صورت مفهومی تعریف شده‌اند.")


def dfs_impl(
    nodes: Set[str],
    edges: Dict[str, List[str]],
    start: str,
    max_depth: Optional[int] = None,
    min_similarity: float = 0.0,
) -> List[str]:
    raise NotImplementedError("Phase 1: الگوریتم‌ها به‌صورت مفهومی تعریف شده‌اند.")


def dijkstra_impl(
    nodes: Set[str],
    edges: Dict[str, List[str]],
    start: str,
    goal: str,
    min_similarity: float = 0.0,
) -> Tuple[Optional[float], List[str]]:
    raise NotImplementedError("Phase 1: الگوریتم‌ها به‌صورت مفهومی تعریف شده‌اند.")


def a_star_impl(
    nodes: Set[str],
    edges: Dict[str, List[str]],
    start: str,
    goal: str,
    heuristic: Optional[Callable[[str, str], float]] = None,
    min_similarity: float = 0.0,
) -> Tuple[Optional[float], List[str]]:
    raise NotImplementedError("Phase 1: الگوریتم‌ها به‌صورت مفهومی تعریف شده‌اند.")


def floyd_warshall_impl(
    nodes_list: List[str],
    edges: Dict[str, List[str]],
    min_similarity: float = 0.0,
) -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], Optional[str]]]:
    raise NotImplementedError("Phase 1: الگوریتم‌ها به‌صورت مفهومی تعریف شده‌اند.")

