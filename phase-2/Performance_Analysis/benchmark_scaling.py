import os
import sys
import time
import random
from dataclasses import dataclass
from typing import Any, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import arabic_reshaper
from bidi.algorithm import get_display
from matplotlib import font_manager, rcParams

# When executed as a script, ensure the project root (folder that contains phase_2/) is importable
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
    preferred = ["Tahoma", "Arial", "Segoe UI", "Vazirmatn", "IRANSans", "B Nazanin"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in preferred:
        if name in available:
            rcParams["font.family"] = name
            break


@dataclass(frozen=True)
class BenchCase:
    idx: int
    n: int
    k: int
    threshold: float
    seed: int


def _make_nodes(n: int) -> list[str]:
    # Persian-ish tokens to ensure RTL rendering works too
    return [f"گره{i}" for i in range(1, n + 1)]


def _simple_sim(a: str, b: str) -> float:
    common = set(a.lower()) & set(b.lower())
    return len(common) / max(len(set(a.lower())), 1)


def build_graph_topk(nodes: list[str], threshold: float, top_k: int) -> SemanticGraph:
    g = SemanticGraph(similarity_threshold=threshold)
    for x in nodes:
        g.add_node(x)

    for i, a in enumerate(nodes):
        sims: list[tuple[str, float]] = []
        for j, b in enumerate(nodes):
            if i == j:
                continue
            s = _simple_sim(a, b)
            if s >= threshold:
                sims.append((b, s))
        sims.sort(key=lambda t: t[1], reverse=True)
        for b, s in sims[:top_k]:
            g.add_bidirectional_edge(a, b, s)

    return g


def run_floyd(g: SemanticGraph, start: str, goal: str, threshold: float) -> bool:
    dist, next_hop = g.floyd_warshall(min_similarity=threshold)
    path = g.reconstruct_path(start, goal, next_hop)
    return bool(path)


def bench_case(case: BenchCase) -> dict[str, Any]:
    random.seed(case.seed)
    nodes = _make_nodes(case.n)
    start = nodes[0]
    goal = nodes[-1]

    t0 = time.perf_counter()
    g = build_graph_topk(nodes, threshold=case.threshold, top_k=case.k)
    t1 = time.perf_counter()

    build_ms = (t1 - t0) * 1000.0
    stats = g.get_statistics()

    def timed(fn):
        s = time.perf_counter()
        ok = fn()
        e = time.perf_counter()
        return ok, (e - s) * 1000.0

    bfs_ok, bfs_ms = timed(lambda: SemanticBFS.search(g, start, goal, min_similarity=case.threshold) is not None)
    d_ok, d_ms = timed(lambda: SemanticDijkstra.search(g, start, goal, min_similarity=case.threshold) is not None)
    a_ok, a_ms = timed(lambda: SemanticAStar.search(g, start, goal, min_similarity=case.threshold) is not None)
    h_ok, h_ms = timed(lambda: HybridSearch.search(g, start, goal, bfs_depth_limit=3, min_similarity=case.threshold) is not None)

    # Floyd-Warshall is expensive; skip it for larger graphs to keep the benchmark practical.
    if case.n <= 60:
        f_ok, f_ms = timed(lambda: run_floyd(g, start, goal, threshold=case.threshold))
    else:
        f_ok, f_ms = False, float("nan")

    return {
        "idx": case.idx,
        "n": case.n,
        "k": case.k,
        "threshold": case.threshold,
        "seed": case.seed,
        "num_nodes": stats["num_nodes"],
        "num_edges": stats["num_edges"],
        "build_ms": build_ms,
        "bfs_ok": bfs_ok,
        "bfs_ms": bfs_ms,
        "dijkstra_ok": d_ok,
        "dijkstra_ms": d_ms,
        "astar_ok": a_ok,
        "astar_ms": a_ms,
        "hybrid_ok": h_ok,
        "hybrid_ms": h_ms,
        "floyd_ok": f_ok,
        "floyd_ms": f_ms,
    }


def generate_cases(num_cases: int = 100) -> list[BenchCase]:
    # Build ~100 cases by sweeping larger sizes and more densities (Top-K)
    # Larger V makes differences more visible.
    sizes = list(range(10, 101, 5))  # 10..100
    ks = [2, 3, 4, 6, 8, 10]
    threshold = 0.65

    cases: list[BenchCase] = []
    idx = 0
    for n in sizes:
        for k in ks:
            idx += 1
            cases.append(BenchCase(idx=idx, n=n, k=k, threshold=threshold, seed=idx * 1337))
            if len(cases) >= num_cases:
                return cases

    return cases[:num_cases]


def plot_scaling(results: list[dict[str, Any]], out_path: str) -> None:
    _configure_persian_font()

    # Aggregate by n (mean runtime) to reduce noise and make differences visible.
    by_n: dict[int, list[dict[str, Any]]] = {}
    for r in results:
        by_n.setdefault(r["n"], []).append(r)

    xs = sorted(by_n.keys())

    def mean(vals: list[float]) -> float:
        return sum(vals) / len(vals) if vals else 0.0

    def mean_key(n: int, key: str) -> float:
        vals = [r[key] for r in by_n[n] if r[key] == r[key]]  # filter NaN
        return mean(vals)

    def mask_nans(y: list[float]) -> list[float]:
        # matplotlib breaks the line automatically on NaNs
        return [v if v == v else float("nan") for v in y]

    bfs_y = mask_nans([mean_key(n, "bfs_ms") for n in xs])
    dijkstra_y = mask_nans([mean_key(n, "dijkstra_ms") for n in xs])
    astar_y = mask_nans([mean_key(n, "astar_ms") for n in xs])
    hybrid_y = mask_nans([mean_key(n, "hybrid_ms") for n in xs])
    floyd_y = mask_nans([mean_key(n, "floyd_ms") for n in xs])

    # Winner (fastest) among BFS/Dijkstra/A*/Hybrid for each V
    winner_names = []
    for i, n in enumerate(xs):
        candidates = {
            "BFS": bfs_y[i],
            "Dijkstra": dijkstra_y[i],
            "A*": astar_y[i],
            "Hybrid": hybrid_y[i],
        }
        winner_names.append(min(candidates, key=candidates.get))

    # Main plot (symlog) including Floyd
    plt.figure(figsize=(14, 8))
    plt.plot(xs, bfs_y, label="BFS", marker="o", markersize=4)
    plt.plot(xs, dijkstra_y, label="Dijkstra", marker="s", markersize=4)
    plt.plot(xs, astar_y, label="A*", marker="^", markersize=4)
    plt.plot(xs, hybrid_y, label="Hybrid", marker="d", markersize=4)
    # Plot Floyd only for points where it was actually computed (NaNs are skipped)
    plt.plot(xs, floyd_y, label="Floyd–Warshall", marker="x", markersize=4)

    plt.yscale("symlog", linthresh=0.1)
    plt.xlabel(_fa_text("تعداد گره‌ها (V)"))
    plt.ylabel(_fa_text("زمان اجرا (میلی‌ثانیه) - مقیاس لگاریتمی"))
    plt.title(_fa_text("رفتار الگوریتم‌ها هنگام افزایش اندازه ورودی (میانگین‌گیری شده)"))
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()

    # Winner strip at bottom (shows which algorithm is fastest for that V)
    ax = plt.gca()
    y_bottom = min([v for v in bfs_y + dijkstra_y + astar_y + hybrid_y if v == v] + [0.0])
    y_strip = max(y_bottom * 0.2, 0.001)
    for i, n in enumerate(xs):
        ax.text(n, y_strip, winner_names[i], ha="center", va="bottom", fontsize=7, alpha=0.75)

    plt.tight_layout()
    plt.savefig(out_path, dpi=160)

    # Zoom plot (exclude Floyd) for clearer comparison among main search algorithms
    zoom_path = out_path.replace(".png", "_zoom.png")
    plt.figure(figsize=(14, 8))
    plt.plot(xs, bfs_y, label="BFS", marker="o", markersize=4)
    plt.plot(xs, dijkstra_y, label="Dijkstra", marker="s", markersize=4)
    plt.plot(xs, astar_y, label="A*", marker="^", markersize=4)
    plt.plot(xs, hybrid_y, label="Hybrid", marker="d", markersize=4)

    plt.yscale("symlog", linthresh=0.1)
    plt.xlabel(_fa_text("تعداد گره‌ها (V)"))
    plt.ylabel(_fa_text("زمان اجرا (میلی‌ثانیه) - مقیاس لگاریتمی"))
    plt.title(_fa_text("مقایسه الگوریتم‌های جستجو (بدون فلوید–وارشال)"))
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()

    for i, n in enumerate(xs):
        best_y = min(bfs_y[i], dijkstra_y[i], astar_y[i], hybrid_y[i])
        plt.annotate(winner_names[i], (n, best_y), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=7)

    plt.tight_layout()
    plt.savefig(zoom_path, dpi=160)
    print(f"Saved zoomed chart: {zoom_path}")


def write_report(results: list[dict[str, Any]], report_path: str, chart_path: str) -> None:
    # Aggregate by n (mean runtime)
    by_n: dict[int, list[dict[str, Any]]] = {}
    for r in results:
        by_n.setdefault(r["n"], []).append(r)

    def mean(vals: list[float]) -> float:
        return sum(vals) / len(vals) if vals else 0.0

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# گزارش رفتار الگوریتم‌ها هنگام افزایش اندازه ورودی\n\n")
        f.write("این گزارش بر اساس حدود ۱۰۰ تست تولیدشده به‌صورت مصنوعی (با گراف‌های Top-K و آستانه ثابت) تهیه شده است.\n\n")
        f.write(f"فایل نمودار: `{os.path.basename(chart_path)}`\n\n")
        f.write("## تنظیمات بنچمارک\n\n")
        f.write("- شباهت: overlap حروف (همان روش ساده‌ی وب‌دمو)\n")
        f.write("- threshold: 0.65\n")
        f.write("- top_k: در بازه 2 تا 5\n\n")

        f.write("## خلاصه پیچیدگی تئوری\n\n")
        f.write("- BFS/DFS: `O(V + E)`\n")
        f.write("- Dijkstra/A*: `O((V + E) log V)`\n")
        f.write("- Floyd–Warshall: `O(V^3)`\n\n")

        f.write("## میانگین زمان اجرا بر اساس اندازه ورودی\n\n")
        f.write("| V | BFS(ms) | Dijkstra(ms) | A*(ms) | Hybrid(ms) | Floyd(ms) |\n")
        f.write("|---:|---:|---:|---:|---:|---:|\n")

        for n in sorted(by_n.keys()):
            rows = by_n[n]
            f.write(
                f"| {n} | {mean([r['bfs_ms'] for r in rows]):.3f} | {mean([r['dijkstra_ms'] for r in rows]):.3f} | {mean([r['astar_ms'] for r in rows]):.3f} | {mean([r['hybrid_ms'] for r in rows]):.3f} | {mean([r['floyd_ms'] for r in rows]):.3f} |\n"
            )

        f.write("\n## تفسیر\n\n")
        f.write("- با افزایش V (و افزایش ضمنی E به دلیل Top-K)، انتظار داریم BFS رشد نزدیک به خطی داشته باشد.\n")
        f.write("- Dijkstra/A* معمولاً به دلیل استفاده از heap کمی کندتر از BFS هستند و رشد مطابق `log V` مشاهده می‌شود.\n")
        f.write("- Floyd–Warshall با `O(V^3)` بسیار سریع‌تر از سایرین رشد می‌کند و برای ورودی‌های بزرگ مناسب نیست.\n")


def main(output_dir: str | None = None):
    cases = generate_cases(100)
    results = [bench_case(c) for c in cases]

    out_dir = output_dir or PHASE2_DIR
    os.makedirs(out_dir, exist_ok=True)

    chart_path = os.path.join(out_dir, "scaling_chart.png")
    report_path = os.path.join(out_dir, "SCALING_ANALYSIS_REPORT.md")

    plot_scaling(results, chart_path)
    write_report(results, report_path, chart_path)

    print(f"Saved chart: {chart_path}")
    print(f"Saved report: {report_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    main(output_dir=args.output)

