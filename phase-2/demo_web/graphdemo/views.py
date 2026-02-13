from django.shortcuts import render

from src.semantic_graph import SemanticGraph
from src.similarity import LMStudioSimilarity
from src.analysis import AlgorithmComplexityAnalyzer, GraphMetrics

from django.http import JsonResponse
import requests
import time
import tracemalloc
import json

SCENARIOS = {
    # --- سناریوهای ساده (۴ عدد) ---
    "fruits_easy": {
        "name": "میوه‌ها (ساده)",
        "concepts": "سیب, پرتقال, موز, انبه, انگور, میوه",
        "start": "سیب",
        "goal": "میوه",
        "manual_edges": "سیب -> میوه\nپرتقال -> میوه\nموز -> میوه\nانبه -> میوه\nانگور -> میوه",
        "desc": "روابط سلسله‌مراتبی مستقیم."
    },
    "transport_easy": {
        "name": "حمل و نقل (ساده)",
        "concepts": "ماشین, دوچرخه, اتوبوس, قطار, وسیله نقلیه",
        "start": "ماشین",
        "goal": "وسیله نقلیه",
        "manual_edges": "ماشین -> وسیله نقلیه\nدوچرخه -> وسیله نقلیه\nاتوبوس -> وسیله نقلیه\nقطار -> وسیله نقلیه",
        "desc": "مسیر مستقیم حمل و نقل."
    },
    "colors_easy": {
        "name": "رنگ‌ها (ساده)",
        "concepts": "قرمز, آبی, سبز, زرد, رنگ, طیف",
        "start": "قرمز",
        "goal": "رنگ",
        "manual_edges": "قرمز -> رنگ\nآبی -> رنگ\nسبز -> رنگ\nزرد -> رنگ\nطیف -> رنگ",
        "desc": "ارتباط دسته‌ای پایه."
    },
    "family_easy": {
        "name": "خانواده (ساده)",
        "concepts": "پدر, مادر, فرزند, برادر, خواهر, خانواده",
        "start": "فرزند",
        "goal": "خانواده",
        "manual_edges": "فرزند -> خانواده\nپدر -> خانواده\nمادر -> خانواده\nبرادر -> خانواده\nخواهر -> خانواده\nپدر -> فرزند\nمادر -> فرزند",
        "desc": "سلسله‌مراتب خانوادگی."
    },
    # --- سناریوهای متوسط (۴ عدد) ---
    "ai_medium": {
        "name": "هوش مصنوعی (متوسط)",
        "concepts": "هوش مصنوعی, یادگیری ماشین, یادگیری عمیق, شبکه های عصبی, داده, الگوریتم, پردازنده گرافیکی, آموزش",
        "start": "هوش مصنوعی",
        "goal": "پردازنده گرافیکی",
        "manual_edges": "هوش مصنوعی -> یادگیری ماشین\nیادگیری ماشین -> یادگیری عمیق\nیادگیری عمیق -> شبکه های عصبی\nشبکه های عصبی -> آموزش\nآموزش -> داده\nداده -> الگوریتم\nآموزش -> پردازنده گرافیکی\nیادگیری عمیق -> پردازنده گرافیکی",
        "desc": "حوزه تکنولوژی با وابستگی‌های چندگانه."
    },
    "web_medium": {
        "name": "توسعه وب (متوسط)",
        "concepts": "فرانت اند, بک اند, پایگاه داده, رابط برنامه نویسی, ریکت, نود جی اس, مرورگر, سرور",
        "start": "فرانت اند",
        "goal": "سرور",
        "manual_edges": "فرانت اند -> مرورگر\nمرورگر -> سرور\nفرانت اند -> ریکت\nریکت -> رابط برنامه نویسی\nرابط برنامه نویسی -> بک اند\nبک اند -> سرور\nبک اند -> پایگاه داده\nنود جی اس -> بک اند",
        "desc": "مسیر توسعه وب کامل."
    },
    "eco_medium": {
        "name": "محیط زیست (متوسط)",
        "concepts": "درخت, جنگل, اکسیژن, فتوسنتز, خورشید, حیات, اتمسفر, گرمایش جهانی",
        "start": "خورشید",
        "goal": "گرمایش جهانی",
        "manual_edges": "خورشید -> فتوسنتز\nفتوسنتز -> اکسیژن\nاکسیژن -> اتمسفر\nاتمسفر -> گرمایش جهانی\nدرخت -> جنگل\nجنگل -> اکسیژن\nحیات -> اتمسفر",
        "desc": "روابط علمی زیست‌محیطی."
    },
    "disconnected_edge": {
        "name": "گره ایزوله (Edge Case)",
        "concepts": "تهران, اصفهان, شیراز, تبریز, کهکشان آندرومدا",
        "start": "تهران",
        "goal": "کهکشان آندرومدا",
        "manual_edges": "تهران -> اصفهان\nاصفهان -> شیراز\nشیراز -> تبریز",
        "desc": "تست حالتی که هیچ مسیری وجود ندارد."
    },
    # --- سناریوهای سخت (۲ عدد) ---
    "cross_domain_hard": {
        "name": "ترکیبی پیچیده (سخت)",
        "concepts": "بازی, گرافیک, موتور فیزیک, هوش مصنوعی, شبکه های عصبی, ریاضیات, منطق, سخت افزار, سیلیکون, معدن",
        "start": "بازی",
        "goal": "معدن",
        "manual_edges": "بازی -> گرافیک\nگرافیک -> سخت افزار\nسخت افزار -> سیلیکون\nسیلیکون -> معدن\nبازی -> موتور فیزیک\nموتور فیزیک -> ریاضیات\nریاضیات -> منطق\nهوش مصنوعی -> شبکه های عصبی\nشبکه های عصبی -> ریاضیات",
        "desc": "ارتباط بین حوزه‌های کاملاً متفاوت."
    },
    "dense_worst_case": {
        "name": "گراف متراکم (Worst-Case)",
        "concepts": "کلمه۱, کلمه۲, کلمه۳, کلمه۴, کلمه۵, کلمه۶, کلمه۷, کلمه۸, کلمه۹, کلمه۱۰",
        "start": "کلمه۱",
        "goal": "کلمه۱۰",
        "manual_edges": "کلمه۱ -> کلمه۲\nکلمه۱ -> کلمه۳\nکلمه۱ -> کلمه۴\nکلمه۱ -> کلمه۵\nکلمه۱ -> کلمه۶\nکلمه۱ -> کلمه۷\nکلمه۱ -> کلمه۸\nکلمه۱ -> کلمه۹\nکلمه۱ -> کلمه۱۰\nکلمه۲ -> کلمه۳\nکلمه۳ -> کلمه۴\nکلمه۴ -> کلمه۵\nکلمه۵ -> کلمه۶\nکلمه۶ -> کلمه۷\nکلمه۷ -> کلمه۸\nکلمه۸ -> کلمه۹\nکلمه۹ -> کلمه۱۰",
        "desc": "تعداد یال‌های زیاد برای فشار به الگوریتم."
    }
}

def llm_status(request):
    """Checks if LM Studio is alive."""
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=2)
        return JsonResponse({"ok": response.status_code == 200})
    except:
        return JsonResponse({"ok": False})

import time

def index(request):
    """
    Main demo page with test scenarios support and performance monitoring.
    """
    # Get theoretical complexity data
    complexity_data = AlgorithmComplexityAnalyzer.get_all_analyses()
    
    context = {
        "concepts_input": "",
        "manual_edges_input": "",
        "start": "",
        "goal": "",
        "use_llm": False,
        "threshold": 0.65,
        "top_k": 3,
        "path": None,
        "error": None,
        "scenarios": SCENARIOS,
        "algorithm": "dijkstra",
        "performance": None,
        "complexity_data": complexity_data,
        "graph_metrics": None
    }

    if request.method == "POST":
        start_total = time.perf_counter()
        tracemalloc.start()
        scenario_key = request.POST.get("scenario")
        
        # 1. Parse Inputs & Validation
        try:
            threshold = float(request.POST.get("threshold", 0.65))
            top_k = int(request.POST.get("top_k", 3))
            algorithm = request.POST.get("algorithm", "dijkstra")
            sim_mode = request.POST.get("sim_mode", "rule") # rule, llm, matrix
            
            # Algorithm specific params
            max_depth = request.POST.get("max_depth")
            max_depth = int(max_depth) if max_depth else None
            min_similarity_param = request.POST.get("min_similarity_param")
            min_similarity_param = float(min_similarity_param) if min_similarity_param else threshold
        except ValueError as e:
            return render(request, "graphdemo/index.html", {**context, "error": f"خطا در پارامترهای عددی: {str(e)}"})

        manual_edges_input = ""

        if scenario_key in SCENARIOS:
            s = SCENARIOS[scenario_key]
            concepts_input = s["concepts"]
            start = s["start"]
            goal = s["goal"]
            manual_edges_input = s.get("manual_edges", "")
            use_llm = (sim_mode == "llm")
        else:
            concepts_input = request.POST.get("concepts", "")
            manual_edges_input = request.POST.get("manual_edges", "")
            start = request.POST.get("start", "").strip()
            goal = request.POST.get("goal", "").strip()
            use_llm = (request.POST.get("sim_mode") == "llm")

        concepts = [c.strip() for c in concepts_input.split(",") if c.strip()]
        
        # Validation: check mandatory inputs
        if not concepts or len(concepts) < 2:
            context.update({"error": "حداقل دو مفهوم وارد کنید.", "concepts_input": concepts_input})
            return render(request, "graphdemo/index.html", context)
        if not start or not goal:
            context.update({"error": "مبدأ و مقصد نمی‌توانند خالی باشند.", "concepts_input": concepts_input})
            return render(request, "graphdemo/index.html", context)
        if start not in concepts or goal not in concepts:
            context.update({"error": "مبدأ و مقصد باید در لیست مفاهیم باشند.", "concepts_input": concepts_input, "start": start, "goal": goal})
            return render(request, "graphdemo/index.html", context)

        context.update({
            "concepts_input": concepts_input,
            "manual_edges_input": manual_edges_input if 'manual_edges_input' in locals() else "",
            "start": start,
            "goal": goal,
            "sim_mode": sim_mode,
            "threshold": threshold,
            "top_k": top_k,
            "algorithm": algorithm,
            "max_depth": max_depth,
            "min_similarity_param": min_similarity_param
        })

        try:
            # 2. Graph Construction
            start_graph = time.perf_counter()
            graph = SemanticGraph(similarity_threshold=threshold)
            
            # Check if manual edges are provided (ignored when sim_mode is llm)
            has_manual_edges = False
            if sim_mode != "llm" and 'manual_edges_input' in locals() and manual_edges_input.strip():
                lines = manual_edges_input.strip().split('\n')
                for line in lines:
                    if '->' in line:
                        parts = line.split('->')
                        if len(parts) == 2:
                            src_node = parts[0].strip()
                            tgt_node = parts[1].strip()
                            if src_node in concepts and tgt_node in concepts:
                                graph.add_bidirectional_edge(src_node, tgt_node, 1.0)
                                has_manual_edges = True

            if not has_manual_edges:
                # Similarity Function/Matrix logic
                if sim_mode == "matrix":
                    # Implementation for matrix input if provided (simplified for demo)
                    pass 
                
                def _normalize_text(x: str) -> str:
                    return "".join(ch for ch in x.strip().lower() if not ch.isspace())

                def _char_jaccard(a_txt: str, b_txt: str) -> float:
                    a_set = set(a_txt)
                    b_set = set(b_txt)
                    if not a_set and not b_set:
                        return 0.0
                    inter = len(a_set & b_set)
                    union = len(a_set | b_set)
                    return inter / union if union else 0.0

                def _token_overlap(a_raw: str, b_raw: str) -> float:
                    a_tokens = [t for t in a_raw.strip().lower().split() if t]
                    b_tokens = [t for t in b_raw.strip().lower().split() if t]
                    if not a_tokens and not b_tokens:
                        return 0.0
                    a_set = set(a_tokens)
                    b_set = set(b_tokens)
                    inter = len(a_set & b_set)
                    union = len(a_set | b_set)
                    return inter / union if union else 0.0

                def get_sim(a, b):
                    if sim_mode == "llm":
                        llm_sim = LMStudioSimilarity()
                        return llm_sim.compute_similarity(a, b)
                    # Rule-based: combine char-level and token-level similarity
                    a_norm = _normalize_text(a)
                    b_norm = _normalize_text(b)
                    char_sim = _char_jaccard(a_norm, b_norm)
                    token_sim = _token_overlap(a, b)
                    return max(char_sim, token_sim)

                for i, concept in enumerate(concepts):
                    similarities = []
                    for j, other in enumerate(concepts):
                        if i == j: continue
                        sim = get_sim(concept, other)
                        if sim >= threshold:
                            similarities.append((other, sim))
                    
                    similarities.sort(key=lambda x: x[1], reverse=True)
                    for target, sim in similarities[:top_k]:
                        graph.add_bidirectional_edge(concept, target, sim)
            
            end_graph = time.perf_counter()
            graph_time = (end_graph - start_graph) * 1000

            # 3. Execution & Performance
            metrics = GraphMetrics.analyze_graph_structure(graph)
            context["graph_metrics"] = metrics
            
            # Prepare data for D3.js visualization
            viz_data = {
                "nodes": [{"id": node, "group": 1} for node in graph.nodes],
                "links": []
            }
            seen_edges = set()
            for u, v, w in graph.get_all_edges():
                edge_id = tuple(sorted((u, v)))
                if edge_id not in seen_edges:
                    viz_data["links"].append({"source": u, "target": v, "value": w})
                    seen_edges.add(edge_id)
            context["viz_data_json"] = json.dumps(viz_data)

            cost, path = None, None
            nodes_visited = 0
            start_algo = time.perf_counter()

            if algorithm == "dijkstra":
                cost, path = graph.dijkstra(start, goal, min_similarity=min_similarity_param)
                nodes_visited = len(path) if path else 0
            elif algorithm == "a_star":
                # Default heuristic: 0 (Manhattan/Euclidean not applicable to words without vectors)
                cost, path = graph.a_star(start, goal, min_similarity=min_similarity_param)
                nodes_visited = len(path) if path else 0
            elif algorithm == "bfs":
                path = graph.bfs(start, max_depth=max_depth, min_similarity=min_similarity_param)
                # BFS in semantic_graph returns all reachable if goal not found, 
                # so we need to filter/re-check if goal is reached
                if goal in path:
                    # find actual path (simplified here, in real app we'd use the search results)
                    idx = path.index(goal)
                    path = path[:idx+1]
                    cost = 1.0
                else:
                    path = None
                nodes_visited = len(path) if path else 0
            elif algorithm == "floyd_warshall":
                dist, next_hop = graph.floyd_warshall(min_similarity=min_similarity_param)
                path = graph.reconstruct_path(start, goal, next_hop)
                cost = dist.get((start, goal), 0) if path else None
                nodes_visited = len(graph.nodes)

            end_algo = time.perf_counter()
            algo_time = (end_algo - start_algo) * 1000
            
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            stats = graph.get_statistics()
            context["performance"] = {
                "graph_construction_ms": f"{graph_time:.2f}",
                "algorithm_execution_ms": f"{algo_time:.2f}",
                "total_ms": f"{(time.perf_counter() - start_total)*1000:.2f}",
                "num_nodes": stats["num_nodes"],
                "num_edges": stats["num_edges"],
                "nodes_visited": nodes_visited,
                "memory_kb": f"{peak_mem / 1024:.2f}"
            }

            if path:
                context["path"] = path
                context["cost"] = f"{cost:.4f}" if cost is not None else "N/A"
            else:
                context["error"] = "هیچ مسیر معنایی بین این مفاهیم پیدا نشد."

        except Exception as e:
            tracemalloc.stop()
            context["error"] = f"Error: {str(e)}"
            return render(request, "graphdemo/index.html", context)

    return render(request, "graphdemo/index.html", context)

    return render(request, "graphdemo/index.html", context)


