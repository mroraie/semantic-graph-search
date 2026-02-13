import os
import sys
import time
import random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display
from matplotlib import font_manager, rcParams

# Path setup
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

def build_graph(n: int, k: int) -> SemanticGraph:
    nodes = [f"node{i}" for i in range(n)]
    g = SemanticGraph(similarity_threshold=0.5)
    for node in nodes: g.add_node(node)
    for i, a in enumerate(nodes):
        sims = []
        for j, b in enumerate(nodes):
            if i == j: continue
            s = _simple_sim(a, b)
            if s >= 0.5: sims.append((b, s))
        sims.sort(key=lambda t: t[1], reverse=True)
        for b, s in sims[:k]:
            g.add_bidirectional_edge(a, b, s)
    return g

def main(output_dir: str | None = None):
    _configure_persian_font()

    out_dir = output_dir or PHASE2_DIR
    os.makedirs(out_dir, exist_ok=True)

    sizes = list(range(10, 101, 10))
    results = {"BFS": [], "Dijkstra": [], "A*": [], "Hybrid": []}
    
    print("Generating Time Growth Data...")
    for n in sizes:
        g = build_graph(n, k=4)
        start, goal = "node0", f"node{n-1}"
        
        # Measure BFS
        t0 = time.perf_counter()
        SemanticBFS.search(g, start, goal, min_similarity=0.5)
        results["BFS"].append((time.perf_counter() - t0) * 1000)
        
        # Measure Dijkstra
        t0 = time.perf_counter()
        SemanticDijkstra.search(g, start, goal, min_similarity=0.5)
        results["Dijkstra"].append((time.perf_counter() - t0) * 1000)

        # Measure A*
        t0 = time.perf_counter()
        SemanticAStar.search(g, start, goal, min_similarity=0.5)
        results["A*"].append((time.perf_counter() - t0) * 1000)

        # Measure Hybrid
        t0 = time.perf_counter()
        HybridSearch.search(g, start, goal, min_similarity=0.5)
        results["Hybrid"].append((time.perf_counter() - t0) * 1000)

    plt.figure(figsize=(12, 7))
    for alg, times in results.items():
        plt.plot(sizes, times, label=alg, marker='o')

    plt.xlabel(_fa_text("اندازه ورودی (تعداد گره‌ها)"))
    plt.ylabel(_fa_text("زمان اجرا (میلی‌ثانیه)"))
    plt.title(_fa_text("نمودار رشد زمانی الگوریتم‌ها"))
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    out_path = os.path.join(out_dir, "time_growth_chart.png")
    plt.savefig(out_path, dpi=160)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    main(output_dir=args.output)

