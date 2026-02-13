import os
import sys
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import arabic_reshaper
from bidi.algorithm import get_display
from matplotlib import font_manager, rcParams

# Ensure imports work regardless of where the script is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(PHASE2_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from phase_2.src.semantic_graph import SemanticGraph
from phase_2.src.algorithms import (
    SemanticBFS,
    SemanticDijkstra,
    SemanticAStar,
    HybridSearch,
)


def _fa_text(s: str) -> str:
    reshaped = arabic_reshaper.reshape(s)
    return get_display(reshaped)


def _configure_persian_font() -> None:
    preferred = ["Tahoma", "Arial", "Segoe UI", "Vazirmatn", "IRANSans", "B Nazanin"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in preferred:
        if name in available:
            rcParams["font.family"] = name
            break


@dataclass(frozen=True)
class Scenario:
    key: str
    name: str
    difficulty: str
    concepts: list[str]
    start: str
    goal: str


SCENARIOS: list[Scenario] = [
    Scenario("fruits_easy", "میوه‌ها (ساده)", "easy", ["سیب", "پرتقال", "موز", "انبه", "انگور", "میوه"], "سیب", "میوه"),
    Scenario("transport_easy", "حمل‌ونقل (ساده)", "easy", ["ماشین", "دوچرخه", "اتوبوس", "قطار", "وسیله نقلیه"], "ماشین", "وسیله نقلیه"),
    Scenario("colors_easy", "رنگ‌ها (ساده)", "easy", ["قرمز", "آبی", "سبز", "زرد", "رنگ", "طیف"], "قرمز", "رنگ"),
    Scenario("family_easy", "خانواده (ساده)", "easy", ["پدر", "مادر", "فرزند", "برادر", "خواهر", "خانواده"], "فرزند", "خانواده"),

    Scenario("ai_medium", "هوش مصنوعی (متوسط)", "medium", ["هوش مصنوعی", "یادگیری ماشین", "یادگیری عمیق", "شبکه های عصبی", "داده", "الگوریتم", "پردازنده گرافیکی", "آموزش"], "هوش مصنوعی", "پردازنده گرافیکی"),
    Scenario("web_medium", "توسعه وب (متوسط)", "medium", ["فرانت اند", "بک اند", "پایگاه داده", "رابط برنامه نویسی", "ریکت", "نود جی اس", "مرورگر", "سرور"], "فرانت اند", "سرور"),
    Scenario("eco_medium", "محیط زیست (متوسط)", "medium", ["درخت", "جنگل", "اکسیژن", "فتوسنتز", "خورشید", "حیات", "اتمسفر", "گرمایش جهانی"], "خورشید", "گرمایش جهانی"),
    Scenario("disconnected_edge", "گره ایزوله (Edge Case)", "medium", ["تهران", "اصفهان", "شیراز", "تبریز", "کهکشان آندرومدا"], "تهران", "کهکشان آندرومدا"),

    Scenario("cross_domain_hard", "ترکیبی پیچیده (سخت)", "hard", ["بازی", "گرافیک", "موتور فیزیک", "هوش مصنوعی", "شبکه های عصبی", "ریاضیات", "منطق", "سخت افزار", "سیلیکون", "معدن"], "بازی", "معدن"),
    Scenario("dense_worst_case", "گراف متراکم (Worst-Case)", "hard", [f"کلمه{i}" for i in range(1, 41)], "کلمه1", "کلمه40"),
]


def build_graph_simple(concepts: list[str], threshold: float, top_k: int) -> SemanticGraph:
    graph = SemanticGraph(similarity_threshold=threshold)
    for c in concepts:
        graph.add_node(c)

    def sim(a: str, b: str) -> float:
        common = set(a.lower()) & set(b.lower())
        return len(common) / max(len(set(a.lower())), 1)

    for i, concept in enumerate(concepts):
        sims: list[tuple[str, float]] = []
        for j, other in enumerate(concepts):
            if i == j:
                continue
            s = sim(concept, other)
            if s >= threshold:
                sims.append((other, s))
        sims.sort(key=lambda x: x[1], reverse=True)
        for target, s in sims[:top_k]:
            graph.add_bidirectional_edge(concept, target, s)

    return graph


def run_bfs_path(graph: SemanticGraph, start: str, goal: str, threshold: float) -> Optional[list[str]]:
    res = SemanticBFS.search(graph, start, goal, min_similarity=threshold)
    return None if res is None else res.path


def run_dijkstra(graph: SemanticGraph, start: str, goal: str, threshold: float) -> Dict[str, Any]:
    res = SemanticDijkstra.search(graph, start, goal, min_similarity=threshold)
    if res is None:
        return {"success": False}
    return {
        "success": True,
        "path": res.path,
        "path_length": res.path_length,
        "total_similarity": res.total_similarity,
    }


def run_a_star(graph: SemanticGraph, start: str, goal: str, threshold: float) -> Dict[str, Any]:
    res = SemanticAStar.search(graph, start, goal, min_similarity=threshold)
    if res is None:
        return {"success": False}
    return {
        "success": True,
        "path": res.path,
        "path_length": res.path_length,
        "total_similarity": res.total_similarity,
    }


def run_hybrid(graph: SemanticGraph, start: str, goal: str, threshold: float) -> Dict[str, Any]:
    res = HybridSearch.search(graph, start, goal, bfs_depth_limit=3, min_similarity=threshold)
    if res is None:
        return {"success": False}
    return {
        "success": True,
        "path": res.path,
        "path_length": res.path_length,
        "total_similarity": res.total_similarity,
    }


def run_floyd(graph: SemanticGraph, start: str, goal: str, threshold: float) -> Dict[str, Any]:
    dist, next_hop = graph.floyd_warshall(min_similarity=threshold)
    path = graph.reconstruct_path(start, goal, next_hop)
    if not path:
        return {"success": False}

    total_sim = 1.0
    for i in range(len(path) - 1):
        w = graph.get_edge_weight(path[i], path[i + 1])
        if w is None:
            continue
        total_sim *= w

    return {
        "success": True,
        "path": path,
        "path_length": len(path),
        "total_similarity": total_sim,
    }


ALGORITHMS = [
    ("BFS", "bfs", True),
    ("Dijkstra", "dijkstra", True),
    ("A*", "a_star", True),
    ("Floyd–Warshall", "floyd", True),
    ("Hybrid", "hybrid", True),
]


def main(output_dir: str | None = None):
    _configure_persian_font()

    threshold = 0.65
    top_k = 3

    out_dir = output_dir or PHASE2_DIR
    os.makedirs(out_dir, exist_ok=True)

    # results[scenario_key][alg_key] = {...}
    results: dict[str, dict[str, dict[str, Any]]] = {}

    for sc in SCENARIOS:
        graph = build_graph_simple(sc.concepts, threshold=threshold, top_k=top_k)
        results[sc.key] = {}

        for (label, alg_key, _enabled) in ALGORITHMS:
            t0 = time.perf_counter()

            if alg_key == "bfs":
                path = run_bfs_path(graph, sc.start, sc.goal, threshold)
                ok = path is not None
                out = {
                    "success": ok,
                    "path_length": len(path) if ok else None,
                    "total_similarity": None,
                }
            elif alg_key == "dijkstra":
                out = run_dijkstra(graph, sc.start, sc.goal, threshold)
            elif alg_key == "a_star":
                out = run_a_star(graph, sc.start, sc.goal, threshold)
            elif alg_key == "floyd":
                out = run_floyd(graph, sc.start, sc.goal, threshold)
            elif alg_key == "hybrid":
                out = run_hybrid(graph, sc.start, sc.goal, threshold)
            else:
                out = {"success": False}

            t1 = time.perf_counter()
            out["runtime_ms"] = (t1 - t0) * 1000.0
            results[sc.key][alg_key] = out

    # Compute winner per scenario
    # Winner criteria:
    # 1) Prefer success
    # 2) Among successes: maximize total_similarity if available, else minimize path_length
    # 3) Tie-breaker: minimize runtime
    winners: dict[str, str] = {}
    for sc in SCENARIOS:
        candidates = []
        for (_label, alg_key, _enabled) in ALGORITHMS:
            out = results[sc.key][alg_key]
            if not out.get("success"):
                continue
            sim = out.get("total_similarity")
            path_len = out.get("path_length")
            runtime = out.get("runtime_ms", float("inf"))
            candidates.append((sim if sim is not None else -1.0, -(path_len or 10**9), -runtime, alg_key))

        if not candidates:
            winners[sc.key] = "none"
        else:
            candidates.sort(reverse=True)
            winners[sc.key] = candidates[0][3]

    # Build chart: runtime by algorithm per scenario (grouped bars)
    scenario_labels = [_fa_text(sc.name) for sc in SCENARIOS]
    alg_labels = [a[0] for a in ALGORITHMS]
    alg_keys = [a[1] for a in ALGORITHMS]

    data = []
    for alg_key in alg_keys:
        data.append([results[sc.key][alg_key].get("runtime_ms", 0.0) for sc in SCENARIOS])

    x = list(range(len(SCENARIOS)))
    width = 0.14

    plt.figure(figsize=(16, 7))

    for i, alg_key in enumerate(alg_keys):
        offsets = [xi + (i - (len(alg_keys) - 1) / 2) * width for xi in x]
        plt.bar(offsets, data[i], width=width, label=alg_labels[i])

    plt.xticks(x, scenario_labels, rotation=35, ha="right")
    plt.ylabel(_fa_text("زمان اجرا (میلی‌ثانیه)"))
    plt.title(_fa_text("مقایسه زمان اجرای الگوریتم‌ها روی ۱۰ سناریو"))
    plt.yscale("symlog", linthresh=0.05)
    plt.legend()

    out_chart = os.path.join(out_dir, "algorithm_comparison_chart.png")
    plt.tight_layout()
    plt.savefig(out_chart, dpi=160)

    # Zoomed chart (exclude Floyd–Warshall) for better separation
    plt.figure(figsize=(16, 7))
    zoom_alg_keys = [k for k in alg_keys if k != "floyd"]
    zoom_alg_labels = [lbl for (lbl, k, _en) in ALGORITHMS if k != "floyd"]
    zoom_data = []
    for alg_key in zoom_alg_keys:
        zoom_data.append([results[sc.key][alg_key].get("runtime_ms", 0.0) for sc in SCENARIOS])

    for i, alg_key in enumerate(zoom_alg_keys):
        offsets = [xi + (i - (len(zoom_alg_keys) - 1) / 2) * width for xi in x]
        plt.bar(offsets, zoom_data[i], width=width, label=zoom_alg_labels[i])

    plt.xticks(x, scenario_labels, rotation=35, ha="right")
    plt.ylabel(_fa_text("زمان اجرا (میلی‌ثانیه)"))
    plt.title(_fa_text("مقایسه زمان اجرا (بدون فلوید–وارشال)"))
    plt.yscale("symlog", linthresh=0.05)
    plt.legend()

    out_chart_zoom = os.path.join(out_dir, "algorithm_comparison_chart_zoom.png")
    plt.tight_layout()
    plt.savefig(out_chart_zoom, dpi=160)

    # Write report
    report_path = os.path.join(out_dir, "ALGORITHM_COMPARISON_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# گزارش مقایسه الگوریتم‌ها\n\n")
        f.write(f"پارامترها: threshold={threshold}, top_k={top_k} (شباهت ساده: overlap حروف)\n\n")
        f.write("## برنده هر سناریو\n\n")
        for sc in SCENARIOS:
            w = winners[sc.key]
            w_label = w if w != "none" else "هیچ‌کدام"
            f.write(f"- **{sc.name}**: {w_label}\n")

        f.write("\n## جدول نتایج (زمان اجرا)\n\n")
        f.write("| سناریو | " + " | ".join([a[0] for a in ALGORITHMS]) + " |\n")
        f.write("|---|" + "---|" * len(ALGORITHMS) + "\n")
        for sc in SCENARIOS:
            row = [sc.name]
            for alg_key in alg_keys:
                out = results[sc.key][alg_key]
                if not out.get("success"):
                    row.append("FAIL")
                else:
                    row.append(f"{out.get('runtime_ms', 0.0):.2f}ms")
            f.write("| " + " | ".join(row) + " |\n")

        f.write("\n## معیار موفقیت\n\n")
        f.write("- ابتدا الگوریتم‌هایی که مسیر پیدا می‌کنند (Success) برتری دارند.\n")
        f.write("- بین موارد موفق: اگر total_similarity قابل محاسبه باشد، بیشترین total_similarity بهتر است؛ در غیر این صورت مسیر کوتاه‌تر بهتر است.\n")
        f.write("- در تساوی: زمان اجرا کمتر برنده است.\n")

        f.write("\n## یادداشت تئوری (پیچیدگی)\n\n")
        f.write("- BFS: O(V + E)\n")
        f.write("- Dijkstra / A*: O((V + E) log V)\n")
        f.write("- Floyd–Warshall: O(V^3)\n")

    print(f"Saved chart: {out_chart}")
    print(f"Saved report: {report_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    main(output_dir=args.output)

