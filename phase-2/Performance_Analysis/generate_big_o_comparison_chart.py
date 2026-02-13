import os
import sys
import time
import math
from dataclasses import dataclass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import arabic_reshaper
from bidi.algorithm import get_display
from matplotlib import font_manager, rcParams

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(PHASE2_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from phase_2.src.semantic_graph import SemanticGraph
from phase_2.src.algorithms import SemanticBFS, SemanticDijkstra, SemanticAStar, HybridSearch


def _fa_text(s: str) -> str:
    return get_display(arabic_reshaper.reshape(s))


def _configure_persian_font() -> None:
    preferred = ["Tahoma", "Arial", "Segoe UI", "Vazirmatn", "IRANSans"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in preferred:
        if name in available:
            rcParams["font.family"] = name
            break


def _simple_sim(a: str, b: str) -> float:
    common = set(a.lower()) & set(b.lower())
    return len(common) / max(len(set(a.lower())), 1)


def build_graph(n: int, k: int, threshold: float) -> tuple[SemanticGraph, int, int]:
    nodes = [f"node{i}" for i in range(n)]
    g = SemanticGraph(similarity_threshold=threshold)
    for node in nodes:
        g.add_node(node)

    for i, a in enumerate(nodes):
        sims: list[tuple[str, float]] = []
        for j, b in enumerate(nodes):
            if i == j:
                continue
            s = _simple_sim(a, b)
            if s >= threshold:
                sims.append((b, s))
        sims.sort(key=lambda t: t[1], reverse=True)
        for b, s in sims[:k]:
            g.add_bidirectional_edge(a, b, s)

    stats = g.get_statistics()
    return g, stats["num_nodes"], stats["num_edges"]


def _measure_ms(fn) -> float:
    t0 = time.perf_counter()
    fn()
    t1 = time.perf_counter()
    return (t1 - t0) * 1000.0


def _normalize_curve(curve: list[float], target: list[float]) -> list[float]:
    # Scale curve to match target in least-squares sense (simple ratio using sums)
    num = sum(t * c for t, c in zip(target, curve))
    den = sum(c * c for c in curve)
    if den == 0:
        return curve
    a = num / den
    return [a * c for c in curve]


def main(output_dir: str | None = None):
    _configure_persian_font()

    threshold = 0.5
    k = 4
    sizes = list(range(10, 101, 10))

    # Empirical
    bfs_ms: list[float] = []
    dijkstra_ms: list[float] = []
    astar_ms: list[float] = []
    hybrid_ms: list[float] = []

    V: list[int] = []
    E: list[int] = []

    for n in sizes:
        g, v, e = build_graph(n, k=k, threshold=threshold)
        start, goal = "node0", f"node{n-1}"

        V.append(v)
        E.append(e)

        bfs_ms.append(_measure_ms(lambda: SemanticBFS.search(g, start, goal, min_similarity=threshold)))
        dijkstra_ms.append(_measure_ms(lambda: SemanticDijkstra.search(g, start, goal, min_similarity=threshold)))
        astar_ms.append(_measure_ms(lambda: SemanticAStar.search(g, start, goal, min_similarity=threshold)))
        hybrid_ms.append(_measure_ms(lambda: HybridSearch.search(g, start, goal, bfs_depth_limit=3, min_similarity=threshold)))

    # Theoretical proxies
    ve = [v + e for v, e in zip(V, E)]
    ve_logv = [(v + e) * math.log(max(v, 2)) for v, e in zip(V, E)]
    v3 = [v ** 3 for v in V]

    # Normalize theoretical curves to empirical (pick Dijkstra as reference)
    ve_n = _normalize_curve(ve, dijkstra_ms)
    ve_logv_n = _normalize_curve(ve_logv, dijkstra_ms)
    v3_n = _normalize_curve(v3, dijkstra_ms)

    plt.figure(figsize=(13, 7))

    # Empirical
    plt.plot(V, bfs_ms, marker='o', label="BFS (واقعی)")
    plt.plot(V, dijkstra_ms, marker='s', label="Dijkstra (واقعی)")
    plt.plot(V, astar_ms, marker='^', label="A* (واقعی)")
    plt.plot(V, hybrid_ms, marker='d', label="Hybrid (واقعی)")

    # Theoretical overlays
    plt.plot(V, ve_n, linestyle='--', label="O(V+E) (نرمال‌شده)")
    plt.plot(V, ve_logv_n, linestyle='--', label="O((V+E)logV) (نرمال‌شده)")
    plt.plot(V, v3_n, linestyle='--', label="O(V^3) (نرمال‌شده)")

    plt.yscale('symlog', linthresh=0.1)
    plt.xlabel(_fa_text("تعداد گره‌ها (V)"))
    plt.ylabel(_fa_text("زمان اجرا (میلی‌ثانیه) - مقیاس لگاریتمی"))
    plt.title(_fa_text("مقایسه زمان اجرای واقعی با منحنی‌های Big-O"))
    plt.grid(True, which='both', alpha=0.3)
    plt.legend()

    out_dir = output_dir or PHASE2_DIR
    os.makedirs(out_dir, exist_ok=True)

    out_path = os.path.join(out_dir, "big_o_comparison_chart.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)

    print(f"Saved: {out_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    main(output_dir=args.output)

