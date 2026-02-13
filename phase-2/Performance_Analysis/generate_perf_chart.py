import os
import sys
import time
from dataclasses import dataclass

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


@dataclass(frozen=True)
class Scenario:
    key: str
    name: str
    difficulty: str  # easy|medium|hard
    concepts: list[str]
    start: str
    goal: str


SCENARIOS: list[Scenario] = [
    # 4 Easy
    Scenario(
        key="fruits_easy",
        name="میوه‌ها (ساده)",
        difficulty="easy",
        concepts=["سیب", "پرتقال", "موز", "انبه", "انگور", "میوه"],
        start="سیب",
        goal="میوه",
    ),
    Scenario(
        key="transport_easy",
        name="حمل‌ونقل (ساده)",
        difficulty="easy",
        concepts=["ماشین", "دوچرخه", "اتوبوس", "قطار", "وسیله نقلیه"],
        start="ماشین",
        goal="وسیله نقلیه",
    ),
    Scenario(
        key="colors_easy",
        name="رنگ‌ها (ساده)",
        difficulty="easy",
        concepts=["قرمز", "آبی", "سبز", "زرد", "رنگ", "طیف"],
        start="قرمز",
        goal="رنگ",
    ),
    Scenario(
        key="family_easy",
        name="خانواده (ساده)",
        difficulty="easy",
        concepts=["پدر", "مادر", "فرزند", "برادر", "خواهر", "خانواده"],
        start="فرزند",
        goal="خانواده",
    ),
    # 4 Medium
    Scenario(
        key="ai_medium",
        name="هوش مصنوعی (متوسط)",
        difficulty="medium",
        concepts=[
            "هوش مصنوعی",
            "یادگیری ماشین",
            "یادگیری عمیق",
            "شبکه های عصبی",
            "داده",
            "الگوریتم",
            "پردازنده گرافیکی",
            "آموزش",
        ],
        start="هوش مصنوعی",
        goal="پردازنده گرافیکی",
    ),
    Scenario(
        key="web_medium",
        name="توسعه وب (متوسط)",
        difficulty="medium",
        concepts=[
            "فرانت اند",
            "بک اند",
            "پایگاه داده",
            "رابط برنامه نویسی",
            "ریکت",
            "نود جی اس",
            "مرورگر",
            "سرور",
        ],
        start="فرانت اند",
        goal="سرور",
    ),
    Scenario(
        key="eco_medium",
        name="محیط زیست (متوسط)",
        difficulty="medium",
        concepts=[
            "درخت",
            "جنگل",
            "اکسیژن",
            "فتوسنتز",
            "خورشید",
            "حیات",
            "اتمسفر",
            "گرمایش جهانی",
        ],
        start="خورشید",
        goal="گرمایش جهانی",
    ),
    Scenario(
        key="disconnected_edge",
        name="گره ایزوله (Edge Case)",
        difficulty="medium",
        concepts=["تهران", "اصفهان", "شیراز", "تبریز", "کهکشان آندرومدا"],
        start="تهران",
        goal="کهکشان آندرومدا",
    ),
    # 2 Hard
    Scenario(
        key="cross_domain_hard",
        name="ترکیبی پیچیده (سخت)",
        difficulty="hard",
        concepts=[
            "بازی",
            "گرافیک",
            "موتور فیزیک",
            "هوش مصنوعی",
            "شبکه های عصبی",
            "ریاضیات",
            "منطق",
            "سخت افزار",
            "سیلیکون",
            "معدن",
        ],
        start="بازی",
        goal="معدن",
    ),
    Scenario(
        key="dense_worst_case",
        name="گراف متراکم (Worst-Case)",
        difficulty="hard",
        concepts=[f"کلمه{i}" for i in range(1, 41)],
        start="کلمه1",
        goal="کلمه40",
    ),
]


def build_graph_simple(concepts: list[str], threshold: float, top_k: int) -> SemanticGraph:
    # Same simple similarity as the web demo (character overlap)
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


def _fa_text(s: str) -> str:
    reshaped = arabic_reshaper.reshape(s)
    return get_display(reshaped)


def _configure_persian_font() -> None:
    # Try common Windows fonts that support Persian.
    preferred = ["Tahoma", "Arial", "Segoe UI", "Vazirmatn", "IRANSans", "B Nazanin"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in preferred:
        if name in available:
            rcParams["font.family"] = name
            break


def main(output_dir: str | None = None):
    _configure_persian_font()

    # Parameters used for the benchmark
    threshold = 0.65
    top_k = 3

    names: list[str] = []
    total_ms: list[float] = []
    colors: list[str] = []

    for sc in SCENARIOS:
        t0 = time.perf_counter()
        graph = build_graph_simple(sc.concepts, threshold=threshold, top_k=top_k)
        _cost, _path = graph.dijkstra(sc.start, sc.goal)
        t1 = time.perf_counter()

        names.append(_fa_text(sc.name))
        total_ms.append((t1 - t0) * 1000.0)

        if sc.difficulty == "easy":
            colors.append("#4caf50")
        elif sc.difficulty == "medium":
            colors.append("#ff9800")
        else:
            colors.append("#f44336")

    plt.figure(figsize=(14, 6))
    bars = plt.bar(names, total_ms, color=colors)
    plt.ylabel("Total time (ms) - graph build + Dijkstra")
    plt.title("Phase 2 - Runtime palette across 10 scenarios")
    plt.xticks(rotation=35, ha="right")

    for b in bars:
        y = b.get_height()
        plt.text(b.get_x() + b.get_width() / 2, y, f"{y:.1f}", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()

    out_dir = output_dir or PHASE2_DIR
    os.makedirs(out_dir, exist_ok=True)

    out_path = os.path.join(out_dir, "performance_chart.png")
    plt.savefig(out_path, dpi=160)

    print(f"Saved: {out_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    main(output_dir=args.output)
